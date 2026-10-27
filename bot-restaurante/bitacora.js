// Bitácora del panel: quién entró, quién falló la contraseña, quién salió y quién cambió cada pedido.
// Se guarda en DATA_DIR/bitacora.log, una línea por evento, cifrada con DATA_KEY si la hay.
// Solo se agregan líneas; cuando pasa de 5,000 se dejan las últimas 3,000. El panel la muestra en Seguridad.
const fs = require("fs");
const path = require("path");
const { cifrado } = require("./cifrado");

const MAX = 5000, QUEDAN = 3000;

function createBitacora({ dir = null, cifra = null, now = () => new Date(), log = () => {} } = {}) {
  const file = dir ? path.join(dir, "bitacora.log") : null;
  const memoria = [];
  const linea = e => { const t = JSON.stringify(e); return cifra ? cifra.cifrar(t) : t; };
  const abrir = l => { try { return JSON.parse(cifrado(l) ? cifra.descifrar(l) : l); } catch { return null; } };
  const leer = () => {
    if (!file) return memoria.slice();
    let t; try { t = fs.readFileSync(file, "utf8"); } catch { return []; }
    return t.split("\n").filter(Boolean).map(abrir).filter(Boolean);
  };
  let lineas = file ? leer().length : 0;

  function anotar(evento, datos = {}) {
    const e = { en: now().toISOString(), evento, ...datos };
    if (!file) { memoria.push(e); if (memoria.length > MAX) memoria.splice(0, memoria.length - QUEDAN); return e; }
    try {
      fs.mkdirSync(dir, { recursive: true });
      fs.appendFileSync(file, linea(e) + "\n", { mode: 0o600 });
      if (++lineas > MAX) {
        const resto = leer().slice(-QUEDAN);
        fs.writeFileSync(file + ".tmp", resto.map(linea).join("\n") + "\n", { mode: 0o600 });
        fs.renameSync(file + ".tmp", file);
        lineas = resto.length;
      }
    } catch (err) { log(`[bitácora] no se pudo guardar: ${err.message}`); }
    return e;
  }

  // newest first
  const ultimos = (n = 200) => leer().slice(-n).reverse();
  return { anotar, ultimos };
}

module.exports = { createBitacora };
