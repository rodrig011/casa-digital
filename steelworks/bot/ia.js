// Modo IA (Claude): entiende mensajes libres ("quiero un portón de unos 3 metros, cuánto sale?").
// Claude conversa; los precios, las piezas, las sucursales y las fichas salen de engine.js por medio
// de herramientas, así nunca inventa un precio. Si la API falla, server.js usa el menú de siempre.
//
//   const ia = createIA({ apiKey, model });          // o { client } para pruebas sin internet
//   const r = await ia.turn(history, texto, now, { numero: () => "COT-2215" });
//   r = { reply, history, lead?, persona?, motivo?, sucursal? }
const E = require("./engine");

const MODELO = "claude-haiku-5-5";
const MAX_TURNOS = 20;          // mensajes del cliente que se guardan en la sesión
const MAX_VUELTAS = 5;          // llamadas a la API por mensaje (herramientas incluidas)

const lps = n => "L " + Math.round(n).toLocaleString("es-HN");
const SIN_CODIGO = p => p.name.replace(" " + p.code, "").trim();
const SUC = k => (/sps|pedro/i.test(String(k || "")) ? "SPS" : "TGU");

const SYSTEM = `Usted es el asistente de WhatsApp de Steel Works Honduras, empresa de herrería y hierro forjado. Atiende a clientes que quieren cotizar portones, puertas, protecciones de ventanas, barandas o balcones, o comprar piezas para herrería.

Cómo escribe:
- Español de Honduras, trato de usted, cálido pero profesional.
- Mensajes cortos de WhatsApp: 1 a 4 líneas. Una pregunta a la vez.
- Para resaltar use *asteriscos* (negrita de WhatsApp). Sin títulos, tablas ni listas largas.

Lo que sabe de Steel Works (no afirme nada más sobre la empresa):
- Más de 40 años de experiencia y una planta de 2,000 m² en Tegucigalpa.
- Sucursales en Tegucigalpa y San Pedro Sula; direcciones y teléfonos con la herramienta sucursales.
- El horario no está confirmado: si se lo preguntan, diga que una persona de la sucursal se lo confirma.
- La visita para medir no tiene costo.

Cómo cotiza:
- Para dar un precio necesita el tipo de trabajo, las medidas aproximadas (ancho y alto en metros; para barandas, metros de largo) y el estilo: Moderno (líneas rectas, perfil negro), Forjado clásico (barrotes con lanzas y volutas) o Calado CNC (lámina cortada con diseño). Si no sabe el estilo, ofrézcale los tres.
- Solo dé precios que le devuelva la herramienta estimar_precio, como rango en lempiras. Diga siempre que es un *precio estimado* y que el precio exacto se da después de medir, sin costo. Nunca calcule ni invente precios por su cuenta.
- El estimado incluye fabricación, pintura e instalación en Tegucigalpa o San Pedro Sula; en otras ciudades se suma el traslado.
- Si el cliente no sabe las medidas, no hay problema: ofrezca la visita para medir.

Cómo agenda:
- Para agendar la visita pida el nombre, la ciudad o zona y el día y la hora que le quedan bien. Use la sucursal de San Pedro Sula para la zona norte (San Pedro Sula, Choloma, Villanueva, El Progreso, Puerto Cortés, La Lima, Tela, La Ceiba, Santa Bárbara, Copán) y la de Tegucigalpa para lo demás.
- Cuando tenga esos datos llame a agendar_visita una sola vez y luego confirme con el número de cotización que le devuelve. Diga que la sucursal le confirma la cita por este mismo chat.

Piezas para herrería:
- Use buscar_piezas. Describa las piezas por su nombre y categoría con su precio y si hay existencia; no empiece por el código del producto (déselo solo si el cliente lo pide). La tienda tiene más de 750 piezas: si no aparece, pida una foto y ofrezca que un asesor le confirme.

Límites:
- No prometa enlaces de pago, descuentos, tiempos de entrega ni nada que no le dé una herramienta.
- Si el cliente quiere hablar con una persona, está molesto, o pide algo que usted no puede resolver, ofrézcale pasarlo con un asesor y use pasar_a_persona.
- Si le escriben de algo que no tiene que ver con Steel Works, responda con amabilidad que solo puede ayudar con cotizaciones y piezas de Steel Works.`;

const TIPO = { type: "string", enum: ["porton", "puerta", "ventana", "baranda"], description: "porton = portón; puerta; ventana = protección de ventanas; baranda = baranda, balcón o pasamanos" };
const ESTILO = { type: "string", enum: E.ESTILOS.map(e => e.key), description: "moderno, forjado (forjado clásico) o cnc (calado CNC)" };
const MEDIDAS = {
  ancho: { type: "number", description: "Ancho en metros (portón, puerta, ventana)" },
  alto: { type: "number", description: "Alto en metros (portón, puerta, ventana)" },
  metros: { type: "number", description: "Metros lineales (solo baranda)" },
  cantidad: { type: "integer", description: "Cuántas piezas iguales (por ejemplo, número de ventanas). Por defecto 1" },
  motor: { type: "boolean", description: "Portón con motor eléctrico" },
};

