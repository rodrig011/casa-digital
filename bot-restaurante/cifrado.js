// Cifrado de los datos en el disco (DATA_KEY): pedidos, clientes, conversaciones, usuarios y bitácora.
//
// Cada archivo se guarda con AES-256-GCM: sin la llave nadie lo puede leer, y si alguien cambia un byte
// el servidor lo nota y no lo usa. La llave vive solo en la configuración del servidor (Render la genera),
// nunca en el repositorio ni en el disco donde están los datos. Si se pierde la llave, se pierden los datos:
// guarde una copia en un lugar seguro (gestor de contraseñas).
//
// Los archivos viejos sin cifrar se siguen leyendo y quedan cifrados la próxima vez que se escriben.
const crypto = require("crypto");
const fs = require("fs");

const PREFIJO = "cd1:";

// any text works as DATA_KEY (Render's generated value is base64); it is turned into 32 bytes
function createCifra(llave) {
  if (!llave) return null;
  const k = crypto.createHash("sha256").update(String(llave)).digest();
  return {
    cifrar(texto) {
      const iv = crypto.randomBytes(12);
      const c = crypto.createCipheriv("aes-256-gcm", k, iv);
      const datos = Buffer.concat([c.update(String(texto), "utf8"), c.final()]);
      return PREFIJO + Buffer.concat([iv, c.getAuthTag(), datos]).toString("base64");
    },
    descifrar(texto) {
      const b = Buffer.from(String(texto).slice(PREFIJO.length), "base64");
      const d = crypto.createDecipheriv("aes-256-gcm", k, b.subarray(0, 12));
      d.setAuthTag(b.subarray(12, 28));
      return Buffer.concat([d.update(b.subarray(28)), d.final()]).toString("utf8");
    },
  };
}

const cifrado = t => String(t).startsWith(PREFIJO);

// a JSON file, encrypted when there is a key. A file that is encrypted but cannot be opened
// (wrong or missing key, or tampered) throws: better to stop than to start over with empty data.
function leerJSON(file, vacio, cifra) {
  let t;
  try { t = fs.readFileSync(file, "utf8"); } catch { return vacio; }
  if (cifrado(t)) {
    if (!cifra) throw new Error(`${file} está cifrado y falta DATA_KEY`);
    try { t = cifra.descifrar(t); } catch { throw new Error(`${file} no se pudo abrir: DATA_KEY no es la correcta o el archivo fue alterado`); }
  }
  try { return JSON.parse(t); } catch { return vacio; }
}
function escribirJSON(file, data, cifra, espacios) {
  const t = JSON.stringify(data, null, espacios);
  const tmp = file + ".tmp";
  fs.writeFileSync(tmp, cifra ? cifra.cifrar(t) : t, { mode: 0o600 });
  fs.renameSync(tmp, file);
}

module.exports = { createCifra, leerJSON, escribirJSON, cifrado, PREFIJO };
