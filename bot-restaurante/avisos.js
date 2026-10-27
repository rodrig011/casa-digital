// Avisos por WhatsApp: cada pedido nuevo y cada "quiero hablar con una persona" le llegan al dueño
// y a la sucursal que lo atiende (si tiene WhatsApp propio en negocios/<cliente>.json).
// Así nadie depende de que alguien esté pendiente del celular del negocio.
//
// WhatsApp solo deja mandar texto libre a alguien que le escribió al número del bot en las últimas 24 h.
// Por eso, en producción, los avisos al dueño salen con una plantilla aprobada por Meta (TWILIO_ALERT_CONTENT_SID).
// El "su pedido está listo" al cliente sí va como texto libre: el cliente acaba de escribir.
const { lineaTexto, L } = require("./negocio");

// "+504 3189-6607", "50431896607" o "whatsapp:+50431896607" -> "whatsapp:+50431896607"
const waAddr = n => { const d = String(n || "").replace(/\D/g, ""); return d ? "whatsapp:+" + d : null; };
const digits = n => String(n || "").replace(/\D/g, "");

function fichaTexto(p, fmt = L) {
  if (p.tipo === "persona") return {
    titulo: `${p.nombre || "Un cliente"} pidió hablar con una persona · ${p.sucursal}`,
    lineas: [`👤 ${p.nombre || "Sin nombre"} · +${digits(p.tel)}`, p.motivo ? `💬 ${p.motivo}` : null, `Responder: https://wa.me/${digits(p.tel)}`].filter(Boolean),
  };
  if (p.tipo === "reservacion") return {
    titulo: `${p.grupo ? "Reservación de grupo" : "Nueva reservación"} ${p.n} · ${p.sucursal}`,
    lineas: [`👤 ${p.nombre || "Sin nombre"} · +${digits(p.tel)}`, `📅 ${p.dia}, ${p.hora}`, `👥 ${p.personas} ${p.personas === 1 ? "persona" : "personas"}`, p.ocasion ? `🎉 ${p.ocasion}` : null, "Confirme o diga que no hay cupo desde el panel: al cliente le llega el aviso.", `Responder: https://wa.me/${digits(p.tel)}`].filter(Boolean),
  };
  const porPagar = p.estado === "por_pagar", espera = p.estado === "en_espera";
  return {
    titulo: `${espera ? "Lista de espera" : porPagar ? "Pedido por pagar" : "Nuevo pedido"} ${p.n} · ${p.sucursal}`,
    lineas: [
      espera ? `⏳ No había cupo: quiere ${p.cupos} ${p.cupos === 1 ? "cupo" : "cupos"} para ${p.dia}. Si se libera uno, escríbale.` : null,
      p.tanda ? `📅 ${p.dia.replace(/^\p{L}/u, c => c.toUpperCase())} · tanda de ${p.tanda} · ${p.cupos} ${p.cupos === 1 ? "cupo" : "cupos"}` : null,
      porPagar ? "⏳ Todavía no va a cocina: espera el pago" : null,
      p.pagado && p.metodoPago === "tarjeta" ? "💳 Pagado con tarjeta" : null,
      p.faltas ? `⚠️ Este número no vino a recoger ${p.faltas === 1 ? "1 vez" : p.faltas + " veces"} antes` : null,
      `👤 ${p.nombre || "Sin nombre"} · +${digits(p.tel)}`,
      ...(p.lineas || []).map(l => lineaTexto(l, fmt)),
      `💰 Total ${fmt(p.total)}`,
      p.entrega === "domicilio" ? `🛵 A domicilio: ${p.direccion}` : p.tanda || espera ? "📍 Lo recoge" : p.hora ? `🕒 Recoge: ${p.hora}` : null,
      `Responder: https://wa.me/${digits(p.tel)}`,
    ].filter(Boolean),
  };
}

