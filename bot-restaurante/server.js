// Bot de WhatsApp para restaurantes · webhook de Twilio + panel del dueño.  npm start
//
//   POST /whatsapp                 Twilio > WhatsApp sender > "When a message comes in"
//   GET|POST /meta                 WhatsApp directo con Meta (Cloud API, ver meta.js): con META_TOKEN no hace falta Twilio
//   GET  /panel                    panel del dueño y pantalla de cocina (correo y contraseña, ver auth.js)
//   GET  /api/pedidos              pedidos en JSON (sesión del panel, o Authorization: Bearer <LEADS_TOKEN>)
//   POST /api/pedidos/:n/estado    { estado } por_pagar | nuevo | cocina | listo | entregado | no_vino | cancelado | atendido (sesión del panel)
//   GET  /api/negocio              menú y sucursales para el panel (sesión del panel)
//   POST /pagos/aviso/:n?t=        aviso de la pasarela de pago (Tilopay webhook_url); el pago se confirma consultando la API
//   GET  /pagos/listo/:n?t=        a donde vuelve el cliente después de pagar con tarjeta
//   GET  /                         "<restaurante> · bot activo" (chequeo de salud)
//
// Cada pedido se guarda en pedidos.json y se avisa por WhatsApp al dueño y a la sucursal. Cuando la cocina
// lo marca "listo" en el panel, al cliente le llega "su pedido está listo". Configuración: .env (ver .env.example).
// Cobro antes de cocinar (negocio.cobro): el pedido queda "por_pagar"; el cliente manda la foto del comprobante,
// le llega al dueño, y al tocar "Pago recibido" en el panel pasa a "nuevo" (cocina). "No vino" cuenta faltas por número.
// Con pasarela (PAGOS_PASARELA=tilopay, ver pagos.js) cada pedido lleva su link de tarjeta y, si el pago sale bien,
// pasa solo a cocina: al cliente le llega "recibimos su pago" y a la sucursal el pedido.
// El restaurante (menú, precios, sucursales) está en negocios/<cliente>.json; NEGOCIO dice cuál.
// Con ANTHROPIC_API_KEY, WhatsApp contesta en modo IA (ia.js, Claude); si la API falla contesta el menú de engine.js.
const path = require("path");
const crypto = require("crypto");
const express = require("express");
const twilio = require("twilio");
const { cargarNegocio, LINK, fechasCupos } = require("./negocio");
const { createPasarela } = require("./pagos");
const { createEngine, toText } = require("./engine");
const { createStore } = require("./store");
const { createCifra } = require("./cifrado");
const { createBitacora } = require("./bitacora");
const { createNotifier, fichaTexto, waAddr, digits } = require("./avisos");
const { createUsuarios, montarPanel } = require("./auth");
const { createIA, MODELO } = require("./ia");
const { cabeceras, soloHttps, createLimite } = require("./seguridad");
const { montarDemo } = require("./demo");
const { createMeta, mensajes: mensajesMeta } = require("./meta");

const on = v => /^(1|true|si|sí|yes)$/i.test(String(v || "").trim());
const ESTADOS = ["por_pagar", "nuevo", "cocina", "listo", "entregado", "no_vino", "cancelado", "atendido", "por_confirmar", "confirmada", "sin_cupo", "en_espera"];

