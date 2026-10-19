// Arma los PDF del kit para un restaurante, desde los .md de esta carpeta:
// bienvenida, lista de lo que necesitamos, acuerdo de servicio, guía del panel, hoja del personal
// y el cartel con el QR del WhatsApp del bot. Los "[Restaurante]", "[Dueño]", etc. se llenan con los datos.
//
// Uso (desde la raíz del repo):
//   cd kit-cliente && npm install && cd ..
//   node kit-cliente/generar.mjs --restaurante "Pollo de Ejemplo" --dueno "Juan Pérez" \
//     --numero "9999-9999" --instalacion "L32,000" --mensual "L3,500" --inicio "20 de octubre de 2026"
// Solo --restaurante es obligatorio; lo que falte queda en blanco para escribirlo a mano.
// Salida: kit-cliente/pdf/<restaurante>/  (no se sube a GitHub: tiene datos del cliente)
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";
import { marked } from "marked";
import QRCode from "qrcode";
import { chromium } from "playwright";

const aqui = dirname(fileURLToPath(import.meta.url));
const raiz = join(aqui, "..");
const { values: a } = parseArgs({ options: {
  restaurante: { type: "string" }, dueno: { type: "string" }, numero: { type: "string" },
  instalacion: { type: "string" }, mensual: { type: "string" }, inicio: { type: "string" },
  salida: { type: "string" },
} });
if (!a.restaurante) { console.error('Falta --restaurante "Nombre"'); process.exit(1); }

const slug = a.restaurante.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const salida = a.salida || join(aqui, "pdf", slug);
mkdirSync(salida, { recursive: true });

const blanco = "______________________";
const datos = {
  "[Restaurante]": a.restaurante, "[Dueño]": a.dueno || blanco, "[Instalación]": a.instalacion || `L ${blanco}`,
  "[Mensualidad]": a.mensual || `L ${blanco}`, "[Fecha de inicio]": a.inicio || blanco,
};
const digitos = (a.numero || "").replace(/\D/g, "");
const waNum = digitos ? (digitos.length === 8 ? "504" + digitos : digitos) : "";

const dataUri = (f, tipo) => `data:${tipo};base64,${readFileSync(f).toString("base64")}`;
const letra = dataUri(join(raiz, "clientia-tech", "src", "fonts", "hanken-grotesk-latin.woff2"), "font/woff2");
const simbolo = readFileSync(join(raiz, "clientia-tech", "src", "img", "simbolo.svg"), "utf8").replace(/fill="#fff"/gi, 'fill="#0A1230"');

const CSS = `
@font-face{font-family:H;src:url(${letra}) format("woff2");font-weight:100 900}
@page{size:Letter;margin:16mm 17mm 18mm}
*{box-sizing:border-box}
body{font-family:H,system-ui,sans-serif;color:#1C2333;font-size:10.5pt;line-height:1.5;margin:0}
.top{display:flex;align-items:center;gap:8px;font-size:8.5pt;letter-spacing:.06em;text-transform:uppercase;color:#5B6478;border-bottom:1px solid #E3E7EF;padding-bottom:8px;margin-bottom:18px}
.top svg{width:15px;height:17px}
h1{font-size:21pt;line-height:1.15;color:#0A1230;margin:0 0 10px;letter-spacing:-.01em}
h2{font-size:13pt;color:#0A1230;margin:20px 0 6px;break-after:avoid}
h3{font-size:11pt;margin:14px 0 4px;break-after:avoid}
p{margin:0 0 8px}
ul,ol{margin:0 0 8px;padding-left:20px}
li{margin:2px 0}
li:has(>input){list-style:none;margin-left:-20px;padding-left:19px;text-indent:-19px}
input[type=checkbox]{appearance:none;width:11px;height:11px;border:1.4px solid #0A1230;border-radius:2px;vertical-align:-1px;margin:0 8px 0 0}
table{border-collapse:collapse;width:100%;margin:6px 0 10px;font-size:10pt;break-inside:avoid}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid #E3E7EF;vertical-align:top}
th{color:#0A1230;font-weight:600}
strong{color:#0A1230}
code{font-size:9.5pt;background:#F4F6FA;padding:1px 4px;border-radius:3px}
img{display:block;width:100%;max-width:132mm;margin:4px 0 8px;border:1px solid #E3E7EF;border-radius:8px}
.compacto{font-size:9.8pt;line-height:1.45}.compacto h2{margin:14px 0 4px}
p:last-child em{display:block;margin-top:22px;color:#8A93A6;font-size:9pt}
.firmas td{border:0;padding:10px 8px 10px 0;width:50%}
`;

