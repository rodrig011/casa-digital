/* Steel Works · asistente de WhatsApp (motor de conversación).
 * El mismo archivo corre en el navegador (demo) y en Node (server.js).
 * handle(state, text) -> { state, messages: [{ text, buttons?, card?, list? }] }
 * Los precios y códigos son los publicados en steelworkshn.com (oct. 2026, IVA incluido).
 * Existencias por sucursal, horario y números de pedido son datos de ejemplo para la demo. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.SteelBot = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const CATALOGO = [
    ["PCA-3", "Portacarteras PCA-3", "Accesorios", 2472.5, true],
    ["401-1801B", "Tubo forjado 401-1801B", "Tubos forjados", 948.75, true],
    ["401-1801A", "Tubo forjado 401-1801A", "Tubos forjados", 491.05, true],
    ["401-1802B", "Tubo forjado 401-1802B", "Tubos forjados", 1224.75, true],
    ["222-2650", "Llamador INOX 222-2650", "Llamadores", 765.74, true],
    ["222-2950", "Llamador INOX 222-2950", "Llamadores", 877.74, true],
    ["222-1950", "Llamador INOX 222-1950", "Llamadores", 877.74, false],
    ["222-1650", "Llamador INOX 222-1650", "Llamadores", 748.59, true],
    ["120-1016", "Adorno de barra 120-1016", "Adornos de barra", 57.28, false],
    ["120-1018", "Adorno de barra 120-1018", "Adornos de barra", 30.48, false],
    ["120-1048", "Adorno de barra 120-1048", "Adornos de barra", 81.47, true],
    ["120-801B", "Adorno de barra 120-801B", "Adornos de barra", 19.34, true],
    ["120-802B", "Adorno de barra 120-802B", "Adornos de barra", 21.51, true],
    ["120-804F-H", "Adorno de barra 120-804F-H", "Adornos de barra", 21.51, true],
    ["120-808A", "Adorno de barra 120-808A", "Adornos de barra", 13.96, true],
    ["120-818", "Adorno de barra 120-818", "Adornos de barra", 17.65, true],
    ["120-830", "Adorno de barra 120-830", "Adornos de barra", 25.31, true],
    ["120-840", "Adorno de barra 120-840", "Adornos de barra", 47.77, false],
    ["120-841", "Adorno de barra 120-841", "Adornos de barra", 29.76, true],
    ["130-1024", "Adorno de barra 130-1024", "Adornos de barra", 11.42, true],
    ["130-1027", "Adorno de barra 130-1027", "Adornos de barra", 48.4, true],
    ["130-1028", "Adorno de barra 130-1028", "Adornos de barra", 39.32, true],
    ["130-1033", "Adorno de barra 130-1033", "Adornos de barra", 32.53, true],
    ["130-1050", "Adorno de barra 130-1050", "Adornos de barra", 29.82, true],
    ["130-1051", "Adorno de barra 130-1051", "Adornos de barra", 7.88, true],
    ["130-1100", "Adorno de barra 130-1100", "Adornos de barra", 50.84, true],
    ["110-702", "Adorno de poste 110-702", "Adornos de poste", 64.63, false],
    ["110-705", "Adorno de poste 110-705", "Adornos de poste", 66.14, false],
    ["110-721", "Adorno de poste 110-721", "Adornos de poste", 81.27, false],
  ].map(([code, name, cat, price, stock]) => ({ code, name, cat, price, stock }));

  const SUCURSALES = {
    TGU: { nombre: "Tegucigalpa", dir: "Col. Miramontes, Ave. Principal, entre 3ra y 4ta calle", tel: ["3265-8800", "2232-5628", "2239-7624"] },
    SPS: { nombre: "San Pedro Sula", dir: "Col. Trejo, 12 calle, 20 avenida S.O., local 1909", tel: ["8906-9307", "2556-5355", "2556-5477"] },
  };
  const HORARIO = "Lunes a viernes 8:00 a. m. a 5:00 p. m., sábado 8:00 a. m. a 12:00 m. (ejemplo, por confirmar)";

  const MENU = ["Buscar una pieza", "Cotizar fabricación", "Pedido rápido de taller", "Enviar foto de un diseño", "Estado de mi pedido", "Sucursales y horario", "Hablar con un asesor"];
  const TIPOS = ["Portón", "Balcón", "Barandal", "Puerta", "Verja", "Otro"];
  const ESTILOS = ["Liso, moderno", "Forjado clásico", "Diseño CNC"];

  const L = n => "L " + n.toLocaleString("es-HN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const norm = s => (s || "").toString().trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  const codeKey = s => norm(s).replace(/[^a-z0-9]/g, "");

  function fresh() { return { step: "menu", cart: [], data: {}, seq: 1047 }; }

  function find(q) {
    const k = codeKey(q);
    if (!k) return [];
    const exact = CATALOGO.filter(p => codeKey(p.code) === k);
    if (exact.length) return exact;
    const byCode = CATALOGO.filter(p => codeKey(p.code).includes(k) && k.length >= 3);
    if (byCode.length) return byCode;
    const words = norm(q).split(/\s+/).filter(w => w.length > 2).map(w => w.replace(/(es|s)$/, ""));
    return CATALOGO.filter(p => words.every(w => norm(p.name + " " + p.cat).includes(w)));
  }

  // match a reply against the buttons we offered: by number, emoji number or label
  function pick(text, options) {
    const t = norm(text).replace(/[^\w\s]/g, "").trim();
    const n = parseInt(t, 10);
    if (n >= 1 && n <= options.length && String(n) === t) return options[n - 1];
    return options.find(o => norm(o) === norm(text)) || options.find(o => t.length > 2 && norm(o).startsWith(t)) || null;
  }

  const card = p => ({ title: p.name, sub: p.cat + " · código " + p.code, price: L(p.price), stock: p.stock });
  const menuMsg = (pre) => ({ text: (pre ? pre + "\n\n" : "") + "¿En qué te ayudo?", buttons: MENU });
  const cartTotal = c => c.reduce((s, i) => s + i.qty * i.p.price, 0);
  const cartText = c => c.map(i => `• ${i.qty} × ${i.p.code}  ${L(i.qty * i.p.price)}`).join("\n") + `\n*Total: ${L(cartTotal(c))}* (IVA incluido)`;

  function handle(state, input) {
    const s = state ? JSON.parse(JSON.stringify(state)) : fresh();
    const text = (input || "").toString();
    const t = norm(text);
    const out = [];
    const offered = s.offer || [];
    s.offer = null;
    const say = (m) => { m = typeof m === "string" ? { text: m } : m; if (m.buttons) s.offer = m.buttons; out.push(m); };
    const go = (step) => { s.step = step; };

    if (!state || ["hola", "menu", "menú", "inicio", "0", "buenas", "buenos dias", "buenas tardes"].includes(t)) {
      go("menu");
      if (!state || !["menu", "menú", "inicio", "0"].includes(t)) say("¡Hola! 👋 Soy el asistente de *Steel Works*. Todo en hierro, con envíos a toda Honduras.");
      say(menuMsg());
      return { state: s, messages: out };
    }

    switch (s.step) {
      case "menu": {
        const o = pick(text, MENU);
        if (o === MENU[0]) { go("buscar"); say("Escríbeme el *código* de la pieza (por ejemplo 120-1048) o lo que buscas (por ejemplo «llamador»)."); }
        else if (o === MENU[1]) { go("fab_tipo"); s.data = {}; say({ text: "Con gusto cotizamos tu proyecto. ¿Qué necesitas fabricar?", buttons: TIPOS }); }
        else if (o === MENU[2]) { go("rapido"); say("Pega tu lista con un código y una cantidad por línea, así:\n\n120-1048 x 20\n130-1024 x 50\n401-1801A x 4\n\nTe devuelvo el total y qué hay en existencia."); }
        else if (o === MENU[3]) { go("foto"); say({ text: "Mándame la foto o el dibujo del diseño que tienes en mente. Si tienes medidas, escríbelas con la foto.", buttons: ["📷 Enviar foto de ejemplo"] }); }
        else if (o === MENU[4]) { go("estado"); say("Escríbeme tu número de pedido (por ejemplo SW-1046)."); }
        else if (o === MENU[5]) {
          say(Object.values(SUCURSALES).map(b => `📍 *${b.nombre}*\n${b.dir}\nTel. ${b.tel.join(" · ")}`).join("\n\n") + `\n\n🕗 ${HORARIO}`);
          say({ text: "¿Algo más?", buttons: ["Menú", "Hablar con un asesor"] }); go("post");
        }
        else if (o === MENU[6]) { go("asesor"); say({ text: "¿Con qué sucursal te comunico?", buttons: ["Tegucigalpa", "San Pedro Sula"] }); }
        else {
          const hits = find(text);
          if (hits.length) { go("buscar"); return handle(s, text); }
          say(menuMsg("No te entendí bien. Responde con el número o toca una opción."));
        }
        break;
      }

      case "buscar": {
        const hits = find(text);
        if (!hits.length) { say({ text: `No encontré «${text}». Prueba con el código que aparece en el catálogo, o te paso con un asesor.`, buttons: ["Buscar otra", "Hablar con un asesor", "Menú"] }); go("post"); break; }
        if (hits.length === 1) {
          const p = hits[0]; s.data.p = p.code;
          say({ card: card(p), text: p.stock ? "✅ Disponible. ¿Cuántas unidades quieres?" : "⏳ Agotado por ahora. Te aviso por aquí apenas vuelva a entrar." , buttons: p.stock ? ["1", "10", "50"] : ["Avisarme cuando llegue", "Buscar otra", "Menú"] });
          go(p.stock ? "cantidad" : "agotado");
        } else {
          say({ text: `Encontré ${hits.length} piezas. Toca una:`, list: hits.slice(0, 8).map(p => ({ id: p.code, title: p.code, sub: `${p.name.replace(" " + p.code, "")} · ${L(p.price)}${p.stock ? "" : " · agotado"}` })) });
        }
        break;
      }

      case "cantidad": {
        const qty = parseInt(t.replace(/[^0-9]/g, ""), 10);
        if (!qty) { say("Escríbeme solo el número de unidades, por ejemplo 12."); break; }
        const p = CATALOGO.find(x => x.code === s.data.p);
        const line = s.cart.find(i => i.p.code === p.code);
        if (line) line.qty += qty; else s.cart.push({ p, qty });
        say({ text: `Agregué ${qty} × ${p.code} a tu pedido.\n\n${cartText(s.cart)}`, buttons: ["Agregar otra pieza", "Finalizar pedido", "Menú"] });
        go("carrito");
        break;
      }

      case "agotado": {
        if (pick(text, ["Avisarme cuando llegue"])) { say({ text: `Listo. Te escribo aquí cuando entre el ${s.data.p}. 🔔`, buttons: ["Buscar otra", "Menú"] }); go("post"); }
        else { go("post"); s.offer = offered; return handle(s, text); }
        break;
      }

      case "carrito": {
        const o = pick(text, ["Agregar otra pieza", "Finalizar pedido", "Menú"]);
        if (o === "Agregar otra pieza") { go("buscar"); say("Dale. ¿Qué código o pieza buscas?"); }
        else if (o === "Finalizar pedido") { go("entrega"); say({ text: "¿Cómo lo quieres recibir?", buttons: ["Retiro en Tegucigalpa", "Retiro en San Pedro Sula", "Envío a mi ciudad"] }); }
        else { go("menu"); say(menuMsg()); }
        break;
      }

      case "rapido": {
        const lines = text.split(/\n|,|;/).map(x => x.trim()).filter(Boolean);
        const ok = [], miss = [], out_ = [];
        lines.forEach(ln => {
          const m = ln.match(/^([A-Za-z0-9-]+)\s*[x×*]?\s*(\d+)?$/i);
          if (!m) { miss.push(ln); return; }
          const p = CATALOGO.find(x => codeKey(x.code) === codeKey(m[1]));
          if (!p) miss.push(m[1]); else if (!p.stock) out_.push(p.code); else ok.push({ p, qty: parseInt(m[2] || "1", 10) });
        });
        if (!ok.length && !out_.length) { say("No reconocí ningún código. Usa una línea por pieza, por ejemplo: 120-1048 x 20"); break; }
        ok.forEach(i => { const l = s.cart.find(c => c.p.code === i.p.code); if (l) l.qty += i.qty; else s.cart.push(i); });
        let msg = ok.length ? `Listo, armé tu pedido:\n\n${cartText(s.cart)}` : "";
        if (out_.length) msg += `\n\n⏳ Agotados: ${out_.join(", ")}. Te aviso cuando entren.`;
        if (miss.length) msg += `\n\n❓ No encontré: ${miss.join(", ")}.`;
        say({ text: msg.trim(), buttons: ok.length ? ["Finalizar pedido", "Agregar otra pieza", "Menú"] : ["Menú"] });
        go(ok.length ? "carrito" : "post");
        break;
      }

      case "entrega": {
        const o = pick(text, ["Retiro en Tegucigalpa", "Retiro en San Pedro Sula", "Envío a mi ciudad"]);
        if (!o) { say({ text: "Toca una opción:", buttons: ["Retiro en Tegucigalpa", "Retiro en San Pedro Sula", "Envío a mi ciudad"] }); break; }
        if (o === "Envío a mi ciudad") { go("ciudad"); say("¿A qué ciudad y dirección lo enviamos?"); break; }
        s.data.entrega = o;
        return handle(Object.assign(s, { step: "confirmar" }), "");
      }

      case "ciudad": {
        s.data.entrega = "Envío a " + text;
        return handle(Object.assign(s, { step: "confirmar" }), "");
      }

      case "confirmar": {
        const n = "SW-" + (++s.seq);
        say({ text: `🧾 *Pedido ${n}*\n\n${cartText(s.cart)}\n\n🚚 ${s.data.entrega}\n\nTe dejo el enlace de pago con tarjeta. También puedes pagar por transferencia o al retirar.`, pay: { amount: L(cartTotal(s.cart)), ref: n } });
        say({ text: "Un asesor confirma existencias y te avisa por aquí cuando esté listo. ¡Gracias por comprar en Steel Works! 🔩", buttons: ["Menú"] });
        s.last = { n, total: cartTotal(s.cart), entrega: s.data.entrega };
        s.cart = []; go("post");
        break;
      }

      case "fab_tipo": {
        const o = pick(text, TIPOS) || (t.length > 2 ? text : null);
        if (!o) { say({ text: "Toca una opción:", buttons: TIPOS }); break; }
        s.data.tipo = o; go("fab_medidas");
        say(`Perfecto, ${o.toLowerCase()}. ¿Qué medidas tiene el espacio? Escribe ancho × alto en metros, por ejemplo: 3 x 2.2`);
        break;
      }

      case "fab_medidas": {
        const m = text.replace(",", ".").match(/(\d+(?:\.\d+)?)\s*(?:m)?\s*[x×por*]+\s*(\d+(?:\.\d+)?)/i);
        if (!m && t.includes("no se")) s.data.med = "Por medir en visita";
        else if (!m) { say("No logré leer las medidas. Escríbelas así: 3 x 2.2 (ancho por alto, en metros). Si no las tienes, escribe «no sé» y te visitamos para medir."); break; }
        else { s.data.med = `${m[1]} m × ${m[2]} m`; s.data.m2 = (+m[1] * +m[2]).toFixed(1); }
        go("fab_estilo"); say({ text: "¿Qué estilo te gusta?", buttons: ESTILOS });
        break;
      }

      case "fab_estilo": {
        const o = pick(text, ESTILOS);
        if (!o) { say({ text: "Toca una opción:", buttons: ESTILOS }); break; }
        s.data.estilo = o; go("fab_ciudad");
        say({ text: "¿En qué ciudad es la instalación?", buttons: ["Tegucigalpa", "San Pedro Sula", "Otra ciudad"] });
        break;
      }

      case "fab_ciudad": {
        s.data.ciudad = text; go("fab_foto");
        say({ text: "Último paso: si tienes una foto del lugar o de un diseño que te guste, mándala. Ayuda a cotizar más rápido.", buttons: ["📷 Enviar foto de ejemplo", "Sin foto"] });
        break;
      }

      case "fab_foto": {
        const foto = !t.includes("sin foto");
        const n = "COT-" + (2200 + s.seq % 100);
        if (foto) say({ image: true, text: "" });
        say({ text: `📐 *Solicitud ${n}*\n\nTipo: ${s.data.tipo}\nMedidas: ${s.data.med}${s.data.m2 ? ` (${s.data.m2} m²)` : ""}\nEstilo: ${s.data.estilo}\nCiudad: ${s.data.ciudad}\nFoto: ${foto ? "sí ✅" : "no"}\n\nYa la pasé al taller de fabricación. Un asesor te escribe con el precio y, si hace falta, agenda una visita para medir.` });
        say({ text: "¿Te ayudo con algo más?", buttons: ["Menú"] });
        s.lastCot = n; go("post");
        break;
      }

      case "foto": {
        say({ image: true, text: "" });
        say({ text: "¡Recibida! 📷 La revisa un asesor de fabricación. Para cotizar mejor, ¿qué es y qué medidas tiene?", buttons: TIPOS });
        s.data = {}; go("fab_tipo");
        break;
      }

      case "estado": {
        const k = t.replace(/[^0-9]/g, "");
        if (!k) { say("Escríbeme el número, por ejemplo SW-1046."); break; }
        say({ text: `📦 *Pedido SW-${k}* (ejemplo)\n\n✅ Recibido\n✅ Pagado\n✅ Preparado en bodega TGU\n🚚 En camino con la empresa de envíos\n⬜ Entregado\n\nGuía: CAEX 88412 · llega mañana.`, buttons: ["Menú", "Hablar con un asesor"] });
        go("post");
        break;
      }

      case "asesor": {
        const o = pick(text, ["Tegucigalpa", "San Pedro Sula"]) || "Tegucigalpa";
        const b = SUCURSALES[o === "Tegucigalpa" ? "TGU" : "SPS"];
        say({ text: `Listo, le pasé la conversación a un asesor de *${b.nombre}* con todo lo que hablamos. Te escribe por aquí mismo en horario de tienda. 🙌\n\nSi es urgente: ${b.tel[0]}`, buttons: ["Menú"] });
        s.handoff = b.nombre; go("post");
        break;
      }

      default: { // "post": short follow-up menus
        const o = pick(text, offered);
        if (o === "Buscar otra") { go("buscar"); say("¿Qué código o pieza buscas?"); }
        else if (o === "Hablar con un asesor") { go("asesor"); say({ text: "¿Con qué sucursal te comunico?", buttons: ["Tegucigalpa", "San Pedro Sula"] }); }
        else { go("menu"); return handle(s, text); }
      }
    }
    return { state: s, messages: out };
  }

  // plain-text rendering for channels without buttons (Twilio sandbox, SMS)
  function toText(m) {
    let s = m.text || "";
    if (m.card) s = `*${m.card.title}*\n${m.card.sub}\n${m.card.price}\n\n` + s;
    if (m.list) s += "\n" + m.list.map(i => `• ${i.title}: ${i.sub}`).join("\n");
    if (m.buttons) s += "\n\n" + m.buttons.map((b, i) => `${i + 1}. ${b}`).join("\n");
    if (m.pay) s += `\n\n💳 Pagar ${m.pay.amount}: https://pagos.steelworkshn.com/${m.pay.ref}`;
    return s.trim();
  }

  return { handle, toText, fresh, CATALOGO, SUCURSALES, MENU, L };
});
