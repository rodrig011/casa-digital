/* Steel Works · asistente de WhatsApp (motor de conversación).
 * El mismo archivo corre en el navegador (demo) y en Node (server.js).
 * handle(state, text) -> { state, messages: [{ text, buttons?, gallery?, image? }] }
 *
 * La idea: que nadie que escribe a cotizar se quede sin respuesta. El bot pregunta qué le
 * interesa, pide medidas, deja escoger el estilo con fotos de trabajos reales, da un precio
 * estimado y agenda la visita para medir o una llamada. La ficha completa le llega a la sucursal.
 *
 * TARIFAS son de ejemplo para la demo: Steel Works pone las suyas. Los precios de piezas
 * son los publicados en steelworkshn.com (oct. 2026, IVA incluido). */
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

  // Qué se puede cotizar. unidad "m2": ancho × alto; "ml": metros lineales de baranda.
  const TIPOS = {
    porton:  { label: "Portón", unidad: "m2", ejemplo: "3 x 2.2", tipico: [3, 2.2], uno: "un portón típico" },
    puerta:  { label: "Puerta", unidad: "m2", ejemplo: "1 x 2.1", tipico: [1, 2.1], uno: "una puerta típica" },
    ventana: { label: "Protección de ventanas", unidad: "m2", ejemplo: "1.5 x 1.2", tipico: [1.5, 1.2], cuantas: true, uno: "la protección de una ventana típica" },
    baranda: { label: "Baranda o balcón", unidad: "ml", ejemplo: "6 metros", tipico: [6], uno: "una baranda típica" },
  };
  const MENU = ["Portón", "Puerta", "Protección de ventanas", "Baranda o balcón", "Piezas para herrería", "Hablar con una persona"];

  // Estilos con foto de trabajos reales de Steel Works (las claves son archivos de fotos/).
  const ESTILOS = [
    { key: "moderno", label: "Moderno", foto: "obra-puerta-arco", sub: "Líneas rectas, perfil negro" },
    { key: "forjado", label: "Forjado clásico", foto: "obra-cerco", sub: "Barrotes con lanzas y volutas" },
    { key: "cnc", label: "Calado CNC", foto: "obra-puerta-cnc", sub: "Lámina cortada con diseño" },
  ];

  // Tarifas de ejemplo en lempiras (fabricación, pintura e instalación en TGU o SPS).
  const TARIFAS = {
    porton:  { moderno: [3200, 4200], forjado: [4200, 5800], cnc: [5200, 7200] },   // por m²
    puerta:  { moderno: [3600, 4800], forjado: [4600, 6200], cnc: [5600, 7800] },   // por m²
    ventana: { moderno: [1600, 2400], forjado: [2200, 3200], cnc: [2800, 4000] },   // por m²
    baranda: { moderno: [2200, 3000], forjado: [3000, 4400], cnc: [3800, 5400] },   // por metro lineal
  };
  const MOTOR = [16000, 26000];

  const L = n => "L " + n.toLocaleString("es-HN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const L0 = n => "L " + Math.round(n).toLocaleString("es-HN");
  const r100 = n => Math.round(n / 100) * 100;
  const norm = s => (s || "").toString().trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");

  function fresh() { return { step: "inicio", data: {}, seq: 2214 }; }

  // match a reply against the buttons we offered: by number or label
  function pick(text, options) {
    const t = norm(text).replace(/[^\w\s]/g, "").trim();
    const n = parseInt(t, 10);
    if (n >= 1 && n <= options.length && String(n) === t) return options[n - 1];
    return options.find(o => norm(o) === norm(text)) || options.find(o => t.length > 2 && norm(o).startsWith(t)) || null;
  }

  // what the person wants, from their own words
  function tipoDe(t) {
    if (/porton|portones|porto/.test(t)) return "porton";
    if (/ventana|proteccion|balcon(es)? de ventana/.test(t)) return "ventana";
    if (/baranda|barandal|pasamano|balcon|escalera|terraza|verja|cerco|muro/.test(t)) return "baranda";
    if (/puerta/.test(t)) return "puerta";
    return null;
  }
  const quierePersona = t => /persona|asesor|humano|alguien|llamen|llamar|hablar con/.test(t);
  const quierePiezas = t => /pieza|adorno|llamador|tubo|lanza|remate|voluta|hoja|flor|herreri|taller|soy herrero/.test(t);

  // "3 x 2.2", "3 por 2", "3 metros de ancho y 2 de alto", "300 x 220" (cm), "6 metros"
  const CONTADOS = /(\d+)\s*(ventanas?|puertas?|portones|protecciones)/;
  const cuantasDe = t => { const m = t.match(CONTADOS); return m ? +m[1] : 0; };
  function medidas(text) {
    const nums = (norm(text).replace(CONTADOS, "").replace(/(\d),(\d)/g, "$1.$2").match(/\d+(?:\.\d+)?/g) || []).map(Number).filter(n => n > 0);
    const cm = n => (n > 20 ? n / 100 : n);
    return nums.slice(0, 2).map(cm);
  }
  const fmt = n => String(Math.round(n * 100) / 100);

  function estilo(text) {
    const t = norm(text);
    const n = parseInt(t, 10);
    if (n >= 1 && n <= ESTILOS.length && String(n) === t) return ESTILOS[n - 1];
    if (/moderno|liso|recto|sencillo|minimal/.test(t)) return ESTILOS[0];
    if (/forja|clasic|lanza|voluta|colonial/.test(t)) return ESTILOS[1];
    if (/cnc|calad|lamina|laser|diseno|dibujo/.test(t)) return ESTILOS[2];
    return null;
  }

  function estimado(d) {
    const tar = TARIFAS[d.tipo][d.estilo];
    const cant = TIPOS[d.tipo].unidad === "ml" ? d.med[0] : d.med[0] * d.med[1] * (d.cuantas || 1);
    let lo = tar[0] * cant, hi = tar[1] * cant;
    if (d.motor) { lo += MOTOR[0]; hi += MOTOR[1]; }
    return [r100(lo), r100(hi), cant];
  }

  // next three working days, for the visit
  function dias(now) {
    const n = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];
    const out = []; const d = new Date(now || Date.now());
    while (out.length < 3) { d.setDate(d.getDate() + 1); if (d.getDay() !== 0) out.push(n[d.getDay()][0].toUpperCase() + n[d.getDay()].slice(1) + " " + d.getDate()); }
    return out;
  }
  const FRANJAS = ["8 a 10 a. m.", "10 a 12 m.", "2 a 4 p. m."];
  const LLAMADA = ["Hoy en la tarde", "Mañana en la mañana", "Mañana en la tarde"];

  const menuMsg = pre => ({ text: (pre ? pre + "\n\n" : "") + "¿Qué te gustaría cotizar?", buttons: MENU });

  function resumen(d) {
    const T = TIPOS[d.tipo], E = ESTILOS.find(e => e.key === d.estilo);
    const med = d.med ? (T.unidad === "ml" ? `${fmt(d.med[0])} m de largo` : `${fmt(d.med[0])} × ${fmt(d.med[1])} m${d.cuantas > 1 ? ` (${d.cuantas} iguales)` : ""}`) : "por medir";
    return [`${T.label}${d.motor ? " con motor" : ""}`, `Medidas: ${med}`, E ? `Estilo: ${E.label}` : null, d.ciudad ? `Lugar: ${d.ciudad}` : null].filter(Boolean).join("\n");
  }

  function handle(state, input, now) {
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

    const askMedidas = () => {
      const T = TIPOS[d.tipo];
      go("medidas");
      say({ text: T.unidad === "ml"
        ? "¿Cuántos metros de largo tiene, más o menos? Por ejemplo: 6 metros."
        : `¿Cuánto mide el espacio, más o menos? Ancho por alto en metros, por ejemplo: ${T.ejemplo}.`,
        buttons: ["No sé las medidas"] });
    };
    const askEstilo = () => {
      go("estilo");
      say({ text: "¿Qué estilo te gusta? Estos son trabajos nuestros:", gallery: ESTILOS.map(e => ({ foto: e.foto, title: e.label, sub: e.sub })), buttons: ESTILOS.map(e => e.label).concat("📷 Tengo una foto") });
    };
    const askCiudad = () => { go("ciudad"); say({ text: "¿En qué ciudad sería la instalación?", buttons: ["Tegucigalpa", "San Pedro Sula", "Otra ciudad"] }); };
    const askSiguiente = () => { go("siguiente"); say({ text: "¿Cómo seguimos?", buttons: ["Agendar visita para medir", "Que me llamen", "Escribirle a un asesor"] }); };

    const saludo = !state || /^(hola|buenas|buenos dias|buenas tardes|buenas noches|menu|inicio|0)$/.test(t);
    if (saludo) {
      reset(); go("inicio");
      if (!/^(menu|inicio|0)$/.test(t)) say("¡Hola! 👋 Soy el asistente de *Steel Works*. Te ayudo a cotizar portones, puertas, protecciones y barandas, a cualquier hora.");
      say(menuMsg());
      return { state: s, messages: out };
    }

    switch (s.step) {
      case "inicio": {
        const o = pick(text, MENU);
        const tipo = o ? Object.keys(TIPOS).find(k => TIPOS[k].label === o) : tipoDe(t);
        if (o === "Hablar con una persona" || (!tipo && quierePersona(t))) { reset(); go("asesor"); say({ text: "Claro. ¿Con qué sucursal te comunico?", buttons: ["Tegucigalpa", "San Pedro Sula"] }); break; }
        if (o === "Piezas para herrería" || (!tipo && quierePiezas(t))) {
          reset(); go("piezas");
          const desde = c => L(Math.min(...CATALOGO.filter(p => p.cat === c && p.stock).map(p => p.price)));
          say({ text: `Tenemos más de 750 piezas: adornos de barra desde ${desde("Adornos de barra")}, llamadores de acero inoxidable desde ${desde("Llamadores")}, tubos forjados, paneles CNC y más.\n\nMándame una foto de la pieza o dime para qué trabajo es, y un asesor te confirma precio y existencia.`, buttons: ["📷 Enviar foto de la pieza", "Hablar con un asesor"] });
          break;
        }
        if (!tipo) { say(menuMsg("Disculpa, no te entendí bien. Puedes tocar una opción o escribirme con tus palabras, por ejemplo «un portón de 3 metros».")); break; }
        reset({ tipo });
        // if they already wrote the measures ("portón de 4 x 2.5"), keep them and skip ahead
        const m = o ? [] : medidas(text), cuantas = o ? 0 : cuantasDe(t);
        if (cuantas > 1) d.cuantas = cuantas;
        if (TIPOS[tipo].unidad === "ml" ? m.length >= 1 : m.length >= 2) {
          d.med = m.slice(0, TIPOS[tipo].unidad === "ml" ? 1 : 2);
          say(`Perfecto: ${TIPOS[tipo].label.toLowerCase()}, ${resumen(d).split("\n")[1].replace("Medidas: ", "")}.`);
          if (tipo === "porton") { go("motor"); say({ text: "¿Lo quieres con motor eléctrico?", buttons: ["Sí, con motor", "No, manual", "Todavía no sé"] }); }
          else if (TIPOS[tipo].cuantas && !d.cuantas) { go("cuantas"); say({ text: "¿Cuántas ventanas son de ese tamaño?", buttons: ["1", "2", "3", "4", "5 o más"] }); }
          else askEstilo();
          break;
        }
        say(`Perfecto, ${TIPOS[tipo].label.toLowerCase()}.`);
        askMedidas();
        break;
      }

      case "medidas": {
        const T = TIPOS[d.tipo];
        if (/no se|no las|ni idea|no tengo/.test(t) || pick(text, ["No sé las medidas"])) {
          d.med = null; d.sinMedidas = true;
          const ref = { ...d, med: T.tipico, estilo: "moderno" };
          const [lo] = estimado(ref);
          const [, hi] = estimado({ ...ref, estilo: "cnc" });
          say(`No hay problema, para eso vamos a medir sin costo. Para que tengas una idea: ${T.uno} de ${T.unidad === "ml" ? T.tipico[0] + " metros" : T.tipico.join(" × ") + " m"} anda entre *${L0(lo)}* y *${L0(hi)}*, según el estilo.`);
          askCiudad();
          break;
        }
        const m = medidas(text);
        if (T.unidad === "ml" ? !m.length : m.length < 2) {
          say({ text: T.unidad === "ml" ? "No logré leer los metros. Escríbeme solo el número, por ejemplo: 6." : `No logré leer las medidas. Escríbelas así: ${T.ejemplo} (ancho por alto). Si no las tienes, no pasa nada, te visitamos para medir.`, buttons: ["No sé las medidas"] });
          break;
        }
        d.med = m.slice(0, T.unidad === "ml" ? 1 : 2);
        if (T.cuantas && !d.cuantas) { go("cuantas"); say({ text: "¿Cuántas ventanas son de ese tamaño?", buttons: ["1", "2", "3", "4", "5 o más"] }); break; }
        if (d.tipo === "porton") { go("motor"); say({ text: "¿Lo quieres con motor eléctrico?", buttons: ["Sí, con motor", "No, manual", "Todavía no sé"] }); break; }
        askEstilo();
        break;
      }

      case "cuantas": {
        const n = parseInt(t.replace(/[^0-9]/g, ""), 10);
        if (!n) { say({ text: "Escríbeme solo el número, por ejemplo 3.", buttons: ["1", "2", "3", "4", "5 o más"] }); break; }
        if (/mas/.test(t)) { go("cuantas_n"); say("¿Cuántas en total?"); break; }
        d.cuantas = n; askEstilo();
        break;
      }
      case "cuantas_n": {
        const n = parseInt(t.replace(/[^0-9]/g, ""), 10);
        if (!n) { say("Escríbeme solo el número, por ejemplo 6."); break; }
        d.cuantas = n; askEstilo();
        break;
      }

      case "motor": {
        d.motor = /^si|motor|1/.test(t) && !/^no/.test(t);
        askEstilo();
        break;
      }

      case "estilo": {
        if (/foto/.test(t)) { say({ image: true, text: "" }); d.foto = true; d.estilo = "cnc"; say("¡Qué bonito! 📷 Se parece a nuestro calado CNC. Con esa foto el taller lo cotiza igual."); askCiudad(); break; }
        const e = estilo(text);
        if (!e) { say({ text: "Toca uno de los estilos, o mándame una foto de uno que te guste.", buttons: ESTILOS.map(x => x.label).concat("📷 Tengo una foto") }); break; }
        d.estilo = e.key;
        askCiudad();
        break;
      }

      case "ciudad": {
        if (/otra/.test(t) && text.length < 14) { go("ciudad_n"); say("¿En qué ciudad?"); break; }
        d.ciudad = pick(text, ["Tegucigalpa", "San Pedro Sula"]) || text.trim();
        return handle(Object.assign(s, { step: "cotizar" }), "", now);
      }
      case "ciudad_n": { d.ciudad = text.trim(); return handle(Object.assign(s, { step: "cotizar" }), "", now); }

      case "cotizar": {
        d.sucursal = /pedro|sps|choloma|villanueva|progreso|puerto cortes|la lima|tela|ceiba|santa barbara|copan/.test(norm(d.ciudad)) ? "SPS" : "TGU";
        const lejos = !/tegucigalpa|comayaguela|tgu|san pedro|sps/.test(norm(d.ciudad));
        if (d.med && d.estilo) {
          const [lo, hi] = estimado(d);
          d.rango = [lo, hi];
          say({ text: `📐 *Tu cotización inicial*\n\n${resumen(d)}\n\n💰 Precio estimado: *${L0(lo)} a ${L0(hi)}*\nIncluye fabricación, pintura e instalación${lejos ? ". Fuera de Tegucigalpa y San Pedro Sula se suma el traslado" : ""}.\n\nEl precio final lo confirma el taller cuando mide, sin costo.` });
        } else {
          say({ text: `📐 *Tu solicitud*\n\n${resumen(d)}\n\nCon la visita para medir te damos el precio exacto, sin costo.` });
        }
        askSiguiente();
        break;
      }

      case "siguiente": {
        const o = pick(text, offered.length ? offered : ["Agendar visita para medir", "Que me llamen", "Escribirle a un asesor"]) || (/visita|medir|agend/.test(t) ? "Agendar visita para medir" : /llam/.test(t) ? "Que me llamen" : /asesor|persona/.test(t) ? "Escribirle a un asesor" : null);
        if (o === "Agendar visita para medir") { go("dia"); s.dias = dias(now); say({ text: "¿Qué día te queda bien?", buttons: s.dias }); }
        else if (o === "Que me llamen") { go("hora_llamada"); say({ text: "¿Cuándo te llamamos?", buttons: LLAMADA }); }
        else if (o === "Escribirle a un asesor") { d.cita = "Le escribe un asesor por este chat"; go("nombre"); say("Va. ¿A nombre de quién dejo la cotización?"); }
        else askSiguiente();
        break;
      }

      case "dia": {
        const o = pick(text, s.dias || dias(now)) || text.trim();
        d.dia = o; go("franja");
        say({ text: `${o}. ¿A qué hora?`, buttons: FRANJAS });
        break;
      }
      case "franja": {
        const o = pick(text, FRANJAS) || text.trim();
        d.cita = `Visita para medir: ${d.dia}, ${o}`;
        go("nombre"); say("¿A nombre de quién la agendo?");
        break;
      }
      case "hora_llamada": {
        const o = pick(text, LLAMADA) || text.trim();
        d.cita = `Llamada: ${o.toLowerCase()}`;
        go("nombre"); say("¿A nombre de quién?");
        break;
      }

      case "nombre": {
        d.nombre = text.trim().replace(/^(soy|me llamo|a nombre de)\s+/i, "").replace(/^\w/, c => c.toUpperCase());
        const b = SUCURSALES[d.sucursal || "TGU"];
        const n = "COT-" + (++s.seq);
        s.lead = { n, nombre: d.nombre, resumen: resumen(d).replace(/\n/g, " · "), rango: d.rango || null, cita: d.cita, sucursal: b.nombre };
        say({ text: `✅ *Listo, ${d.nombre.split(" ")[0]}.*\n\n${d.cita}\nCotización ${n}\n\nLe pasé tu ficha a la sucursal de *${b.nombre}* con ${[d.med && "las medidas", d.estilo && "el estilo", d.foto && "tu foto", d.rango && "el precio estimado"].filter(Boolean).join(", ").replace(/, ([^,]*)$/, " y $1") || "lo que hablamos"}. Te confirman por aquí mismo.\n\nSi necesitas algo antes: ${b.tel[0]}` });
        say({ text: "¿Te ayudo con algo más?", buttons: ["Cotizar otra cosa", "Sucursales y horario"] });
        go("post");
        break;
      }

      case "piezas": {
        if (/foto/.test(t)) { say({ image: true, text: "" }); }
        if (/asesor|persona/.test(t)) { go("asesor"); say({ text: "¿Con qué sucursal te comunico?", buttons: ["Tegucigalpa", "San Pedro Sula"] }); break; }
        say({ text: "Recibido. Un asesor de bodega lo revisa y te escribe con precio y existencia. Si se nos agotó, te avisamos apenas vuelva a entrar. 🔔\n\n¿De qué sucursal te queda mejor retirar, o te la enviamos?", buttons: ["Tegucigalpa", "San Pedro Sula", "Envío a mi ciudad"] });
        go("piezas_entrega");
        break;
      }
      case "piezas_entrega": {
        const o = pick(text, offered) || text.trim();
        s.lead = { n: "PZ-" + (++s.seq), nombre: "Cliente de piezas", resumen: "Piezas para herrería · foto enviada", rango: null, cita: o, sucursal: /pedro/i.test(o) ? "San Pedro Sula" : "Tegucigalpa" };
        say({ text: `Anotado: ${o}. Te escriben por aquí en horario de tienda.`, buttons: ["Cotizar otra cosa"] });
        go("post");
        break;
      }

      case "asesor": {
        const o = pick(text, ["Tegucigalpa", "San Pedro Sula"]) || "Tegucigalpa";
        const b = SUCURSALES[o === "Tegucigalpa" ? "TGU" : "SPS"];
        say({ text: `Listo, le pasé la conversación a un asesor de *${b.nombre}* con todo lo que hablamos. Te escribe por aquí mismo en horario de tienda. 🙌\n\nSi es urgente: ${b.tel[0]}`, buttons: ["Cotizar otra cosa"] });
        s.handoff = b.nombre; go("post");
        break;
      }

      default: { // "post"
        const o = pick(text, offered);
        if (o === "Sucursales y horario" || /sucursal|horario|direccion|donde/.test(t)) {
          say(Object.values(SUCURSALES).map(b => `📍 *${b.nombre}*\n${b.dir}\nTel. ${b.tel.join(" · ")}`).join("\n\n") + `\n\n🕗 ${HORARIO}`);
          say({ text: "¿Algo más?", buttons: ["Cotizar otra cosa"] });
          break;
        }
        reset(); go("inicio");
        if (o === "Cotizar otra cosa" || !t) { say(menuMsg()); break; }
        return handle(s, text, now);
      }
    }
    return { state: s, messages: out };
  }

  // plain-text rendering for channels without buttons (Twilio, SMS)
  function toText(m) {
    let s = m.text || "";
    if (m.gallery) s += "\n\n" + m.gallery.map((g, i) => `${i + 1}. ${g.title}: ${g.sub}`).join("\n");
    const rest = m.buttons ? m.buttons.slice(m.gallery ? m.gallery.length : 0) : [];
    const k = m.gallery ? m.gallery.length : 0;
    if (rest.length) s += (k ? "\n" : "\n\n") + rest.map((b, i) => `${k + i + 1}. ${b}`).join("\n");
    return s.trim();
  }

  return { handle, toText, fresh, CATALOGO, SUCURSALES, ESTILOS, TARIFAS, MENU, L };
});
