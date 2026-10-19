// Steel Works · webhook de WhatsApp y de llamadas (Twilio).  npm start
//
//   POST /whatsapp  Twilio > WhatsApp sender > "When a message comes in"
//   POST /voice     Twilio > número de teléfono > "A call comes in" (ver LLAMADAS.md)
//   GET  /leads     fichas en JSON para el panel del dueño (Authorization: Bearer <LEADS_TOKEN>)
//   GET  /          "Steel Works bot activo" (chequeo de salud)
//
// Cada ficha terminada se guarda en leads.json y se avisa por WhatsApp al dueño y a la sucursal.
// Si el cliente pide hablar con una persona, también se avisa. Configuración: .env (ver .env.example).
// Con ANTHROPIC_API_KEY, WhatsApp contesta en modo IA (ia.js, Claude); si la API falla contesta el menú de engine.js.
const path = require("path");
const crypto = require("crypto");
const express = require("express");
const twilio = require("twilio");
const { handle, toText } = require("./engine");
const { createStore } = require("./store");
const { createNotifier, fichaTexto, waAddr, digits } = require("./avisos");
const voz = require("./voz");
const { createUsuarios, montarPanel } = require("./auth");
const { createIA, MODELO } = require("./ia");

const on = v => /^(1|true|si|sí|yes)$/i.test(String(v || "").trim());

function loadConfig(env = process.env) {
  const sandbox = on(env.TWILIO_SANDBOX);
  return {
    port: +env.PORT || 3000,
    sid: env.TWILIO_ACCOUNT_SID || "",
    token: env.TWILIO_AUTH_TOKEN || "",
    sandbox,
    from: waAddr(env.TWILIO_WHATSAPP_FROM || (sandbox ? "+14155238886" : "")),
    contentSid: env.TWILIO_ALERT_CONTENT_SID || "",
    owner: env.OWNER_WHATSAPP || "",
    branches: { TGU: env.BRANCH_TGU_WHATSAPP || "", SPS: env.BRANCH_SPS_WHATSAPP || "" },
    transfer: { TGU: env.VOICE_TRANSFER_TGU || "", SPS: env.VOICE_TRANSFER_SPS || "" },
    publicUrl: (env.PUBLIC_URL || "").replace(/\/$/, ""),
    skipSignature: on(env.SKIP_TWILIO_SIGNATURE),
    leadsToken: env.LEADS_TOKEN || "",
    panelSecret: env.PANEL_SECRET || "",
    panelUsuarios: env.PANEL_USUARIOS || "",
    dataDir: env.DATA_DIR === "" ? null : path.resolve(__dirname, env.DATA_DIR || "data"),
    ttlHours: +env.SESSION_TTL_HOURS || 24,
    fotosUrl: (env.FOTOS_URL || "").replace(/\/$/, ""),
    voiceLang: env.VOICE_LANG || "es-MX",
    voiceTts: env.VOICE_TTS || "Polly.Mia",
    speechModel: env.VOICE_SPEECH_MODEL || "",
    // modo IA (Claude): solo si hay clave y BOT_IA no es "off"
    anthropicKey: /^off$/i.test(String(env.BOT_IA || "").trim()) ? "" : env.ANTHROPIC_API_KEY || "",
    anthropicModel: env.ANTHROPIC_MODEL || MODELO,
  };
}

