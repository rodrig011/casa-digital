// Bot de WhatsApp para restaurantes · webhook de Twilio + panel del dueño.  npm start
//
//   POST /whatsapp                 Twilio > WhatsApp sender > "When a message comes in"
//   GET  /panel                    panel del dueño y pantalla de cocina (correo y contraseña, ver auth.js)
//   GET  /api/pedidos              pedidos en JSON (sesión del panel, o Authorization: Bearer <LEADS_TOKEN>)
//   POST /api/pedidos/:n/estado    { estado } nuevo | cocina | listo | entregado | cancelado | atendido (sesión del panel)
//   GET  /api/negocio              menú y sucursales para el panel (sesión del panel)
//   GET  /                         "<restaurante> · bot activo" (chequeo de salud)
//
// Cada pedido se guarda en pedidos.json y se avisa por WhatsApp al dueño y a la sucursal. Cuando la cocina
// lo marca "listo" en el panel, al cliente le llega "su pedido está listo". Configuración: .env (ver .env.example).
// El restaurante (menú, precios, sucursales) está en negocios/<cliente>.json; NEGOCIO dice cuál.
// Con ANTHROPIC_API_KEY, WhatsApp contesta en modo IA (ia.js, Claude); si la API falla contesta el menú de engine.js.
const path = require("path");
const crypto = require("crypto");
const express = require("express");
const twilio = require("twilio");
const { cargarNegocio, L } = require("./negocio");
const { createEngine, toText } = require("./engine");
const { createStore } = require("./store");
const { createNotifier, fichaTexto, waAddr, digits } = require("./avisos");
const { createUsuarios, montarPanel } = require("./auth");
const { createIA, MODELO } = require("./ia");

const on = v => /^(1|true|si|sí|yes)$/i.test(String(v || "").trim());
const ESTADOS = ["nuevo", "cocina", "listo", "entregado", "cancelado", "atendido"];

function loadConfig(env = process.env) {
  const sandbox = on(env.TWILIO_SANDBOX);
  return {
    port: +env.PORT || 3000,
    negocio: env.NEGOCIO || "negocios/ejemplo.json",
    sid: env.TWILIO_ACCOUNT_SID || "",
    token: env.TWILIO_AUTH_TOKEN || "",
    sandbox,
    from: waAddr(env.TWILIO_WHATSAPP_FROM || (sandbox ? "+14155238886" : "")),
    contentSid: env.TWILIO_ALERT_CONTENT_SID || "",
    owner: env.OWNER_WHATSAPP || "",
    publicUrl: (env.PUBLIC_URL || "").replace(/\/$/, ""),
    skipSignature: on(env.SKIP_TWILIO_SIGNATURE),
    leadsToken: env.LEADS_TOKEN || "",
    panelSecret: env.PANEL_SECRET || "",
    panelUsuarios: env.PANEL_USUARIOS || "",
    dataDir: env.DATA_DIR === "" ? null : path.resolve(__dirname, env.DATA_DIR || "data"),
    ttlHours: +env.SESSION_TTL_HOURS || 12,
    // modo IA (Claude): solo si hay clave y BOT_IA no es "off"
    anthropicKey: /^off$/i.test(String(env.BOT_IA || "").trim()) ? "" : env.ANTHROPIC_API_KEY || "",
    anthropicModel: env.ANTHROPIC_MODEL || MODELO,
  };
}

