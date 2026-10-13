// Avisos por WhatsApp al dueño y a la sucursal: cada ficha nueva y cada "quiero hablar con una persona".
// Así nadie depende de una secretaria: la cotización llega sola al celular de quien la atiende.
//
// WhatsApp solo deja mandar texto libre a alguien que le escribió al número del bot en las últimas 24 h.
// Por eso, en producción, los avisos salen con una plantilla aprobada por Meta (TWILIO_ALERT_CONTENT_SID).
// Truco gratis: si el dueño le escribe "agenda" al bot cada mañana, la ventana queda abierta todo el día.

// "+504 3265-8800", "50432658800" o "whatsapp:+50432658800" -> "whatsapp:+50432658800"
const waAddr = n => { const d = String(n || "").replace(/\D/g, ""); return d ? "whatsapp:+" + d : null; };
const digits = n => String(n || "").replace(/\D/g, "");

function fichaTexto(l) {
  const titulo = l.persona
    ? `${l.nombre || "Un cliente"} pidió hablar con una persona · ${l.canal === "llamada" ? "llamada" : "WhatsApp"}`
    : `Nueva cotización ${l.n} · ${l.canal === "llamada" ? "llamada" : "WhatsApp"}`;
  const lineas = [
    `👤 ${l.nombre || "Sin nombre"} · +${digits(l.tel)}`,
    l.resumen,
    l.rango ? `💰 Estimado: L ${l.rango[0].toLocaleString("es-HN")} a L ${l.rango[1].toLocaleString("es-HN")}` : null,
    l.cita ? `📅 ${l.cita}` : null,
    `📍 Sucursal ${l.sucursal}`,
    `Responder: https://wa.me/${digits(l.tel)}`,
  ].filter(Boolean);
  return { titulo, lineas };
}

// client: Twilio client (or a mock with messages.create). Without client, alerts only go to the log.
function createNotifier({ client, from, contentSid, sandbox, owner, branches = {}, log = console.log }) {
  async function enviar(to, { titulo, lineas }) {
    if (!client || !from) { log(`[aviso sin enviar a ${to}: faltan credenciales de Twilio]\n🔔 ${titulo}\n${lineas.join("\n")}`); return null; }
    const msg = contentSid && !sandbox
      // template variables cannot contain line breaks
      ? { from, to, contentSid, contentVariables: JSON.stringify({ 1: titulo, 2: lineas.join(" · ") }) }
      : { from, to, body: `🔔 *${titulo}*\n\n${lineas.join("\n")}` };
    try { return await client.messages.create(msg); }
    catch (e) { log(`[aviso falló a ${to}] ${e.message}`); return null; }
  }

  // owner always; plus the branch that handles the city, if it has its own number
  function destinos(sucursal) {
    const b = /pedro/i.test(sucursal || "") ? branches.SPS : branches.TGU;
    return [...new Set([owner, b].map(waAddr).filter(Boolean))];
  }

  return {
    destinos,
    async ficha(lead) {
      const t = fichaTexto(lead), to = destinos(lead.sucursal);
      if (!to.length) { log(`[aviso sin destino: falta OWNER_WHATSAPP]\n🔔 ${t.titulo}\n${t.lineas.join("\n")}`); return []; }
      return Promise.all(to.map(n => enviar(n, t)));
    },
    enviar,
  };
}

module.exports = { createNotifier, fichaTexto, waAddr, digits };