function createApp(cfg = loadConfig(), deps = {}) {
  const log = deps.log || console.log;
  const store = deps.store || createStore(cfg.dataDir, { ttlHours: cfg.ttlHours });
  const client = "client" in deps ? deps.client : cfg.sid && cfg.token ? twilio(cfg.sid, cfg.token) : null;
  const avisos = createNotifier({ client, from: cfg.from, contentSid: cfg.contentSid, sandbox: cfg.sandbox, owner: cfg.owner, branches: cfg.branches, log });
  const now = deps.now || (() => new Date());
  const ia = "ia" in deps ? deps.ia : cfg.anthropicKey ? createIA({ apiKey: cfg.anthropicKey, model: cfg.anthropicModel }) : null;
  const pending = new Set();                      // alerts in flight (tests wait on them)
  const track = p => { pending.add(p); p.finally(() => pending.delete(p)); return p; };

  const app = express();
  app.set("trust proxy", true);
  app.use(express.urlencoded({ extended: false }));

  // only Twilio may post to the webhooks (SKIP_TWILIO_SIGNATURE=true for local tests)
  function firma(req, res, next) {
    if (cfg.skipSignature) return next();
    if (!cfg.token) { log("[error] falta TWILIO_AUTH_TOKEN para validar la firma de Twilio"); return res.status(500).send("Falta configuración"); }
    const url = (cfg.publicUrl || `${req.protocol}://${req.get("host")}`) + req.originalUrl;
    if (twilio.validateRequest(cfg.token, req.get("X-Twilio-Signature") || "", url, req.body || {})) return next();
    log(`[firma inválida] ${url}`);
    res.status(403).send("Firma de Twilio inválida");
  }

  // runs one turn of the engine for a customer and handles what it produced (ficha, person)
  function conversar(key, tel, canal, text) {
    const sess = store.getSession(key) || { state: null, convo: [] };
    if (sess.state) sess.state.seq = store.seq;    // one numbering for all customers
    const r = handle(sess.state, text, now());
    const out = r.messages.map(toText).filter(Boolean);
    sess.convo = sess.convo.concat([[text, 1]], out.map(m => [m, 0])).slice(-16);
    let lead = null;
    if (r.state.lead) {
      store.seq = r.state.seq;
      lead = guardar({ ...r.state.lead, persona: false }, tel, canal, sess.convo);
      delete r.state.lead;
    }
    if (r.state.handoff) {
      lead = guardar({ n: "AS-" + (store.seq = store.seq + 1), nombre: r.state.data.nombre || null, resumen: "Pidió hablar con una persona", rango: null, cita: "Pidió hablar con una persona", sucursal: r.state.handoff, persona: true }, tel, canal, sess.convo);
      delete r.state.handoff;
    }
    sess.state = r.state;
    store.setSession(key, sess);
    return { r, lead, sess };
  }

  // WhatsApp in AI mode: Claude answers; on any API error or timeout this message goes to the rule engine
  async function conversarIA(key, tel, text) {
    const sess = store.getSession(key) || { state: null, convo: [] };
    const numero = () => "COT-" + (store.seq = store.seq + 1);
    const persona = (p, convo) => guardar({ n: "AS-" + (store.seq = store.seq + 1), nombre: null, resumen: "Pidió hablar con una persona" + (p.motivo ? ": " + p.motivo : ""), rango: null, cita: "Pidió hablar con una persona", sucursal: p.sucursal, persona: true }, tel, "whatsapp", convo);
    let r;
    try {
      r = await ia.turn(sess.ia || [], text, now(), { numero });
    } catch (e) {
      log(`[ia] error, contesta el menú: ${e.constructor && e.constructor.name}${e.status ? " " + e.status : ""} ${e.message}`);
      const convo = sess.convo.concat([[text, 1]]).slice(-16);
      if (e.lead) guardar({ ...e.lead, persona: false }, tel, "whatsapp", convo);
      if (e.persona) persona(e.persona, convo);
      return null;
    }
    sess.ia = r.history;
    sess.convo = sess.convo.concat([[text, 1], [r.reply, 0]]).slice(-16);
    if (r.lead) guardar({ ...r.lead, n: r.lead.n || numero(), persona: false }, tel, "whatsapp", sess.convo);
    if (r.persona) persona(r, sess.convo);
    store.setSession(key, sess);
    return r.reply;
  }

  function guardar(base, tel, canal, convo) {
    const lead = store.addLead({ ...base, id: base.n, tel: "+" + digits(tel), canal, fecha: now().toISOString(), estado: "nuevo", convo });
    log(`[ficha ${lead.sucursal}] ${lead.tel}`, JSON.stringify({ n: lead.n, nombre: lead.nombre, resumen: lead.resumen, rango: lead.rango, cita: lead.cita }));
    track(avisos.ficha(lead));
    return lead;
  }

  const esDueno = from => cfg.owner && digits(from) === digits(cfg.owner);
  function agenda() {
    const ls = store.leads.slice(-10).reverse();
    if (!ls.length) return "📋 Todavía no hay fichas.";
    return "📋 *Últimas fichas*\n\n" + ls.map(l => { const t = fichaTexto(l); return `*${t.titulo}*\n${t.lineas.slice(0, -1).join("\n")}`; }).join("\n\n");
  }

  // ---- WhatsApp ----
  app.post("/whatsapp", firma, async (req, res) => {
    const p = req.body || {};
    const from = p.From || "anon";
    const text = Number(p.NumMedia || 0) > 0 ? "📷 foto" : p.Body || "";
    const tw = new twilio.twiml.MessagingResponse();
    let reply;
    if (esDueno(from) && /^(agenda|citas|pendientes|fichas)$/i.test(text.trim())) {
      tw.message(agenda().slice(0, 1590));
    } else if (ia && (reply = await conversarIA(from, from, text))) {
      tw.message(reply.slice(0, 1590));
    } else {
      const { r } = conversar(from, from, "whatsapp", text);
      // photos of real work for the style question, when FOTOS_URL is set
      for (const m of r.messages) if (m.gallery && cfg.fotosUrl) m.gallery.forEach((g, i) => { const msg = tw.message(); msg.body(`${i + 1}. ${g.title}`); msg.media(`${cfg.fotosUrl}/${g.foto}.jpg`); });
      // one WhatsApp message per turn keeps the order and costs one message, not three
      const partes = r.messages.map(toText).filter(Boolean);
      let buf = "";
      for (const t of partes) { if (buf && (buf + "\n\n" + t).length > 1590) { tw.message(buf); buf = t; } else buf = buf ? buf + "\n\n" + t : t; }
      if (buf) tw.message(buf);
    }
    res.type("text/xml").send(tw.toString());
  });

  // ---- Llamadas (Twilio <Gather input="speech">) ----
  app.post("/voice", firma, (req, res) => {
    const p = req.body || {};
    const key = "call:" + (p.CallSid || "anon");
    const tel = p.From || "";
    const vr = new twilio.twiml.VoiceResponse();
    const decir = (el, t) => el.say({ voice: cfg.voiceTts, language: cfg.voiceLang }, t);
    const send = () => res.type("text/xml").send(vr.toString());
    const sess0 = store.getSession(key);

    let r, lead;
    if (!sess0) ({ r, lead } = conversar(key, tel, "llamada", "hola"));
    else {
      const v = sess0.voz || { opciones: [], texto: "", silencios: 0 };
      const input = voz.entrada(p, v.opciones);
      if (!input) {
        v.silencios++;
        sess0.voz = v; store.setSession(key, sess0);
        if (v.silencios >= 3) { decir(vr, "No te escucho bien. Escríbenos por WhatsApp a este mismo número y te atendemos. ¡Gracias por llamar a Steel Works!"); vr.hangup(); store.deleteSession(key); return send(); }
        return preguntar("Disculpa, no te escuché. " + v.texto, v.opciones);
      }
      ({ r, lead } = conversar(key, tel, "llamada", input));
    }

    const { texto, opciones } = voz.turno(r.messages);
    const sess = store.getSession(key);
    if (lead && lead.persona) {
      const n = /pedro/i.test(lead.sucursal) ? cfg.transfer.SPS : cfg.transfer.TGU;
      if (n) { decir(vr, `Claro, te comunico con un asesor de ${lead.sucursal}.`); vr.dial(n); }
      else { decir(vr, voz.hablar(r.messages[0].text) + " ¡Gracias por llamar!"); vr.hangup(); }
      store.deleteSession(key); return send();
    }
    if (lead) {
      decir(vr, voz.hablar(r.messages[0].text) + " ¡Gracias por llamar a Steel Works!");
      vr.hangup(); store.deleteSession(key); return send();
    }
    if (r.state.step === "piezas") {           // parts need a photo: continue on WhatsApp
      guardar({ n: "PZ-" + (store.seq = store.seq + 1), nombre: null, resumen: "Llamó buscando piezas para herrería", rango: null, cita: "Escribirle por WhatsApp para pedir la foto de la pieza", sucursal: "Tegucigalpa", persona: true }, tel, "llamada", sess.convo);
      decir(vr, "Tenemos más de 750 piezas. Te escribimos por WhatsApp a este número para que nos mandes la foto de la pieza y te confirmamos precio y existencia. ¡Gracias por llamar a Steel Works!");
      vr.hangup(); store.deleteSession(key); return send();
    }
    sess.voz = { opciones, texto, silencios: 0 };
    store.setSession(key, sess);
    return preguntar(texto, opciones);

    function preguntar(t, ops) {
      const g = vr.gather({
        input: ops.length ? "speech dtmf" : "speech", action: "/voice", method: "POST", language: cfg.voiceLang,
        speechTimeout: cfg.speechModel ? "2" : "auto", timeout: 6, actionOnEmptyResult: true,
        ...(ops.length ? { numDigits: 1, hints: ops.join(",") } : {}), ...(cfg.speechModel ? { speechModel: cfg.speechModel } : {}),
      });
      decir(g, t);
      return send();
    }
  });

  // ---- Panel del dueño (correo y contraseña; ver auth.js) ----
  const usuarios = deps.usuarios || createUsuarios({ env: cfg.panelUsuarios, file: cfg.dataDir ? path.join(cfg.dataDir, "usuarios.json") : null });
  const panel = montarPanel(app, { secret: cfg.panelSecret, usuarios, archivoPanel: path.join(__dirname, "panel", "panel.html"), archivoSesiones: cfg.dataDir ? path.join(cfg.dataDir, "sesiones-cerradas.json") : null, log });

  // ---- Fichas para el panel del dueño (sesión del panel o token) ----
  app.get("/leads", (req, res) => {
    if (panel.usuarioDe(req)) return res.set("Cache-Control", "no-store").json(store.leads.slice().reverse());
    res.set("Access-Control-Allow-Origin", "*");
    const given = (req.get("Authorization") || "").replace(/^Bearer\s+/i, "") || String(req.query.token || "");
    const a = Buffer.from(given), b = Buffer.from(cfg.leadsToken);
    if (!cfg.leadsToken || a.length !== b.length || !crypto.timingSafeEqual(a, b)) return res.status(401).json({ error: "token inválido" });
    res.json(store.leads.slice().reverse());
  });

  app.get("/", (req, res) => res.type("text/plain").send("Steel Works bot activo"));

  app.locals.store = store;
  app.locals.idle = () => Promise.all([...pending]);
  return app;
}

