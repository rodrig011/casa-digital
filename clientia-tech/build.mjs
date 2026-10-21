// Arma clientia-tech/index.html (un solo archivo) desde src/index.html, y las páginas legales desde src/legal/:
// mete la letra, los pantallazos y el logo como data: URI, y el motor real del bot
// (bot-restaurante/engine.js + negocio.js + negocios/ejemplo.json) para la demostración.
// Uso: node clientia-tech/build.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const aqui = dirname(fileURLToPath(import.meta.url));
const bot = join(aqui, "..", "bot-restaurante");
const leer = (...p) => readFileSync(join(...p));
const dataUri = (buf, tipo) => `data:${tipo};base64,${buf.toString("base64")}`;

const WA_NUM = "17655434251";
const WA_TXT = "Hola Rodrigo, vi la página de Clientia Tech. Mi negocio es: ";
const WA = `https://wa.me/${WA_NUM}?text=${encodeURIComponent(WA_TXT)}`;
const WA_ICON = `<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.8-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.4.8 3.2.7.5-.1 1.5-.6 1.8-1.2.2-.6.2-1.1.1-1.2l-.2-.3Z"/></svg>`;

// the bot's own CommonJS files, wired with a tiny require() so they run in the browser untouched
const mod = f => `function(module,exports,require){${leer(bot, f).toString()}\n}`;
const BOT = `const BOT=(()=>{const defs={"./negocio":${mod("negocio.js")},"./engine":${mod("engine.js")}},cache={};
function req(n){if(n==="fs"||n==="path")return{};if(cache[n])return cache[n].exports;const m={exports:{}};cache[n]=m;defs[n](m,m.exports,req);return m.exports}
const ng=req("./negocio"),en=req("./engine");
return{preparar:ng.preparar,cuenta:ng.cuenta,L:ng.L,createEngine:en.createEngine,NEGOCIO:${leer(bot, "negocios", "ejemplo.json").toString()}}})();`;

const logo = leer(aqui, "src", "img", "simbolo.svg");
// favicon: the white mark on the navy square
const fav = logo.toString().replace(/<svg([^>]*)>/, '<svg$1><rect x="-30" y="-10" width="460" height="486" rx="80" fill="#0A1230"/>');

const armar = archivo => leer(aqui, "src", archivo).toString()
  .replace("{{FONT}}", () => dataUri(leer(aqui, "src", "fonts", "hanken-grotesk-latin.woff2"), "font/woff2"))
  .replace("{{FONT_HORAS}}", () => dataUri(leer(aqui, "src", "fonts", "big-shoulders-latin.woff2"), "font/woff2"))
  .replace(/\{\{FONTF:([\w-]+)\}\}/g, (_, n) => dataUri(leer(aqui, "src", "fonts", n + ".woff2"), "font/woff2"))
  .replace("{{FONT_TEXTO}}", () => dataUri(leer(aqui, "src", "fonts", "instrument-sans-latin.woff2"), "font/woff2"))
  .replaceAll("{{LOGO}}", dataUri(logo, "image/svg+xml"))
  .replace("{{LOGO_FAVICON}}", dataUri(Buffer.from(fav.replace('viewBox="13 20 374 426"', 'viewBox="-30 -10 460 486"')), "image/svg+xml"))
  .replaceAll("{{WA}}", WA.replaceAll("&", "&amp;"))
  .replaceAll("{{WA_ICON}}", WA_ICON)
  .replace("/*{{BOT}}*/", () => BOT)
  .replace(/\{\{IMG:([\w-]+)\}\}/g, (_, n) => dataUri(leer(aqui, "src", "img", n + ".webp"), "image/webp"));

// each page goes to clientia-tech/ and to the repo root: GitHub Pages ("Deploy from a branch", main / root) serves the root copy at clientiatech.com
const publicar = (nombre, h) => {
  if (/\{\{/.test(h)) throw new Error(`Quedó un {{...}} sin reemplazar en ${nombre}`);
  writeFileSync(join(aqui, nombre), h);
  writeFileSync(join(aqui, "..", nombre), h);
  console.log(`clientia-tech/${nombre}: ${(h.length / 1024).toFixed(0)} KB`);
};
publicar("index.html", armar("index.html"));
// test page made with the frontend-design skill (clientiatech.com/prueba.html); the home page stays as it is
publicar("prueba.html", armar("prueba.html"));
// second test page, sober corporate look in IBM Plex (clientiatech.com/prueba-ibm.html)
publicar("prueba-ibm.html", armar("prueba-ibm.html"));

// legal pages: src/legal/<archivo> inside src/legal/plantilla.html
const LEGAL = [
  ["terminos.html", "Términos y condiciones", "Términos", "Condiciones de uso de la página y del servicio de Clientia Tech: prueba de 30 días, pagos, cancelación y límites."],
  ["privacidad.html", "Política de privacidad", "Privacidad", "Qué datos pide Clientia Tech, para qué, con quién trabaja, cuánto tiempo los guarda y cómo pedir que se borren."],
  ["cookies.html", "Política de cookies", "Cookies", "La página de Clientia Tech no usa cookies; el panel del dueño usa solo una cookie de sesión."],
  ["reembolsos.html", "Política de reembolso", "Reembolsos", "Cuándo devuelve Clientia Tech un pago y cómo pedirlo."],
  ["legal.html", "Aviso legal", "Aviso legal", "Titular de la página, leyes revisadas, registro de aceptaciones y derechos de las imágenes."],
];
const plantilla = leer(aqui, "src", "legal", "plantilla.html").toString();
for (const [archivo, titulo, corto, descripcion] of LEGAL) {
  const enlaces = LEGAL.map(([a, , c]) => `<a href="${a}"${a === archivo ? ' aria-current="page"' : ""}>${c}</a>`).join("");
  publicar(archivo, plantilla
    .replace("{{CONTENIDO}}", () => leer(aqui, "src", "legal", archivo).toString())
    .replace("{{TITULO}}", titulo)
    .replace("{{DESCRIPCION}}", descripcion)
    .replace("{{INDICE}}", () => enlaces)
    .replace("{{INDICE_PIE}}", () => LEGAL.map(([a, , c]) => `<a href="${a}">${c}</a>`).join(""))
    .replace("{{FONT}}", dataUri(leer(aqui, "src", "fonts", "hanken-grotesk-latin.woff2"), "font/woff2"))
    .replaceAll("{{LOGO}}", dataUri(logo, "image/svg+xml"))
    .replace("{{LOGO_FAVICON}}", dataUri(Buffer.from(fav.replace('viewBox="13 20 374 426"', 'viewBox="-30 -10 460 486"')), "image/svg+xml"))
    .replaceAll("{{WA}}", WA.replaceAll("&", "&amp;")));
}
