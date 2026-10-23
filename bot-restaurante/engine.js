// Bot de WhatsApp para restaurantes (motor de conversación con menú de opciones).
// createEngine(negocio).handle(state, text, now, ctx?) -> { state, messages: [{ text, buttons? }] }
//   ctx.faltas = veces que este número no vino a recoger (server.js lo cuenta); decide si paga antes
//
// La idea: que ningún cliente se quede sin respuesta. El bot muestra el menú con precios, toma el
// pedido para recoger, da sucursales y horario, explica cómo pedir a domicilio y pasa a una persona
// cuando el cliente lo pide. Cada pedido terminado sale en state.lead y server.js lo guarda y avisa.
// Si el negocio cobra antes (negocio.cobro), el pedido sale "por_pagar": no va a cocina hasta que se confirme el pago.
// Todo lo que dice del negocio sale de negocios/<cliente>.json (ver negocio.js).
const { cuenta, lineaTexto, requiereCobro, textoCobro, norm, L } = require("./negocio");

const SALUDO = /^(hola|holi|buenas|buen dia|buenos dias|buenas tardes|buenas noches|hey|menu principal|inicio|0)[\s!.,]*$/;
const quierePersona = t => /persona|asesor|humano|alguien|encargad|gerente|hablar con|me llamen|queja|reclamo/.test(t);
const quiereDomicilio = t => /domicilio|delivery|envio|enviar|envian|llevan|a mi casa|pedidos ?ya|bip ?bip|motorista|repartidor/.test(t);
const quiereSucursal = t => /donde|ubicacion|ubicados|direccion|sucursal|horario|abren|cierran|abierto|mapa|como llego/.test(t);
const quiereMenu = t => /menu|precio|cuanto|cuesta|vale|valen|combo|carta|que tienen|que venden/.test(t);
const quierePedir = t => /pedir|pedido|ordenar|orden|quiero|me da|me das|recoger|para llevar|apartar/.test(t);

const HORAS = ["Lo antes posible", "En 30 minutos", "En 1 hora", "Otra hora"];

