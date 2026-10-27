// Memoria del bot: conversaciones en curso y pedidos, guardados en archivos JSON.
// dir = carpeta de datos (DATA_DIR). Sin dir todo queda solo en memoria (pruebas).
// pedidos.json se escribe al instante (es lo que el dueño no puede perder);
// sessions.json se escribe agrupado cada 300 ms (si se pierde, el cliente solo vuelve a empezar).
// Pedidos cerrados con más de archivoDias pasan a archivo/pedidos-AAAA-MM.json, así pedidos.json no crece
// para siempre; resumen.json guarda el último número y las faltas ("No vino") de lo archivado.
// Con DATA_KEY los archivos quedan cifrados (cifrado.js).
const fs = require("fs");
const path = require("path");
const { leerJSON, escribirJSON } = require("./cifrado");

const ABIERTOS = ["por_pagar", "nuevo", "cocina"];
const tel = t => String(t || "").replace(/\D/g, "");

function createStore(dir, { ttlHours = 24, archivoDias = 30, now = () => Date.now(), cifra = null } = {}) {
  const f = dir ? { pedidos: path.join(dir, "pedidos.json"), sessions: path.join(dir, "sessions.json"), resumen: path.join(dir, "resumen.json"), archivo: path.join(dir, "archivo") } : null;
  const read = (file, empty) => leerJSON(file, empty, cifra);
  const write = (file, data) => escribirJSON(file, data, cifra, 1);

  const pedidos = f ? read(f.pedidos, []) : [];
  const sessions = new Map(Object.entries(f ? read(f.sessions, {}) : {}));
  // next order number: global, so two customers never get the same PED number
  const resumen = { seq: 0, faltas: {}, ...(f ? read(f.resumen, {}) : {}) };
  let seq = pedidos.reduce((m, l) => Math.max(m, +String(l.n || "").replace(/\D/g, "") || 0), Math.max(1000, resumen.seq));
  let timer = null, archivadoEl = 0;

  // move closed orders older than archivoDias to one file per month (at most once an hour)
  function archivar() {
    if (!f || now() - archivadoEl < 3600e3) return;
    archivadoEl = now();
    const limite = now() - archivoDias * 86400e3;
    const viejos = pedidos.filter(p => !ABIERTOS.includes(p.estado) && new Date(p.fecha).getTime() < limite);
    if (!viejos.length) return;
    fs.mkdirSync(f.archivo, { recursive: true });
    const porMes = {};
    for (const p of viejos) (porMes[String(p.fecha).slice(0, 7)] ||= []).push(p);
    for (const [mes, ls] of Object.entries(porMes)) {
      const file = path.join(f.archivo, `pedidos-${mes}.json`);
      write(file, read(file, []).concat(ls));
    }
    for (const p of viejos) if (p.estado === "no_vino") resumen.faltas[tel(p.tel)] = (resumen.faltas[tel(p.tel)] || 0) + 1;
    resumen.seq = seq;
    write(f.resumen, resumen);
    const quedan = pedidos.filter(p => !viejos.includes(p));
    pedidos.length = 0; pedidos.push(...quedan);
  }

  function flush() {
    clearTimeout(timer); timer = null;
    if (!f) return;
    fs.mkdirSync(dir, { recursive: true });
    const old = Date.now() - ttlHours * 2 * 3600e3;          // drop conversations idle for two TTLs
    for (const [k, v] of sessions) if ((v.updated || 0) < old) sessions.delete(k);
    write(f.sessions, Object.fromEntries(sessions));
    archivar();
    write(f.pedidos, pedidos);
  }
  const later = () => { if (f && !timer) timer = setTimeout(flush, 300); };

  return {
    pedidos,
    get seq() { return seq; },
    set seq(n) { seq = Math.max(seq, n); },
    // a conversation idle longer than the TTL starts over with a greeting
    getSession(key) {
      const s = sessions.get(key);
      if (s && Date.now() - (s.updated || 0) > ttlHours * 3600e3) { sessions.delete(key); return null; }
      return s || null;
    },
    setSession(key, s) { s.updated = Date.now(); sessions.set(key, s); later(); },
    deleteSession(key) { sessions.delete(key); later(); },
    addPedido(p) { pedidos.push(p); flush(); return p; },
    getPedido: n => pedidos.find(p => p.n === n) || null,
    // "No vino" of this number, counting the archived months too
    faltas: t => (resumen.faltas[tel(t)] || 0) + pedidos.filter(p => p.estado === "no_vino" && tel(p.tel) === tel(t)).length,
    updatePedido(n, cambios) { const p = pedidos.find(x => x.n === n); if (!p) return null; Object.assign(p, cambios); flush(); return p; },
    flush,
  };
}

module.exports = { createStore };