function createApp(cfg = loadConfig(), deps = {}) {
  const log = deps.log || console.log;
  const negocio = deps.negocio || cargarNegocio(cfg.negocio);
  const motor = createEngine(negocio);
  const store = deps.store || createStore(cfg.dataDir, { ttlHours: cfg.ttlHours });
  const client = "client" in deps ? deps.client : cfg.sid && cfg.token ? twilio(cfg.sid, cfg.token) : null;
  const avisos = createNotifier({ client, from: cfg.from, contentSid: cfg.contentSid, sandbox: cfg.sandbox, owner: cfg.owner, negocio, log });
  const now = deps.now || (() => new Date());
  const ia = "ia" in deps ? deps.ia : cfg.anthropicKey ? createIA({ negocio, apiKey: cfg.anthropicKey, model: cfg.anthropicModel }) : null;
  const pending = new Set();                      // messages in flight (tests wait on them)
  const track = p => { pending.add(p); p.finally(() => pending.delete(p)); return p; };

  const app = express();
  app.set("trust proxy", true);
  app.use(express.urlencoded({ extended: false }));

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
  function guardar(base, tel, convo) {
    const p = store.addPedido({ ...base, n: base.n || numero(base.tipo === "persona" ? "AS" : "PED"), tel: "+" + digits(tel), fecha: now().toISOString(), estado: "nuevo", convo });
    log(`[${p.tipo} ${p.n} · ${p.sucursal}] ${p.tel} ${p.tipo === "pedido" ? L(p.total) : p.motivo || ""}`);
    track(avisos.ficha(p));
    return p;
  }
  const persona = (motivo, sucursal, tel, convo) => guardar({ tipo: "persona", nombre: null, sucursal, motivo }, tel, convo);

  // one turn of the menu engine
  function conversar(key, text) {
    const sess = store.getSession(key) || { state: null, convo: [] };
    if (sess.state) sess.state.seq = store.seq;    // one numbering for all customers
    const r = motor.handle(sess.state, text, now());
    const out = r.messages.map(toText).filter(Boolean);
    sess.convo = sess.convo.concat([[text, 1]], out.map(m => [m, 0])).slice(-16);
    if (r.state.lead) { store.seq = r.state.seq; guardar(r.state.lead, key, sess.convo); delete r.state.lead; }
    if (r.state.handoff) { persona("", r.state.handoff, key, sess.convo); delete r.state.handoff; }
    sess.state = r.state;
    store.setSession(key, sess);
    return out;
  }

  // AI mode: Claude answers; on any API error or timeout this message goes to the menu engine
  async function conversarIA(key, text) {
    const sess = store.getSession(key) || { state: null, convo: [] };
    let r;
    try {
      r = await ia.turn(sess.ia || [], text, now(), { numero: () => numero("PED") });
    } catch (e) {
      log(`[ia] error, contesta el menú: ${e.constructor && e.constructor.name}${e.status ? " " + e.status : ""} ${e.message}`);
      const convo = sess.convo.concat([[text, 1]]).slice(-16);
      if (e.pedido) guardar(e.pedido, key, convo);
      if (e.persona) persona(e.persona.motivo, e.persona.sucursal, key, convo);
      return null;
    }
    sess.ia = r.history;
    sess.convo = sess.convo.concat([[text, 1], [r.reply, 0]]).slice(-16);
    if (r.pedido) guardar(r.pedido, key, sess.convo);
    if (r.persona) persona(r.persona.motivo, r.persona.sucursal, key, sess.convo);
    store.setSession(key, sess);
    return r.reply;
  }

  const esDueno = from => cfg.owner && digits(from) === digits(cfg.owner);
  function pendientes() {
    const ls = store.pedidos.filter(p => ["nuevo", "cocina"].includes(p.estado)).slice(-10).reverse();
    if (!ls.length) return "📋 No hay pedidos ni clientes pendientes.";
    return "📋 *Pendientes*\n\n" + ls.map(p => { const t = fichaTexto(p); return `*${t.titulo}*\n${t.lineas.slice(0, -1).join("\n")}`; }).join("\n\n");
  }

  // ---- WhatsApp ----
  app.post("/whatsapp", firma, async (req, res) => {
    const p = req.body || {};
    const from = p.From || "anon";
    const text = Number(p.NumMedia || 0) > 0 && !p.Body ? "📷 foto" : p.Body || "";
    const tw = new twilio.twiml.MessagingResponse();
    let reply;
    if (esDueno(from) && /^(pedidos|pendientes|agenda)$/i.test(text.trim())) tw.message(pendientes().slice(0, 1590));
    else if (ia && (reply = await conversarIA(from, text))) tw.message(reply.slice(0, 1590));
    else {
      // one WhatsApp message per turn keeps the order and costs one message
      let buf = "";
      for (const t of conversar(from, text)) { if (buf && (buf + "\n\n" + t).length > 1590) { tw.message(buf); buf = t; } else buf = buf ? buf + "\n\n" + t : t; }
      if (buf) tw.message(buf.slice(0, 1590));
    }
    res.type("text/xml").send(tw.toString());
  });

  // ---- Panel del dueño (correo y contraseña; ver auth.js) ----
  const usuarios = deps.usuarios || createUsuarios({ env: cfg.panelUsuarios, file: cfg.dataDir ? path.join(cfg.dataDir, "usuarios.json") : null });
  const panel = montarPanel(app, { secret: cfg.panelSecret, usuarios, archivoPanel: path.join(__dirname, "panel", "panel.html"), marca: negocio.nombre, color: negocio.color, log });
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
    res.set("Cache-Control", "no-store").json({ nombre: negocio.nombre, color: negocio.color, sucursales: negocio.sucursales.map(({ id, nombre }) => ({ id, nombre })), menu: negocio.items.map(({ id, nombre, categoria, precio }) => ({ id, nombre, categoria, precio })), modoIA: !!ia, usuario: panel.usuarioDe(req).nombre });
  });
  app.post("/api/pedidos/:n/estado", express.json({ limit: "2kb" }), (req, res) => {
    if (sinSesion(req, res)) return;
    const origen = req.get("Origin");
    if (origen && origen !== `${req.protocol}://${req.get("host")}`) return res.status(403).json({ error: "origen no permitido" });
    const estado = String((req.body || {}).estado || "");
    if (!ESTADOS.includes(estado)) return res.status(400).json({ error: "estado inválido" });
    const antes = store.getPedido(req.params.n);
    if (!antes) return res.status(404).json({ error: "no existe" });
    const yaAvisado = antes.avisoListo;
    const p = store.updatePedido(req.params.n, { estado, [`t_${estado}`]: now().toISOString(), por: panel.usuarioDe(req).correo });
    if (estado === "listo" && p.tipo === "pedido" && !yaAvisado) { store.updatePedido(p.n, { avisoListo: true }); track(avisos.listo(p)); }
    log(`[panel] ${p.n} -> ${estado} (${p.por})`);
    res.json(p);
  });

  app.get("/", (req, res) => res.type("text/plain").send(`${negocio.nombre} · bot activo`));

  app.locals.store = store;
  app.locals.negocio = negocio;
  app.locals.idle = () => Promise.all([...pending]);
  return app;
}

