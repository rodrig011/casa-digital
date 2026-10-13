/* Steel Works · asistente de cotización (motor de conversación).
 * El cliente no sabe códigos: describe lo que quiere con sus palabras, el asistente le muestra
 * fotos reales de obras y piezas, calcula cantidades y arma una cotización preliminar que un
 * asesor confirma. El mismo archivo corre en el navegador (demos) y en Node (server.js).
 *
 * handle(state, text) -> { state, messages }
 *   message: { text?, chips?: [..], cards?: [{ id, img, title, sub, price? }], quote?: {...}, pay?: {...}, userImage?: img }
 * En producción, detectar() lo reemplaza un modelo de lenguaje con el catálogo como herramienta;
 * esta versión usa reglas para que la demo funcione sin conexión.
 * Precios y códigos: steelworkshn.com (oct. 2026, IVA incluido). Fechas de visita y números son de ejemplo. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.SteelBot = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const PIEZAS = [
    { code: "110-702", fam: "remates", name: "Remate en punta", price: 64.63, img: "p-110-702" },
    { code: "110-705", fam: "remates", name: "Remate tallado", price: 66.14, img: "p-110-705" },
    { code: "110-721", fam: "remates", name: "Remate de bola", price: 81.27, img: "p-110-721" },
    { code: "120-1016", fam: "adornos", name: "Adorno tallado para barrote", price: 57.28, img: "p-120-1016" },
    { code: "120-1048", fam: "adornos", name: "Adorno de anillos para barrote", price: 81.47, img: "p-120-1048" },
    { code: "222-2650", fam: "jaladores", name: "Jalador INOX negro, doble", price: 765.74, img: "p-222-2650" },
    { code: "222-2950", fam: "jaladores", name: "Jalador INOX negro, delgado", price: 877.74, img: "p-222-2950" },
    { code: "222-1650", fam: "jaladores", name: "Jalador INOX acero pulido", price: 748.59, img: "p-222-1650" },
  ];
  const FAMILIAS = {
    remates: "Remates para postes y rejas",
    adornos: "Adornos para barrotes",
    jaladores: "Jaladores para puertas",
  };
  const TIPOS = {
    porton: { label: "Portón", art: "un portón", medida: "area" },
    cerco: { label: "Cerco o verja", art: "un cerco", medida: "lineal" },
    puerta: { label: "Puerta", art: "una puerta", medida: "area" },
    ventana: { label: "Ventana o balcón", art: "una protección de ventana", medida: "area" },
    barandal: { label: "Barandal o gradas", art: "un barandal", medida: "lineal" },
  };
  const ESTILOS = [
    { id: "clasico", title: "Clásico forjado", sub: "Barrotes con puntas y volutas", img: "obra-cerco", imgVentana: "obra-ventana" },
    { id: "calado", title: "Panel calado", sub: "Diseño cortado en lámina, da privacidad", img: "obra-puerta-cnc" },
    { id: "moderno", title: "Moderno", sub: "Líneas rectas, hierro y vidrio", img: "obra-puerta-arco" },
  ];
  const SUCURSALES = {
    TGU: { nombre: "Tegucigalpa", dir: "Col. Miramontes, Ave. Principal, entre 3ra y 4ta calle", tel: ["3265-8800", "2232-5628", "2239-7624"] },
    SPS: { nombre: "San Pedro Sula", dir: "Col. Trejo, 12 calle, 20 avenida S.O., local 1909", tel: ["8906-9307", "2556-5355", "2556-5477"] },
  };
  const INICIO = ["Portón o cerco", "Puerta", "Ventana o balcón", "Barandal o gradas", "Busco una pieza", "📷 Enviar una foto"];

  const low = s => s[0].toLowerCase() + s.slice(1);
  const L = n => "L " + n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const norm = s => (s || "").toString().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").trim();
  const has = (t, words) => words.some(w => new RegExp("\\b" + w).test(t));
  const pieza = code => PIEZAS.find(p => p.code === code);
  const card = p => ({ id: p.code, img: p.img, title: p.name, sub: "Código " + p.code, price: L(p.price) });

  // what the customer is asking for, from free text
  function detectar(raw) {
    const t = norm(raw), d = {};
    if (has(t, ["porton", "cochera", "garage", "garaje", "entrada de carro"])) d.tipo = "porton";
    else if (has(t, ["cerco", "verja", "reja perimetral", "muro", "malla", "perimetr"])) d.tipo = "cerco";
    else if (has(t, ["barandal", "baranda", "grada", "escalera", "pasamano"])) d.tipo = "barandal";
    else if (has(t, ["ventana", "balcon", "proteccion", "verjas para ventana"])) d.tipo = "ventana";
    else if (has(t, ["puerta"])) d.tipo = "puerta";
    if (has(t, ["punta", "lanza", "remate", "bola", "poste", "pinacho"])) d.fam = "remates";
    else if (has(t, ["jalador", "manija", "tirador", "llamador", "agarrader", "halador"])) d.fam = "jaladores";
    else if (has(t, ["adorno", "anillo", "collar", "barrote"])) d.fam = "adornos";
    if (has(t, ["pieza", "repuesto", "accesorio", "busco unas", "busco un"]) && !d.tipo) d.pieza = true;
    if (d.fam) d.pieza = true;
    const exacta = PIEZAS.find(p => t.includes(norm(p.name).replace(/,/g, "")) || t.includes(norm(p.name)));
    if (exacta) { d.code = exacta.code; d.fam = exacta.fam; d.pieza = true; }
    if (has(t, ["asesor", "persona", "humano", "llamar", "llamen", "hablar con"])) d.asesor = true;
    if (has(t, ["horario", "direccion", "donde estan", "ubicacion", "sucursal", "abren"])) d.info = true;
    const m = t.replace(/,/g, ".").match(/(\d+(?:\.\d+)?)\s*(?:m|mts|metros?)?\s*(?:de\s+ancho\s*)?(?:x|por|×|\*)\s*(\d+(?:\.\d+)?)/);
    if (m) { d.ancho = +m[1]; d.alto = +m[2]; }
    else { const s = t.replace(/,/g, ".").match(/(\d+(?:\.\d+)?)\s*(?:m\b|mts|metros?)/); if (s) d.largo = +s[1]; }
    if (has(t, ["no se", "no lo se", "vengan a medir", "medir"])) d.medir = true;
    return d;
  }

  function pick(text, options) {
    const t = norm(text).replace(/[^\w\s]/g, "").trim();
    return options.find(o => norm(o).replace(/[^\w\s]/g, "").trim() === t) || null;
  }

  function fresh() { return { step: "inicio", p: {}, items: [], seq: 2050 }; }

  function cotizacion(s) {
    const p = s.p, lines = [];
    let piezas = 0;
    s.items.forEach(i => { const x = pieza(i.code); piezas += x.price * i.qty; lines.push({ qty: i.qty, name: x.name, code: x.code, img: x.img, total: L(x.price * i.qty), unit: L(x.price) }); });
    const q = { n: "COT-" + (++s.seq), lines, piezas: L(piezas) };
    if (p.tipo) {
      const T = TIPOS[p.tipo];
      q.proyecto = T.label + (p.estilo ? " · " + p.estilo.title.toLowerCase() : "");
      q.medidas = p.medir ? "Por medir en visita" : T.medida === "lineal" ? `${p.largo} m lineales` : `${p.ancho} × ${p.alto} m (${(p.ancho * p.alto).toFixed(1)} m²)`;
      q.ciudad = p.ciudad;
      q.fabricacion = "La confirma el taller después de medir";
      q.img = p.estilo && (p.tipo === "ventana" && p.estilo.imgVentana || p.estilo.img);
    }
    return q;
  }

  function handle(state, input) {
    const s = state ? JSON.parse(JSON.stringify(state)) : fresh();
    let text = (input || "").toString().trim();
    // in plain-text channels the customer answers with the option number
    if (/^\d{1,2}$/.test(text) && s.opts && !["cantidad", "medidas", "alto"].includes(s.step) && s.opts[+text - 1]) text = s.opts[+text - 1];
    const t = norm(text);
    const out = [];
    const say = m => out.push(typeof m === "string" ? { text: m } : m);
    const go = st => { s.step = st; };
    const d = detectar(text);
    const done = () => {
      const last = [...out].reverse().find(m => m.cards || m.chips);
      s.opts = last ? [...(last.cards || []).map(c => c.id), ...(last.chips || [])] : null;
      return { state: s, messages: out };
    };

    const askMedidas = () => {
      const T = TIPOS[s.p.tipo];
      if (s.p.medir || (T.medida === "area" ? s.p.ancho : s.p.largo)) return askEstilo();
      go("medidas");
      say({ text: T.medida === "lineal"
        ? `Perfecto, ${T.art}. ¿Cuántos metros de largo tiene, más o menos? Con un aproximado basta.`
        : `Perfecto, ${T.art}. ¿Más o menos cuánto mide el espacio? Con el ancho y el alto basta, por ejemplo «4 de ancho por 2 de alto».`,
        chips: ["No sé, que vengan a medir"] });
    };
    const askEstilo = () => {
      if (s.p.estilo) return askExtras();
      go("estilo");
      say({ text: "Estos son tres estilos que fabricamos en nuestro taller. ¿Cuál le gusta más?",
        cards: ESTILOS.map(e => ({ id: e.id, img: s.p.tipo === "ventana" && e.imgVentana || e.img, title: e.title, sub: e.sub })) });
    };
    const askExtras = () => {
      if (s.p.extrasHechos) return askCiudad();
      if (s.p.estilo.id === "clasico" && (s.p.tipo === "porton" || s.p.tipo === "cerco")) {
        const metros = s.p.ancho || s.p.largo || 4;
        s.p.puntas = Math.ceil(metros / 0.12) + 1;
        go("extras");
        say({ text: `Para ese estilo van remates en cada barrote. Con ${metros} m y barrotes cada 12 cm son unos ${s.p.puntas}. Estos son los que más piden:`,
          cards: PIEZAS.filter(p => p.fam === "remates").map(card), chips: ["Sin remates"] });
      } else if (s.p.tipo === "puerta") {
        go("extras");
        say({ text: "¿Le ponemos jalador? Estos son los de acero inoxidable que tenemos:", cards: PIEZAS.filter(p => p.fam === "jaladores").map(card), chips: ["Sin jalador"] });
      } else { s.p.extrasHechos = true; askCiudad(); }
    };
    const askCiudad = () => { go("ciudad"); say({ text: "¿En qué ciudad sería la obra?", chips: ["Tegucigalpa", "San Pedro Sula", "Otra ciudad"] }); };
    const quote = () => {
      const q = cotizacion(s);
      s.last = q.n;
      say({ text: "Listo. Esta es su cotización preliminar:", quote: q });
      return q;
    };
    const startProject = tipo => { s.p = { tipo, ancho: d.ancho, alto: d.alto, largo: d.largo || (d.ancho && TIPOS[tipo].medida === "lineal" ? d.ancho : undefined), medir: d.medir }; s.items = []; askMedidas(); };
    const showFam = fam => { go("piezas"); s.fam = fam; say({ text: `${FAMILIAS[fam]}. ¿Cuál se parece a lo que busca?`, cards: PIEZAS.filter(p => p.fam === fam).map(card), chips: ["No veo la que busco"] }); };

    // greetings and resets
    if (!state || has(t, ["^hola", "^buenas", "^buenos", "^inicio", "^menu", "cotizar otra"])) {
      if (!state || !has(t, ["cotizar otra"])) say("Buenas, bienvenido a Steel Works. 👋");
      go("inicio"); s.p = {}; s.items = [];
      say({ text: "Cuénteme qué quiere hacer, con sus palabras. Por ejemplo «un portón para la cochera» o «unas puntas para una reja».", chips: INICIO });
      return done();
    }
    if (d.asesor && s.step !== "asesor" && s.step !== "visita") { go("asesor"); say({ text: "Con gusto le paso con una persona. ¿Con qué sucursal?", chips: ["Tegucigalpa", "San Pedro Sula"] }); return done(); }
    if (d.info) {
      say(Object.values(SUCURSALES).map(b => `📍 *${b.nombre}*\n${b.dir}\nTel. ${b.tel.join(" · ")}`).join("\n\n"));
      say({ text: "¿Le ayudo a cotizar algo?", chips: INICIO });
      go("inicio");
      return done();
    }

    switch (s.step) {
      case "inicio":
      case "listo": {
        const o = pick(text, INICIO);
        if (o === "Portón o cerco") { go("porton_o_cerco"); say({ text: "¿Es un portón de entrada o un cerco alrededor de la propiedad?", chips: ["Portón", "Cerco o verja"] }); }
        else if (o === "Puerta") startProject("puerta");
        else if (o === "Ventana o balcón") startProject("ventana");
        else if (o === "Barandal o gradas") startProject("barandal");
        else if (o === "Busco una pieza") { go("familia"); say({ text: "¿Para qué es la pieza?", chips: Object.values(FAMILIAS) }); }
        else if (o === "📷 Enviar una foto") {
          say({ userImage: "detalle-calado" });
          say({ text: "Gracias. Ese diseño es un panel calado, cortado en CNC sobre lámina. Esta es una puerta que hicimos con un panel así:", cards: [{ id: "calado", img: "obra-puerta-cnc", title: "Puerta con panel calado", sub: "Fabricada por Steel Works" }] });
          say({ text: "¿Quiere cotizar una así?", chips: ["Sí, una puerta así", "Es otra cosa"] });
          go("foto");
        }
        else if (d.code && !d.tipo) { const p = pieza(d.code); s.sel = p.code; go("cantidad"); say({ text: `Claro, ${low(p.name)} a ${L(p.price)} cada uno. ¿Cuántos necesita?`, chips: ["10", "25", "50"] }); }
        else if (d.tipo) startProject(d.tipo);
        else if (d.fam) showFam(d.fam);
        else if (d.pieza) { go("familia"); say({ text: "Claro. ¿Para qué es la pieza?", chips: Object.values(FAMILIAS) }); }
        else say({ text: "Para ayudarle mejor, ¿qué le gustaría hacer? Puede escribirlo como le salga o tocar una opción.", chips: INICIO });
        break;
      }
      case "porton_o_cerco": startProject(norm(text).startsWith("cerco") || d.tipo === "cerco" ? "cerco" : "porton"); break;
      case "foto": {
        if (/^si/.test(t)) { s.p = { tipo: "puerta", estilo: ESTILOS[1] }; s.items = []; askMedidas(); }
        else { go("inicio"); say({ text: "Entendido. Cuénteme qué es y se lo cotizo.", chips: INICIO }); }
        break;
      }
      case "medidas": {
        if (d.medir) s.p.medir = true;
        else if (d.ancho) { s.p.ancho = d.ancho; s.p.alto = d.alto; if (TIPOS[s.p.tipo].medida === "lineal") s.p.largo = d.ancho; }
        else if (d.largo || /^\d/.test(t)) {
          const n = d.largo || parseFloat(t);
          if (TIPOS[s.p.tipo].medida === "lineal") s.p.largo = n;
          else { s.p.ancho = n; go("alto"); say(`Bien, ${n} m de ancho. ¿Y de alto, más o menos?`); break; }
        } else { say({ text: "No logré entender la medida. Escríbala así: «4 por 2», o si prefiere vamos a medir.", chips: ["No sé, que vengan a medir"] }); break; }
        askEstilo();
        break;
      }
      case "alto": { const n = d.largo || parseFloat(t.replace(",", ".")); s.p.alto = n || 2; askEstilo(); break; }
      case "estilo": {
        const e = ESTILOS.find(x => x.id === t || norm(x.title) === t || t.includes(norm(x.title).split(" ")[0]));
        if (!e) { say({ text: "Toque el estilo que más le guste:", cards: ESTILOS.map(x => ({ id: x.id, img: x.img, title: x.title, sub: x.sub })) }); break; }
        s.p.estilo = e; askExtras();
        break;
      }
      case "extras": {
        const p = PIEZAS.find(x => x.code === text.trim() || norm(x.name) === t);
        if (p) s.items.push({ code: p.code, qty: p.fam === "remates" ? s.p.puntas : (s.p.tipo === "puerta" ? 1 : 1) });
        s.p.extrasHechos = true; askCiudad();
        break;
      }
      case "ciudad": {
        if (/^otra ciudad$/.test(t)) { say("¿En cuál ciudad? Hacemos obras y envíos a toda Honduras."); break; }
        s.p.ciudad = text;
        const q = quote();
        say({ text: "El precio de fabricación lo confirma el taller al medir, para no darle un número inventado. ¿Le agendo la visita?", chips: ["Jueves en la mañana", "Viernes en la tarde", "Prefiero que me llamen"] });
        go("visita");
        s.cot = q;
        break;
      }
      case "visita": {
        const suc = /pedro|sps/.test(norm(s.p.ciudad || "")) ? "San Pedro Sula" : "Tegucigalpa";
        s.visita = text; s.handoff = suc;
        say({ text: (/llamen/.test(t) ? `Listo. Un asesor de ${suc} le llama hoy` : `Agendado para el ${text.toLowerCase()}. Un asesor de ${suc} le confirma la hora por aquí`) + `, y ya tiene su cotización ${s.last} con el estilo que eligió. 🙌`, chips: ["Cotizar otra cosa"] });
        go("listo");
        break;
      }
      case "familia": {
        const fam = Object.keys(FAMILIAS).find(k => FAMILIAS[k] === text) || d.fam;
        if (fam) showFam(fam);
        else say({ text: "¿Cuál de estas?", chips: Object.values(FAMILIAS) });
        break;
      }
      case "piezas": {
        const p = PIEZAS.find(x => x.code === text.trim() || norm(x.name) === t);
        if (!p) { if (d.fam) { showFam(d.fam); break; } go("asesor"); say({ text: "Tenemos más de 700 piezas, así que seguro la hay. Mándeme una foto o le paso con un asesor. ¿Con qué sucursal?", chips: ["Tegucigalpa", "San Pedro Sula"] }); break; }
        s.sel = p.code; go("cantidad");
        say({ text: `Buena elección, ${low(p.name)} a ${L(p.price)} cada uno. ¿Cuántos necesita?`, chips: ["10", "25", "50"] });
        break;
      }
      case "cantidad": {
        const n = parseInt(t.replace(/\D/g, ""), 10);
        if (!n) { say("¿Cuántas unidades? Escriba solo el número."); break; }
        const l = s.items.find(i => i.code === s.sel); if (l) l.qty += n; else s.items.push({ code: s.sel, qty: n });
        say({ text: `Agregué ${n}. ¿Algo más?`, chips: ["Ver mi cotización", "Buscar otra pieza", "Hablar con un asesor"] });
        go("carrito");
        break;
      }
      case "carrito": {
        if (/otra pieza/.test(t)) { go("familia"); say({ text: "¿Para qué es?", chips: Object.values(FAMILIAS) }); break; }
        quote();
        say({ text: "¿La retira en tienda o se la enviamos?", chips: ["Retiro en Tegucigalpa", "Retiro en San Pedro Sula", "Envío a mi ciudad"] });
        go("entrega");
        break;
      }
      case "entrega": {
        const total = s.items.reduce((a, i) => a + pieza(i.code).price * i.qty, 0);
        say({ text: (/envio/.test(t) ? "Se la enviamos con la empresa de envíos. El costo se suma al confirmar la dirección." : "Se la tenemos lista para retirar.") + " Aquí puede pagar con tarjeta:", pay: { amount: L(total), ref: s.last } });
        say({ text: "Un asesor confirma la existencia antes de cobrar y le avisa por aquí. 🙌", chips: ["Cotizar otra cosa"] });
        s.pedido = { n: s.last, total, entrega: text };
        s.items = []; go("listo");
        break;
      }
      case "asesor": {
        const suc = /pedro|sps/.test(t) ? "San Pedro Sula" : "Tegucigalpa";
        s.handoff = suc;
        say({ text: `Listo. Le pasé la conversación a un asesor de ${suc} con todo lo que hablamos. Le escribe por aquí en horario de tienda.`, chips: ["Cotizar otra cosa"] });
        go("listo");
        break;
      }
    }
    return done();
  }

  // plain text for channels without buttons or images (Twilio sandbox, SMS)
  function toText(m) {
    let s = m.text || "";
    if (m.cards) s += "\n" + m.cards.map((c, i) => `${i + 1}) ${c.title}${c.price ? " · " + c.price : ""}`).join("\n");
    if (m.quote) {
      const q = m.quote;
      s += `\n\n*${q.n}*` + (q.proyecto ? `\n${q.proyecto}\n${q.medidas}${q.ciudad ? " · " + q.ciudad : ""}` : "") +
        q.lines.map(l => `\n• ${l.qty} × ${l.name} (${l.code}) ${l.total}`).join("") + (q.lines.length ? `\nPiezas: ${q.piezas}` : "") + (q.fabricacion ? `\nFabricación: ${q.fabricacion}` : "");
    }
    const k = m.cards ? m.cards.length : 0;
    if (m.chips) s += "\n\n" + m.chips.map((b, i) => `${k + i + 1}) ${b}`).join("\n");
    if (m.pay) s += `\n\n💳 Pagar ${m.pay.amount}: https://pagos.steelworkshn.com/${m.pay.ref}`;
    return s.trim();
  }

  return { handle, toText, fresh, detectar, PIEZAS, FAMILIAS, ESTILOS, SUCURSALES, INICIO, L };
});
