// Quién puede entrar al panel.   npm run usuario -- <orden>
//
//   agregar correo@x.com "Nombre" [WhatsApp]
//                                   guarda la persona en DATA_DIR/usuarios.json (pide la contraseña).
//                                   Con WhatsApp (504XXXXXXXX), al entrar le llega un código por ahí.
//   quitar correo@x.com             la saca; su sesión deja de valer de inmediato
//   lista                           muestra quién tiene acceso
//   linea correo@x.com "Nombre" [WhatsApp]  no guarda nada: imprime la línea para pegar en PANEL_USUARIOS
//                                   (útil si el servidor no tiene disco o no tiene consola)
// La contraseña se escribe sin que se vea en pantalla y nunca queda guardada, solo su hash.
const path = require("path");
const readline = require("readline");
const { createUsuarios, hashClave, normWa, MIN_CLAVE } = require("./auth");
const { createCifra } = require("./cifrado");

try { process.loadEnvFile(path.join(__dirname, ".env")); } catch { /* no .env */ }
const dataDir = process.env.DATA_DIR === "" ? null : path.resolve(__dirname, process.env.DATA_DIR || "data");
const usuarios = createUsuarios({ env: process.env.PANEL_USUARIOS || "", file: dataDir ? path.join(dataDir, "usuarios.json") : null, cifra: createCifra(process.env.DATA_KEY) });

// one readline and a queue of lines, so piped input (two lines) works as well as typing
let rl = null;
const lineas = [], esperando = [];
function pedirClave(texto) {
  if (!rl) {
    rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: !!process.stdin.isTTY });
    rl._writeToOutput = s => { if (s.startsWith("Contraseña") || s.startsWith("Repítala") || s === "\n" || s === "\r\n") rl.output.write(s); };   // hide what is typed
    rl.on("line", l => { if (!process.stdin.isTTY) process.stdout.write("\n"); esperando.length ? esperando.shift()(l) : lineas.push(l); });
    rl.on("close", () => { while (esperando.length) esperando.shift()(""); });
  }
  rl.setPrompt(texto); rl.prompt();
  return new Promise(ok => lineas.length ? ok(lineas.shift()) : esperando.push(ok));
}
async function claveDoble() {
  const a = await pedirClave(`Contraseña (mínimo ${MIN_CLAVE} caracteres): `);
  const b = await pedirClave("Repítala: ");
  rl.close();
  if (a !== b) throw new Error("Las contraseñas no coinciden.");
  return a;
}

(async () => {
  const [orden, correo, nombre, whatsapp = ""] = process.argv.slice(2);
  try {
    if (orden === "agregar" && correo) {
      if (whatsapp && !normWa(whatsapp)) throw new Error("Ese número de WhatsApp no es válido.");
      const u = await usuarios.agregar(correo, nombre, await claveDoble(), whatsapp);
      console.log(`Listo: ${u.nombre} <${u.correo}> ya puede entrar al panel.${u.whatsapp ? ` Al entrar le llega un código al WhatsApp que termina en ${u.whatsapp.slice(-4)}.` : " Sin WhatsApp: entra solo con la contraseña."}`);
    } else if (orden === "linea" && correo) {
      const h = await hashClave(await claveDoble());
      console.log("\nPegue esta línea en PANEL_USUARIOS (una persona por línea):\n");
      console.log(`${correo.trim().toLowerCase()}|${nombre || correo}|${h}${normWa(whatsapp) ? "|" + normWa(whatsapp) : ""}`);
    } else if (orden === "quitar" && correo) {
      console.log(usuarios.quitar(correo) ? `Listo: ${correo} ya no puede entrar.` : `${correo} no estaba en usuarios.json (si está en PANEL_USUARIOS, bórrelo allí).`);
    } else if (orden === "lista") {
      const l = usuarios.lista();
      console.log(l.length ? l.map(u => `${u.correo}  ${u.nombre}  ${u.whatsapp ? "código a •••• " + u.whatsapp.slice(-4) : "sin código"}  (${u.origen})`).join("\n") : "Nadie tiene acceso todavía.");
    } else {
      console.log('Uso: npm run usuario -- agregar correo@x.com "Nombre" [504XXXXXXXX] | quitar correo | lista | linea correo "Nombre" [504XXXXXXXX]');
      process.exitCode = 1;
    }
  } catch (e) { console.error(e.message); process.exitCode = 1; }
})();
