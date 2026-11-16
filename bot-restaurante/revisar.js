// Revisa que el servidor quedó bien configurado, sin mostrar ninguna clave.   npm run revisar   (en Render > Shell)
//   npm run revisar -- --en-linea   además pregunta a Meta por el número y a Claude por la clave (no manda mensajes ni gasta)
// Cada línea dice ✓ (bien), ! (funciona pero falta algo) o ✗ (hay que arreglarlo) y qué hacer.
const path = require("path");
const fs = require("fs");
const { cargarNegocio } = require("./negocio");
const { createCifra, leerJSON } = require("./cifrado");

async function revisar(env = process.env, { enLinea = false, fetch: f = globalThis.fetch, anthropic = null } = {}) {
  const out = [];
  const ok = t => out.push(["✓", t]), aviso = (t, haga) => out.push(["!", t, haga]), mal = (t, haga) => out.push(["✗", t, haga]);
  const dig = v => String(v || "").replace(/\D/g, "");
  // 1. el negocio y sus datos privados
  let N = null;
  if (env.NEGOCIO_PRIVADO) { try { JSON.parse(env.NEGOCIO_PRIVADO); } catch { mal("NEGOCIO_PRIVADO no es JSON válido", "Cópielo otra vez completo, desde la primera { hasta la última }."); } }
  try { N = cargarNegocio(env.NEGOCIO || "negocios/ejemplo.json", env.NEGOCIO_PRIVADO || undefined); ok(`Negocio: ${N.nombre} (${N.items.length} productos, ${N.sucursales.length} sucursales)`); }
  catch (e) { mal(`El negocio no carga: ${e.message}`, "Revise NEGOCIO (debe ser negocios/con-sabor-a-pueblo.json) y NEGOCIO_PRIVADO."); }
  if (N) {
    const sinWa = N.sucursales.filter(s => !dig(s.whatsapp));
    if (sinWa.length) aviso(`Sin WhatsApp para avisos: ${sinWa.map(s => s.nombre).join(", ")}`, "Esos pedidos solo le llegan a OWNER_WHATSAPP. Póngalo en NEGOCIO_PRIVADO > sucursales.");
    else ok("Cada sucursal tiene su WhatsApp para avisos");
    if (N.cobro && N.cobro.activo) ok("Datos para transferencia puestos"); else aviso("No hay datos para transferencia", "El dueño los pone en el panel > Configuración > Pagos.");
    ok(`Repartidores: ${N.repartidores.length}`);
  }
  // 2. datos guardados y cifrados
  const dataDir = env.DATA_DIR === "" || env.DATA_DIR == null ? null : path.resolve(__dirname, env.DATA_DIR);
  if (!dataDir) mal("Sin DATA_DIR: los pedidos se pierden al reiniciar", "Use el plan con disco y DATA_DIR=/var/data.");
  else {
    try { fs.mkdirSync(dataDir, { recursive: true }); const p = path.join(dataDir, ".prueba-escritura"); fs.writeFileSync(p, "ok"); fs.unlinkSync(p); ok(`Disco en ${dataDir} (se puede escribir)`); }
    catch (e) { mal(`No se puede escribir en ${dataDir}`, "En Render > Disks revise que el disco esté montado en /var/data."); }
    const cifra = createCifra(env.DATA_KEY);
    if (!cifra) mal("Falta DATA_KEY", "Render la genera sola con el Blueprint. Guarde una copia en su gestor de contraseñas.");
    else {
      let abre = true;
      for (const n of ["pedidos.json", "usuarios.json", "ajustes.json"]) { const f2 = path.join(dataDir, n); if (fs.existsSync(f2)) { try { leerJSON(f2, null, cifra); } catch { abre = false; mal(`${n} no abre con esta DATA_KEY`, "Alguien cambió DATA_KEY. Ponga la llave anterior (la copia guardada)."); } } }
      if (abre) ok("Datos cifrados con DATA_KEY");
    }
  }
  // 3. panel
  if (!env.PANEL_SECRET) mal("Falta PANEL_SECRET: el panel está cerrado", "Render la genera con el Blueprint; si no, ponga 40 letras y números al azar.");
  else {
    let n = 0;
    try { const { createUsuarios } = require("./auth"); n = createUsuarios({ env: env.PANEL_USUARIOS || "", file: dataDir ? path.join(dataDir, "usuarios.json") : null, cifra: createCifra(env.DATA_KEY) }).lista().length; } catch {}
    if (n) ok(`Panel con ${n} usuario(s)`); else aviso("El panel no tiene usuarios todavía", 'En Render > Shell: npm run usuario -- agregar correo@ejemplo.com "Nombre" 504XXXXXXXX');
  }
  // 4. WhatsApp con Meta
  const tieneMeta = env.META_TOKEN && env.META_PHONE_ID;
  if (!tieneMeta) mal("Faltan META_TOKEN o META_PHONE_ID: el bot no puede contestar por WhatsApp", "Meta > su app > WhatsApp > Configuración de la API: copie el identificador del número y el token.");
  else {
    if (!/^\d{10,20}$/.test(String(env.META_PHONE_ID).trim())) mal("META_PHONE_ID no parece un identificador", "Es el número largo «Identificador del número de teléfono», no el número de WhatsApp.");
    else ok("META_PHONE_ID con formato correcto");
    if (String(env.META_TOKEN).trim().length < 60) mal("META_TOKEN muy corto", "Copie el token completo (empieza con EAA).");
  }
  if (!/^[0-9a-f]{32}$/i.test(String(env.META_APP_SECRET || "").trim())) mal("META_APP_SECRET falta o está mal: el bot rechaza todos los mensajes", "Meta > Configuración de la app > Básica > Clave secreta de la app > Mostrar. Son 32 letras y números.");
  else ok("META_APP_SECRET con formato correcto");
  if (!env.META_VERIFY_TOKEN) mal("Falta META_VERIFY_TOKEN", "Render la genera con el Blueprint. Es el texto que se pega en Meta > Webhook > Token de verificación.");
  else ok("META_VERIFY_TOKEN puesto");
  if (env.META_PLANTILLA) ok(`Plantilla de avisos: ${env.META_PLANTILLA}`); else aviso("Sin META_PLANTILLA", "Los avisos al dueño solo llegan si él le escribió al bot en las últimas 24 horas. Cree la plantilla aviso_pedido.");
  const dueno = dig(env.OWNER_WHATSAPP);
  if (!dueno) mal("Falta OWNER_WHATSAPP: a nadie le llegan los pedidos", "El WhatsApp personal del dueño, con 504 adelante.");
  else if (!/^504\d{8}$/.test(dueno) && !/^1\d{10}$/.test(dueno)) aviso("OWNER_WHATSAPP no parece de Honduras ni de EE. UU.", "Póngalo como +504 9999-9999.");
  else if (dig(env.META_NUMERO) && dueno === dig(env.META_NUMERO)) mal("OWNER_WHATSAPP es el mismo número del bot", "Ponga el celular personal del dueño, no el del negocio.");
  else ok("OWNER_WHATSAPP con formato correcto");
  // 5. Claude
  const clave = String(env.ANTHROPIC_API_KEY || "").trim();
  if (/^off$/i.test(String(env.BOT_IA || ""))) aviso("BOT_IA=off: contesta solo con el menú", "Póngalo en on para la IA.");
  else if (!clave) aviso("Sin ANTHROPIC_API_KEY: contesta solo con el menú", "console.anthropic.com > API Keys > Create Key, y péguela en Render.");
  else if (!clave.startsWith("sk-ant-")) mal("ANTHROPIC_API_KEY no parece una clave de Claude", "Empieza con sk-ant-. Cópiela completa.");
  else ok(`Clave de Claude puesta (modelo ${env.ANTHROPIC_MODEL || "por defecto"})`);
  if (!env.PUBLIC_URL) aviso("Sin PUBLIC_URL", "Ponga la dirección del servicio, por ejemplo https://con-sabor-a-pueblo-bot.onrender.com");
  // 6. en línea: solo lecturas, no manda mensajes ni gasta
  if (enLinea) {
    if (tieneMeta) {
      try {
        const r = await f(`https://graph.facebook.com/v21.0/${encodeURIComponent(String(env.META_PHONE_ID).trim())}?fields=display_phone_number,verified_name,quality_rating,code_verification_status,name_status`, { headers: { Authorization: `Bearer ${String(env.META_TOKEN).trim()}` } });
        const d = await r.json();
        if (!r.ok) mal(`Meta no acepta el token o el número: ${(d.error && d.error.message) || r.status}`, "Si dice que el token venció, cree el token permanente (guía, paso 3.6).");
        else ok(`Meta contesta: número ${d.display_phone_number}, nombre «${d.verified_name}», calidad ${d.quality_rating || "sin dato"}${d.name_status ? `, nombre ${d.name_status}` : ""}`);
      } catch (e) { mal(`No se pudo hablar con Meta: ${e.message}`, "Revise la conexión y vuelva a probar."); }
    }
    if (clave.startsWith("sk-ant-")) {
      try {
        const c = anthropic || new (require("@anthropic-ai/sdk"))({ apiKey: clave, maxRetries: 0, timeout: 15000 });
        await c.models.list({ limit: 1 });
        ok("Claude acepta la clave");
      } catch (e) { mal(`Claude no acepta la clave: ${e.status || ""} ${e.message}`.trim(), "Cree otra clave y revise que la cuenta tenga crédito (Billing)."); }
    }
    if (env.PUBLIC_URL) {
      try { const r = await f(String(env.PUBLIC_URL).replace(/\/$/, "") + "/"); r.ok ? ok(`${env.PUBLIC_URL} responde`) : mal(`${env.PUBLIC_URL} responde ${r.status}`, "Revise en Render > Logs que el servicio arrancó."); }
      catch (e) { mal(`${env.PUBLIC_URL} no responde`, "Revise en Render > Logs que el servicio arrancó."); }
    }
  }
  return out;
}

if (require.main === module) {
  try { process.loadEnvFile(path.join(__dirname, ".env")); } catch { /* no .env */ }
  revisar(process.env, { enLinea: process.argv.includes("--en-linea") }).then(out => {
    for (const [s, t, h] of out) console.log(`${s} ${t}${h ? `\n    → ${h}` : ""}`);
    const malos = out.filter(x => x[0] === "✗").length, avisos = out.filter(x => x[0] === "!").length;
    console.log(malos ? `\n${malos} cosa(s) por arreglar.` : avisos ? `\nListo para funcionar; ${avisos} aviso(s) para completar.` : "\nTodo bien.");
    process.exitCode = malos ? 1 : 0;
  });
}
module.exports = { revisar };
