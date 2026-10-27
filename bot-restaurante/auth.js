// Bot de restaurante · acceso al panel del dueño con correo y contraseña.
//
// Solo entran los correos autorizados. Se cargan de dos lugares (se suman):
//   1. PANEL_USUARIOS (variable de entorno): una línea por persona, "correo|Nombre|hash|WhatsApp"
//   2. DATA_DIR/usuarios.json, que maneja `npm run usuario -- agregar correo "Nombre" 504XXXXXXXX`
// Las contraseñas nunca se guardan: solo su hash scrypt. La sesión es una cookie firmada con
// PANEL_SECRET (HttpOnly, SameSite=Strict, Secure en https) que dura 12 horas. Si se cambia la
// contraseña o se quita a la persona, su sesión deja de valer. Sin PANEL_SECRET el panel no abre.
//
// Segundo paso: si la persona tiene WhatsApp registrado, después de la contraseña le llega un código
// de 6 números que vence en 5 minutos. Con "Recordar este teléfono" no se lo vuelve a pedir en ese
// teléfono por 30 días (cambiar la contraseña también borra eso).
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { leerJSON, escribirJSON } = require("./cifrado");

const N = 16384, R = 8, P = 1, LEN = 64;     // scrypt: ~50 ms por intento, 16 MB de memoria
const HORAS = 12;
const COOKIE = "cd_panel";
const MIN_CLAVE = 10;
const PASO = "cd_paso", EQUIPO = "cd_equipo";
const MIN_CODIGO = 5, DIAS_EQUIPO = 30, INTENTOS_CODIGO = 5;

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
// a Honduran number may come without the country code
const normWa = n => { const d = String(n || "").replace(/\D/g, ""); return d.length === 8 ? "504" + d : d.length >= 10 ? d : ""; };

function parseEnv(txt) {
  return String(txt || "").split(/[\n;]+/).map(l => l.trim()).filter(Boolean).map(l => {
    const [correo, nombre, hash, whatsapp] = l.split("|").map(x => x.trim());
    return { correo: normCorreo(correo), nombre: nombre || correo, hash, whatsapp: normWa(whatsapp) };
  }).filter(u => valido(u.correo) && u.hash);
}

function createUsuarios({ env = "", file = null, cifra = null } = {}) {
  const leerArchivo = () => { if (!file) return []; const us = leerJSON(file, [], cifra); return Array.isArray(us) ? us : []; };
  const guardar = us => { fs.mkdirSync(path.dirname(file), { recursive: true }); escribirJSON(file, us, cifra, 2); };
  const todos = () => {
    const m = new Map();
    for (const u of leerArchivo()) m.set(normCorreo(u.correo), { ...u, correo: normCorreo(u.correo), origen: "archivo" });
    for (const u of parseEnv(env)) m.set(u.correo, { ...u, origen: "entorno" });   // la variable manda
    return m;
  };
  return {
    get: correo => todos().get(normCorreo(correo)) || null,
    lista: () => [...todos().values()],
    async agregar(correo, nombre, clave, whatsapp = "") {
      correo = normCorreo(correo);
      if (!valido(correo)) throw new Error("Ese correo no es válido.");
      if (whatsapp && !normWa(whatsapp)) throw new Error("Ese número de WhatsApp no es válido.");
      if (!file) throw new Error("Falta DATA_DIR para guardar usuarios.json.");
      const hash = await hashClave(clave);
      const us = leerArchivo().filter(u => normCorreo(u.correo) !== correo);
      const u = { correo, nombre: nombre || correo, hash, whatsapp: normWa(whatsapp), creado: new Date().toISOString() };
      us.push(u);
      guardar(us);
      return u;
    },
    quitar(correo) {
      correo = normCorreo(correo);
      if (!file) return false;
      const us = leerArchivo(), resto = us.filter(u => normCorreo(u.correo) !== correo);
      if (resto.length === us.length) return false;
      guardar(resto);
      return true;
    },
  };
}

