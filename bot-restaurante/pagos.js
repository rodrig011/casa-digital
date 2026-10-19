// Pago con tarjeta por pasarela: un link de pago por pedido, y el pedido pasa solo a cocina cuando el pago sale bien.
// Hoy hay una pasarela: Tilopay (API pública: https://tilopay.com/developers/api/links-de-pago).
// La cuenta de comercio es del restaurante (el dinero cae en su banco); las claves van en Render > Environment.
//
//   const p = createPasarela({ proveedor: "tilopay", usuario, clave, key, moneda: "HNL", fetch });
//   await p.crearLink({ n, total, nombre, descripcion, webhookUrl, volverUrl })  -> { id, url }
//   await p.verificar(id, total)                                                  -> { pagado, monto }
//
// El aviso de la pasarela (webhook) solo despierta al bot: el pago se confirma siempre consultando la API,
// como recomienda Tilopay, para que nadie pueda mandar a cocina un pedido con un aviso falso.
// NUNCA PROBADO con una cuenta real: con el primer pago de prueba hay que revisar los campos de "payments".

const TILOPAY = "https://app.tilopay.com/api/v1";

function createTilopay({ usuario, clave, key, moneda = "HNL", fetch = globalThis.fetch, now = () => Date.now() }) {
  let token = null, vence = 0;
  async function api(ruta, opciones = {}) {
    const r = await fetch(TILOPAY + ruta, { ...opciones, headers: { "Content-Type": "application/json", Accept: "application/json", ...(opciones.headers || {}) } });
    const txt = await r.text();
    let j; try { j = JSON.parse(txt); } catch { j = null; }
    if (!r.ok || !j) throw new Error(`Tilopay ${ruta.split("/")[1]} respondió ${r.status}: ${txt.slice(0, 200)}`);
    return j;
  }
  async function auth() {
    if (token && now() < vence) return token;
    const j = await api("/login", { method: "POST", body: JSON.stringify({ apiuser: usuario, password: clave }) });
    if (!j.access_token) throw new Error("Tilopay no devolvió access_token");
    token = j.access_token; vence = now() + Math.max(60, (+j.expires_in || 3600) - 300) * 1000;
    return token;
  }
  const conToken = async () => ({ Authorization: "bearer " + (await auth()) });

  return {
    proveedor: "tilopay",
    async crearLink({ n, total, nombre, descripcion, webhookUrl, volverUrl }) {
      const j = await api("/createLinkPayment", {
        method: "POST", headers: await conToken(),
        body: JSON.stringify({ key, amount: (+total).toFixed(2), currency: moneda, reference: n, type: 1, description: (descripcion || `Pedido ${n}`).slice(0, 250), client: (nombre || "Cliente").slice(0, 60), ...(volverUrl ? { callback_url: volverUrl } : {}), ...(webhookUrl ? { webhook_url: webhookUrl } : {}) }),
      });
      if (String(j.type) !== "200" || !j.url) throw new Error(`Tilopay no creó el link: ${j.message || JSON.stringify(j).slice(0, 200)}`);
      return { id: String(j.id), url: j.url };
    },
    // paid = an approved payment on this single-use link for at least the order total
    async verificar(id, total) {
      const j = await api(`/getDetailLinkPayment/${encodeURIComponent(id)}/${encodeURIComponent(key)}`, { headers: await conToken() });
      const pagos = Array.isArray(j.payments) ? j.payments : [];
      const aprobado = x => {
        const code = String(x.code ?? x.response_code ?? x.responseCode ?? "");
        const estado = String(x.status ?? x.estado ?? x.state ?? "");
        return code === "1" || /aprob|approv|success|exito/i.test(estado);
      };
      const ok = pagos.filter(aprobado);
      const monto = ok.reduce((a, x) => a + (+(x.amount ?? x.monto ?? 0) || 0), 0);
      return { pagado: ok.length > 0 && (monto === 0 || monto + 0.005 >= +total), monto, pagos: pagos.length };
    },
  };
}

function createPasarela(cfg) {
  if (!cfg || !cfg.proveedor) return null;
  if (cfg.proveedor === "tilopay") {
    if (!cfg.usuario || !cfg.clave || !cfg.key) return null;
    return createTilopay(cfg);
  }
  return null;   // unknown gateway: card payment stays off (server.js says so at startup)
}

module.exports = { createPasarela, createTilopay };
