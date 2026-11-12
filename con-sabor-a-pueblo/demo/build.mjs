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
const SALIR = `<script>document.addEventListener("click",e=>{const a=e.target.closest('a[href="/panel/salir"],a[href="/panel/entrar"]');if(a){e.preventDefault();window.parent.DEMO.salir()}})</script>`;
const panel = leer(bot, "panel", "panel.html").replace("<script>", SHIM + SALIR + "<script>");

// the real login page (auth.js), with the form answered by this page; the demo's email and password are shown on it
const { paginaEntrar } = require(join(bot, "auth.js"));
const FORM = `<script>document.addEventListener("click",e=>{if(e.target.closest("a[href^='/panel/']")){e.preventDefault();window.parent.DEMO.salir()}});document.addEventListener("submit",e=>{e.preventDefault();window.parent.DEMO.entrar(Object.fromEntries(new FormData(e.target)))});
addEventListener("DOMContentLoaded",()=>{const c=document.querySelector("input[name=clave]");if(c)c.value="Sabor-2026-demo"})</script>`;
const N = require(join(bot, "negocio.js")).cargarNegocio(D.archivo, D.privado);
const pag = o => paginaEntrar({ marca: N.nombre, color: N.color, logo: "LOGO_DEMO", ...o }).replace("</head>", FORM + "</head>");
const demoAviso = "Demo: el correo y la contraseña ya están puestos. Toque Entrar.";
const ENTRAR = {
  entrar: pag({ correo: "dueno@consaborapueblo.demo", aviso: demoAviso }),
  entrarError: pag({ correo: "dueno@consaborapueblo.demo", error: "ERROR_DEMO" }),
  codigo: pag({ paso: { final: "0003" } }),
  codigoError: pag({ paso: { final: "0003" }, error: "Código incorrecto. Revise el WhatsApp y vuelva a probar." }),
};

const fuente = readFileSync(join(raiz, "clientia-tech", "src", "fonts", "hanken-grotesk-latin.woff2")).toString("base64");
const logo = leer(bot, N.logo);
let html = leer(aqui, "src.html")
  .replace("/*BOT*/", () => BOT)
  .replace("/*FUENTE*/", fuente)
  .replace("/*LOGOSVG*/", () => JSON.stringify(logo));
mkdirSync(join(aqui, "dist"), { recursive: true });
writeFileSync(join(aqui, "dist", "con-sabor-a-pueblo.html"), html);
// the owner panel on its own link: the real panel full screen, connected to the demo tab (BroadcastChannel)
const panelPag = leer(aqui, "panel-src.html")
  .replace("/*LOGOSVG*/", () => JSON.stringify(logo))
  .replace("/*PANEL*/", () => JSON.stringify(panel).replace(/<\/script>/gi, "<\\/script>"))
  .replace("/*ENTRAR*/", () => JSON.stringify(ENTRAR).replace(/<\/script>/gi, "<\\/script>"));
writeFileSync(join(aqui, "dist", "con-sabor-a-pueblo-panel.html"), panelPag);
// the demo links to the panel with a version, so a phone never opens an old cached copy
const ver = (await import("node:crypto")).createHash("sha256").update(panelPag).digest("hex").slice(0, 8);
writeFileSync(join(aqui, "dist", "con-sabor-a-pueblo.html"), html.replaceAll("con-sabor-a-pueblo-panel.html", "con-sabor-a-pueblo-panel.html?v=" + ver));
console.log("dist/con-sabor-a-pueblo-panel.html", Math.round(panelPag.length / 1024) + " KB");
console.log("dist/con-sabor-a-pueblo.html", Math.round(html.length / 1024) + " KB", IA_URL ? "con IA: " + IA_URL : "sin IA (menú de opciones)");