const TOOLS = [
  {
    name: "estimar_precio",
    description: "Calcula el rango de precio estimado en lempiras con las tarifas de Steel Works. Úsela siempre antes de dar un precio. Sin estilo devuelve el rango del más sencillo al más elaborado.",
    input_schema: { type: "object", properties: { tipo: TIPO, estilo: ESTILO, ...MEDIDAS }, required: ["tipo"], additionalProperties: false },
  },
  {
    name: "buscar_piezas",
    description: "Busca piezas para herrería en el catálogo (adornos de barra, adornos de poste, llamadores, tubos forjados, accesorios). Devuelve nombre, categoría, precio con IVA y si hay existencia.",
    input_schema: { type: "object", properties: { texto: { type: "string", description: "Lo que busca el cliente, por ejemplo: llamador, adorno, tubo" }, categoria: { type: "string", description: "Categoría, si la sabe" } }, additionalProperties: false },
  },
  {
    name: "sucursales",
    description: "Direcciones y teléfonos de las sucursales de Steel Works.",
    input_schema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "agendar_visita",
    description: "Crea la ficha del cliente y agenda la visita para medir. La ficha le llega al dueño y a la sucursal. Llámela una sola vez, cuando tenga nombre, tipo de trabajo, sucursal y día u hora preferidos.",
    input_schema: {
      type: "object",
      properties: {
        nombre: { type: "string", description: "Nombre del cliente" },
        tipo: TIPO,
        medidas: { type: "string", description: "Medidas como las dijo el cliente, o 'por medir'" },
        ...MEDIDAS,
        estilo: ESTILO,
        acabado: { type: "string", description: "Color o acabado, si lo dijo" },
        sucursal: { type: "string", enum: ["TGU", "SPS"], description: "TGU = Tegucigalpa, SPS = San Pedro Sula" },
        cuando: { type: "string", description: "Día y hora preferidos para la visita, por ejemplo: miércoles 14 en la mañana" },
        zona: { type: "string", description: "Ciudad, colonia o zona de la instalación" },
      },
      required: ["nombre", "tipo", "sucursal", "cuando"],
      additionalProperties: false,
    },
  },
  {
    name: "pasar_a_persona",
    description: "Avisa a un asesor de Steel Works para que le escriba al cliente por este chat. Úsela cuando el cliente lo pida o cuando usted no pueda ayudarle.",
    input_schema: { type: "object", properties: { motivo: { type: "string", description: "Por qué, en pocas palabras" }, sucursal: { type: "string", enum: ["TGU", "SPS"] } }, required: ["motivo"], additionalProperties: false },
  },
];

// same numbers engine.js uses: TARIFAS × medidas (cm if > 20), + motor, rounded to L 100
function estimar(i) {
  const T = E.TIPOS[i.tipo];
  if (!T) return { error: "Tipo desconocido. Use porton, puerta, ventana o baranda." };
  const cm = n => (n > 20 ? n / 100 : n);
  const med = T.unidad === "ml" ? [cm(+i.metros || +i.ancho || 0)] : [cm(+i.ancho || 0), cm(+i.alto || 0)];
  if (med.some(n => !(n > 0))) return { error: T.unidad === "ml" ? "Faltan los metros de largo." : "Faltan el ancho y el alto en metros." };
  const d = { tipo: i.tipo, med, cuantas: Math.max(1, Math.round(+i.cantidad || 1)), motor: i.tipo === "porton" && !!i.motor };
  const estilos = i.estilo && E.TARIFAS[i.tipo][i.estilo] ? [i.estilo] : ["moderno", "cnc"];
  const [lo, , cant] = E.estimado({ ...d, estilo: estilos[0] });
  const [, hi] = E.estimado({ ...d, estilo: estilos[estilos.length - 1] });
  return { rango: [lo, hi], texto: `${lps(lo)} a ${lps(hi)}`, d: { ...d, estilo: i.estilo || null }, cant };
}

function buscarPiezas({ texto, categoria } = {}) {
  const q = E.norm([texto, categoria].filter(Boolean).join(" ")).split(/\s+/).filter(w => w.length > 2).map(w => w.replace(/(es|s)$/, ""));
  const hay = p => { const h = E.norm(p.name + " " + p.cat); return !q.length || q.some(w => h.includes(w)); };
  const found = E.CATALOGO.filter(hay);
  const lista = [...(found.length ? found : E.CATALOGO)].sort((a, b) => b.stock - a.stock || a.price - b.price).slice(0, 8);
  return {
    encontradas: found.length,
    piezas: lista.map(p => ({ nombre: SIN_CODIGO(p), categoria: p.cat, precio: E.L(p.price), existencia: p.stock ? "sí" : "agotada", codigo: p.code })),
    nota: "Precios con IVA. Es un extracto: la tienda tiene más de 750 piezas; para otras, pida una foto y un asesor confirma precio y existencia.",
  };
}