function loadConfig(env = process.env) {
  const sandbox = on(env.TWILIO_SANDBOX);
  return {
    port: +env.PORT || 3000,
    negocio: env.NEGOCIO || "negocios/ejemplo.json",
    sid: env.TWILIO_ACCOUNT_SID || "",
    token: env.TWILIO_AUTH_TOKEN || "",
    sandbox,
    from: waAddr(env.TWILIO_WHATSAPP_FROM || env.META_NUMERO || (sandbox ? "+14155238886" : "")),
    // WhatsApp directo con Meta (Cloud API): con token e id del número, el bot habla por Meta y no usa Twilio
    meta: { token: env.META_TOKEN || "", phoneId: env.META_PHONE_ID || "", appSecret: env.META_APP_SECRET || "", verifyToken: env.META_VERIFY_TOKEN || "", plantilla: env.META_PLANTILLA || "", plantillaCodigo: env.META_PLANTILLA_CODIGO || "", idioma: env.META_PLANTILLA_IDIOMA || "es" },
    contentSid: env.TWILIO_ALERT_CONTENT_SID || "",
    owner: env.OWNER_WHATSAPP || "",
    publicUrl: (env.PUBLIC_URL || "").replace(/\/$/, ""),
    skipSignature: on(env.SKIP_TWILIO_SIGNATURE),
    leadsToken: env.LEADS_TOKEN || "",
    panelSecret: env.PANEL_SECRET || "",
    panelUsuarios: env.PANEL_USUARIOS || "",
    dataDir: env.DATA_DIR === "" ? null : path.resolve(__dirname, env.DATA_DIR || "data"),
    // cifra pedidos, clientes y usuarios en el disco (cifrado.js). En Render es obligatoria
    dataKey: env.DATA_KEY || "",
    exigirCifrado: on(env.RENDER) || on(env.EXIGIR_CIFRADO),
    ttlHours: +env.SESSION_TTL_HOURS || 12,
    // modo IA (Claude): solo si hay clave y BOT_IA no es "off"
    anthropicKey: /^off$/i.test(String(env.BOT_IA || "").trim()) ? "" : env.ANTHROPIC_API_KEY || "",
    anthropicModel: env.ANTHROPIC_MODEL || MODELO,
    // pago con tarjeta (opcional): cuenta de comercio del restaurante en la pasarela
    pasarela: { proveedor: (env.PAGOS_PASARELA || "").trim().toLowerCase(), usuario: env.TILOPAY_API_USER || "", clave: env.TILOPAY_API_PASSWORD || "", key: env.TILOPAY_KEY || "", moneda: env.PAGOS_MONEDA || "HNL" },
    pagosSecret: env.PAGOS_SECRET || env.PANEL_SECRET || "",
    // freno por número de WhatsApp: mensajes cada 10 minutos, y respuestas con IA por día (después contesta el menú)
    limiteMensajes: +env.LIMITE_MENSAJES || 40,
    limiteIA: +env.LIMITE_IA_DIA || 80,
    // demostración con IA para la página de Clientia Tech (demo.js): DEMO_IA=on y la misma ANTHROPIC_API_KEY
    demoIA: on(env.DEMO_IA),
    demoKey: env.ANTHROPIC_API_KEY || "",
    demoOrigenes: String(env.DEMO_ORIGENES || "https://clientiatech.com,https://www.clientiatech.com").split(",").map(s => s.trim()).filter(Boolean),
    demoPorVisitante: +env.DEMO_LIMITE_VISITANTE || 15,
    demoPorDia: +env.DEMO_LIMITE_DIA || 400,
  };
}

