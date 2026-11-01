// Respaldo de los datos del bot: pedidos (y los meses archivados), números y faltas, usuarios del panel,
// sesiones cerradas y bitácora. Las conversaciones en curso no entran: si se pierden, el cliente vuelve a empezar.
//
// El respaldo es un solo archivo JSON con los archivos tal como están en el disco: con DATA_KEY siguen cifrados,
// así que sin la llave nadie lo puede leer. Guarde la llave aparte (gestor de contraseñas), nunca junto al respaldo.
//
//   node respaldo.js bajar <url-del-bot> [salida.json]       baja el respaldo (pide LEADS_TOKEN en el ambiente)
//   node respaldo.js crear <carpeta-de-datos> [salida.json]  lo arma desde la carpeta (en el servidor)
//   node respaldo.js comprobar <respaldo.json>               lo abre con DATA_KEY y dice qué trae
//   node respaldo.js restaurar <respaldo.json> <carpeta>     lo escribe en una carpeta vacía y comprueba que abre
//
// El servidor lo entrega en GET /api/respaldo (Authorization: Bearer <LEADS_TOKEN>, o la sesión del panel).
const fs = require("fs");
const path = require("path");
const { createCifra, leerJSON } = require("./cifrado");
const { createStore } = require("./store");

const ARCHIVOS = ["pedidos.json", "resumen.json", "usuarios.json", "sesiones-cerradas.json", "bitacora.log"];

function crearRespaldo(dir, now = new Date()) {
  const archivos = {};
  for (const n of ARCHIVOS) { const f = path.join(dir, n); if (fs.existsSync(f)) archivos[n] = fs.readFileSync(f, "utf8"); }
  const arch = path.join(dir, "archivo");
  if (fs.existsSync(arch)) for (const n of fs.readdirSync(arch).filter(x => /^pedidos-\d{4}-\d{2}\.json$/.test(x)).sort()) archivos["archivo/" + n] = fs.readFileSync(path.join(arch, n), "utf8");
  return { respaldo: "casa-digital", version: 1, creado: now.toISOString(), archivos };
}

// opens every file with the key; throws if the key is wrong or a file was altered. Returns what it holds
function comprobar(r, dataKey) {
  if (!r || r.respaldo !== "casa-digital" || r.version !== 1 || typeof r.archivos !== "object") throw new Error("No es un respaldo del bot.");
  const nombres = Object.keys(r.archivos);
  if (nombres.some(n => !(ARCHIVOS.includes(n) || /^archivo\/pedidos-\d{4}-\d{2}\.json$/.test(n)))) throw new Error("El respaldo trae archivos que no son del bot.");
  const tmp = fs.mkdtempSync(path.join(require("os").tmpdir(), "respaldo-"));
  try {
    escribir(r, tmp);
    return abrir(tmp, dataKey, r.creado);
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
}

function escribir(r, dir) {
  for (const [n, t] of Object.entries(r.archivos)) {
    const f = path.join(dir, n);
    fs.mkdirSync(path.dirname(f), { recursive: true });
    fs.writeFileSync(f, t, { mode: 0o600 });
  }
}

function abrir(dir, dataKey, creado) {
  const cifra = createCifra(dataKey);
  const store = createStore(dir, { cifra, archivoDias: 1e6 });         // never archives while checking
  const archivados = fs.existsSync(path.join(dir, "archivo")) ? fs.readdirSync(path.join(dir, "archivo")).reduce((a, n) => a + leerJSON(path.join(dir, "archivo", n), [], cifra).length, 0) : 0;
  const usuarios = Object.keys(leerJSON(path.join(dir, "usuarios.json"), {}, cifra) || {}).length;
  const abiertos = store.pedidos.filter(p => ["por_pagar", "nuevo", "cocina"].includes(p.estado)).length;
  return { creado, pedidos: store.pedidos.length, abiertos, archivados, ultimoNumero: store.seq, usuarios };
}

// restore only into an empty folder (never on top of live data), then open it to prove it works
function restaurar(r, dir, dataKey) {
  const antes = comprobar(r, dataKey);
  if (fs.existsSync(dir) && fs.readdirSync(dir).length) throw new Error(`${dir} no está vacía: restaure en una carpeta nueva y luego cambie DATA_DIR.`);
  fs.mkdirSync(dir, { recursive: true });
  escribir(r, dir);
  const despues = abrir(dir, dataKey, r.creado);
  if (JSON.stringify(antes) !== JSON.stringify(despues)) throw new Error("Lo restaurado no coincide con el respaldo.");
  return despues;
}

const resumenTexto = c => `${c.pedidos} pedidos (${c.abiertos} abiertos), ${c.archivados} archivados, último número ${c.ultimoNumero}, ${c.usuarios} usuario(s) del panel. Respaldo del ${c.creado}.`;

async function main([cmd, a, b]) {
  try { process.loadEnvFile(path.join(__dirname, ".env")); } catch { /* sin .env */ }
  const key = process.env.DATA_KEY || "";
  const hoy = new Date().toISOString().slice(0, 10);
  if (cmd === "crear") {
    const out = b || `respaldo-${hoy}.json`;
    fs.writeFileSync(out, JSON.stringify(crearRespaldo(a)), { mode: 0o600 });
    console.log(`Respaldo guardado en ${out}.`);
  } else if (cmd === "bajar") {
    const token = process.env.LEADS_TOKEN || "";
    if (!a || !token) throw new Error("Uso: LEADS_TOKEN=... node respaldo.js bajar https://su-bot.onrender.com [salida.json]");
    const r = await fetch(a.replace(/\/$/, "") + "/api/respaldo", { headers: { Authorization: "Bearer " + token } });
    if (!r.ok) throw new Error(`El bot contestó ${r.status}.`);
    const out = b || `respaldo-${hoy}.json`;
    fs.writeFileSync(out, await r.text(), { mode: 0o600 });
    console.log(`Respaldo guardado en ${out}.${key ? " " + resumenTexto(comprobar(JSON.parse(fs.readFileSync(out, "utf8")), key)) : " (Sin DATA_KEY no se puede comprobar aquí.)"}`);
  } else if (cmd === "comprobar") {
    console.log("Abre bien: " + resumenTexto(comprobar(JSON.parse(fs.readFileSync(a, "utf8")), key)));
  } else if (cmd === "restaurar") {
    if (!a || !b) throw new Error("Uso: node respaldo.js restaurar respaldo.json carpeta-nueva");
    console.log(`Restaurado en ${b}: ` + resumenTexto(restaurar(JSON.parse(fs.readFileSync(a, "utf8")), b, key)) + "\nAhora apunte DATA_DIR a esa carpeta y reinicie el bot.");
  } else {
    console.log(fs.readFileSync(__filename, "utf8").split("\n").slice(0, 12).join("\n"));
  }
}

if (require.main === module) main(process.argv.slice(2)).catch(e => { console.error("Error: " + e.message); process.exit(1); });
module.exports = { crearRespaldo, comprobar, restaurar };
