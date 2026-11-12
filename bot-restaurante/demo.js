// Demostración con IA para clientiatech.com: la página pública manda lo que escribe el visitante y aquí contesta Claude
// con el restaurante de ejemplo. La clave de Anthropic se queda en este servidor; la página nunca la ve.
// Los pedidos de la demo no se guardan ni avisan a nadie: solo vuelven a la página para la pantalla de cocina.
//
//   POST /demo/chat   { sesion, texto }  ->  { reply, pedido? }      (solo desde DEMO_ORIGENES)
//   POST /demo/claude { negocio, messages } -> la respuesta de Claude, para las demos de un cliente que corren el bot
//        en el navegador (demos.js). El sistema, las herramientas y el modelo los pone este servidor; la página solo
//        manda la conversación. Mismos frenos: por visitante y por día.
//
// Frenos: mensajes por visitante (IP) cada 10 minutos, y un tope de respuestas por día para todo el sitio,
// así nadie puede gastar el saldo de Anthropic. Pasado el tope la página contesta con el menú de siempre.
const express = require("express");
const { createIA, system, tools, MODELO } = require("./ia");
const { negocioDemo } = require("./demos");
const { createLimite } = require("./seguridad");

const SESION_MIN = 30;     // minutos que se recuerda una conversación de la demo
const MAX_SESIONES = 500;

function montarDemo(app, { negocio, apiKey, model, client, origenes = [], porVisitante = 15, porDia = 400, log = console.log, ahora = () => Date.now() }) {
  const ia = createIA({ negocio, apiKey, model, client });
  const claude = client || (apiKey ? new (require("@anthropic-ai/sdk"))({ apiKey, maxRetries: 1, timeout: 15000 }) : null);
  const demos = new Map();
  const limiteClaude = createLimite({ max: porVisitante * 5, minutos: 10, ahora });   // one customer message = up to 5 calls (tools)
  const sesiones = new Map();
  const limite = createLimite({ max: porVisitante, minutos: 10, ahora });
  let dia = "", usadas = 0;
  let seq = 0;

  const permitido = o => !!o && origenes.includes(o);
  function cors(req, res, next) {
    const o = req.get("Origin");
    if (permitido(o)) res.set({ "Access-Control-Allow-Origin": o, "Access-Control-Allow-Methods": "POST", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Max-Age": "600", Vary: "Origin" });
    if (req.method === "OPTIONS") return res.sendStatus(permitido(o) ? 204 : 403);
    if (!permitido(o)) return res.status(403).json({ error: "origen" });
    next();
  }
  function hoy() {
    const d = new Date(ahora()).toISOString().slice(0, 10);
    if (d !== dia) { dia = d; usadas = 0; }
    return usadas < porDia;
  }
  function limpiar() {
    const t = ahora();
    for (const [k, s] of sesiones) if (t - s.t > SESION_MIN * 6e4) sesiones.delete(k);
    while (sesiones.size > MAX_SESIONES) sesiones.delete(sesiones.keys().next().value);
  }

  app.options("/demo/chat", cors);
  app.post("/demo/chat", cors, express.json({ limit: "4kb" }), async (req, res) => {
    const id = String((req.body && req.body.sesion) || "").slice(0, 40);
    const texto = String((req.body && req.body.texto) || "").trim().slice(0, 500);
    if (!/^[\w-]{8,40}$/.test(id) || !texto) return res.status(400).json({ error: "datos" });
    if (!limite.pasa(req.ip) || !hoy()) return res.status(429).json({ error: "limite" });
    limpiar();
    const s = sesiones.get(id) || { h: [], t: 0 };
    try {
      usadas++;
      const r = await ia.turn(s.h, texto, ahora(), { numero: () => "DEMO-" + (1001 + (seq++ % 9000)) });
      s.h = r.history; s.t = ahora();
      sesiones.delete(id); sesiones.set(id, s);
      res.json({ reply: r.reply, ...(r.pedido ? { pedido: r.pedido } : {}) });
    } catch (e) {
      log(`[demo ia] ${e.status || ""} ${e.message}`);
      res.status(502).json({ error: "ia" });
    }
  });

  // who opened a client's demo page: a count per day and the last time, so rodrigo knows if the prospect looked.
  // Only in memory (the free server restarts) and in the log; nothing personal is kept.
  const visitas = new Map();
  app.options("/demo/visita", cors);
  app.post("/demo/visita", cors, express.json({ limit: "2kb" }), (req, res) => {
    const id = String((req.body && req.body.negocio) || "").slice(0, 40);
    if (!id) return res.status(400).json({ error: "datos" });
    const d = new Date(ahora()).toISOString().slice(0, 10);
    const v = visitas.get(id) || { dia: d, hoy: 0, total: 0, ultima: null };
    if (v.dia !== d) { v.dia = d; v.hoy = 0; }
    v.hoy++; v.total++; v.ultima = new Date(ahora()).toISOString();
    visitas.set(id, v);
    log(`[demo] visita a la demo de ${id} (${v.hoy} hoy)`);
    res.json({ ok: true });
  });
  app.get("/demo/visitas", (req, res) => res.set("Cache-Control", "no-store").json(Object.fromEntries([...visitas].map(([k, v]) => [k, { hoy: v.hoy, total: v.total, ultima: v.ultima }]))));

  app.options("/demo/claude", cors);
  app.post("/demo/claude", cors, express.json({ limit: "48kb" }), async (req, res) => {
    const id = String((req.body && req.body.negocio) || "");
    if (!demos.has(id)) { const n = negocioDemo(id); if (n) demos.set(id, { n, system: system(n), tools: tools(n) }); }
    const d = demos.get(id), messages = req.body && req.body.messages;
    if (!d || !Array.isArray(messages) || !messages.length || messages.length > 60) return res.status(400).json({ error: "datos" });
    if (!claude) return res.status(503).json({ error: "sin clave" });
    if (!limiteClaude.pasa(req.ip) || !hoy()) return res.status(429).json({ error: "limite" });
    try {
      usadas += 0.2;
      const r = await claude.messages.create({ model: model || MODELO, max_tokens: 1024, output_config: { effort: "low" },
        system: [{ type: "text", text: d.system, cache_control: { type: "ephemeral" } }], tools: d.tools, cache_control: { type: "ephemeral" }, messages });
      res.json({ content: r.content, stop_reason: r.stop_reason, usage: r.usage });
    } catch (e) {
      log(`[demo claude] ${e.status || ""} ${e.message}`);
      res.status(502).json({ error: "ia" });
    }
  });
}

module.exports = { montarDemo };