function createApp(cfg = loadConfig(), deps = {}) {
  const log = deps.log || console.log;
  const negocio = deps.negocio || cargarNegocio(cfg.negocio);
  const pasarela = "pasarela" in deps ? deps.pasarela : createPasarela(cfg.pasarela);
  if (pasarela) negocio.cobro = { ...negocio.cobro, activo: true, pasarela: true };
  const motor = createEngine(negocio);
  const cifra = createCifra(cfg.dataKey);
  if (cfg.dataDir && !cifra && cfg.exigirCifrado) throw new Error("Falta DATA_KEY: en el servidor los datos de los clientes se guardan cifrados (ver README, Seguridad).");
  const store = deps.store || createStore(cfg.dataDir, { ttlHours: cfg.ttlHours, cifra });
  const bitacora = createBitacora({ dir: cfg.dataDir, cifra, now: deps.now || (() => new Date()), log });
  const now = deps.now || (() => new Date());
  const mc = cfg.meta || {};
  const meta = "meta" in deps ? deps.meta : mc.token && mc.phoneId ? createMeta({ ...mc, log, ...(deps.metaFetch ? { fetch: deps.metaFetch } : {}) }) : null;
  const client = meta ? null : "client" in deps ? deps.client : cfg.sid && cfg.token ? twilio(cfg.sid, cfg.token) : null;
  const avisos = createNotifier({ client, canal: meta, from: cfg.from, contentSid: cfg.contentSid, sandbox: cfg.sandbox, owner: cfg.owner, negocio, log });
  const ia = "ia" in deps ? deps.ia : cfg.anthropicKey ? createIA({ negocio, apiKey: cfg.anthropicKey, model: cfg.anthropicModel }) : null;
  const pending = new Set();                      // messages in flight (tests wait on them)
  const track = p => { pending.add(p); p.finally(() => pending.delete(p)); return p; };

  const app = express();
  app.set("trust proxy", true);
  app.disable("x-powered-by");
  app.use(soloHttps, cabeceras());
  app.use(express.urlencoded({ extended: false, limit: "20kb" }));
  const limite = createLimite({ max: cfg.limiteMensajes, minutos: 10 });
  const limiteIA = createLimite({ max: cfg.limiteIA, minutos: 24 * 60 });

  // only Twilio may post to the webhook (SKIP_TWILIO_SIGNATURE=true for local tests)
  function firma(req, res, next) {
    if (cfg.skipSignature) return next();
    if (!cfg.token) { log("[error] falta TWILIO_AUTH_TOKEN para validar la firma de Twilio"); return res.status(500).send("Falta configuración"); }
    const url = (cfg.publicUrl || `${req.protocol}://${req.get("host")}`) + req.originalUrl;
    if (twilio.validateRequest(cfg.token, req.get("X-Twilio-Signature") || "", url, req.body || {})) return next();
    log(`[firma inválida] ${url}`);
    res.status(403).send("Firma de Twilio inválida");
  }

  const numero = pre => pre + "-" + (store.seq = store.seq + 1);
  const faltasDe = tel => store.faltas(tel);
  // cupos already taken in one batch (negocio.cupos): every order of that day and batch except cancelled ones and the waiting list
  const ocupados = (fecha, tanda) => store.pedidos.reduce((a, p) => a + (p.tipo === "pedido" && p.diaFecha === fecha && p.tanda === tanda && !["cancelado", "en_espera"].includes(p.estado) ? p.cupos || 0 : 0), 0);
  const porPagar = tel => store.pedidos.findLast(p => p.estado === "por_pagar" && digits(p.tel) === digits(tel)) || null;
  function guardar(base, tel, convo) {
    const faltas = base.tipo === "pedido" ? faltasDe(tel) : 0;
    const p = store.addPedido({ ...base, n: base.n || numero({ persona: "AS", reservacion: "RES" }[base.tipo] || "PED"), tel: "+" + digits(tel), fecha: now().toISOString(), estado: base.estado || "nuevo", ...(faltas ? { faltas } : {}), convo });
    log(`[${p.tipo} ${p.n} · ${p.sucursal}] ${p.tel} ${p.tipo === "pedido" ? negocio.L(p.total) : p.tipo === "reservacion" ? p.resumen : p.motivo || ""}`);
    track(avisos.ficha(p));
    return p;
  }
  const persona = (motivo, sucursal, tel, convo) => guardar({ tipo: "persona", nombre: null, sucursal, motivo }, tel, convo);

  // one turn of the menu engine
  function conversar(key, text) {
    const sess = store.getSession(key) || { state: null, convo: [] };
    if (sess.state) sess.state.seq = store.seq;    // one numbering for all customers
    const r = motor.handle(sess.state, text, now(), { faltas: faltasDe(key), ocupados });
    const out = r.messages.map(toText).filter(Boolean);
    out.mensajes = r.messages.filter(m => m.text);
    sess.convo = sess.convo.concat([[text, 1]], out.map(m => [m, 0])).slice(-16);
    if (r.state.lead) { store.seq = r.state.seq; out.pedido = guardar(r.state.lead, key, sess.convo); delete r.state.lead; }
    if (r.state.handoff) { persona("", r.state.handoff, key, sess.convo); delete r.state.handoff; }
    if (r.state.cancelar) { cancelarPorCliente(r.state.cancelar, key); delete r.state.cancelar; }
    sess.state = r.state;
    store.setSession(key, sess);
    return out;
  }

  // AI mode: Claude answers; on any API error or timeout this message goes to the menu engine
  async function conversarIA(key, text, base) {
    const sess = store.getSession(key) || { state: null, convo: [] };
    let r;
    try {
      r = await ia.turn(sess.ia || [], text, now(), { numero: (pre = "PED") => numero(pre), faltas: faltasDe(key), ocupados });
    } catch (e) {
      log(`[ia] error, contesta el menú: ${e.constructor && e.constructor.name}${e.status ? " " + e.status : ""} ${e.message}`);
      const convo = sess.convo.concat([[text, 1]]).slice(-16);
      if (e.pedido) guardar(e.pedido, key, convo);
      if (e.persona) persona(e.persona.motivo, e.persona.sucursal, key, convo);
      if (e.reservacion) guardar(e.reservacion, key, convo);
      return null;
    }
    sess.ia = r.history;
    sess.convo = sess.convo.concat([[text, 1], [r.reply, 0]]).slice(-16);
    let reply = r.reply;
    if (r.pedido) {
      const p = guardar(r.pedido, key, sess.convo);
      if (p.estado === "por_pagar" && pasarela) {
        if (!reply.includes(LINK)) reply += `\n\n💳 *Con tarjeta:* ${LINK}`;
        reply = await conLink(reply, p, base);
      }
    }
    reply = reply.split(LINK).join("");          // never show the placeholder
    if (r.persona) persona(r.persona.motivo, r.persona.sucursal, key, sess.convo);
    if (r.reservacion) guardar(r.reservacion, key, sess.convo);
    store.setSession(key, sess);
    return reply;
  }

  // ---- pago con tarjeta por pasarela ----
  const firmaPago = n => crypto.createHmac("sha256", cfg.pagosSecret || "sin-secreto").update("pago:" + n).digest("base64url").slice(0, 32);
  const firmaOk = (n, t) => { const a = Buffer.from(String(t || "")), b = Buffer.from(firmaPago(n)); return !!cfg.pagosSecret && a.length === b.length && crypto.timingSafeEqual(a, b); };
  // one card payment link per order; replaces the placeholder in the bot's message
  async function conLink(texto, p, base) {
    if (!texto.includes(LINK)) return texto;
    let url = p.pagoLink && p.pagoLink.url;
    if (!url && pasarela) {
      try {
        const q = `?t=${firmaPago(p.n)}`;
        const l = await pasarela.crearLink({ n: p.n, total: p.total, nombre: p.nombre, descripcion: `${negocio.nombre} · pedido ${p.n}: ${p.resumen || ""}`, webhookUrl: `${base}/pagos/aviso/${encodeURIComponent(p.n)}${q}`, volverUrl: `${base}/pagos/listo/${encodeURIComponent(p.n)}${q}` });
        store.updatePedido(p.n, { pagoLink: { ...l, proveedor: pasarela.proveedor, fecha: now().toISOString() } });
        url = l.url;
      } catch (e) { log(`[pago ${p.n}] no se pudo crear el link: ${e.message}`); }
    }
    return texto.split(LINK).join(url || "no está disponible en este momento. Puede pagar por transferencia o escribirnos.");
  }
  // marks the order paid and sends it to the kitchen (from the panel, or when the gateway confirms a card payment)
  function confirmarPago(p, { por, metodo }) {
    const t = now().toISOString();
    const q = store.updatePedido(p.n, { estado: "nuevo", t_nuevo: t, pagado: true, t_pagado: t, metodoPago: metodo, por });
    track(avisos.pagado(q));
    if (metodo === "tarjeta") track(avisos.ficha(q));   // the kitchen and owner get the order, now paid
    log(`[${q.n}] pago confirmado (${metodo}, ${por})`);
    return q;
  }
  // asks the gateway whether the order's link was paid; the gateway's notice alone is never trusted
  const revisando = new Map();
  function revisarPago(n, aviso = {}) {
    if (revisando.has(n)) return revisando.get(n);
    const tarea = (async () => {
      const p = store.getPedido(n);
      if (!pasarela || !p || !p.pagoLink) return p;
      if (p.estado !== "por_pagar") return p;
      let v;
      try { v = await pasarela.verificar(p.pagoLink.id, p.total); }
      catch (e) { log(`[pago ${n}] no se pudo consultar la pasarela: ${e.message}`); return p; }
      const actual = store.getPedido(n);
      if (actual.estado !== "por_pagar") return actual;
      if (v.pagado) return confirmarPago(actual, { por: pasarela.proveedor, metodo: "tarjeta" });
      const code = aviso.code ?? aviso.codigo;
      if (code != null && String(code) !== "1" && !actual.avisoRechazo) {
        store.updatePedido(n, { avisoRechazo: true });
        track(avisos.enviar(waAddr(actual.tel), `⚠️ Su pago con tarjeta del pedido *${n}* no pasó${aviso.codeDescription ? ` (${String(aviso.codeDescription).slice(0, 80)})` : ""}. Puede intentar otra vez con el mismo link o con otra tarjeta${negocio.cobro.transferencia ? ", o pagar por transferencia" : ""}.`));
      }
      return actual;
    })().finally(() => revisando.delete(n));
    revisando.set(n, tarea);
    return track(tarea);
  }
  // safety net: the gateway sends its notice once, so unpaid card orders from the last 3 hours are checked again
  function revisarPendientes() {
    const desde = now() - 3 * 3600e3;
    return Promise.all(store.pedidos.filter(p => p.estado === "por_pagar" && p.pagoLink && new Date(p.pagoLink.fecha) >= desde).map(p => revisarPago(p.n)));
  }

  // the customer cancels an order that was still waiting for payment
  function cancelarPorCliente(n, tel) {
    const p = store.getPedido(n);
    if (!p || p.estado !== "por_pagar" || digits(p.tel) !== digits(tel)) return;
    store.updatePedido(n, { estado: "cancelado", t_cancelado: now().toISOString(), por: "cliente" });
    log(`[${n}] cancelado por el cliente antes de pagar`);
    liberados(p);
  }
  // a cancelled order frees its cupos: the owner hears who is on the waiting list, to write to them
  function liberados(p) {
    if (!p.tanda) return;
    const espera = store.pedidos.filter(x => x.estado === "en_espera");
    if (!espera.length) return;
    const t = { titulo: `Se liberaron ${p.cupos} ${p.cupos === 1 ? "cupo" : "cupos"} · ${p.dia}, ${p.tanda}`,
      lineas: [`${p.n} se canceló. En lista de espera:`, ...espera.slice(0, 5).map(x => `👤 ${x.nombre || "Sin nombre"} · ${x.cupos} ${x.cupos === 1 ? "cupo" : "cupos"} para ${x.dia} · https://wa.me/${digits(x.tel)}`)] };
    track(Promise.all(avisos.destinos(p.sucursal).map(to => avisos.enviar(to, `🔔 *${t.titulo}*\n\n${t.lineas.join("\n")}`, t))));
  }
  // a photo from a customer with an unpaid order = the payment receipt: goes to the owner and branch
  function comprobante(from, mediaUrl) {
    const p = porPagar(from);
    if (!p) return null;
    store.updatePedido(p.n, { comprobante: true, t_comprobante: now().toISOString(), ...(typeof mediaUrl === "string" ? { comprobanteUrl: mediaUrl } : {}) });
    track(avisos.comprobante(p, mediaUrl));
    const sess = store.getSession(from);
    if (sess && sess.state && sess.state.step === "pago") { sess.state.step = "post"; sess.state.pago = null; sess.state.offer = null; store.setSession(from, sess); }
    log(`[${p.n}] comprobante recibido`);
    return `📩 Recibimos su comprobante del pedido *${p.n}*. Lo revisamos y, en cuanto se confirme, entra a cocina. Le avisamos por aquí.`;
  }

  const esDueno = from => cfg.owner && digits(from) === digits(cfg.owner);
  function pendientes() {
    const ls = store.pedidos.filter(p => ["por_pagar", "nuevo", "cocina", "por_confirmar"].includes(p.estado)).slice(-10).reverse();
    if (!ls.length) return "📋 No hay pedidos ni clientes pendientes.";
    return "📋 *Pendientes*\n\n" + ls.map(p => { const t = fichaTexto(p, negocio.L); return `*${t.titulo}*\n${t.lineas.slice(0, -1).join("\n")}`; }).join("\n\n");
  }

  const baseDe = req => cfg.publicUrl || `${req.protocol}://${req.get("host")}`;

  // ---- WhatsApp ----
  // one customer message -> the bot's replies [{ text, buttons? }] (the same for Twilio and Meta)
  async function turno(from, text, { foto, media, base }) {
    let reply;
    // too many messages from one number: one notice, then silence until the window passes
    if (!esDueno(from) && !limite.pasa(digits(from) || from)) {
      if (!limite.primeraVezFuera(digits(from) || from)) return [];
      log(`[freno] ${from} pasó de ${cfg.limiteMensajes} mensajes en 10 minutos`);
      return [{ text: "Recibimos muchos mensajes seguidos. En unos minutos le seguimos atendiendo por aquí." }];
    }
    if (esDueno(from) && /^(pedidos|pendientes|agenda)$/i.test(text.trim())) return [{ text: pendientes().slice(0, 1590) }];
    if (foto && (reply = comprobante(from, media))) return [{ text: reply }];
    if (ia && limiteIA.pasa(digits(from) || from) && (reply = await conversarIA(from, text, base))) return [{ text: reply.slice(0, 1590) }];
    const out = conversar(from, text);
    return Promise.all(out.mensajes.map(async m => ({ ...m, text: (out.pedido ? await conLink(m.text, out.pedido, base) : m.text).split(LINK).join("") })));
  }

  app.post("/whatsapp", firma, async (req, res) => {
    const p = req.body || {};
    const foto = Number(p.NumMedia || 0) > 0;
    const text = (foto && !p.Body ? "📷 foto" : String(p.Body || "")).slice(0, 1000);
    const tw = new twilio.twiml.MessagingResponse();
    // one WhatsApp message per turn keeps the order and costs one message
    let buf = "";
    for (const t of (await turno(p.From || "anon", text, { foto, media: p.MediaUrl0, base: baseDe(req) })).map(toText)) { if (buf && (buf + "\n\n" + t).length > 1590) { tw.message(buf); buf = t; } else buf = buf ? buf + "\n\n" + t : t; }
    if (buf) tw.message(buf.slice(0, 1590));
    res.type("text/xml").send(tw.toString());
  });

  // Meta Cloud API: answers 200 at once (Meta retries otherwise) and replies with its own calls
  if (meta) {
    const vistos = new Set();
    app.get("/meta", (req, res) => {
      const q = req.query;
      if (q["hub.mode"] === "subscribe" && mc.verifyToken && q["hub.verify_token"] === mc.verifyToken) return res.type("text/plain").send(String(q["hub.challenge"] || ""));
      res.sendStatus(403);
    });
    app.post("/meta", express.json({ limit: "200kb", verify: (req, res, buf) => { req.crudo = buf; } }), (req, res) => {
      if (!meta.firmaOk(req.crudo, req.get("X-Hub-Signature-256"))) { log("[meta] firma inválida"); return res.sendStatus(403); }
      res.sendStatus(200);
      const base = baseDe(req);
      track((async () => {
        for (const m of mensajesMeta(req.body)) {
          if (vistos.has(m.id)) continue;                 // Meta can deliver the same message twice
          vistos.add(m.id); if (vistos.size > 2000) vistos.delete(vistos.values().next().value);
          const foto = !!m.foto;
          if (!foto && !m.text) { await meta.responder(m.from, "Por ahora solo leo texto y fotos. ¿Me lo puede escribir?").catch(e => log(`[meta] ${e.message}`)); continue; }
          let id = null;
          const media = foto ? () => (id = id || meta.reenviable(m.foto).catch(e => { log(`[meta] foto: ${e.message}`); return null; })) : null;
          try {
            const out = await turno(m.from, foto && !m.text ? "📷 foto" : m.text, { foto, media, base });
            for (const r of out) await meta.responder(m.from, r);
          } catch (e) { log(`[meta] no se pudo contestar a ${m.from}: ${e.message}`); }
        }
      })());
    });
  }

  // ---- Panel del dueño (correo y contraseña; ver auth.js) ----
  const usuarios = deps.usuarios || createUsuarios({ env: cfg.panelUsuarios, file: cfg.dataDir ? path.join(cfg.dataDir, "usuarios.json") : null, cifra });
  // the second step: a 6-digit code to the person's WhatsApp, from the business' own number
  const enviarCodigo = (meta || client) ? async (wa, c) => {
    const texto = `🔐 Su código para entrar al panel de ${negocio.nombre} es *${c}*. Vence en 5 minutos.\n\nNo se lo dé a nadie: nadie de ${negocio.nombre} ni de Casa Digital se lo va a pedir.`;
    if (meta) return meta.codigo(wa, c, texto);
    return !!(await avisos.enviar(waAddr(wa), texto, { titulo: `Código para entrar al panel: ${c}`, lineas: ["Vence en 5 minutos. No se lo dé a nadie."] }));
  } : null;
  const panel = montarPanel(app, { secret: cfg.panelSecret, usuarios, archivoPanel: path.join(__dirname, "panel", "panel.html"), archivoSesiones: cfg.dataDir ? path.join(cfg.dataDir, "sesiones-cerradas.json") : null, marca: negocio.nombre, color: negocio.color, log, enviarCodigo: deps.enviarCodigo || enviarCodigo, bitacora: bitacora.anotar });
  const sinSesion = (req, res) => { if (panel.usuarioDe(req)) return false; res.status(401).json({ error: "sin sesión" }); return true; };

  app.get("/api/pedidos", (req, res) => {
    res.set("Cache-Control", "no-store");
    if (panel.usuarioDe(req)) return res.json(store.pedidos.slice(-500).reverse());
    const given = (req.get("Authorization") || "").replace(/^Bearer\s+/i, "");
    const a = Buffer.from(given), b = Buffer.from(cfg.leadsToken);
    if (!cfg.leadsToken || a.length !== b.length || !crypto.timingSafeEqual(a, b)) return res.status(401).json({ error: "token inválido" });
    res.json(store.pedidos.slice(-500).reverse());
  });
  app.get("/api/negocio", (req, res) => {
    if (sinSesion(req, res)) return;
    res.set("Cache-Control", "no-store").json({ nombre: negocio.nombre, color: negocio.color, moneda: negocio.moneda, cobro: negocio.cobro.activo, reservaciones: !!negocio.reservaciones,
      cupos: negocio.cupos ? { tandas: negocio.cupos.tandas, porTanda: negocio.cupos.porTanda, dias: fechasCupos(negocio, now(), true).map(f => ({ ...f, abierto: fechasCupos(negocio, now()).some(x => x.fecha === f.fecha) })) } : null,
      sucursales: negocio.sucursales.map(({ id, nombre }) => ({ id, nombre })), menu: negocio.items.map(({ id, nombre, categoria, precio }) => ({ id, nombre, categoria, precio })), modoIA: !!ia, usuario: panel.usuarioDe(req).nombre });
  });
  app.post("/api/pedidos/:n/estado", express.json({ limit: "2kb" }), (req, res) => {
    if (sinSesion(req, res)) return;
    const origen = req.get("Origin");
    if (origen && origen !== `${req.protocol}://${req.get("host")}`) return res.status(403).json({ error: "origen no permitido" });
    const estado = String((req.body || {}).estado || "");
    if (!ESTADOS.includes(estado)) return res.status(400).json({ error: "estado inválido" });
    const antes = store.getPedido(req.params.n);
    if (!antes) return res.status(404).json({ error: "no existe" });
    const yaAvisado = antes.avisoListo, estadoAntes = antes.estado;
    const pagoRecibido = antes.estado === "por_pagar" && estado !== "cancelado" && !antes.pagado && antes.tipo === "pedido";
    if (pagoRecibido) confirmarPago(antes, { por: panel.usuarioDe(req).correo, metodo: "manual" });
    const p = store.updatePedido(req.params.n, { estado, [`t_${estado}`]: now().toISOString(), por: panel.usuarioDe(req).correo });
    if (estado === "listo" && p.tipo === "pedido" && !yaAvisado) { store.updatePedido(p.n, { avisoListo: true }); track(avisos.listo(p)); }
    if (p.tipo === "reservacion" && ["confirmada", "sin_cupo"].includes(estado) && estadoAntes !== estado) track(avisos.reservacion(p));
    if (estado === "cancelado" && !["cancelado", "en_espera"].includes(estadoAntes)) liberados(p);
    log(`[panel] ${p.n} -> ${estado} (${p.por})`);
    if (estadoAntes !== estado) bitacora.anotar("estado", { correo: p.por, pedido: p.n, de: estadoAntes, a: estado, ip: req.ip });
    res.json(p);
  });

  // who has access, whether the data is encrypted, and the last logins and changes
  app.get("/api/seguridad", (req, res) => {
    if (sinSesion(req, res)) return;
    res.set("Cache-Control", "no-store").json({
      cifrado: !!cifra, disco: !!cfg.dataDir, dosPasos: !!enviarCodigo || !!deps.enviarCodigo, sesionHoras: 12,
      usuarios: usuarios.lista().map(u => ({ correo: u.correo, nombre: u.nombre, whatsapp: u.whatsapp ? "•••• " + u.whatsapp.slice(-4) : "" })),
      eventos: bitacora.ultimos(200).map(({ en, evento, correo, como, pedido, de, a, ip, equipo }) => ({ en, evento, correo, como, pedido, de, a, ip, equipo })),
    });
  });

  // ---- Pasarela de pago ----
  app.post("/pagos/aviso/:n", express.json({ limit: "20kb" }), express.urlencoded({ extended: false, limit: "20kb" }), (req, res) => {
    if (!firmaOk(req.params.n, req.query.t)) return res.status(403).send("no");
    res.status(200).send("ok");                       // answer at once; the check runs after
    revisarPago(req.params.n, { ...(req.body || {}), ...req.query });
  });
  app.get("/pagos/listo/:n", async (req, res) => {
    if (!firmaOk(req.params.n, req.query.t)) return res.status(403).send("Enlace no válido");
    const p = await revisarPago(req.params.n, req.query);
    const pagado = p && p.pagado;
    const wa = digits(cfg.from) ? `https://wa.me/${digits(cfg.from)}` : "";
    const esc = x => String(x).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    res.set("Cache-Control", "no-store").type("html").send(`<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>${esc(negocio.nombre)}</title>
<body style="margin:0;min-height:100svh;display:grid;place-items:center;background:#F5F5F7;font:16px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#111">
<main style="max-width:420px;margin:24px;padding:32px 28px;background:#fff;border-radius:20px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.08)">
<div style="font-size:44px">${pagado ? "✅" : "⏳"}</div>
<h1 style="font-size:22px;margin:8px 0">${pagado ? "Pago recibido" : "Estamos confirmando su pago"}</h1>
<p style="color:#555;margin:0 0 20px">${pagado ? `Su pedido <b>${esc(p.n)}</b> ya está en cocina. Le avisamos por WhatsApp cuando esté listo.` : "En cuanto se confirme, su pedido entra a cocina y le avisamos por WhatsApp."}</p>
${wa ? `<a href="${wa}" style="display:inline-block;background:${esc(negocio.color)};color:#fff;text-decoration:none;font-weight:600;padding:12px 22px;border-radius:12px">Volver a WhatsApp</a>` : ""}
</main></body></html>`);
  });

  if (cfg.demoIA && (cfg.demoKey || deps.demoClient)) {
    montarDemo(app, { negocio: cargarNegocio("negocios/ejemplo.json"), apiKey: cfg.demoKey, model: cfg.anthropicModel, client: deps.demoClient, origenes: cfg.demoOrigenes, porVisitante: cfg.demoPorVisitante, porDia: cfg.demoPorDia, log });
    log(`Demo con IA activa en /demo/chat para ${cfg.demoOrigenes.join(", ")}`);
  }

  app.get("/", (req, res) => res.type("text/plain").send(`${negocio.nombre} · bot activo`));

  app.locals.store = store;
  app.locals.negocio = negocio;
  app.locals.idle = async () => { while (pending.size) await Promise.all([...pending]); };
  app.locals.revisarPendientes = revisarPendientes;
  app.locals.pasarela = pasarela;
  return app;
}

