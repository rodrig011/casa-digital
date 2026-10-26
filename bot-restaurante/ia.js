// Modo IA (Claude): entiende mensajes libres ("me da 2 combos de 3 piezas para las 7, a nombre de Ana").
// Claude conversa; el menú, los precios, las sucursales y los pedidos salen de negocios/<cliente>.json
// por medio de herramientas, así nunca inventa un precio. Si la API falla, server.js usa el menú de siempre.
//
//   const ia = createIA({ negocio, apiKey, model });          // o { client } para pruebas sin internet
//   const r = await ia.turn(history, texto, now, { numero: () => "PED-1001", faltas: 0 });
//   r = { reply, history, pedido?, persona? }
const { cuenta, requiereCobro, textoCobro } = require("./negocio");

const MODELO = "claude-haiku-5-5";
const MAX_TURNOS = 20;          // mensajes del cliente que se guardan en la sesión
const MAX_VUELTAS = 5;          // llamadas a la API por mensaje (herramientas incluidas)

function system(N) {
  const apps = (N.domicilio.apps || []).map(a => a.nombre + (a.url ? ` (${a.url})` : "")).join(", ");
  return `Usted es el asistente de WhatsApp de ${N.nombre}, un restaurante en ${N.pais}. Atiende a clientes que preguntan por el menú, los precios, las sucursales, o que quieren hacer un pedido para recoger.

Cómo escribe:
- Español de ${N.pais}, trato de usted, cálido y rápido.
- Mensajes cortos de WhatsApp: 1 a 5 líneas. Una pregunta a la vez.
- Para resaltar use *asteriscos* (negrita de WhatsApp). Sin títulos ni tablas.

Lo que sabe del restaurante (no afirme nada más):
- Menú, precios, sucursales, direcciones, teléfonos y horarios: solo lo que devuelven las herramientas ver_menu y sucursales. Si un horario viene vacío, diga que una persona de la sucursal se lo confirma.
- ${N.domicilio.propio ? "Hace envíos a domicilio: una persona le confirma el costo y el tiempo." : `No tiene envío propio.${apps ? ` A domicilio se pide por ${apps}.` : ""} Aquí se toman pedidos para recoger.`}
- ${N.pago ? "Pago: " + N.pago : "La forma de pago la confirma una persona de la sucursal."}
${N.tiempoPreparacion ? `- Tiempo aproximado de preparación: ${N.tiempoPreparacion}.\n` : ""}
Cómo toma un pedido para recoger:
- Use ver_menu antes de nombrar productos o precios. Use los nombres exactos del menú.
- Necesita: los productos y cantidades, ${N.variasSucursales ? "la sucursal donde lo recoge, " : ""}la hora en que pasa y el nombre.
- Antes de crear el pedido, repita el detalle con el total y pida que lo confirme.
- Cuando confirme, llame a crear_pedido una sola vez y dé el número de pedido que le devuelve. Diga que le avisan por este chat cuando esté listo.
- Si crear_pedido devuelve "cobro", el pedido no va a cocina hasta que se pague: copie esos datos de pago tal cual, sin cambiarlos, y pida la foto del comprobante por este chat.
- Nunca calcule ni invente precios, promociones ni descuentos: el total sale de crear_pedido o de los precios de ver_menu.

Límites:
- No invente enlaces ni cuentas de pago: solo los que devuelve crear_pedido. No prometa envíos, reservaciones ni nada que no le dé una herramienta.
- Si el cliente quiere hablar con una persona, tiene una queja, o pide algo que usted no puede resolver, use pasar_a_persona.
- Si le escriben de algo que no tiene que ver con el restaurante, responda con amabilidad que solo puede ayudar con el menú y los pedidos.`;
}

