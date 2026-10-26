// Datos de cada restaurante: negocios/<cliente>.json (menú, precios, sucursales, horario, domicilio).
// El bot nunca inventa: todo lo que dice del negocio sale de este archivo.
// Lo que el cliente no ha confirmado (por ejemplo un horario) se deja vacío y el bot dice que una persona lo confirma.
const fs = require("fs");
const path = require("path");

const norm = s => (s || "").toString().trim().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
// "moneda" en negocios/<cliente>.json: HNL (lempiras, por defecto), GTQ (quetzales) o USD (dólares, El Salvador)
const MONEDAS = {
  HNL: { simbolo: "L ", locale: "es-HN", min: 0, pais: "Honduras" },
  GTQ: { simbolo: "Q", locale: "es-GT", min: 0, pais: "Guatemala" },
  USD: { simbolo: "$", locale: "en-US", min: 2, pais: "El Salvador" },
};
const dinero = (moneda = "HNL") => {
  const m = MONEDAS[moneda] || MONEDAS.HNL;
  return n => m.simbolo + (+n || 0).toLocaleString(m.locale, { minimumFractionDigits: m.min, maximumFractionDigits: 2 });
};
const L = dinero("HNL");

function preparar(n) {
  const errores = [];
  if (!n || typeof n !== "object") throw new Error("El archivo del negocio no es un objeto JSON.");
  if (!n.nombre) errores.push("falta nombre");
  if (!Array.isArray(n.sucursales) || !n.sucursales.length) errores.push("falta al menos una sucursal");
  if (!Array.isArray(n.menu) || !n.menu.length) errores.push("falta el menú");
  if (n.moneda && !MONEDAS[n.moneda]) errores.push(`moneda desconocida: ${n.moneda} (use ${Object.keys(MONEDAS).join(", ")})`);
  const items = [];
  const ids = new Set();
  for (const c of n.menu || []) for (const it of c.items || []) {
    if (!it.id || !it.nombre || !(+it.precio >= 0)) { errores.push(`producto incompleto en ${c.categoria}: ${JSON.stringify(it)}`); continue; }
    if (ids.has(it.id)) errores.push(`id repetido: ${it.id}`);
    ids.add(it.id);
    items.push({ ...it, precio: +it.precio, categoria: c.categoria, num: items.length + 1 });
  }
  const sids = new Set();
  for (const s of n.sucursales || []) { if (!s.id || !s.nombre) errores.push("sucursal sin id o nombre"); if (sids.has(s.id)) errores.push(`sucursal repetida: ${s.id}`); sids.add(s.id); }
  if (errores.length) throw new Error("Revise el archivo del negocio: " + errores.join("; "));

  const sucursal = q => {
    const t = norm(q);
    if (!t) return null;
    return n.sucursales.find(s => norm(s.id) === t || norm(s.nombre) === t) || n.sucursales.find(s => t.length > 2 && (norm(s.nombre).includes(t) || t.includes(norm(s.nombre)))) || null;
  };
  // a product by its number in the list, its id, or its name in the customer's words.
  // "combo de 3 piezas" -> Combo 3 piezas (numbers in the name must match); "un combo" matches several equally -> null
  const STOP = new Set(["de", "del", "la", "el", "los", "las", "con", "y", "un", "una", "unas", "unos", "para", "por", "favor", "porfa", "quiero", "me", "da", "deme", "dame"]);
  const tokens = s => norm(s).replace(/[^\w\s]/g, " ").split(/\s+/).filter(w => w && !STOP.has(w)).map(w => (w.length > 3 ? w.replace(/(es|s)$/, "") : w));
  const item = q => {
    const t = norm(q).replace(/[^\w\s]/g, " ").replace(/\s+/g, " ").trim();
    if (!t) return null;
    if (/^#?\d+$/.test(t)) return items[+t.replace("#", "") - 1] || null;
    const exacto = items.find(i => norm(i.id) === t || norm(i.nombre) === t);
    if (exacto) return exacto;
    const qt = new Set(tokens(t)), qn = [...qt].filter(w => /^\d+$/.test(w));
    let mejor = [], max = 0;
    for (const i of items) {
      const nt = tokens(i.nombre), alfa = nt.filter(w => !/^\d+$/.test(w)), nums = nt.filter(w => /^\d+$/.test(w));
      if (qn.length && nums.length && !nums.every(x => qt.has(x))) continue;
      const hits = alfa.filter(w => qt.has(w)).length;
      if (!hits) continue;
      const sc = hits / alfa.length + (nums.length && nums.every(x => qt.has(x)) ? 0.5 : 0);
      if (sc > max + 1e-9) { max = sc; mejor = [i]; } else if (Math.abs(sc - max) < 1e-9) mejor.push(i);
    }
    return mejor.length === 1 ? mejor[0] : null;
  };
  return {
    ...n,
    color: n.color || "#C8102E",
    moneda: n.moneda || "HNL",
    pais: n.pais || (MONEDAS[n.moneda] || MONEDAS.HNL).pais,
    L: dinero(n.moneda),
    pago: n.pago || "",
    domicilio: n.domicilio || { propio: false, apps: [] },
    cobro: prepararCobro(n.cobro),
    items, sucursal, item, tokens,
    variasSucursales: n.sucursales.length > 1,
  };
}

// Cobro antes de cocinar (opcional): para que un pedido grande o de alguien que ya dejó un pedido botado
// no se cocine hasta que esté pagado. Solo se activa si el restaurante dio cómo cobrar (transferencia o enlace).
//   desde: total (en la moneda del negocio) desde el que se cobra antes (0 = todos; vacío = ninguno por monto)
//   faltas: cuántas veces "No vino" a recoger para que ese número tenga que pagar antes (0 = nunca)
//   transferencia: banco, tipo y número de cuenta, a nombre de quién (lo da el dueño)
//   tarjeta: enlace de pago fijo de la pasarela del restaurante; {n} y {total} se cambian por el pedido y el total
// Con una pasarela conectada (pagos.js, claves en Render) server.js pone pasarela: true: cada pedido lleva su propio
// link y, cuando el pago sale bien, pasa solo a cocina.
const LINK = "[[LINK_DE_PAGO]]";   // server.js lo cambia por el link de ese pedido
function prepararCobro(c) {
  c = c || {};
  const num = (v, d) => (v === "" || v == null || !(+v >= 0) ? d : +v);
  const transferencia = String(c.transferencia || "").trim(), tarjeta = String(c.tarjeta || "").trim();
  return { activo: !!(transferencia || tarjeta), desde: num(c.desde, Infinity), faltas: num(c.faltas, 0), transferencia, tarjeta, pasarela: false };
}
// faltas = pedidos de este número que quedaron en "No vino"
function requiereCobro(negocio, total, faltas = 0) {
  const c = negocio.cobro;
  if (!c || !c.activo) return false;
  return total >= c.desde || (c.faltas > 0 && faltas >= c.faltas);
}
function textoCobro(negocio, n, total) {
  const c = negocio.cobro;
  const link = c.tarjeta.replace(/\{n\}/g, encodeURIComponent(n)).replace(/\{total\}/g, String(total));
  return [
    c.pasarela ? `💳 *Con tarjeta:* ${LINK}\nAl pagar con tarjeta, el pedido entra solo a cocina.` : c.tarjeta ? `💳 *Con tarjeta:* ${link}` : null,
    c.transferencia ? `🏦 *Por transferencia:* ${c.transferencia}` : null,
    `Monto: *${negocio.L(total)}* · Referencia: *${n}*`,
    c.transferencia ? `${c.pasarela ? "Si paga por transferencia, mándenos" : "Al pagar, mándenos"} aquí la foto del comprobante.` : null,
  ].filter(Boolean).join("\n");
}

function cargarNegocio(archivo) {
  const f = path.resolve(__dirname, archivo || "negocios/ejemplo.json");
  return preparar(JSON.parse(fs.readFileSync(f, "utf8")));
}

// "2 × Combo 2 piezas (sin picante)" lines and the total, from [{ id, cantidad, nota }]
function cuenta(negocio, lineas) {
  const out = [];
  for (const l of lineas || []) {
    const it = negocio.items.find(i => i.id === l.id);
    if (!it) continue;
    const cantidad = Math.max(1, Math.min(99, Math.round(+l.cantidad || 1)));
    const prev = out.find(o => o.id === it.id && (o.nota || "") === (l.nota || ""));
    if (prev) { prev.cantidad += cantidad; prev.subtotal = prev.cantidad * it.precio; continue; }
    out.push({ id: it.id, nombre: it.nombre, precio: it.precio, cantidad, subtotal: cantidad * it.precio, ...(l.nota ? { nota: String(l.nota).slice(0, 120) } : {}) });
  }
  return { lineas: out, total: out.reduce((a, l) => a + l.subtotal, 0) };
}
const lineaTexto = (l, fmt = L) => `${l.cantidad} × ${l.nombre}${l.nota ? ` (${l.nota})` : ""} · ${fmt(l.subtotal)}`;

module.exports = { cargarNegocio, preparar, cuenta, lineaTexto, requiereCobro, textoCobro, LINK, norm, L, dinero, MONEDAS };