// los .md usan rutas relativas a las imágenes del panel; aquí se meten dentro del PDF
const md = archivo => {
  let t = readFileSync(join(aqui, archivo), "utf8");
  t = t.replace(/^> \*\*Nota para Rodrigo:\*\*.*(\n>.*)*\n\n/m, "");
  for (const [k, v] of Object.entries(datos)) t = t.split(k).join(v);
  let html = marked.parse(t, { gfm: true });
  html = html.replace(/src="\.\.\/clientia-tech\/src\/img\/([\w-]+\.webp)"/g, (_, f) => `src="${dataUri(join(raiz, "clientia-tech", "src", "img", f), "image/webp")}"`);
  // cada sección con pantallazo queda entera en una página (título, imagen y texto juntos)
  html = html.split(/(?=<h2)/).map(x => x.includes("<img") ? `<section style="break-inside:avoid">${x}</section>` : x).join("");
  if (archivo.startsWith("3-")) html = html.replace(/<table>(?=[\s\S]*Por Clientia Tech)/, '<table class="firmas">');
  return html;
};
const pagina = (cuerpo, clase = "") => `<!doctype html><html lang="es"><meta charset="utf-8"><style>${CSS}</style>
<body class="${clase}"><div class="top">${simbolo}<span>Casa Digital · Clientia Tech</span></div>${cuerpo}</body></html>`;

const cartel = async () => {
  if (!waNum) return null;
  const link = `https://wa.me/${waNum}?text=${encodeURIComponent("Hola, quiero hacer un pedido")}`;
  const qr = await QRCode.toString(link, { type: "svg", margin: 0, errorCorrectionLevel: "M", color: { dark: "#0A1230", light: "#0000" } });
  const visible = digitos.length === 8 ? `${digitos.slice(0, 4)}-${digitos.slice(4)}` : "+" + digitos;
  return `<!doctype html><html lang="es"><meta charset="utf-8"><style>
@font-face{font-family:H;src:url(${letra}) format("woff2");font-weight:100 900}
@page{size:Letter;margin:0}
body{margin:0;font-family:H,system-ui,sans-serif;color:#0A1230}
.c{height:279.4mm;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 22mm}
.r{font-size:15pt;letter-spacing:.14em;text-transform:uppercase;color:#5B6478;margin:0 0 8mm}
h1{font-size:46pt;line-height:1.02;margin:0 0 6mm;letter-spacing:-.02em}
.s{font-size:17pt;margin:0 0 12mm;color:#1C2333}
.q{width:92mm;height:92mm;padding:7mm;border:2px solid #0A1230;border-radius:8mm}
.q svg{width:100%;height:100%}
.n{font-size:30pt;font-weight:700;margin:10mm 0 3mm;letter-spacing:.02em}
.p{font-size:13pt;color:#5B6478;margin:0}
.f{position:absolute;bottom:12mm;left:0;right:0;text-align:center;font-size:9pt;color:#8A93A6}
</style><body><div class="c">
<p class="r">${a.restaurante.replace(/</g, "&lt;")}</p>
<h1>Pedí por WhatsApp</h1>
<p class="s">Te contestamos al instante, a cualquier hora.</p>
<div class="q">${qr}</div>
<p class="n">${visible}</p>
<p class="p">Escaneá el código, escogé tu pedido y pasá a recogerlo cuando esté listo.</p>
</div><div class="f">Casa Digital by Clientia Tech</div></body></html>`;
};

const docs = [
  ["bienvenida", "1-bienvenida.md"],
  ["lo-que-necesitamos", "2-lo-que-necesitamos.md"],
  ["acuerdo-de-servicio", "3-acuerdo-de-servicio.md"],
  ["guia-del-panel", "4-guia-del-dueno.md"],
  ["hoja-del-personal", "5-hoja-del-personal.md"],
];

const navegador = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const pdf = async (nombre, html) => {
  const p = await navegador.newPage();
  await p.setContent(html, { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: join(salida, nombre + ".pdf"), format: "Letter", printBackground: true, preferCSSPageSize: true });
  if (process.env.HTML) writeFileSync(join(salida, nombre + ".html"), html);
  await p.close();
  console.log("  " + nombre + ".pdf");
};
console.log(`Kit de ${a.restaurante} → ${salida}`);
for (const [nombre, archivo] of docs) await pdf(nombre, pagina(md(archivo), archivo.startsWith("3-") ? "compacto" : ""));
const c = await cartel();
if (c) await pdf("cartel-whatsapp", c); else console.log("  (sin --numero no se hace el cartel con QR)");
await navegador.close();