function tools(N) {
  const suc = { type: "string", enum: N.sucursales.map(s => s.id), description: "Sucursal: " + N.sucursales.map(s => `${s.id} = ${s.nombre}`).join(", ") };
  return [
    { name: "ver_menu", description: "Menú completo con id, nombre exacto, categoría, descripción y precio con su moneda.", input_schema: { type: "object", properties: {}, additionalProperties: false } },
    { name: "sucursales", description: "Sucursales con dirección, teléfono y horario.", input_schema: { type: "object", properties: {}, additionalProperties: false } },
    {
      name: "crear_pedido",
      description: "Crea el pedido para recoger y lo manda a la cocina y al dueño. Devuelve el número y el total. Llámela una sola vez, cuando el cliente ya confirmó.",
      input_schema: {
        type: "object",
        properties: {
          nombre: { type: "string", description: "Nombre del cliente" },
          ...(N.variasSucursales ? { sucursal: suc } : {}),
          productos: { type: "array", items: { type: "object", properties: { id: { type: "string", description: "id del producto según ver_menu" }, cantidad: { type: "integer" }, nota: { type: "string", description: "Indicación del cliente, por ejemplo: sin cebolla" } }, required: ["id", "cantidad"], additionalProperties: false } },
          hora: { type: "string", description: "Cuándo pasa a recogerlo, por ejemplo: lo antes posible, 7:00 p. m." },
        },
        required: ["nombre", "productos", "hora", ...(N.variasSucursales ? ["sucursal"] : [])],
        additionalProperties: false,
      },
    },
    { name: "pasar_a_persona", description: "Avisa a una persona del restaurante para que le escriba al cliente por este chat.", input_schema: { type: "object", properties: { motivo: { type: "string", description: "Por qué, en pocas palabras" }, ...(N.variasSucursales ? { sucursal: suc } : {}) }, required: ["motivo"], additionalProperties: false } },
  ];
}

function ejecutar(N, name, input, ctx) {
  const b = id => N.sucursales.find(s => s.id === id) || N.sucursales[0];
  switch (name) {
    case "ver_menu": return { menu: N.items.map(i => ({ id: i.id, nombre: i.nombre, categoria: i.categoria, ...(i.desc ? { descripcion: i.desc } : {}), precio: N.L(i.precio) })) };
    case "sucursales": return { sucursales: N.sucursales.map(s => ({ id: s.id, nombre: s.nombre, direccion: s.direccion || "", telefono: s.telefono || "", horario: s.horario || "Por confirmar: una persona de la sucursal lo confirma.", ...(s.mapa ? { mapa: s.mapa } : {}) })) };
    case "crear_pedido": {
      if (ctx.pedido) return { error: "Ya se creó el pedido en este mensaje.", numero: ctx.pedido.n };
      const malos = (input.productos || []).filter(p => !N.items.some(i => i.id === p.id)).map(p => p.id);
      if (malos.length) return { error: "Estos id no están en el menú: " + malos.join(", ") + ". Use ver_menu." };
      const c = cuenta(N, input.productos);
      if (!c.lineas.length) return { error: "El pedido no tiene productos." };
      const s = b(input.sucursal);
      const nombre = String(input.nombre || "").trim().slice(0, 60).replace(/^\p{L}/u, x => x.toUpperCase()) || null;
      ctx.pedido = { tipo: "pedido", n: ctx.numero ? ctx.numero() : null, nombre, sucursal: s.nombre, sucursalId: s.id, lineas: c.lineas, total: c.total, hora: String(input.hora || "").slice(0, 60), resumen: c.lineas.map(l => `${l.cantidad} × ${l.nombre}`).join(" · ") };
      const base = { ok: true, numero: ctx.pedido.n, total: N.L(c.total), detalle: c.lineas.map(l => `${l.cantidad} × ${l.nombre}${l.nota ? ` (${l.nota})` : ""}: ${N.L(l.subtotal)}`), sucursal: s.nombre };
      if (requiereCobro(N, c.total, ctx.faltas || 0)) {
        ctx.pedido.estado = "por_pagar";
        return { ...base, cobro: textoCobro(N, ctx.pedido.n, c.total), nota: "Todavía NO va a cocina: se paga antes. Pásele los datos de cobro tal cual y pídale la foto del comprobante por este chat. Cuando se confirme el pago entra a cocina y se le avisa." };
      }
      return { ...base, ...(N.pago ? { pago: N.pago } : {}), nota: "La cocina ya lo tiene. Se le avisa por este chat cuando esté listo." };
    }
    case "pasar_a_persona": {
      const s = b(input.sucursal);
      ctx.persona = { motivo: String(input.motivo || "").slice(0, 200), sucursal: s.nombre };
      return { ok: true, sucursal: s.nombre, telefono: s.telefono || "", nota: "Una persona le escribe por este chat." };
    }
    default: return { error: "Herramienta desconocida: " + name };
  }
}

