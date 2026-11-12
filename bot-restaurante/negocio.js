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
    items.push({ ...it, precio: +it.precio, cupos: Math.max(0, Math.round(+it.cupos || 0)), categoria: c.categoria, num: items.length + 1,
      minimo: Math.max(1, Math.round(+it.minimo || 1)), sucursales: Array.isArray(it.sucursales) ? it.sucursales.map(String) : null,
      anticipo: it.anticipo === "" || it.anticipo == null ? null : Math.min(100, Math.max(0, +it.anticipo || 0)), encargo: prepararEncargo(it.encargo, it.id, errores) });
  }
  const sids = new Set();
  for (const s of n.sucursales || []) { if (!s.id || !s.nombre) errores.push("sucursal sin id o nombre"); if (sids.has(s.id)) errores.push(`sucursal repetida: ${s.id}`); sids.add(s.id); }
  for (const it of items) for (const x of it.sucursales || []) if (!sids.has(x)) errores.push(`${it.id}: la sucursal "${x}" no existe`);
  let cupos = null;
  try { cupos = prepararCupos(n.cupos); } catch (e) { errores.push(e.message); }
  if (cupos && !cupos.porPedido && !items.some(i => i.cupos)) errores.push("con cupos, al menos un producto necesita \"cupos\" (cuántas personas)");
  let repartidores = [];
  try { repartidores = require("./repartos").prepararRepartidores(n.repartidores, n.sucursales || []); } catch (e) { errores.push(e.message); }
  if (errores.length) throw new Error("Revise el archivo del negocio: " + errores.join("; "));

  const sucursal = q => {
    const t = norm(q);
    if (!t) return null;
    return n.sucursales.find(s => norm(s.id) === t || norm(s.nombre) === t) || n.sucursales.find(s => t.length > 2 && (norm(s.nombre).includes(t) || t.includes(norm(s.nombre)))) || null;
  };
  // a product by its number in the list, its id, or its name in the customer's words.
  // "combo de 3 piezas" -> Combo 3 piezas (numbers in the name must match); "un combo" matches several equally -> null
  const STOP = new Set(["de", "del", "la", "el", "los", "las", "con", "y", "un", "una", "unas", "unos", "para", "por", "favor", "porfa", "quiero", "me", "da", "deme", "dame"]);
  // "x4" and "4px" (Marea x4 (4px), Duo de Mar (2px)) count as the number 4
  const tokens = s => norm(s).replace(/[^\w\s]/g, " ").split(/\s+/).filter(w => w && !STOP.has(w)).map(w => w.replace(/^x(\d+)$|^(\d+)px$/, "$1$2")).map(w => (w.length > 3 ? w.replace(/(es|s)$/, "") : w));
  // suc: only products sold at that branch (a name shared by two branches is not ambiguous once the branch is known)
  const item = (q, suc) => {
    const t = norm(q).replace(/[^\w\s]/g, " ").replace(/\s+/g, " ").trim();
    if (!t) return null;
    if (/^#?\d+$/.test(t)) return items[+t.replace("#", "") - 1] || null;
    const pool = suc ? items.filter(i => vendeEn(i, suc)) : items;
    const exacto = pool.find(i => norm(i.id) === t || norm(i.nombre) === t);
    if (exacto) return exacto;
    const qt = new Set(tokens(t)), qn = [...qt].filter(w => /^\d+$/.test(w));
    let mejor = [], max = 0;
    for (const i of pool) {
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
    reservaciones: prepararReservaciones(n.reservaciones),
    cupos,
    repartidores,
    items, sucursal, item, tokens,
    variasSucursales: n.sucursales.length > 1,
  };
}

// Reservaciones (opcional): el bot toma día, hora, personas y ocasión, y el restaurante confirma desde el panel.
//   ocasiones: lo que el cliente puede elegir (cumpleaños, aniversario...)
//   maxPersonas: más que esto pasa a una persona; grupoDesde: desde cuántas personas se marca como grupo grande
//   nota: lo que el bot dice al cerrar (por ejemplo "la mesa se guarda 15 minutos")
function prepararReservaciones(r) {
  if (!r || r.activo === false) return null;
  const num = (v, d) => (+v > 0 ? Math.round(+v) : d);
  const ocasiones = (Array.isArray(r.ocasiones) ? r.ocasiones : []).map(o => String(o).trim()).filter(Boolean).slice(0, 8);
  return { ocasiones, maxPersonas: num(r.maxPersonas, 20), grupoDesde: num(r.grupoDesde, Infinity), nota: String(r.nota || "").trim() };
}

// Cupos por tanda (opcional), para negocios que venden por adelantado y cocinan por tandas (Gambos).
// Cada producto dice cuántos cupos usa ("cupos": 2 = para dos personas; 0 = adicional). Cada tanda tiene porTanda cupos:
// cuando se llena, el bot ofrece otra tanda, otro día o la lista de espera.
//   dias: días que entregan ("jueves", "viernes"...); tandas: horas de cada tanda ("2:00 p. m.")
//   anticipacion: días antes que hay que pedir (1 = a más tardar el día anterior); cierre: hora (24 h, Honduras) en que se cierra
//   verDias: cuántos días hacia adelante se ofrecen; salsas: si hay, se pregunta la salsa de cada producto con cupos
//   porPedido: cada pedido usa 1 cupo (tope de apartados), sin importar los productos; porSucursal: cada sucursal tiene sus propios cupos
//   Con una sola tanda, el bot no la pregunta: solo el día.
const DIAS = ["domingo", "lunes", "martes", "miercoles", "jueves", "viernes", "sabado"];
const MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
const DIAS_TXT = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];
function prepararCupos(c) {
  if (!c || c.activo === false) return null;
  const dias = (Array.isArray(c.dias) ? c.dias : []).map(d => DIAS.indexOf(norm(d)));
  if (!dias.length || dias.some(d => d < 0)) throw new Error("cupos.dias: use días como \"jueves\", \"sabado\"");
  const tandas = (Array.isArray(c.tandas) ? c.tandas : []).map(t => String(t).trim()).filter(Boolean);
  if (!tandas.length) throw new Error("cupos.tandas: falta al menos una tanda");
  const porTanda = Math.round(+c.porTanda || 0);
  if (!(porTanda >= 1)) throw new Error("cupos.porTanda: cuántos cupos caben en cada tanda");
  const cierre = /^\d{1,2}:\d{2}$/.test(String(c.cierre || "").trim()) ? String(c.cierre).trim() : "21:00";
  const num = (v, d) => (v === "" || v == null || !(+v >= 0) ? d : Math.round(+v));
  const salsas = (Array.isArray(c.salsas) ? c.salsas : []).map(s => String(s).trim()).filter(Boolean).slice(0, 6);
  return { dias, tandas, porTanda, anticipacion: num(c.anticipacion, 1), cierre, verDias: num(c.verDias, 7) || 7, salsas, nota: String(c.nota || "").trim(),
    porPedido: !!c.porPedido, porSucursal: !!c.porSucursal };
}
// the days a customer can still order for, from now (Honduras time, UTC-6 all year): [{ fecha: "2026-10-30", etiqueta: "viernes 30 de octubre" }]
// todos: also days already closed (for the panel)
function fechasCupos(negocio, now, todos = false) {
  const C = negocio.cupos;
  if (!C) return [];
  const local = new Date(new Date(now || Date.now()).getTime() - 6 * 3600e3);
  const hoy = Date.UTC(local.getUTCFullYear(), local.getUTCMonth(), local.getUTCDate());
  const [hh, mm] = C.cierre.split(":").map(Number);
  const out = [];
  for (let k = 0; k <= C.verDias; k++) {
    const d = new Date(hoy + k * 864e5);
    if (!C.dias.includes(d.getUTCDay())) continue;
    const cierra = hoy + (k - C.anticipacion) * 864e5 + (hh * 60 + mm) * 6e4;
    if (!todos && (k < C.anticipacion || local.getTime() >= cierra)) continue;
    out.push({ fecha: d.toISOString().slice(0, 10), etiqueta: `${DIAS_TXT[d.getUTCDay()]} ${d.getUTCDate()} de ${MESES[d.getUTCMonth()]}` });
  }
  return out;
}
// how many cupos an order needs: [{ id, cantidad }]
const cuposDe = (negocio, lineas) => negocio.cupos && negocio.cupos.porPedido ? ((lineas || []).length ? 1 : 0) : (lineas || []).reduce((a, l) => { const it = negocio.items.find(i => i.id === l.id); return a + (it ? it.cupos * Math.max(1, Math.round(+l.cantidad || 1)) : 0); }, 0);

