// WhatsApp directo con Meta (Cloud API), sin Twilio: Meta no cobra las respuestas a quien escribió primero.
//
//   GET  /meta    Meta comprueba el webhook (hub.verify_token = META_VERIFY_TOKEN)
//   POST /meta    mensajes que llegan; la firma X-Hub-Signature-256 se revisa con META_APP_SECRET
//
// Los menús salen como botones de WhatsApp (hasta 3) o como lista (hasta 10); el id de cada opción es su número,
// así el motor lo entiende igual que si el cliente escribiera "2".
// Fuera de las 24 horas desde el último mensaje del cliente, WhatsApp solo deja mandar plantillas aprobadas:
// si un aviso no pasa por eso, sale con la plantilla META_PLANTILLA (categoría Utilidad, cuerpo "{{1}}" y "{{2}}").
// El código para entrar al panel sale con META_PLANTILLA_CODIGO (categoría Autenticación, botón "Copiar código"),
// que es la que Meta pide para códigos; sin ella sale como aviso normal.
const crypto = require("crypto");
const { toText } = require("./engine");

const VERSION = "v21.0";
const digits = n => String(n || "").replace(/\D/g, "");
// template parameters cannot carry line breaks, tabs or more than 4 spaces in a row
const param = s => String(s || "").replace(/[\n\t]+/g, " · ").replace(/ {4,}/g, "   ").trim().slice(0, 900) || "-";
const corta = (s, n) => (s.length > n ? s.slice(0, n - 1) + "…" : s);