function start() {
  try { process.loadEnvFile(path.join(__dirname, ".env")); } catch { /* no .env: use the host's variables */ }
  const cfg = loadConfig();
  const app = createApp(cfg);
  const server = app.listen(cfg.port, () => {
    const N = app.locals.negocio;
    console.log(`Bot de ${N.nombre} escuchando en :${cfg.port} (${N.items.length} productos, ${N.sucursales.length} sucursales, ${cfg.negocio})`);
    if (!cfg.sid || !cfg.token) console.log("Aviso: faltan TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN; los avisos solo van al log.");
    if (!cfg.owner) console.log("Aviso: falta OWNER_WHATSAPP; nadie recibe los pedidos por WhatsApp.");
    console.log(cfg.anthropicKey ? `Modo IA activo (${cfg.anthropicModel}); si falla, contesta el menú.` : "Modo IA apagado: contesta el menú (falta ANTHROPIC_API_KEY o BOT_IA=off).");
    const nu = createUsuarios({ env: cfg.panelUsuarios, file: cfg.dataDir ? path.join(cfg.dataDir, "usuarios.json") : null }).lista().length;
    console.log(!cfg.panelSecret ? "Panel cerrado: falta PANEL_SECRET." : nu ? `Panel en /panel con ${nu} usuario(s) autorizado(s).` : "Panel en /panel, pero no hay usuarios: npm run usuario -- agregar correo \"Nombre\"");
    if (cfg.skipSignature) console.log("Aviso: SKIP_TWILIO_SIGNATURE está activo; no lo uses en producción.");
  });
  const bye = () => { app.locals.store.flush(); server.close(() => process.exit(0)); };
  process.on("SIGTERM", bye); process.on("SIGINT", bye);
}

if (require.main === module) start();
module.exports = { createApp, loadConfig, ESTADOS };
