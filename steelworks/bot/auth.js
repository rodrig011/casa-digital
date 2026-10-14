// Steel Works · acceso al panel del dueño con correo y contraseña.
//
// Solo entran los correos autorizados. Se cargan de dos lugares (se suman):
//   1. PANEL_USUARIOS (variable de entorno): una línea por persona, "correo|Nombre|hash"
//   2. DATA_DIR/usuarios.json, que maneja `npm run usuario -- agregar correo "Nombre"`
// Las contraseñas nunca se guardan: solo su hash scrypt. La sesión es una cookie firmada con
// PANEL_SECRET (HttpOnly, SameSite=Strict, Secure en https) que dura 12 horas. Si se cambia la
// contraseña o se quita a la persona, su sesión deja de valer. Sin PANEL_SECRET el panel no abre.
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const N = 16384, R = 8, P = 1, LEN = 64;     // scrypt: ~50 ms por intento, 16 MB de memoria
const HORAS = 12;
const COOKIE = "sw_panel";
const MIN_CLAVE = 10;

const b64 = b => Buffer.from(b).toString("base64url");
const scrypt = (clave, sal, n = N, r = R, p = P) => new Promise((ok, mal) =>
  crypto.scrypt(String(clave).normalize("NFKC"), sal, LEN, { N: n, r, p, maxmem: 64 * 1024 * 1024 }, (e, k) => e ? mal(e) : ok(k)));

async function hashClave(clave) {
  if (String(clave || "").length < MIN_CLAVE) throw new Error(`La contraseña debe tener al menos ${MIN_CLAVE} caracteres.`);
  const sal = crypto.randomBytes(16);
  return `scrypt$${N}$${R}$${P}$${b64(sal)}$${b64(await scrypt(clave, sal))}`;
}
async function verificarClave(clave, hash) {
  const [alg, n, r, p, sal, h] = String(hash || "").split("$");
  if (alg !== "scrypt" || !sal || !h) return false;
  const esperado = Buffer.from(h, "base64url");
  const k = await scrypt(clave, Buffer.from(sal, "base64url"), +n, +r, +p);
  return k.length === esperado.length && crypto.timingSafeEqual(k, esperado);
}
// a hash with a random salt, so a wrong email takes as long as a wrong password
const FALSO = `scrypt$${N}$${R}$${P}$${b64(crypto.randomBytes(16))}$${b64(crypto.randomBytes(LEN))}`;

const normCorreo = c => String(c || "").trim().toLowerCase();
const valido = c => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(c);

function parseEnv(txt) {
  return String(txt || "").split(/[\n;]+/).map(l => l.trim()).filter(Boolean).map(l => {
    const [correo, nombre, hash] = l.split("|").map(x => x.trim());
    return { correo: normCorreo(correo), nombre: nombre || correo, hash };
  }).filter(u => valido(u.correo) && u.hash);
}

function createUsuarios({ env = "", file = null } = {}) {
  const leerArchivo = () => { if (!file) return []; try { return JSON.parse(fs.readFileSync(file, "utf8")); } catch { return []; } };
  const todos = () => {
    const m = new Map();
    for (const u of leerArchivo()) m.set(normCorreo(u.correo), { ...u, correo: normCorreo(u.correo), origen: "archivo" });
    for (const u of parseEnv(env)) m.set(u.correo, { ...u, origen: "entorno" });   // la variable manda
    return m;
  };
  return {
    get: correo => todos().get(normCorreo(correo)) || null,
    lista: () => [...todos().values()],
    async agregar(correo, nombre, clave) {
      correo = normCorreo(correo);
      if (!valido(correo)) throw new Error("Ese correo no es válido.");
      if (!file) throw new Error("Falta DATA_DIR para guardar usuarios.json.");
      const hash = await hashClave(clave);
      const us = leerArchivo().filter(u => normCorreo(u.correo) !== correo);
      us.push({ correo, nombre: nombre || correo, hash, creado: new Date().toISOString() });
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, JSON.stringify(us, null, 2), { mode: 0o600 });
      return { correo, nombre: nombre || correo, hash };
    },
    quitar(correo) {
      correo = normCorreo(correo);
      if (!file) return false;
      const us = leerArchivo(), resto = us.filter(u => normCorreo(u.correo) !== correo);
      if (resto.length === us.length) return false;
      fs.writeFileSync(file, JSON.stringify(resto, null, 2), { mode: 0o600 });
      return true;
    },
  };
}

