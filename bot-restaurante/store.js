// Memoria del bot: conversaciones en curso y pedidos, guardados en archivos JSON.
// dir = carpeta de datos (DATA_DIR). Sin dir todo queda solo en memoria (pruebas).
// pedidos.json se escribe al instante (es lo que el dueño no puede perder);
// sessions.json se escribe agrupado cada 300 ms (si se pierde, el cliente solo vuelve a empezar).
const fs = require("fs");
const path = require("path");

function createStore(dir, { ttlHours = 24 } = {}) {
  const f = dir ? { pedidos: path.join(dir, "pedidos.json"), sessions: path.join(dir, "sessions.json") } : null;
  const read = (file, empty) => { try { return JSON.parse(fs.readFileSync(file, "utf8")); } catch { return empty; } };
  const write = (file, data) => { const tmp = file + ".tmp"; fs.writeFileSync(tmp, JSON.stringify(data, null, 1)); fs.renameSync(tmp, file); };

  const pedidos = f ? read(f.pedidos, []) : [];
  const sessions = new Map(Object.entries(f ? read(f.sessions, {}) : {}));
  // next order number: global, so two customers never get the same PED number
  let seq = pedidos.reduce((m, l) => Math.max(m, +String(l.n || "").replace(/\D/g, "") || 0), 1000);
  let timer = null;

  function flush() {
    clearTimeout(timer); timer = null;
    if (!f) return;
    fs.mkdirSync(dir, { recursive: true });
    const old = Date.now() - ttlHours * 2 * 3600e3;          // drop conversations idle for two TTLs
    for (const [k, v] of sessions) if ((v.updated || 0) < old) sessions.delete(k);
    write(f.sessions, Object.fromEntries(sessions));
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
    updatePedido(n, cambios) { const p = pedidos.find(x => x.n === n); if (!p) return null; Object.assign(p, cambios); flush(); return p; },
    flush,
  };
}

module.exports = { createStore };