function ejecutar(name, input, ctx) {
  switch (name) {
    case "estimar_precio": {
      const r = estimar(input);
      if (r.error) return r;
      return { rango_lempiras: r.texto, cantidad: `${Math.round(r.cant * 100) / 100} ${E.TIPOS[input.tipo].unidad === "ml" ? "metros lineales" : "m²"}`, estilo: r.d.estilo || "sin escoger (rango del moderno al calado CNC)", incluye: "fabricación, pintura e instalación en Tegucigalpa o San Pedro Sula; fuera de esas ciudades se suma el traslado", aviso: "Es un precio estimado; el precio exacto se da después de medir, sin costo." };
    }
    case "buscar_piezas": return buscarPiezas(input);
    case "sucursales":
      return { sucursales: Object.values(E.SUCURSALES).map(b => ({ nombre: b.nombre, direccion: b.dir, telefonos: b.tel })), horario: "Por confirmar: una persona de la sucursal confirma el horario." };
    case "agendar_visita": {
      if (ctx.lead) return { error: "Ya se agendó en este mensaje.", numero: ctx.lead.n };
      const T = E.TIPOS[input.tipo];
      if (!T) return { error: "Tipo desconocido." };
      const est = estimar(input);
      const d = est.error ? { tipo: input.tipo, estilo: input.estilo || null, motor: input.tipo === "porton" && !!input.motor } : { ...est.d };
      d.ciudad = input.zona || null;
      const sucursal = E.SUCURSALES[SUC(input.sucursal)];
      let resumen = E.resumen(d).replace(/\n/g, " · ");
      if (est.error && input.medidas) resumen = resumen.replace("Medidas: por medir", `Medidas: ${input.medidas}`);
      if (input.acabado) resumen += ` · Acabado: ${input.acabado}`;
      const nombre = String(input.nombre || "").trim().replace(/^\w/, c => c.toUpperCase()) || null;
      ctx.lead = { n: ctx.numero ? ctx.numero() : null, nombre, resumen, rango: est.error || !input.estilo ? null : est.rango, cita: `Visita para medir: ${input.cuando}`, sucursal: sucursal.nombre };
      return { ok: true, numero: ctx.lead.n, sucursal: sucursal.nombre, telefono: sucursal.tel[0], nota: "Ficha enviada a la sucursal; le confirman la cita por este chat." };
    }
    case "pasar_a_persona": {
      const b = E.SUCURSALES[SUC(input.sucursal)];
      ctx.persona = { motivo: String(input.motivo || "").slice(0, 200), sucursal: b.nombre };
      return { ok: true, sucursal: b.nombre, telefono: b.tel[0], nota: "Un asesor le escribe por este chat en horario de tienda." };
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
  const d = new Date(now || Date.now());
  return d.toLocaleString("es-HN", { timeZone: "America/Tegucigalpa", weekday: "long", day: "numeric", month: "long", year: "numeric", hour: "numeric", minute: "2-digit" });
}

function createIA({ apiKey, model, client, timeoutMs = 11000, maxTokens = 2048 } = {}) {
  if (!client) {
    const Anthropic = require("@anthropic-ai/sdk");
    client = new Anthropic({ apiKey, maxRetries: 1, timeout: timeoutMs });
  }
  model = model || MODELO;

  async function turn(history, text, now, { numero } = {}) {
    const ctx = { numero, lead: null, persona: null };
    const base = recortar((history || []).map(sinPensar));
    const nuevo = [{ role: "user", content: [{ type: "text", text: String(text || "").slice(0, 2000) || "(mensaje vacío)" }, { type: "text", text: `[Fecha y hora en Honduras: ${fecha(now)}]` }] }];
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
            try { out = ejecutar(u.name, u.input || {}, ctx); } catch (e) { out = { error: e.message }; }
            return { type: "tool_result", tool_use_id: u.id, content: JSON.stringify(out), ...(out && out.error ? { is_error: true } : {}) };
          }) });
          continue;
        }
        if (r.stop_reason === "pause_turn") continue;
        const reply = r.content.filter(b => b.type === "text").map(b => b.text).join("\n").trim();
        if (!reply) throw new Error(`respuesta vacía (stop_reason ${r.stop_reason})`);
        return {
          reply,
          history: recortar(base.concat(nuevo).map(sinPensar)),
          lead: ctx.lead,
          persona: !!ctx.persona,
          ...(ctx.persona || {}),
          usage: r.usage,
        };
      }
      throw new Error(`más de ${MAX_VUELTAS} llamadas a la API en un mensaje`);
    } catch (e) {
      // a ficha already created in this message must not be lost: server.js saves it anyway
      e.lead = ctx.lead; e.persona = ctx.persona;
      throw e;
    } finally { clearTimeout(timer); }
  }

  return { model, turn };
}

module.exports = { createIA, SYSTEM, TOOLS, MODELO, estimar, buscarPiezas, ejecutar };
