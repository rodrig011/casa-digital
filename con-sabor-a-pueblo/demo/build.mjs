// Arma la demo en línea de Con Sabor a Pueblo: un solo HTML con el bot REAL (bot-restaurante) corriendo en el
// navegador: los teléfonos del cliente, de Kevin (repartidor) y del dueño, y el panel del dueño de verdad.
// La IA (Claude) contesta por el servidor de la demo (bot-restaurante/demo.js, /demo/claude); si no está, contesta
// el menú de opciones, igual que el bot real cuando falla la IA.
// Uso: node con-sabor-a-pueblo/demo/build.mjs   ->  con-sabor-a-pueblo/demo/dist/con-sabor-a-pueblo.html
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const aqui = dirname(fileURLToPath(import.meta.url));
const raiz = join(aqui, "..", "..");
const bot = join(raiz, "bot-restaurante");
const leer = (...p) => readFileSync(join(...p), "utf8");
const require = createRequire(import.meta.url);
const { DEMOS } = require(join(bot, "demos.js"));
const D = DEMOS["con-sabor-a-pueblo"];
const IA_URL = process.env.DEMO_IA_URL ?? JSON.parse(leer(raiz, "clientia-tech", "config.json")).demoIA ?? "";

// the bot's own CommonJS files, wired with a tiny require() so they run in the browser untouched
const mods = ["negocio", "engine", "avisos", "repartos", "store", "ia"];
const mod = f => `function(module,exports,require){${leer(bot, f + ".js")}\n}`;
const BOT = `const BOT=(()=>{const defs={${mods.map(m => `"./${m}":${mod(m)}`).join(",")},"./cifrado":function(module){module.exports={leerJSON:(f,e)=>e,escribirJSON:()=>{}}}},cache={};
function req(n){if(!defs[n])return{};if(cache[n])return cache[n].exports;const m={exports:{}};cache[n]=m;defs[n](m,m.exports,req);return m.exports}
const r={};for(const m of ${JSON.stringify(mods)})r[m]=req("./"+m);return r})();
const NEGOCIO_JSON=${leer(bot, D.archivo)};const PRIVADO=${JSON.stringify(D.privado)};const IA_URL=${JSON.stringify(IA_URL ? IA_URL.replace(/\/demo\/chat$/, "") + "/demo/claude" : "")};`;

// the owner panel, with fetch() answered by the bot running in this page
const SHIM = `<script>window.fetch=async(u,o)=>{const r=await window.parent.DEMO.api(String(u),o||{});return new Response(JSON.stringify(r.body),{status:r.status,headers:{"Content-Type":"application/json"}})};</script>`;
const panel = leer(bot, "panel", "panel.html").replace("<script>", SHIM + "<script>");

const fuente = readFileSync(join(raiz, "clientia-tech", "src", "fonts", "hanken-grotesk-latin.woff2")).toString("base64");
const logo = readFileSync(join(raiz, "con-sabor-a-pueblo", "redes", "logo-tiktok.jpg")).toString("base64");
let html = leer(aqui, "src.html")
  .replace("/*BOT*/", () => BOT)
  .replace("/*PANEL*/", () => JSON.stringify(panel).replace(/<\/script>/gi, "<\\/script>"))
  .replace("/*FUENTE*/", fuente)
  .replace(/\/\*LOGO\*\//g, "data:image/jpeg;base64," + logo);
mkdirSync(join(aqui, "dist"), { recursive: true });
writeFileSync(join(aqui, "dist", "con-sabor-a-pueblo.html"), html);
console.log("dist/con-sabor-a-pueblo.html", Math.round(html.length / 1024) + " KB", IA_URL ? "con IA: " + IA_URL : "sin IA (menú de opciones)");