function createMeta({ token, phoneId, appSecret = "", plantilla = "", plantillaCodigo = "", idioma = "es", version = VERSION, fetch: f = globalThis.fetch, log = console.log } = {}) {
  const api = `https://graph.facebook.com/${version}`;
  async function llamar(ruta, cuerpo) {
    const r = await f(`${api}/${ruta}`, { method: "POST", headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }, body: JSON.stringify(cuerpo) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) { const e = new Error((j.error && j.error.message) || `Meta ${r.status}`); e.code = j.error && j.error.code; throw e; }
    return j;
  }
  const mandar = (to, m) => llamar(`${phoneId}/messages`, { messaging_product: "whatsapp", to: digits(to), ...m });

  // one bot message: buttons when they fit, a list up to 10 options, plain text otherwise
  function formato(m) {
    const text = m.text || "", bs = m.buttons || [];
    if (bs.length && bs.length <= 3 && bs.every(b => b.length <= 20) && text.length <= 1024)
      return { type: "interactive", interactive: { type: "button", body: { text }, action: { buttons: bs.map((b, i) => ({ type: "reply", reply: { id: String(i + 1), title: b } })) } } };
    if (bs.length && bs.length <= 10 && text.length <= 1024)
      return { type: "interactive", interactive: { type: "list", body: { text }, action: { button: "Ver opciones", sections: [{ title: "Opciones", rows: bs.map((b, i) => ({ id: String(i + 1), title: corta(b, 24), ...(b.length > 24 ? { description: corta(b, 72) } : {}) })) }] } } };
    return { type: "text", text: { body: corta(toText(m), 4096), preview_url: false } };
  }
  const conPlantilla = (to, uno, dos) => mandar(to, { type: "template", template: { name: plantilla, language: { code: idioma }, components: [{ type: "body", parameters: [{ type: "text", text: param(uno) }, { type: "text", text: param(dos) }] }] } });

  // a bot reply (just after the customer wrote: always inside the 24 h)
  const responder = (to, m) => mandar(to, formato(typeof m === "string" ? { text: m } : m));

  // a notice (owner, branch, or a customer whose last message may be old). aviso = { titulo, lineas } for the template
  async function enviar(to, body, aviso, media) {
    try {
      if (aviso && plantilla) return await conPlantilla(to, aviso.titulo, aviso.lineas.join(" · "));
      const r = await mandar(to, { type: "text", text: { body: corta(body, 4096), preview_url: false } });
      const foto = typeof media === "function" ? await media() : media;
      if (foto) await mandar(to, { type: "image", image: { id: foto } }).catch(e => log(`[meta] la foto no salió a ${to}: ${e.message}`));
      return r;
    } catch (e) {
      // 131047: more than 24 h since the person last wrote; only a template gets through
      if (e.code === 131047 && plantilla && !aviso) {
        const [uno, ...resto] = body.split("\n").filter(Boolean);
        try { return await conPlantilla(to, uno, resto.join(" · ")); } catch (e2) { e = e2; }
      }
      log(`[mensaje falló a ${to}] ${e.message}${e.code === 131047 && !plantilla ? " (pasaron más de 24 h: falta META_PLANTILLA)" : ""}`);
      return null;
    }
  }

  // a photo the customer sent (media id) -> a new media id the bot can forward to the owner
  async function reenviable(id) {
    const auth = { headers: { Authorization: `Bearer ${token}` } };
    const info = await (await f(`${api}/${id}`, auth)).json();
    if (!info.url) throw new Error("Meta no dio la foto");
    const foto = await f(info.url, auth);
    if (!foto.ok) throw new Error(`no se pudo bajar la foto (${foto.status})`);
    const form = new FormData();
    form.append("messaging_product", "whatsapp");
    form.append("file", new Blob([await foto.arrayBuffer()], { type: info.mime_type || "image/jpeg" }), "comprobante.jpg");
    const r = await f(`${api}/${phoneId}/media`, { method: "POST", headers: { Authorization: `Bearer ${token}` }, body: form });
    const j = await r.json();
    if (!j.id) throw new Error((j.error && j.error.message) || "Meta no guardó la foto");
    return j.id;
  }

  // X-Hub-Signature-256 = "sha256=" + HMAC of the raw body with the app secret
  function firmaOk(raw, header) {
    if (!appSecret) return false;
    const esperado = "sha256=" + crypto.createHmac("sha256", appSecret).update(raw || "").digest("hex");
    const a = Buffer.from(String(header || "")), b = Buffer.from(esperado);
    return a.length === b.length && crypto.timingSafeEqual(a, b);
  }

  // login code for the owner panel: true when WhatsApp took it
  async function codigo(to, c, texto) {
    if (!plantillaCodigo) return !!(await enviar(to, texto, { titulo: `Código para entrar al panel: ${c}`, lineas: ["Vence en 5 minutos. No se lo dé a nadie."] }));
    try {
      await mandar(to, { type: "template", template: { name: plantillaCodigo, language: { code: idioma }, components: [{ type: "body", parameters: [{ type: "text", text: c }] }, { type: "button", sub_type: "url", index: "0", parameters: [{ type: "text", text: c }] }] } });
      return true;
    } catch (e) { log(`[meta] el código no salió a ${to}: ${e.message}`); return false; }
  }

  return { responder, enviar, reenviable, firmaOk, formato, codigo };
}

// the messages inside one webhook post: [{ id, from, nombre, text, foto }]
// a tapped button or list row comes back as its number; a photo comes with its media id
function mensajes(body) {
  const out = [];
  for (const e of (body && body.entry) || []) for (const c of e.changes || []) {
    const v = c.value || {};
    const nombres = Object.fromEntries((v.contacts || []).map(x => [x.wa_id, x.profile && x.profile.name]));
    for (const m of v.messages || []) {
      const i = m.interactive || {};
      const text = m.type === "text" ? m.text.body
        : m.type === "interactive" ? (i.button_reply || i.list_reply || {}).id || ""
        : m.type === "button" ? (m.button || {}).text || ""
        : m.type === "image" ? (m.image && m.image.caption) || ""
        : "";
      out.push({ id: m.id, from: m.from, nombre: nombres[m.from] || "", text: String(text).slice(0, 1000), foto: m.type === "image" ? m.image.id : null, tipo: m.type });
    }
  }
  return out;
}

module.exports = { createMeta, mensajes, VERSION };