function createEngine(negocio) {
  const N = negocio;
  const MENU = ["Ver el menú y precios", "Hacer un pedido para recoger", "Sucursales y horario", "Pedir a domicilio", "Hablar con una persona"];

  // numbered menu, grouped by category; corto = one line per product (for the cart step)
  function menuTexto(corto) {
    return N.menu.map(c => `*${c.categoria}*\n` + (c.items || []).map(i => {
      const it = N.items.find(x => x.id === i.id);
      return `${it.num}. ${it.nombre} · ${L(it.precio)}${!corto && it.desc ? `\n    ${it.desc}` : ""}`;
    }).join("\n")).join("\n\n");
  }
  function sucursalesTexto() {
    return N.sucursales.map(s => [`📍 *${s.nombre}*`, s.direccion, s.telefono ? `Tel. ${s.telefono}` : null, `🕗 ${s.horario || "Horario: se lo confirma una persona de la sucursal."}`, s.mapa || null].filter(Boolean).join("\n")).join("\n\n");
  }
  function domicilioTexto() {
    const apps = (N.domicilio.apps || []).filter(a => a.nombre);
    const lista = apps.map(a => `• ${a.nombre}${a.url ? `: ${a.url}` : ""}`).join("\n");
    return `Por ahora no tenemos envío propio.${apps.length ? ` A domicilio puede pedirnos por:\n${lista}` : ""}\n\nTambién puede hacer su pedido aquí y pasar a recogerlo sin hacer fila.`;
  }

  // "1 x2, 4", "2 del 3", "2 combos 3 piezas", "papas grandes y un refresco", "el combo 1 con 4 papas"
  // one piece of the order -> { it, cantidad, n } (n = list number the customer used, if any)
  const RELLENO = new Set(["x", "numero", "no", "orden", "pedido", "porcion", "solo", "nada", "mas", "tambien", "regaleme", "mandeme", "das", "mi", "favor", "y", "con"]);
  // every word the customer wrote is explained by the product, the quantity or the list number
  const completo = (p, r) => {
    const nombre = new Set(N.tokens(r.it.nombre));
    return N.tokens(p).every(w => nombre.has(w) || RELLENO.has(w) || w === String(r.cantidad) || w === r.n);
  };
  function uno(p) {
    const l = p.replace(/^(?:(?:quiero|me da|me das|deme|dame|regaleme|mandeme|para mi|y|con)\s+)+/, "");
    let m, r = null;
    if ((m = l.match(/^(?:el |la |numero |#)?(\d+)\s*(?:x|×|\*|por)\s*(\d+)$/))) r = { it: N.item(m[1]), n: m[1], cantidad: +m[2] };
    else if ((m = l.match(/^(\d+)\s*(?:del?|de la)\s*(?:numero |#)?(\d+)$/))) r = { it: N.item(m[2]), n: m[2], cantidad: +m[1] };
    else if ((m = l.match(/^(?:el |la |numero |#)(\d+)$/)) || (m = p.match(/^(\d+)$/))) r = { it: N.item(m[1]), n: m[1], cantidad: 1 };
    if (r) return r.it ? r : null;
    // a quantity in front wins over a number that is part of the name ("2 refrescos" = two Refresco 2 litros)
    const ops = [];
    let it;
    if ((m = l.match(/^(\d+)\s+(.+)$/)) && (it = N.item(m[2]))) ops.push({ it, cantidad: +m[1], n: null });
    // "combo 1", "2 combo numero 1": a word of the product plus its number in the list
    if ((m = l.match(/^(?:(\d+)\s+)?([a-z][a-z\s]*?)\s*(?:numero |no |#)?(\d+)$/)) && (it = N.item(m[3]))) {
      const w = N.tokens(m[2]), nombre = N.tokens(it.nombre);
      if (w.length && w.every(x => nombre.includes(x))) ops.push({ it, cantidad: m[1] ? +m[1] : 1, n: m[3] });
    }
    if ((m = l.match(/^(.+?)\s*(?:x|×)\s*(\d+)$/)) && (it = N.item(m[1]))) ops.push({ it, cantidad: +m[2], n: null });
    if ((it = N.item(l))) ops.push({ it, cantidad: 1, n: null });
    return ops.find(o => completo(p, o)) || ops[0] || null;
  }
  const conectores = s => s.replace(/^(?:con|y|mas|tambien|ademas)\s+/, "").trim();
  // a piece with two products and no comma ("el combo 1 con 4 papas") is cut where both halves make sense,
  // trying the longest first half first
  function partir(p, hondo) {
    const r = uno(p);
    if (r && completo(p, r)) return [r];
    const w = p.split(/\s+/);
    if (hondo < 3) for (let i = w.length - 1; i >= 1; i--) {
      const a = conectores(w.slice(0, i).join(" ")), b = conectores(w.slice(i).join(" "));
      if (!a || !b) continue;
      const ra = uno(a);
      if (!ra || !completo(a, ra)) continue;
      const rb = partir(b, hondo + 1);
      if (rb) return [ra, ...rb];
    }
    return hondo ? null : r ? [r] : null;
  }
  // last try: "pizza con papas" -> papas, and pizza is asked about
  const porConector = p => p.split(/\s+(?:con|y)\s+/).map(conectores).filter(Boolean);
  const NUMEROS = ["dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"];
  function leerPedido(text) {
    const encontrados = [], dudas = [];
    const partes = norm(text).replace(/\bun[oa]?\s+(?=[a-z])/g, "1 ").replace(/\b(dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\b/g, w => String(NUMEROS.indexOf(w) + 2)).split(/,|;|\n|\+|\by\b|\btambien\b|\bmas\b/).map(p => p.replace(/[^\w\s#×*]/g, " ").replace(/\s+/g, " ").trim()).filter(Boolean);
    for (const p of partes) {
      let rs = partir(p, 0);
      if (rs && rs.length === 1 && !completo(p, rs[0]) && porConector(p).length > 1) {
        rs = [];
        for (const q of porConector(p)) { const r = partir(q, 0); if (r) rs.push(...r); else if (q.length > 1) dudas.push(q); }
      }
      if (rs) rs.forEach(r => encontrados.push({ id: r.it.id, cantidad: r.cantidad }));
      else if (p.length > 1) dudas.push(p);
    }
    return { encontrados, dudas };
  }

  function fresh() { return { step: "inicio", data: {}, seq: 1000 }; }

  // match a reply against the buttons we offered: by number or label
  function pick(text, options) {
    const t = norm(text).replace(/[^\w\s]/g, "").trim();
    if (/^\d+$/.test(t)) return options[+t - 1] || null;
    return options.find(o => norm(o) === norm(text)) || options.find(o => t.length > 2 && norm(o).startsWith(t)) || null;
  }

  function handle(state, input, now, ctx = {}) {
    const s = state ? JSON.parse(JSON.stringify(state)) : fresh();
    const text = (input || "").toString();
    const t = norm(text);
    const out = [];
    const offered = s.offer || [];
    s.offer = null;
    const say = m => { m = typeof m === "string" ? { text: m } : m; if (m.buttons) s.offer = m.buttons; out.push(m); };
    const go = step => { s.step = step; };
    let d = s.data;
    const reset = o => { s.data = d = o || {}; };
    const done = () => ({ state: s, messages: out });

    const menuInicio = pre => say({ text: (pre ? pre + "\n\n" : "") + "¿En qué le ayudo?", buttons: MENU });
    const carritoTexto = () => { const c = cuenta(N, d.carrito); return c.lineas.map(lineaTexto).join("\n") + `\n\n*Total: ${L(c.total)}*`; };
    const pedirSucursal = (siguiente, pregunta) => {
      if (!N.variasSucursales) { d.sucursal = N.sucursales[0].id; return false; }
      d.despues = siguiente; go("sucursal");
      say({ text: pregunta, buttons: N.sucursales.map(x => x.nombre) });
      return true;
    };
    const pedirProductos = () => {
      go("carrito");
      say(`¿Qué le preparamos? Escriba el número y la cantidad, por ejemplo *1 x2* (dos del número 1). Puede pedir varios separados por coma.\n\n${menuTexto(true)}`);
    };
    const mostrarCarrito = pre => {
      go("carrito_ok");
      say({ text: `${pre ? pre + "\n\n" : ""}🧾 *Su pedido*\n${carritoTexto()}`, buttons: ["Confirmar pedido", "Agregar algo más", "Empezar de nuevo"] });
    };
    const empezarPedido = (encontrados = []) => {
      reset({ carrito: encontrados, domicilio: false });
      if (pedirSucursal("pedido", "¿En qué sucursal lo recoge?")) return;
      encontrados.length ? mostrarCarrito() : pedirProductos();
    };
    const pasarPersona = () => {
      reset();
      if (pedirSucursal("persona", "Claro. ¿Con qué sucursal le comunico?")) return;
      handoff();
    };
    const handoff = () => {
      const b = N.sucursales.find(x => x.id === d.sucursal) || N.sucursales[0];
      say({ text: `Listo, le pasé la conversación a una persona de *${b.nombre}*. Le escribe por aquí mismo. 🙌${b.telefono ? `\n\nSi es urgente: ${b.telefono}` : ""}`, buttons: ["Volver al inicio"] });
      s.handoff = b.nombre; go("post");
    };

    if (!state || SALUDO.test(t)) {
      reset(); go("inicio");
      if (!/^(menu principal|inicio|0)$/.test(t)) say(`¡Hola! 👋 Gracias por escribirle a *${N.nombre}*. Le atiendo a cualquier hora: menú y precios, pedidos para recoger y sucursales.`);
      menuInicio();
      return done();
    }

    switch (s.step) {
      case "inicio": {
        const o = pick(text, MENU);
        if (o === MENU[4] || (!o && quierePersona(t))) { pasarPersona(); break; }
        if (o === MENU[3] || (!o && quiereDomicilio(t))) { reset(); go("post"); say({ text: domicilioTexto(), buttons: ["Hacer un pedido para recoger", "Ver el menú y precios"] }); break; }
        if (o === MENU[2] || (!o && quiereSucursal(t))) { reset(); go("post"); say(sucursalesTexto()); say({ text: "¿Algo más?", buttons: ["Hacer un pedido para recoger", "Ver el menú y precios"] }); break; }
        if (o === MENU[0] || (!o && quiereMenu(t) && !quierePedir(t))) { reset(); go("menu"); say({ text: `🍽️ *Menú de ${N.nombre}*\n\n${menuTexto(false)}`, buttons: ["Hacer un pedido para recoger", "Volver al inicio"] }); break; }
        const leido = o ? { encontrados: [] } : leerPedido(text);
        if (o === MENU[1] || quierePedir(t) || leido.encontrados.length) { empezarPedido(leido.encontrados); break; }
        menuInicio("Disculpe, no le entendí bien. Puede tocar una opción o escribirme con sus palabras, por ejemplo «quiero 2 combos de 3 piezas».");
        break;
      }

      case "menu": {
        const o = pick(text, offered);
        if (o === "Volver al inicio") { reset(); go("inicio"); menuInicio(); break; }
        const leido = o ? { encontrados: [] } : leerPedido(text);
        if (o === "Hacer un pedido para recoger" || leido.encontrados.length || quierePedir(t)) { empezarPedido(leido.encontrados); break; }
        go("inicio"); return handle(s, text, now, ctx);
      }

      case "sucursal": {
        const b = N.sucursal(pick(text, N.sucursales.map(x => x.nombre)) || text);
        if (!b) { say({ text: "¿Cuál de estas sucursales?", buttons: N.sucursales.map(x => x.nombre) }); break; }
        d.sucursal = b.id;
        if (d.despues === "persona") { handoff(); break; }
        say(`Perfecto, sucursal *${b.nombre}*.`);
        d.carrito && d.carrito.length ? mostrarCarrito() : pedirProductos();
        break;
      }

      case "carrito": {
        if (quierePersona(t)) { pasarPersona(); break; }
        const { encontrados, dudas } = leerPedido(text);
        if (!encontrados.length) { say(`No encontré eso en el menú. Escriba el número del producto y la cantidad, por ejemplo *1 x2*.\n\n${menuTexto(true)}`); break; }
        d.carrito = (d.carrito || []).concat(encontrados);
        mostrarCarrito(dudas.length ? `No encontré en el menú: «${dudas.join("», «")}». Una persona puede ayudarle con eso.` : "");
        break;
      }

      case "carrito_ok": {
        const o = pick(text, offered);
        if (o === "Confirmar pedido" || /^(si|listo|confirmo|confirmar|eso es todo|es todo|nada mas|ya)\b/.test(t)) {
          go("hora"); say({ text: `¿Para cuándo lo quiere?${N.tiempoPreparacion ? ` Lo tenemos listo en unos ${N.tiempoPreparacion}.` : ""}`, buttons: HORAS }); break;
        }
        if (o === "Agregar algo más") { pedirProductos(); break; }
        if (o === "Empezar de nuevo") { d.carrito = []; pedirProductos(); break; }
        const { encontrados } = leerPedido(text);
        if (encontrados.length) { d.carrito = d.carrito.concat(encontrados); mostrarCarrito(); break; }
        mostrarCarrito("Toque una opción, o escriba otro producto para agregarlo.");
        break;
      }

      case "hora": {
        const o = pick(text, HORAS);
        if (o === "Otra hora") { go("hora_n"); say("¿A qué hora pasa a recogerlo? Por ejemplo: 6:30 p. m."); break; }
        d.hora = o || text.trim().slice(0, 60);
        go("nombre"); say("¿A nombre de quién lo dejo?");
        break;
      }
      case "hora_n": { d.hora = text.trim().slice(0, 60); go("nombre"); say("¿A nombre de quién lo dejo?"); break; }

      case "nombre": {
        d.nombre = text.trim().replace(/^(soy|me llamo|a nombre de|es)\s+/i, "").slice(0, 60).replace(/^\p{L}/u, c => c.toUpperCase());
        const b = N.sucursales.find(x => x.id === d.sucursal) || N.sucursales[0];
        const c = cuenta(N, d.carrito);
        const n = "PED-" + (++s.seq);
        s.lead = { tipo: "pedido", n, nombre: d.nombre, sucursal: b.nombre, sucursalId: b.id, lineas: c.lineas, total: c.total, hora: d.hora, resumen: c.lineas.map(lineaTexto).join(" · ") };
        if (requiereCobro(N, c.total, ctx.faltas || 0)) {
          s.lead.estado = "por_pagar"; s.pago = { n, total: c.total };
          say({ text: `🧾 *Pedido ${n} apartado, ${d.nombre.split(" ")[0]}.*\n\n${c.lineas.map(lineaTexto).join("\n")}\n*Total: ${L(c.total)}*\nRecoge en *${b.nombre}*: ${d.hora.toLowerCase()}.\n\nPara mandarlo a cocina, se paga antes:\n${textoCobro(N, n, c.total)}\n\nEn cuanto se confirme el pago entra a cocina y le avisamos por aquí.`, buttons: ["Cancelar pedido"] });
          go("pago");
          break;
        }
        say({ text: `✅ *Listo, ${d.nombre.split(" ")[0]}.* Pedido *${n}*\n\n${c.lineas.map(lineaTexto).join("\n")}\n*Total: ${L(c.total)}*\n\nRecoge en *${b.nombre}*: ${d.hora.toLowerCase()}.${N.pago ? `\n${N.pago}` : ""}\n\nLe avisamos por aquí cuando esté listo.`, buttons: ["Hacer otro pedido", "Sucursales y horario"] });
        go("post");
        break;
      }

      case "pago": { // waiting for the payment of s.pago.n (the receipt photo is handled in server.js)
        const o = pick(text, offered.length ? offered : ["Cancelar pedido"]);
        if (o === "Cancelar pedido" || /^cancel/.test(t)) {
          s.cancelar = s.pago.n; s.pago = null; reset(); go("post");
          say({ text: "Listo, cancelamos ese pedido. Cuando guste nos vuelve a escribir.", buttons: ["Hacer otro pedido", "Volver al inicio"] }); break;
        }
        if (/pag|transfer|deposit|comprobante|listo|ya /.test(t + " ")) {
          say({ text: `Para confirmar el pago del pedido *${s.pago.n}*, mándenos aquí la foto del comprobante. 📷`, buttons: ["Cancelar pedido"] }); break;
        }
        go("inicio"); return handle(s, text, now, ctx);
      }

      default: { // "post"
        const o = pick(text, offered);
        reset(); go("inicio");
        if (o === "Volver al inicio" || !t) { menuInicio(); break; }
        if (o === "Hacer otro pedido" || o === "Hacer un pedido para recoger") { empezarPedido(); break; }
        if (o === "Sucursales y horario") return handle(s, "3", now, ctx);
        if (o === "Ver el menú y precios") return handle(s, "1", now, ctx);
        return handle(s, text, now, ctx);
      }
    }
    return done();
  }

  return { handle, fresh, menuTexto, sucursalesTexto, domicilioTexto, leerPedido, MENU };
}

// plain-text rendering for channels without buttons (Twilio)
function toText(m) {
  let s = m.text || "";
  if (m.buttons && m.buttons.length) s += "\n\n" + m.buttons.map((b, i) => `${i + 1}. ${b}`).join("\n");
  return s.trim();
}

module.exports = { createEngine, toText };