function start() {
  try { process.loadEnvFile(path.join(__dirname, ".env")); } catch { /* no .env: use the host's variables */ }
  const cfg = loadConfig();
  const app = createApp(cfg);
  const server = app.listen(cfg.port, () => {
    console.log(`Bot escuchando en :${cfg.port}`);
    if (!cfg.sid || !cfg.token) console.log("Aviso: faltan TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN; los avisos al dueño solo van al log.");
    if (!cfg.owner) console.log("Aviso: falta OWNER_WHATSAPP; nadie recibe las fichas por WhatsApp.");
    console.log(cfg.anthropicKey ? `Modo IA activo (${cfg.anthropicModel}); si falla, contesta el menú.` : "Modo IA apagado: contesta el menú (falta ANTHROPIC_API_KEY o BOT_IA=off).");
    const nu = createUsuarios({ env: cfg.panelUsuarios, file: cfg.dataDir ? path.join(cfg.dataDir, "usuarios.json") : null }).lista().length;
    console.log(!cfg.panelSecret ? "Panel cerrado: falta PANEL_SECRET." : nu ? `Panel en /panel con ${nu} usuario(s) autorizado(s).` : "Panel en /panel, pero no hay usuarios: npm run usuario -- agregar correo \"Nombre\"");
    if (cfg.skipSignature) console.log("Aviso: SKIP_TWILIO_SIGNATURE está activo; no lo uses en producción.");
  });
  const bye = () => { app.locals.store.flush(); server.close(() => process.exit(0)); };
  process.on("SIGTERM", bye); process.on("SIGINT", bye);
}

if (require.main === module) start();
module.exports = { createApp, loadConfig };