// ---- signed tokens: one key per use, so a token made for one thing never opens another ----
function createSello(secret, uso) {
  const firmar = s => crypto.createHmac("sha256", secret + ":" + uso).update(s).digest("base64url");
  return {
    crear: d => { const s = b64(JSON.stringify(d)); return s + "." + firmar(s); },
    abrir(token, ahora = Date.now()) {
      const [s, f] = String(token || "").split(".");
      if (!s || !f) return null;
      const a = Buffer.from(f), b = Buffer.from(firmar(s));
      if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
      let d; try { d = JSON.parse(Buffer.from(s, "base64url").toString()); } catch { return null; }
      return d && d.x >= ahora ? d : null;
    },
  };
}
const huella = hash => crypto.createHash("sha256").update(String(hash)).digest("base64url").slice(0, 12);

// ---- sessions: signed cookie, tied to the current password hash ----
// "Salir" also ends the session on the server: its id goes on a closed list (kept in
// DATA_DIR/sesiones-cerradas.json until it would have expired anyway), so a copied cookie stops working too.
function createSesiones(secret, horas = HORAS, { file = null } = {}) {
  const firmar = s => crypto.createHmac("sha256", secret).update(s).digest("base64url");
  const cerradas = new Map();
  if (file) try { for (const [j, x] of Object.entries(JSON.parse(fs.readFileSync(file, "utf8")))) cerradas.set(j, x); } catch {}
  const abrir = (token, ahora) => {
    const [s, f] = String(token || "").split(".");
    if (!s || !f) return null;
    const a = Buffer.from(f), b = Buffer.from(firmar(s));
    if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
    let d; try { d = JSON.parse(Buffer.from(s, "base64url").toString()); } catch { return null; }
    return d && d.j && d.x >= ahora ? d : null;
  };
  return {
    crear(u, ahora = Date.now()) {
      const s = b64(JSON.stringify({ e: u.correo, h: huella(u.hash), j: b64(crypto.randomBytes(12)), x: ahora + horas * 36e5 }));
      return s + "." + firmar(s);
    },
    leer(token, usuarios, ahora = Date.now()) {
      const d = abrir(token, ahora);
      if (!d || cerradas.has(d.j)) return null;
      const u = usuarios.get(d.e);
      if (!u || huella(u.hash) !== d.h) return null;      // removed, or password changed
      return u;
    },
    cerrar(token, ahora = Date.now()) {
      const d = abrir(token, ahora);
      if (!d) return false;
      for (const [j, x] of cerradas) if (x < ahora) cerradas.delete(j);
      cerradas.set(d.j, d.x);
      if (file) try { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, JSON.stringify(Object.fromEntries(cerradas)), { mode: 0o600 }); } catch {}
      return true;
    },
  };
}

// ---- brute force: 5 wrong tries per email and per IP lock that key for 15 minutes ----
function createFreno({ intentos = 5, minutos = 15 } = {}) {
  const m = new Map();
  const v = k => { const e = m.get(k); if (e && e.hasta < Date.now()) { m.delete(k); return null; } return e; };
  return {
    bloqueado: (...ks) => ks.some(k => { const e = v(k); return e && e.n >= intentos; }),
    fallo: (...ks) => {
      if (m.size > 5000) for (const k of [...m.keys()]) v(k);     // many random emails/IPs: drop the expired ones
      ks.forEach(k => { const e = v(k) || { n: 0, hasta: Date.now() + minutos * 6e4 }; e.n++; m.set(k, e); });
    },
    limpiar: (...ks) => ks.forEach(k => m.delete(k)),
  };
}

function cookies(req) {
  return Object.fromEntries(String(req.get("Cookie") || "").split(";").map(c => c.trim().split("=")).filter(p => p[0]).map(([k, ...v]) => [k, decodeURIComponent(v.join("="))]));
}