// ---- sessions: signed cookie, tied to the current password hash ----
function createSesiones(secret, horas = HORAS) {
  const firmar = s => crypto.createHmac("sha256", secret).update(s).digest("base64url");
  const huella = hash => crypto.createHash("sha256").update(String(hash)).digest("base64url").slice(0, 12);
  return {
    crear(u, ahora = Date.now()) {
      const s = b64(JSON.stringify({ e: u.correo, h: huella(u.hash), x: ahora + horas * 36e5 }));
      return s + "." + firmar(s);
    },
    leer(token, usuarios, ahora = Date.now()) {
      const [s, f] = String(token || "").split(".");
      if (!s || !f) return null;
      const a = Buffer.from(f), b = Buffer.from(firmar(s));
      if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
      let d; try { d = JSON.parse(Buffer.from(s, "base64url").toString()); } catch { return null; }
      if (!d || d.x < ahora) return null;
      const u = usuarios.get(d.e);
      if (!u || huella(u.hash) !== d.h) return null;      // removed, or password changed
      return u;
    },
  };
}

// ---- brute force: 5 wrong tries per email and per IP lock that key for 15 minutes ----
function createFreno({ intentos = 5, minutos = 15 } = {}) {
  const m = new Map();
  const v = k => { const e = m.get(k); if (e && e.hasta < Date.now()) { m.delete(k); return null; } return e; };
  return {
    bloqueado: (...ks) => ks.some(k => { const e = v(k); return e && e.n >= intentos; }),
    fallo: (...ks) => ks.forEach(k => { const e = v(k) || { n: 0, hasta: Date.now() + minutos * 6e4 }; e.n++; m.set(k, e); }),
    limpiar: (...ks) => ks.forEach(k => m.delete(k)),
  };
}

function cookies(req) {
  return Object.fromEntries(String(req.get("Cookie") || "").split(";").map(c => c.trim().split("=")).filter(p => p[0]).map(([k, ...v]) => [k, decodeURIComponent(v.join("="))]));
}

