// Demostración con IA para clientiatech.com: la página pública manda lo que escribe el visitante y aquí contesta Claude
// con el restaurante de ejemplo. La clave de Anthropic se queda en este servidor; la página nunca la ve.
// Los pedidos de la demo no se guardan ni avisan a nadie: solo vuelven a la página para la pantalla de cocina.
//
//   POST /demo/chat   { sesion, texto }  ->  { reply, pedido? }      (solo desde DEMO_ORIGENES)
//
// Frenos: mensajes por visitante (IP) cada 10 minutos, y un tope de respuestas por día para todo el sitio,
// así nadie puede gastar el saldo de Anthropic. Pasado el tope la página contesta con el menú de siempre.
const express = require("express");
const { createIA } = require("./ia");
const { createLimite } = require("./seguridad");

const SESION_MIN = 30;     // minutos que se recuerda una conversación de la demo
const MAX_SESIONES = 500;

function montarDemo(app, { negocio, apiKey, model, client, origenes = [], porVisitante = 15, porDia = 400, log = console.log, ahora = () => Date.now() }) {
  const ia = createIA({ negocio, apiKey, model, client });
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
}

module.exports = { montarDemo };
