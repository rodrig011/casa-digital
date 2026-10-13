// Steel Works · webhook de WhatsApp (Twilio). Sin dependencias: node server.js
// En Twilio > WhatsApp sender > "When a message comes in": POST https://<tu-servidor>/whatsapp
// Las conversaciones viven en memoria; en producción van a una base de datos y el
// traspaso a un asesor se avisa al WhatsApp de la sucursal.
const http = require("http");
const { handle, toText } = require("./engine");

const sessions = new Map();          // número del cliente -> estado de la conversación
const PORT = process.env.PORT || 3000;
const xml = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

http.createServer((req, res) => {
  if (req.method === "POST" && req.url.startsWith("/whatsapp")) {
    let body = "";
    req.on("data", c => (body += c));
    req.on("end", () => {
      const p = new URLSearchParams(body);
      const from = p.get("From") || "anon";
      const text = Number(p.get("NumMedia") || 0) > 0 ? "📷 foto" : p.get("Body") || "";
      const r = handle(sessions.get(from), text);
      sessions.set(from, r.state);
      if (r.state.handoff) console.log(`[asesor ${r.state.handoff}] ${from} pidió hablar con una persona`);
      if (r.state.lead && r.state.lead !== (sessions.prev || {})[from]) console.log(`[ficha ${r.state.lead.sucursal}] ${from}`, r.state.lead);
      const msgs = r.messages.map(toText).filter(Boolean).map(m => `<Message>${xml(m)}</Message>`).join("");
      res.writeHead(200, { "Content-Type": "text/xml" });
      res.end(`<?xml version="1.0" encoding="UTF-8"?><Response>${msgs}</Response>`);
    });
  } else {
    res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Steel Works bot activo");
  }
}).listen(PORT, () => console.log("Bot escuchando en :" + PORT));