// Cobro antes de cocinar (opcional): para que un pedido grande o de alguien que ya dejó un pedido botado
// no se cocine hasta que esté pagado. Solo se activa si el restaurante dio cómo cobrar (transferencia o enlace).
//   desde: total (en la moneda del negocio) desde el que se cobra antes (0 = todos; vacío = ninguno por monto)
//   faltas: cuántas veces "No vino" a recoger para que ese número tenga que pagar antes (0 = nunca)
//   transferencia: banco, tipo y número de cuenta, a nombre de quién (lo da el dueño)
//   tarjeta: enlace de pago fijo de la pasarela del restaurante; {n} y {total} se cambian por el pedido y el total
//   domicilio: false = los pedidos a domicilio no pagan antes (se le paga al repartidor al recibir)
//   anticipo: qué porcentaje del total se paga antes (100 = todo). Un producto puede tener el suyo ("anticipo": 50).
// Con una pasarela conectada (pagos.js, claves en Render) server.js pone pasarela: true: cada pedido lleva su propio
// link y, cuando el pago sale bien, pasa solo a cocina.
const LINK = "[[LINK_DE_PAGO]]";   // server.js lo cambia por el link de ese pedido
function prepararCobro(c) {
  c = c || {};
  const num = (v, d) => (v === "" || v == null || !(+v >= 0) ? d : +v);
  const transferencia = String(c.transferencia || "").trim(), tarjeta = String(c.tarjeta || "").trim();
  return { activo: !!(transferencia || tarjeta), desde: num(c.desde, Infinity), faltas: num(c.faltas, 0), transferencia, tarjeta, pasarela: false,
    domicilio: c.domicilio !== false, anticipo: Math.min(100, Math.max(1, num(c.anticipo, 100))) };
}
// faltas = pedidos de este número que quedaron en "No vino"
function requiereCobro(negocio, total, faltas = 0, { domicilio = false, lineas = null } = {}) {
  const c = negocio.cobro;
  if (!c || !c.activo) return false;
  // an order for a set date (encargo) with a deposit always pays first
  if (lineas && lineas.some(l => { const it = negocio.items.find(i => i.id === l.id); return it && it.encargo && it.anticipo; })) return true;
  if (domicilio && !c.domicilio) return false;
  return total >= c.desde || (c.faltas > 0 && faltas >= c.faltas);
}
// how much is paid before: each line's share by its product's anticipo (or the business's), whole lempiras
function montoCobro(negocio, lineas) {
  const c = negocio.cobro;
  return Math.ceil((lineas || []).reduce((a, l) => { const it = negocio.items.find(i => i.id === l.id); const pct = it && it.anticipo != null ? it.anticipo : c.anticipo; return a + l.subtotal * pct / 100; }, 0));
}
function textoCobro(negocio, n, total, monto = total) {
  const c = negocio.cobro;
  const link = c.tarjeta.replace(/\{n\}/g, encodeURIComponent(n)).replace(/\{total\}/g, String(monto));
  const parcial = monto < total;
  return [
    c.pasarela ? `💳 *Con tarjeta:* ${LINK}\nAl pagar con tarjeta, el pedido entra solo a cocina.` : c.tarjeta ? `💳 *Con tarjeta:* ${link}` : null,
    c.transferencia ? `🏦 *Por transferencia:* ${c.transferencia}` : null,
    parcial ? `Anticipo: *${negocio.L(monto)}* de ${negocio.L(total)} · Referencia: *${n}*\nEl resto (${negocio.L(total - monto)}) se paga al recibir.` : `Monto: *${negocio.L(total)}* · Referencia: *${n}*`,
    c.transferencia ? `${c.pasarela ? "Si paga por transferencia, mándenos" : "Al pagar, mándenos"} aquí la foto del comprobante.` : null,
  ].filter(Boolean).join("\n");
}