function start() {
  try { process.loadEnvFile(path.join(__dirname, ".env")); } catch { /* no .env: use the host's variables */ }
  const cfg = loadConfig();
  const app = createApp(cfg);
  const server = app.listen(cfg.port, () => {
    const N = app.locals.negocio;
    console.log(`Bot de ${N.nombre} escuchando en :${cfg.port} (${N.items.length} productos, ${N.sucursales.length} sucursales, ${cfg.negocio})`);
    if (cfg.meta.token && cfg.meta.phoneId) console.log(`WhatsApp directo con Meta en /meta${cfg.meta.appSecret ? "" : " (falta META_APP_SECRET: se rechazan todos los mensajes)"}${cfg.meta.plantilla ? "" : "; sin META_PLANTILLA los avisos al dueño fuera de 24 h no llegan"}.`);
    else if (!cfg.sid || !cfg.token) console.log("Aviso: faltan META_TOKEN / META_PHONE_ID (o las claves de Twilio); los avisos solo van al log.");
    if (!cfg.owner) console.log("Aviso: falta OWNER_WHATSAPP; nadie recibe los pedidos por WhatsApp.");
    console.log(cfg.dataDir ? (cfg.dataKey ? `Datos cifrados en ${cfg.dataDir} (AES-256-GCM).` : `Aviso: falta DATA_KEY; los datos en ${cfg.dataDir} quedan sin cifrar.`) : "Sin DATA_DIR: los datos solo viven en memoria.");
    console.log(cfg.anthropicKey ? `Modo IA activo (${cfg.anthropicModel}); si falla, contesta el menú.` : "Modo IA apagado: contesta el menú (falta ANTHROPIC_API_KEY o BOT_IA=off).");
    const nu = createUsuarios({ env: cfg.panelUsuarios, file: cfg.dataDir ? path.join(cfg.dataDir, "usuarios.json") : null, cifra: createCifra(cfg.dataKey) }).lista().length;
    console.log(!cfg.panelSecret ? "Panel cerrado: falta PANEL_SECRET." : nu ? `Panel en /panel con ${nu} usuario(s) autorizado(s).` : "Panel en /panel, pero no hay usuarios: npm run usuario -- agregar correo \"Nombre\"");
    if (cfg.skipSignature) console.log("Aviso: SKIP_TWILIO_SIGNATURE está activo; no lo uses en producción.");
    if (app.locals.pasarela) console.log(`Pago con tarjeta por ${app.locals.pasarela.proveedor}: los pedidos pagados pasan solo a cocina.${cfg.publicUrl ? "" : " Falta PUBLIC_URL para los avisos de pago."}`);
    else if (cfg.pasarela.proveedor) console.log(`Aviso: PAGOS_PASARELA=${cfg.pasarela.proveedor} pero faltan sus claves; pago con tarjeta apagado.`);
  });
  if (app.locals.pasarela) setInterval(() => app.locals.revisarPendientes().catch(e => console.log("[pagos] " + e.message)), 120e3).unref();
  const bye = () => { app.locals.store.flush(); server.close(() => process.exit(0)); };
  process.on("SIGTERM", bye); process.on("SIGINT", bye);
}

if (require.main === module) start();
module.exports = { createApp, loadConfig, ESTADOS };