// keep the last MAX_TURNOS customer messages, starting at a customer message (never at a tool_result)
function recortar(h) {
  const inicios = h.map((m, i) => (m.role === "user" && (typeof m.content === "string" || m.content.some(b => b.type === "text")) ? i : -1)).filter(i => i >= 0);
  return inicios.length > MAX_TURNOS ? h.slice(inicios[inicios.length - MAX_TURNOS]) : h;
}
// thinking blocks only matter inside the turn that produced them; dropping them lets us trim history safely
const sinPensar = m => (m.role === "assistant" && Array.isArray(m.content) ? { ...m, content: m.content.filter(b => b.type !== "thinking" && b.type !== "redacted_thinking") } : m);

function fecha(now) {
  return new Date(now || Date.now()).toLocaleString("es-HN", { timeZone: "America/Tegucigalpa", weekday: "long", day: "numeric", month: "long", hour: "numeric", minute: "2-digit" });
}

function createIA({ negocio, apiKey, model, client, timeoutMs = 11000, maxTokens = 2048 } = {}) {
  if (!client) {
    const Anthropic = require("@anthropic-ai/sdk");
    client = new Anthropic({ apiKey, maxRetries: 1, timeout: timeoutMs });
  }
  model = model || MODELO;
  const SYSTEM = system(negocio), TOOLS = tools(negocio);

  async function turn(history, text, now, { numero, faltas = 0 } = {}) {
    const ctx = { numero, faltas, pedido: null, persona: null };
    const base = recortar((history || []).map(sinPensar));
    const nuevo = [{ role: "user", content: [{ type: "text", text: String(text || "").slice(0, 2000) || "(mensaje vacío)" }, { type: "text", text: `[Fecha y hora en ${negocio.pais}: ${fecha(now)}]` }] }];
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), timeoutMs);
    try {
      for (let vuelta = 0; vuelta < MAX_VUELTAS; vuelta++) {
        const r = await client.messages.create({
          model,
          max_tokens: maxTokens,
          output_config: { effort: "low" },
          system: [{ type: "text", text: SYSTEM, cache_control: { type: "ephemeral" } }],   // caches tools + system
          tools: TOOLS,
          cache_control: { type: "ephemeral" },                                               // and the conversation so far
          messages: base.concat(nuevo),
        }, { signal: ac.signal });
        if (r.stop_reason === "refusal") throw new Error("Claude declinó responder (refusal)");
        nuevo.push({ role: "assistant", content: r.content });
        const usos = r.content.filter(b => b.type === "tool_use");
        if (r.stop_reason === "tool_use" && usos.length) {
          nuevo.push({ role: "user", content: usos.map(u => {
            let out;
            try { out = ejecutar(negocio, u.name, u.input || {}, ctx); } catch (e) { out = { error: e.message }; }
            return { type: "tool_result", tool_use_id: u.id, content: JSON.stringify(out), ...(out && out.error ? { is_error: true } : {}) };
          }) });
          continue;
        }
        if (r.stop_reason === "pause_turn") continue;
        const reply = r.content.filter(b => b.type === "text").map(b => b.text).join("\n").trim();
        if (!reply) throw new Error(`respuesta vacía (stop_reason ${r.stop_reason})`);
        return { reply, history: recortar(base.concat(nuevo).map(sinPensar)), pedido: ctx.pedido, persona: ctx.persona, usage: r.usage };
      }
      throw new Error(`más de ${MAX_VUELTAS} llamadas a la API en un mensaje`);
    } catch (e) {
      // an order already created in this message must not be lost: server.js saves it anyway
      e.pedido = ctx.pedido; e.persona = ctx.persona;
      throw e;
    } finally { clearTimeout(timer); }
  }

  return { model, turn, SYSTEM, TOOLS };
}

module.exports = { createIA, MODELO, ejecutar, system, tools };