// Encargos (opcional, por producto): se piden con tiempo para una fecha fija, por ejemplo la pierna del 24 de diciembre.
//   "encargo": { "fecha": "2026-12-24", "hasta": "2026-12-15" }  -> se entrega ese día; se reciben pedidos hasta "hasta" (inclusive)
// No usan los cupos de los días normales y van en un pedido aparte.
function prepararEncargo(e, id, errores) {
  if (!e) return null;
  const f = /^\d{4}-\d{2}-\d{2}$/;
  if (!f.test(String(e.fecha || "")) || (e.hasta && !f.test(String(e.hasta)))) { errores.push(`${id}: encargo necesita "fecha" (y "hasta") como AAAA-MM-DD`); return null; }
  const d = new Date(e.fecha + "T12:00:00Z");
  return { fecha: e.fecha, hasta: e.hasta || e.fecha, etiqueta: `${DIAS_TXT[d.getUTCDay()]} ${d.getUTCDate()} de ${MESES[d.getUTCMonth()]}` };
}
const hoyHN = now => new Date(new Date(now || Date.now()).getTime() - 6 * 3600e3).toISOString().slice(0, 10);
const vendeEn = (it, sucursalId) => !it.sucursales || !sucursalId || it.sucursales.includes(sucursalId);
// the encargo of an order whose products are all encargos (null for a normal order)
function encargoDe(negocio, lineas) {
  const its = (lineas || []).map(l => negocio.items.find(i => i.id === l.id)).filter(Boolean);
  return its.length && its.every(i => i.encargo) ? its[0].encargo : null;
}
// what is wrong with an order before it is saved, in words for the customer (null = fine)
function revisarPedido(negocio, lineas, sucursalId, now) {
  const its = (lineas || []).map(l => [l, negocio.items.find(i => i.id === l.id)]).filter(([, it]) => it);
  const b = negocio.sucursales.find(s => s.id === sucursalId);
  const fuera = its.filter(([, it]) => !vendeEn(it, sucursalId)).map(([, it]) => it.nombre);
  if (fuera.length) return `En ${b ? b.nombre : "esa sucursal"} no tenemos: ${[...new Set(fuera)].join(", ")}.`;
  const cant = id => its.filter(([l]) => l.id === id).reduce((a, [l]) => a + Math.round(+l.cantidad || 1), 0);
  const corto = its.find(([l, it]) => it.minimo > 1 && cant(it.id) < it.minimo);
  if (corto) return `El pedido mínimo de ${corto[1].nombre} es de ${corto[1].minimo}.`;
  const enc = its.filter(([, it]) => it.encargo);
  if (enc.length && enc.length < its.length) return `${enc[0][1].nombre} es por encargo para el ${enc[0][1].encargo.etiqueta}: se pide en un pedido aparte.`;
  if (enc.length && new Set(enc.map(([, it]) => it.encargo.fecha)).size > 1) return "Esos encargos son para fechas distintas: se piden por separado.";
  const vencido = enc.find(([, it]) => hoyHN(now) > it.encargo.hasta);
  if (vencido) return `Ya se cerraron los pedidos de ${vencido[1].nombre}.`;
  return null;
}

// extra: datos que no van en el repositorio público (NEGOCIO_PRIVADO en Render, JSON):
//   { "sucursales": { "<id>": { "whatsapp": "+504 ..." } }, "repartidores": [...], "cobro": { "transferencia": "..." } }
function cargarNegocio(archivo, extra) {
  const f = path.resolve(__dirname, archivo || "negocios/ejemplo.json");
  return preparar(mezclarPrivado(JSON.parse(fs.readFileSync(f, "utf8")), extra));
}
function mezclarPrivado(n, extra) {
  if (!extra) return n;
  const x = typeof extra === "string" ? JSON.parse(extra) : extra;
  return {
    ...n,
    sucursales: (n.sucursales || []).map(s => ({ ...s, ...((x.sucursales || {})[s.id] || {}) })),
    ...(x.repartidores ? { repartidores: x.repartidores } : {}),
    ...(x.cobro ? { cobro: { ...(n.cobro || {}), ...x.cobro } } : {}),
  };
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

module.exports = { cargarNegocio, preparar, cuenta, fechasCupos, cuposDe, lineaTexto, requiereCobro, textoCobro, montoCobro, revisarPedido, encargoDe, vendeEn, mezclarPrivado, LINK, norm, L, dinero, MONEDAS };