// ---- the login page (same look as the panel) ----
function paginaEntrar({ error = "", correo = "", aviso = "" } = {}) {
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Entrar · Panel Steel Works</title><meta name="theme-color" content="#F4F3F0">
<style>
:root{--bg:#F4F3F0;--card:#fff;--line:#E6E3DE;--line2:#D6D2CB;--tx:#1B1C1D;--tx2:#5C6166;--tx3:#868B90;--ember:#D9601A;--red:#C23A2B;--red-bg:#FBE7E4;color-scheme:light;}
@media (prefers-color-scheme:dark){:root{--bg:#111213;--card:#1A1C1E;--line:#2A2D30;--line2:#383C40;--tx:#ECEAE6;--tx2:#A4A9AE;--tx3:#7A8085;--ember:#F07A35;--red:#F0796B;--red-bg:#3A1C18;color-scheme:dark;}}
*{box-sizing:border-box}body{margin:0;min-height:100svh;display:grid;place-items:center;background:var(--bg);color:var(--tx);font:400 15px/1.5 "Helvetica Neue",Arial,sans-serif;padding:16px;-webkit-font-smoothing:antialiased}
main{width:min(400px,100%)}.brand{margin:0 0 22px}.brand img{height:36px;width:auto;display:block}.brand .d{display:none}@media (prefers-color-scheme:dark){.brand .l{display:none}.brand .d{display:block}}
form{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:28px;display:grid;gap:16px}
h1{margin:0;font-size:22px;font-weight:600;letter-spacing:-.01em}p{margin:0;color:var(--tx2)}
label{display:grid;gap:6px;font-size:13px;font-weight:600;color:var(--tx2)}
input{height:44px;border-radius:10px;border:1px solid var(--line2);background:var(--card);color:var(--tx);padding:0 12px;font:inherit;font-size:16px}
input:focus{outline:none;border-color:var(--ember);box-shadow:0 0 0 3px color-mix(in srgb,var(--ember) 18%,transparent)}
button{height:46px;border:0;border-radius:10px;background:var(--ember);color:#fff;font:inherit;font-weight:700;cursor:pointer;transition:transform .15s ease}button:active{transform:scale(.98)}
.err{background:var(--red-bg);color:var(--red);border-radius:10px;padding:10px 12px;font-size:14px;font-weight:500}
.ok{background:color-mix(in srgb,var(--ember) 12%,transparent);border-radius:10px;padding:10px 12px;font-size:14px}
small{display:block;text-align:center;color:var(--tx3);margin-top:16px;font-size:12px}
</style></head><body><main>
<div class="brand"><img class="l" src="/panel/logo-naranja-sobre-blanco.svg" alt="Steel Works Honduras" width="140" height="36"><img class="d" src="/panel/logo-naranja-sobre-negro.svg" alt="Steel Works Honduras" width="140" height="36"></div>
<form method="post" action="/panel/entrar" autocomplete="on">
<div><h1>Entrar al panel</h1><p>Solo para personas autorizadas por Steel Works.</p></div>
${error ? `<div class="err" role="alert">${esc(error)}</div>` : ""}${aviso ? `<div class="ok">${esc(aviso)}</div>` : ""}
<label>Correo<input name="correo" type="email" autocomplete="username" required autofocus value="${esc(correo)}"></label>
<label>Contraseña<input name="clave" type="password" autocomplete="current-password" required minlength="1"></label>
<button type="submit">Entrar</button>
</form>
<small>¿Olvidó su contraseña? Pídale al dueño que se la cambie.</small>
</main></body></html>`;
}

// mounts /panel, /panel/entrar, /panel/salir and /panel/yo on an express app
function montarPanel(app, { secret, usuarios, archivoPanel, log = console.log, freno = createFreno() }) {
  const ses = secret ? createSesiones(secret) : null;
  const seguro = res => res.set({ "Cache-Control": "no-store", "X-Frame-Options": "DENY", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "same-origin" });
  const usuarioDe = req => ses ? ses.leer(cookies(req)[COOKIE], usuarios) : null;
  const ponerCookie = (req, res, v, maxAge) => res.append("Set-Cookie", `${COOKIE}=${v}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${maxAge}${req.secure ? "; Secure" : ""}`);
  const sinConfig = (req, res) => { if (ses) return false; seguro(res).status(503).type("text/plain").send("El panel está cerrado: falta PANEL_SECRET en la configuración."); return true; };

  app.get("/panel", (req, res) => {
    if (sinConfig(req, res)) return;
    const u = usuarioDe(req);
    if (!u) return seguro(res).redirect(303, "/panel/entrar");
    seguro(res).type("html").sendFile(archivoPanel);
  });
  app.get("/panel/entrar", (req, res) => {
    if (sinConfig(req, res)) return;
    if (usuarioDe(req)) return seguro(res).redirect(303, "/panel");
    seguro(res).type("html").send(paginaEntrar({ aviso: req.query.salio ? "Salió del panel." : "" }));
  });
  app.post("/panel/entrar", async (req, res) => {
    if (sinConfig(req, res)) return;
    seguro(res);
    // login form must come from this same site
    const origen = req.get("Origin");
    if (origen && origen !== `${req.protocol}://${req.get("host")}`) return res.status(403).type("text/plain").send("Origen no permitido");
    const correo = normCorreo((req.body || {}).correo), clave = String((req.body || {}).clave || "");
    const kc = "c:" + correo, ki = "i:" + req.ip;
    if (freno.bloqueado(kc, ki)) { log(`[panel] bloqueado ${correo} ${req.ip}`); return res.status(429).type("html").send(paginaEntrar({ correo, error: "Demasiados intentos. Espere 15 minutos y vuelva a probar." })); }
    const u = usuarios.get(correo);
    const ok = await verificarClave(clave, u ? u.hash : FALSO) && !!u;
    if (!ok) { freno.fallo(kc, ki); log(`[panel] intento fallido ${correo} ${req.ip}`); return res.status(401).type("html").send(paginaEntrar({ correo, error: "Correo o contraseña incorrectos." })); }
    freno.limpiar(kc);
    ponerCookie(req, res, ses.crear(u), HORAS * 3600);
    log(`[panel] entró ${u.correo}`);
    res.redirect(303, "/panel");
  });
  for (const k of ["naranja-sobre-blanco", "naranja-sobre-negro"]) app.get(`/panel/logo-${k}.svg`, (req, res) => res.set("Cache-Control", "public, max-age=86400").type("image/svg+xml").sendFile(path.join(path.dirname(archivoPanel), `logo-${k}.svg`)));
  app.all("/panel/salir", (req, res) => { ponerCookie(req, res, "", 0); seguro(res).redirect(303, "/panel/entrar?salio=1"); });
  app.get("/panel/yo", (req, res) => {
    const u = usuarioDe(req);
    if (!u) return seguro(res).status(401).json({ error: "sin sesión" });
    seguro(res).json({ correo: u.correo, nombre: u.nombre });
  });
  return { usuarioDe };
}

module.exports = { hashClave, verificarClave, createUsuarios, createSesiones, createFreno, montarPanel, paginaEntrar, MIN_CLAVE, COOKIE };