// client: Twilio client (or a mock with messages.create). Without client, messages only go to the log.
function createNotifier({ client, from, contentSid, sandbox, owner, negocio, log = console.log }) {
  async function enviar(to, body, plantilla, media) {
    if (!client || !from) { log(`[mensaje sin enviar a ${to}: faltan credenciales de Twilio]\n${body}`); return null; }
    const msg = plantilla && contentSid && !sandbox
      // template variables cannot contain line breaks
      ? { from, to, contentSid, contentVariables: JSON.stringify({ 1: plantilla.titulo, 2: plantilla.lineas.join(" · ") }) }
      : { from, to, body, ...(media ? { mediaUrl: [media] } : {}) };
    try { return await client.messages.create(msg); }
    catch (e) { log(`[mensaje falló a ${to}] ${e.message}`); return null; }
  }

  // owner always; plus the branch, if it has its own WhatsApp
  function destinos(sucursal) {
    const b = negocio.sucursales.find(s => s.nombre === sucursal || s.id === sucursal);
    return [...new Set([owner, b && b.whatsapp].map(waAddr).filter(Boolean))];
  }

  return {
    destinos,
    async ficha(p) {
      const t = fichaTexto(p, negocio.L), to = destinos(p.sucursal);
      const body = `🔔 *${t.titulo}*\n\n${t.lineas.join("\n")}`;
      if (!to.length) { log(`[aviso sin destino: falta OWNER_WHATSAPP]\n${body}`); return []; }
      return Promise.all(to.map(n => enviar(n, body, t)));
    },
    // to the customer, when the kitchen marks the order as ready
    listo(p) {
      if (p.entrega === "domicilio") return enviar(waAddr(p.tel), `🛵 ¡${(p.nombre || "Hola").split(" ")[0]}, su pedido *${p.n}* ya va en camino! Total: ${negocio.L(p.total)}. ¡Gracias por su compra!`);
      const b = negocio.sucursales.find(s => s.nombre === p.sucursal);
      return enviar(waAddr(p.tel), `✅ ¡${(p.nombre || "Hola").split(" ")[0]}, su pedido *${p.n}* ya está listo! Puede pasar a recogerlo a *${p.sucursal}*${b && b.direccion ? ` (${b.direccion})` : ""}.\n\nTotal: ${negocio.L(p.total)}. ¡Gracias por su compra!`);
    },
    // the payment receipt photo, to the owner and branch: someone checks the bank and taps "Pago recibido"
    async comprobante(p, mediaUrl) {
      const t = { titulo: `Comprobante de pago ${p.n} · ${p.sucursal}`, lineas: [`👤 ${p.nombre || "Sin nombre"} · +${digits(p.tel)}`, `💰 Total ${negocio.L(p.total)}`, "Revise que el dinero esté en la cuenta y toque Pago recibido en el panel. Hasta entonces no va a cocina."] };
      const to = destinos(p.sucursal);
      const body = `💳 *${t.titulo}*\n\n${t.lineas.join("\n")}`;
      if (!to.length) { log(`[aviso sin destino: falta OWNER_WHATSAPP]\n${body}`); return []; }
      return Promise.all(to.map(n => enviar(n, body, t, mediaUrl)));
    },
    // to the customer, when the restaurant confirms the table (or has no room) from the panel
    reservacion(p) {
      const nom = (p.nombre || "Hola").split(" ")[0];
      const r = negocio.reservaciones || {};
      return enviar(waAddr(p.tel), p.estado === "confirmada"
        ? `✅ ${nom}, su mesa en *${p.sucursal}* queda apartada: ${p.dia}, ${p.hora}, ${p.personas} ${p.personas === 1 ? "persona" : "personas"}.${r.nota ? `\n${r.nota}` : ""}\n\n¡Le esperamos!`
        : `${nom}, lo sentimos: para ${p.dia} a las ${p.hora} ya no tenemos mesa para ${p.personas}. Si quiere otra hora o día, escríbanos por aquí y se la buscamos.`);
    },
    // to the customer, when someone confirms the payment in the panel
    pagado(p) {
      return enviar(waAddr(p.tel), `✅ Recibimos su pago del pedido *${p.n}* (${negocio.L(p.total)}). Ya está en cocina; le avisamos por aquí cuando esté listo.`);
    },
    enviar,
  };
}

module.exports = { createNotifier, fichaTexto, waAddr, digits };