// ---- the login page (same look as the panel) ----
function paginaEntrar({ error = "", correo = "", aviso = "", marca = "el restaurante", color = "#C8102E", paso = null } = {}) {
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Entrar · Panel ${esc(marca)}</title><meta name="theme-color" content="#F3F3F3">
<style>
:root{--bg:#F3F3F3;--band:#B0C4DF;--card:#fff;--line:#E5E5E5;--line2:#C9C9C9;--tx:#181818;--tx2:#444;--tx3:#706E6B;--brand:#0176D3;--brand-d:#014486;--red:#BA0517;--red-bg:#FEDED8;--ok-bg:#EEF4FF;color-scheme:light;}
@media (prefers-color-scheme:dark){:root{--bg:#1B1B1B;--band:#16325C;--card:#242424;--line:#3A3A3A;--line2:#4A4A4A;--tx:#F3F3F3;--tx2:#C9C9C9;--tx3:#A0A0A0;--brand:#1B96FF;--brand-d:#78B0FD;--red:#FE5C4C;--red-bg:#4A1410;--ok-bg:#0B2A4E;color-scheme:dark;}}
*{box-sizing:border-box}body{margin:0;min-height:100svh;display:grid;place-items:center;background:linear-gradient(var(--band) 0 220px,var(--bg) 220px);color:var(--tx);font:400 14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;padding:16px;-webkit-font-smoothing:antialiased}
main{width:min(400px,100%);min-width:0}
.brand{display:flex;align-items:center;gap:10px;margin:0 0 16px;font-size:16px;font-weight:700}.brand i{width:36px;height:36px;border-radius:4px;display:grid;place-items:center;color:#fff;font-style:normal;font-size:16px;background:${esc(color)}}.brand small{display:block;font-weight:400;font-size:12px;color:var(--tx2)}
form{background:var(--card);border:1px solid var(--line);border-radius:4px;box-shadow:0 2px 2px rgba(0,0,0,.1);padding:24px;display:grid;gap:14px}
h1{margin:0;font-size:18px;font-weight:700}p{margin:0;color:var(--tx3);font-size:13px}
label{display:grid;gap:4px;font-size:12px;color:var(--tx2)}
input{width:100%;min-width:0;height:40px;border-radius:4px;border:1px solid var(--line2);background:var(--card);color:var(--tx);padding:0 12px;font:inherit;font-size:16px}
input:focus{outline:none;border-color:var(--brand);box-shadow:0 0 3px var(--brand)}
button{height:40px;border:1px solid var(--brand);border-radius:4px;background:var(--brand);color:#fff;font:inherit;font-weight:600;cursor:pointer}button:hover{background:var(--brand-d)}
.err{background:var(--red-bg);color:var(--red);border-radius:4px;padding:10px 12px;font-size:13px}
.ok{background:var(--ok-bg);border-radius:4px;padding:10px 12px;font-size:13px}
small.pie{display:block;text-align:center;color:var(--tx3);margin-top:14px;font-size:12px}small.pie a{color:var(--brand)}
input.codigo{font-size:24px;letter-spacing:.4em;text-align:center;font-variant-numeric:tabular-nums}
label.si{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--tx2)}label.si input{flex:none;width:18px;height:18px;margin:0;accent-color:var(--brand)}
.candado{display:flex;align-items:center;gap:6px;justify-content:center;color:var(--tx3);font-size:12px;margin-top:10px}
</style></head><body><main>
<div class="brand"><i>${esc(String(marca).trim()[0] || "?").toUpperCase()}</i><div>${esc(marca)}<small>Panel del dueño · Casa Digital</small></div></div>
${paso ? `<form method="post" action="/panel/codigo" autocomplete="off">
<div><h1>Código de WhatsApp</h1><p>Le mandamos un código de 6 números al WhatsApp que termina en ${esc(paso.final)}. Vence en ${MIN_CODIGO} minutos.</p></div>
${error ? `<div class="err" role="alert">${esc(error)}</div>` : ""}
<label>Código<input class="codigo" name="codigo" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9 ]{6,7}" maxlength="7" required autofocus></label>
<label class="si"><input type="checkbox" name="recordar" value="1" checked>Recordar este teléfono ${DIAS_EQUIPO} días</label>
<button type="submit">Confirmar</button>
</form>
<small class="pie">¿No le llegó? <a href="/panel/entrar">Volver a entrar</a> y le mandamos otro.</small>` : `<form method="post" action="/panel/entrar" autocomplete="on">
<div><h1>Entrar al panel</h1><p>Solo para personas autorizadas por ${esc(marca)}.</p></div>
${error ? `<div class="err" role="alert">${esc(error)}</div>` : ""}${aviso ? `<div class="ok">${esc(aviso)}</div>` : ""}
<label>Correo<input name="correo" type="email" autocomplete="username" required autofocus value="${esc(correo)}"></label>
<label>Contraseña<input name="clave" type="password" autocomplete="current-password" required minlength="1"></label>
<button type="submit">Entrar</button>
</form>
<small class="pie">¿Olvidó su contraseña? Pídale al dueño que se la cambie.</small>`}
<div class="candado"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>Conexión cifrada · Casa Digital</div>
</main></body></html>`;
}

// mounts /panel, /panel/entrar, /panel/codigo, /panel/salir and /panel/yo on an express app
// (the brand color can be dark red; it is only used for the button and the focus ring)
// enviarCodigo(whatsapp, codigo) -> true if it went out; without it nobody gets the second step.
// bitacora(evento, datos) writes down every login, failed try and logout.
function montarPanel(app, { secret, usuarios, archivoPanel, archivoSesiones = null, marca, color, log = console.log, freno = createFreno(), enviarCodigo = null, bitacora = () => {} }) {
  const pagina = o => paginaEntrar({ marca, color, ...o });
  const ses = secret ? createSesiones(secret, HORAS, { file: archivoSesiones }) : null;
  const sPaso = secret ? createSello(secret, "paso") : null, sEquipo = secret ? createSello(secret, "equipo") : null;
  const codigos = new Map();          // pending second steps: id -> { hash of the code, wrong tries }
  const seguro = res => res.set({ "Cache-Control": "no-store", "X-Frame-Options": "DENY", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "same-origin" });
  const usuarioDe = req => ses ? ses.leer(cookies(req)[COOKIE], usuarios) : null;
  const galleta = (req, res, nombre, v, maxAge) => res.append("Set-Cookie", `${nombre}=${v}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${maxAge}${req.secure ? "; Secure" : ""}`);
  const ponerCookie = (req, res, v, maxAge) => galleta(req, res, COOKIE, v, maxAge);
  const sinConfig = (req, res) => { if (ses) return false; seguro(res).status(503).type("text/plain").send("El panel está cerrado: falta PANEL_SECRET en la configuración."); return true; };
  const mismoSitio = req => { const o = req.get("Origin"); return !o || o === `${req.protocol}://${req.get("host")}`; };
  const quien = req => ({ ip: req.ip, equipo: String(req.get("User-Agent") || "").slice(0, 120) });
  const resumenCodigo = c => crypto.createHash("sha256").update(c).digest("base64url");
  const equipoDe = (req, u) => { const d = sEquipo.abrir(cookies(req)[EQUIPO]); return !!d && d.e === u.correo && d.h === huella(u.hash); };
  const pasoDe = req => {
    const d = sPaso.abrir(cookies(req)[PASO]);
    const u = d && codigos.has(d.j) ? usuarios.get(d.e) : null;
    return u && huella(u.hash) === d.h ? { d, u } : null;
  };
  function abrirSesion(req, res, u, como) {
    ponerCookie(req, res, ses.crear(u), HORAS * 3600);
    log(`[panel] entró ${u.correo}`);
    bitacora("entro", { correo: u.correo, como, ...quien(req) });
    res.redirect(303, "/panel");
  }

  app.get("/panel", (req, res) => {
    if (sinConfig(req, res)) return;
    const u = usuarioDe(req);
    if (!u) return seguro(res).redirect(303, "/panel/entrar");
    seguro(res).type("html").sendFile(archivoPanel);
  });
  app.get("/panel/entrar", (req, res) => {
    if (sinConfig(req, res)) return;
    if (usuarioDe(req)) return seguro(res).redirect(303, "/panel");
    seguro(res).type("html").send(pagina({ aviso: req.query.salio ? "Salió del panel." : "" }));
  });
  app.post("/panel/entrar", async (req, res) => {
    if (sinConfig(req, res)) return;
    seguro(res);
    // login form must come from this same site
    if (!mismoSitio(req)) return res.status(403).type("text/plain").send("Origen no permitido");
    const correo = normCorreo((req.body || {}).correo), clave = String((req.body || {}).clave || "");
    const kc = "c:" + correo, ki = "i:" + req.ip;
    if (freno.bloqueado(kc, ki)) { log(`[panel] bloqueado ${correo} ${req.ip}`); bitacora("bloqueado", { correo, ...quien(req) }); return res.status(429).type("html").send(pagina({ correo, error: "Demasiados intentos. Espere 15 minutos y vuelva a probar." })); }
    const u = usuarios.get(correo);
    const ok = await verificarClave(clave, u ? u.hash : FALSO) && !!u;
    if (!ok) { freno.fallo(kc, ki); log(`[panel] intento fallido ${correo} ${req.ip}`); bitacora("fallo", { correo, ...quien(req) }); return res.status(401).type("html").send(pagina({ correo, error: "Correo o contraseña incorrectos." })); }
    freno.limpiar(kc);
    if (!u.whatsapp || !enviarCodigo || equipoDe(req, u)) return abrirSesion(req, res, u, u.whatsapp && enviarCodigo ? "equipo recordado" : "contraseña");
    // second step: a 6-digit code to the person's WhatsApp
    const codigo = String(crypto.randomInt(0, 1e6)).padStart(6, "0");
    const j = b64(crypto.randomBytes(12));
    for (const [k, c] of codigos) if (c.x < Date.now()) codigos.delete(k);
    codigos.set(j, { h: resumenCodigo(codigo), n: 0, x: Date.now() + MIN_CODIGO * 6e4 });
    const salio = await Promise.resolve(enviarCodigo(u.whatsapp, codigo)).catch(e => { log(`[panel] código no salió: ${e.message}`); return false; });
    if (!salio) { codigos.delete(j); bitacora("codigo_no_salio", { correo, ...quien(req) }); return res.status(503).type("html").send(pagina({ correo, error: "No pudimos mandarle el código por WhatsApp. Pruebe otra vez en un momento." })); }
    galleta(req, res, PASO, sPaso.crear({ e: u.correo, h: huella(u.hash), j, x: Date.now() + MIN_CODIGO * 6e4 }), MIN_CODIGO * 60);
    bitacora("codigo_enviado", { correo, ...quien(req) });
    res.type("html").send(pagina({ paso: { final: u.whatsapp.slice(-4) } }));
  });
  app.post("/panel/codigo", (req, res) => {
    if (sinConfig(req, res)) return;
    seguro(res);
    if (!mismoSitio(req)) return res.status(403).type("text/plain").send("Origen no permitido");
    const p = pasoDe(req);
    if (!p) return res.status(401).type("html").send(pagina({ error: "El código venció. Entre otra vez y le mandamos uno nuevo." }));
    const { d, u } = p, c = codigos.get(d.j);
    const dado = Buffer.from(resumenCodigo(String((req.body || {}).codigo || "").replace(/\D/g, ""))), bueno = Buffer.from(c.h);
    if (!crypto.timingSafeEqual(dado, bueno)) {
      c.n++;
      freno.fallo("i:" + req.ip);
      bitacora("codigo_malo", { correo: u.correo, ...quien(req) });
      if (c.n >= INTENTOS_CODIGO) { codigos.delete(d.j); galleta(req, res, PASO, "", 0); return res.status(401).type("html").send(pagina({ correo: u.correo, error: "Demasiados códigos equivocados. Entre otra vez y le mandamos uno nuevo." })); }
      return res.status(401).type("html").send(pagina({ paso: { final: u.whatsapp.slice(-4) }, error: "Ese código no es. Revise el último mensaje de WhatsApp." }));
    }
    codigos.delete(d.j);
    galleta(req, res, PASO, "", 0);
    if ((req.body || {}).recordar) galleta(req, res, EQUIPO, sEquipo.crear({ e: u.correo, h: huella(u.hash), x: Date.now() + DIAS_EQUIPO * 864e5 }), DIAS_EQUIPO * 86400);
    abrirSesion(req, res, u, "código de WhatsApp");
  });
  app.all("/panel/salir", (req, res) => {
    const u = usuarioDe(req);
    if (ses) ses.cerrar(cookies(req)[COOKIE]);
    if (u) bitacora("salio", { correo: u.correo, ...quien(req) });
    ponerCookie(req, res, "", 0);
    seguro(res).redirect(303, "/panel/entrar?salio=1");
  });
  app.get("/panel/yo", (req, res) => {
    const u = usuarioDe(req);
    if (!u) return seguro(res).status(401).json({ error: "sin sesión" });
    seguro(res).json({ correo: u.correo, nombre: u.nombre });
  });
  return { usuarioDe };
}

module.exports = { normWa, createSello, hashClave, verificarClave, createUsuarios, createSesiones, createFreno, montarPanel, paginaEntrar, MIN_CLAVE, COOKIE };
