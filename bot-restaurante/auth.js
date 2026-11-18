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
const express = require("express");
const fs = require("fs");
const path = require("path");
const { leerJSON, escribirJSON } = require("./cifrado");

const N = 16384, R = 8, P = 1, LEN = 64;     // scrypt: ~50 ms por intento, 16 MB de memoria
const HORAS = 12;
const COOKIE = "cd_panel";
const MIN_CLAVE = 10;
const PASO = "cd_paso", EQUIPO = "cd_equipo", GOOGLE = "cd_google";
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
    for (const u of parseEnv(env)) if (!(m.get(u.correo) || {}).cambiada) m.set(u.correo, { ...u, origen: "entorno" });   // la variable manda, salvo que la persona ya cambió su contraseña en el panel
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
    // the person changes their own password from the panel; it is kept in usuarios.json and wins over PANEL_USUARIOS
    async cambiarClave(correo, clave) {
      correo = normCorreo(correo);
      const antes = todos().get(correo);
      if (!antes) throw new Error("Usuario desconocido.");
      if (String(clave || "").length < MIN_CLAVE) throw new Error(`La contraseña nueva necesita al menos ${MIN_CLAVE} caracteres.`);
      if (!file) throw new Error("Falta DATA_DIR para guardar la contraseña.");
      const us = leerArchivo().filter(u => normCorreo(u.correo) !== correo);
      const u = { correo, nombre: antes.nombre, hash: await hashClave(clave), whatsapp: antes.whatsapp || "", creado: antes.creado || new Date().toISOString(), cambiada: new Date().toISOString() };
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
function paginaEntrar({ error = "", correo = "", aviso = "", marca = "el restaurante", color = "#C8102E", logo = "", paso = null, google = false } = {}) {
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Entrar · Panel ${esc(marca)}</title><meta name="theme-color" content="#F3F3F3">
<style>
:root{--bg:#F3F3F3;--band:#B0C4DF;--card:#fff;--line:#E5E5E5;--line2:#C9C9C9;--tx:#181818;--tx2:#444;--tx3:#706E6B;--brand:#0176D3;--brand-d:#014486;--red:#BA0517;--red-bg:#FEDED8;--ok-bg:#EEF4FF;color-scheme:light;}
@media (prefers-color-scheme:dark){:root{--bg:#1B1B1B;--band:#16325C;--card:#242424;--line:#3A3A3A;--line2:#4A4A4A;--tx:#F3F3F3;--tx2:#C9C9C9;--tx3:#A0A0A0;--brand:#1B96FF;--brand-d:#78B0FD;--red:#FE5C4C;--red-bg:#4A1410;--ok-bg:#0B2A4E;color-scheme:dark;}}
*{box-sizing:border-box}body{margin:0;min-height:100svh;display:grid;place-items:center;background:linear-gradient(var(--band) 0 220px,var(--bg) 220px);color:var(--tx);font:400 14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;padding:16px;-webkit-font-smoothing:antialiased}
main{width:min(400px,100%);min-width:0}
.brand{display:flex;align-items:center;gap:10px;margin:0 0 16px;font-size:16px;font-weight:700}.brand i{width:36px;height:36px;border-radius:4px;display:grid;place-items:center;color:#fff;font-style:normal;font-size:16px;background:${esc(color)}}.brand img{width:44px;height:44px;border-radius:50%;flex:none}.brand small{display:block;font-weight:400;font-size:12px;color:var(--tx2)}
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
.o{display:flex;align-items:center;gap:10px;color:var(--tx3);font-size:12px}.o::before,.o::after{content:"";flex:1;height:1px;background:var(--line)}
a.g{height:40px;display:flex;align-items:center;justify-content:center;gap:10px;border:1px solid var(--line2);border-radius:4px;color:var(--tx);text-decoration:none;font-weight:600;background:var(--card)}a.g:hover{background:var(--bg)}
.candado{display:flex;align-items:center;gap:6px;justify-content:center;color:var(--tx3);font-size:12px;margin-top:10px}
</style></head><body><main>
<div class="brand">${logo ? `<img src="${esc(logo)}" alt="">` : `<i>${esc(String(marca).trim()[0] || "?").toUpperCase()}</i>`}<div>${esc(marca)}<small>Panel del dueño · Casa Digital</small></div></div>
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
${google ? `<div class="o"><span>o</span></div><a class="g" href="/panel/google"><svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/><path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg>Entrar con Google</a>` : ""}
</form>
<small class="pie">¿Olvidó su contraseña? Pídale al dueño que se la cambie.</small>`}
<div class="candado"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>Conexión cifrada · Casa Digital</div>
</main></body></html>`;
}

// mounts /panel, /panel/entrar, /panel/codigo, /panel/salir and /panel/yo on an express app
// (the brand color can be dark red; it is only used for the button and the focus ring)
// enviarCodigo(whatsapp, codigo) -> true if it went out; without it nobody gets the second step.
// bitacora(evento, datos) writes down every login, failed try and logout.
function montarPanel(app, { secret, usuarios, archivoPanel, archivoSesiones = null, marca, color, logo = "", log = console.log, freno = createFreno(), enviarCodigo = null, bitacora = () => {}, google = null, fetch: f = globalThis.fetch }) {
  const conGoogle = !!(google && google.id && google.secreto);
  const pagina = o => paginaEntrar({ marca, color, logo, google: conGoogle, ...o });
  const ses = secret ? createSesiones(secret, HORAS, { file: archivoSesiones }) : null;
  const sGoogle = secret ? createSello(secret, "google") : null;
  const sPaso = secret ? createSello(secret, "paso") : null, sEquipo = secret ? createSello(secret, "equipo") : null;
  const codigos = new Map();          // pending second steps: id -> { hash of the code, wrong tries }
  const seguro = res => res.set({ "Cache-Control": "no-store", "X-Frame-Options": "DENY", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "same-origin" });
  const usuarioDe = req => ses ? ses.leer(cookies(req)[COOKIE], usuarios) : null;
  // the Google return is a cross-site navigation: its one-use state cookie must be Lax so the browser sends it back
  const galleta = (req, res, nombre, v, maxAge) => res.append("Set-Cookie", `${nombre}=${v}; Path=/; HttpOnly; SameSite=${nombre === GOOGLE ? "Lax" : "Strict"}; Max-Age=${maxAge}${req.secure ? "; Secure" : ""}`);
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
    // after Google, a redirect would still count as cross-site and the Strict cookie would not go: this page moves on from our own site
    if (como === "Google") return res.type("html").send(`<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/panel"><title>Entrando…</title><p style="font:14px system-ui;text-align:center;margin-top:40vh">Entrando al panel…</p>`);
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
  // Entrar con Google: solo los correos que ya son usuarios del panel. Google ya pide su propia verificación,
  // así que no se manda el código de WhatsApp. Necesita GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET.
  const vuelta = req => `${google && google.base || `${req.protocol}://${req.get("host")}`}/panel/google/vuelta`;
  app.get("/panel/google", (req, res) => {
    if (sinConfig(req, res)) return;
    seguro(res);
    if (!conGoogle) return res.redirect(303, "/panel/entrar");
    const n = b64(crypto.randomBytes(16));
    galleta(req, res, GOOGLE, sGoogle.crear({ n, x: Date.now() + 10 * 6e4 }), 600);
    const q = new URLSearchParams({ client_id: google.id, redirect_uri: vuelta(req), response_type: "code", scope: "openid email", state: n, prompt: "select_account" });
    res.redirect(303, "https://accounts.google.com/o/oauth2/v2/auth?" + q);
  });
  app.get("/panel/google/vuelta", async (req, res) => {
    if (sinConfig(req, res)) return;
    seguro(res);
    const mal = (error, correo = "") => res.status(401).type("html").send(pagina({ error, correo }));
    if (!conGoogle) return res.redirect(303, "/panel/entrar");
    const d = sGoogle.abrir(cookies(req)[GOOGLE]);
    galleta(req, res, GOOGLE, "", 0);
    if (!d || !req.query.state || req.query.state !== d.n || !req.query.code) return mal("No se pudo entrar con Google. Vuelva a intentar.");
    if (freno.bloqueado("i:" + req.ip)) return res.status(429).type("html").send(pagina({ error: "Demasiados intentos. Espere 15 minutos y vuelva a probar." }));
    let datos;
    try {
      const r = await f("https://oauth2.googleapis.com/token", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ code: String(req.query.code), client_id: google.id, client_secret: google.secreto, redirect_uri: vuelta(req), grant_type: "authorization_code" }) });
      const j = await r.json();
      if (!r.ok || !j.id_token) throw new Error(j.error_description || j.error || `Google ${r.status}`);
      // the token comes straight from Google over HTTPS, so its content can be read without checking the signature
      datos = JSON.parse(Buffer.from(String(j.id_token).split(".")[1], "base64url").toString("utf8"));
    } catch (e) { log(`[panel] Google: ${e.message}`); return mal("Google no respondió. Vuelva a intentar."); }
    const correo = normCorreo(datos.email);
    const valido = datos.aud === google.id && ["https://accounts.google.com", "accounts.google.com"].includes(datos.iss) && datos.email_verified === true && +datos.exp * 1000 > Date.now();
    const u = valido ? usuarios.get(correo) : null;
    if (!u) { freno.fallo("i:" + req.ip); log(`[panel] Google sin acceso ${correo} ${req.ip}`); bitacora("fallo", { correo, como: "Google", ...quien(req) }); return mal(`El correo ${correo || "de Google"} no tiene acceso a este panel. Pídale al dueño que lo agregue.`, correo); }
    abrirSesion(req, res, u, "Google");
  });
  // change my own password (asks the current one); the session is renewed so the person stays in
  app.post("/panel/clave", express.json({ limit: "2kb" }), async (req, res) => {
    if (sinConfig(req, res)) return;
    seguro(res);
    if (!mismoSitio(req)) return res.status(403).json({ error: "Origen no permitido" });
    const u = usuarioDe(req);
    if (!u) return res.status(401).json({ error: "sin sesión" });
    const { actual = "", nueva = "" } = req.body || {};
    const ki = "i:" + req.ip, kc = "c:" + u.correo;
    if (freno.bloqueado(kc, ki)) return res.status(429).json({ error: "Demasiados intentos. Espere 15 minutos." });
    if (!(await verificarClave(String(actual), u.hash))) { freno.fallo(kc, ki); bitacora("fallo", { correo: u.correo, como: "cambio de contraseña", ...quien(req) }); return res.status(401).json({ error: "La contraseña actual no es esa." }); }
    if (String(nueva) === String(actual)) return res.status(400).json({ error: "La contraseña nueva tiene que ser distinta." });
    let n;
    try { n = await usuarios.cambiarClave(u.correo, String(nueva)); } catch (e) { return res.status(400).json({ error: e.message }); }
    ponerCookie(req, res, ses.crear(n), HORAS * 3600);
    log(`[panel] ${u.correo} cambió su contraseña`);
    bitacora("clave", { correo: u.correo, ...quien(req) });
    res.json({ ok: true });
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
