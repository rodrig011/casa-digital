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
//
// Diseño: el estilo de la página de Clientia Tech (azul marino, Hanken Grotesk 800, mucho aire).
// Los .md llevan comentarios que GitHub no muestra y que aquí cambian cómo se dibuja el bloque siguiente:
//   <!-- portada: Texto -->   portada azul con ese rótulo (o "no": solo una cabecera)
//   <!-- estilo: ficha -->    título de cada sección a la izquierda y contenido a la derecha
//   <!-- tarjetas -->         la lista siguiente en tarjetas (la primera con sublista va en azul, a lo ancho)
//   <!-- tarjetas: simples --> tarjetas con borde, sin número
//   <!-- pasos -->            la lista siguiente en pasos grandes numerados
//   <!-- linea -->            la tabla siguiente como línea de tiempo
//   <!-- banda: 30 | texto --> la sección siguiente en una banda azul con ese número grande
//   <!-- contraportada -->    la sección siguiente va en la contraportada azul
//   <!-- pagina -->           la sección siguiente empieza en una página nueva
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
const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
const mes = (m => m[0].toUpperCase() + m.slice(1))(new Date().toLocaleDateString("es-HN", { month: "long", year: "numeric" }));

const dataUri = (f, tipo) => `data:${tipo};base64,${readFileSync(f).toString("base64")}`;
const letra = dataUri(join(raiz, "clientia-tech", "src", "fonts", "hanken-grotesk-latin.woff2"), "font/woff2");
const simbolo = readFileSync(join(raiz, "clientia-tech", "src", "img", "simbolo.svg"), "utf8"); // blanco
const simboloAzul = simbolo.replace(/fill="#fff"/gi, 'fill="#0A1230"');
const marca = (svg = simbolo) => `<div class="marca">${svg}<span>Clientia Tech</span></div>`;

const CSS = `
@font-face{font-family:H;src:url(${letra}) format("woff2");font-weight:100 900}
@page{size:Letter;margin:20mm 20mm 18mm}
@page full{margin:0}
:root{--navy:#0A1230;--deep:#16245A;--ink:#0A1230;--soft:#3D4763;--mute:#7A84A0;--bg:#F4F6FA;--line:#E2E7F0;--accent:#1F5BFF;--pale:#9DB6FF;--on:#F4F6FA;--on2:#B7C1DD}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:H,system-ui,sans-serif;color:var(--soft);font-size:10.5pt;line-height:1.55;margin:0;font-feature-settings:"tnum" 0}
h1,h2,h3,p{margin:0}
strong{color:var(--ink);font-weight:700}
h1,h2,h3{color:var(--ink);font-weight:800;letter-spacing:-.035em;text-wrap:balance}
code{font-size:9.5pt;background:var(--bg);padding:1px 5px;border-radius:4px;color:var(--ink)}
.marca{display:flex;align-items:center;gap:3mm;font-weight:800;font-size:12pt;letter-spacing:-.02em}
.marca svg{width:6mm;height:auto}

/* portada y contraportada: página completa azul */
.portada,.contra{page:full;width:215.9mm;height:279.4mm;background:var(--navy);color:var(--on);padding:20mm;display:flex;flex-direction:column;position:relative;overflow:hidden;break-after:page}
.contra{break-before:page;break-after:auto}
.portada .fant,.contra .fant{position:absolute;right:-34mm;bottom:-30mm;width:150mm;opacity:.07}
.portada .fant svg,.contra .fant svg{width:100%;height:auto}
.portada .arriba{display:flex;justify-content:space-between;align-items:center;font-size:9.5pt;color:var(--on2)}
.portada .arriba .marca{color:var(--on)}
.portada .medio{margin-top:auto;margin-bottom:22mm;position:relative}
.rotulo{font-size:10pt;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--pale);margin-bottom:7mm}
.portada h1{color:#fff;font-size:58pt;line-height:.94;letter-spacing:-.05em;max-width:165mm}
.portada .lead{margin-top:9mm;font-size:15pt;line-height:1.4;color:var(--on2);max-width:125mm}
.portada .lead p+p{margin-top:3mm}
.portada .lead strong{color:#fff}
.portada .abajo{display:flex;justify-content:space-between;border-top:1px solid rgba(244,246,250,.18);padding-top:5mm;font-size:9.5pt;color:var(--on2);position:relative}
.contra .medio{margin-top:auto;position:relative}
.contra h2{color:#fff;font-size:44pt;line-height:.96;letter-spacing:-.045em;max-width:150mm}
.contra .txt{margin-top:10mm;font-size:13pt;line-height:1.5;color:var(--on2);max-width:120mm}
.contra .txt strong{color:#fff}
.contra .txt p+p{margin-top:4mm}
.contra .abajo{margin-top:22mm;display:flex;justify-content:space-between;align-items:center;border-top:1px solid rgba(244,246,250,.18);padding-top:5mm;font-size:9.5pt;color:var(--on2);position:relative}
.contra .abajo .marca{color:var(--on)}

/* cabecera cuando no hay portada */
.cab{background:var(--navy);color:var(--on);border-radius:6mm;padding:9mm 10mm 8mm;margin-bottom:8mm;position:relative;overflow:hidden}
.cab .marca{color:var(--on);margin-bottom:7mm}
.cab h1{color:#fff;font-size:30pt;line-height:.96;letter-spacing:-.045em}
.cab .lead{margin-top:4mm;font-size:12pt;color:var(--on2)}
.cab .fant{position:absolute;right:-12mm;top:-14mm;width:70mm;opacity:.08}

/* secciones */
.sec{margin-bottom:13mm}
.hoja .sec{margin-bottom:6mm}.trio{display:grid;grid-template-columns:repeat(3,1fr);gap:6mm;border-top:1px solid var(--line);padding-top:6mm}.trio .sec{margin:0}.trio p,.trio li{font-size:9.8pt}.hoja .sec .cabeza h2{font-size:17pt;margin-bottom:3mm}.hoja .num{margin-bottom:2mm}
.num{font-size:9pt;font-weight:700;letter-spacing:.16em;color:var(--accent);margin-bottom:3mm;font-variant-numeric:tabular-nums}
.cabeza{break-inside:avoid;break-after:avoid}
.sec .cabeza h2,.sec .tit h2{font-size:24pt;line-height:1.04;margin-bottom:6mm;break-after:avoid}
.sec p{margin-bottom:3.5mm;max-width:150mm}
.sec>p:first-of-type{font-size:12pt;line-height:1.5}
.ficha .sec{display:flex;gap:8mm;border-top:1px solid var(--line);padding-top:6mm;margin-bottom:8mm;break-inside:avoid;page-break-inside:avoid}
.ficha .sec .tit{width:52mm;flex:none}.ficha .sec .cuerpo{flex:1;min-width:0}
.ficha .sec .tit h2{font-size:15pt;line-height:1.12;margin:0}
.ficha .sec>.cuerpo>p:first-child{font-size:10.5pt}
.ficha .sec.alta{break-inside:auto}
.compacta .sec{padding-top:4.5mm;margin-bottom:5mm}.compacta .cuerpo li,.compacta .cuerpo p{font-size:9.6pt;line-height:1.45}.compacta ol>li{margin-bottom:1.6mm}
.firmas .f h3{margin-bottom:9mm}

ul,ol{margin:0 0 4mm;padding:0;list-style:none}
ul>li{position:relative;padding-left:6mm;margin:0 0 2.2mm}
ul>li::before{content:"";position:absolute;left:0;top:2.15mm;width:1.7mm;height:1.7mm;border-radius:50%;background:var(--accent)}
ol{counter-reset:n}
ol>li{position:relative;padding-left:8mm;margin:0 0 2.4mm;counter-increment:n}
ol>li::before{content:counter(n);position:absolute;left:0;top:0;font-weight:800;color:var(--accent);font-variant-numeric:tabular-nums}

/* lista para marcar */
ul.check>li{padding:2.6mm 0 2.6mm 9mm;margin:0;border-bottom:1px solid var(--line)}
ul.check>li:last-child{border-bottom:0}
ul.check>li::before{top:2.9mm;width:4.4mm;height:4.4mm;border-radius:50%;background:none;border:1.5px solid var(--accent)}

/* tarjetas */
.cards{display:grid;grid-template-columns:1fr 1fr;gap:4.5mm;margin:2mm 0 4mm}
.card{background:var(--bg);border-radius:5mm;padding:7mm 7mm 6mm;break-inside:avoid}
.card .n{font-size:9pt;font-weight:700;letter-spacing:.16em;color:var(--accent);margin-bottom:5mm}
.card h3{font-size:13.5pt;line-height:1.15;letter-spacing:-.025em;margin-bottom:2.5mm}
.card p{font-size:10pt;line-height:1.5;margin:0}
.card.ancha{grid-column:1/-1;background:var(--navy);color:var(--on2);padding:9mm}
.card.ancha h3{color:#fff;font-size:19pt;max-width:120mm}
.card.ancha p{font-size:11pt;max-width:130mm}
.card.ancha strong{color:#fff}
.card.ancha ul{display:grid;grid-template-columns:1fr 1fr;gap:3mm 8mm;margin:7mm 0 0}
.card.ancha li{margin:0;font-size:10pt;color:var(--on)}
.card.ancha li::before{background:var(--pale)}
.cards.simples .card{background:none;border:1px solid var(--line)}
.cards.simples .card h3{font-size:12pt}

/* pasos */
.pasos{display:grid;grid-template-columns:1fr 1fr;gap:4.5mm;margin:2mm 0 4mm}
.paso{background:var(--bg);border-radius:5mm;padding:6mm;min-height:33mm;display:flex;flex-direction:column;break-inside:avoid}
.paso .gran{font-size:30pt;font-weight:800;letter-spacing:-.05em;line-height:.9;color:var(--accent);margin-bottom:auto;padding-bottom:6mm}
.paso p{font-size:12pt;line-height:1.4;color:var(--ink);margin:0}

/* banda azul con número grande */
.banda{background:var(--navy);border-radius:6mm;padding:10mm 11mm 7mm;display:grid;grid-template-columns:52mm 1fr;gap:10mm;color:var(--on2);break-inside:avoid}
.banda .big{font-size:96pt;font-weight:800;letter-spacing:-.06em;line-height:.8;color:#fff}
.banda .big small{display:block;font-size:13pt;letter-spacing:-.01em;line-height:1.2;margin-top:5mm;color:var(--pale);font-weight:700}
.banda h2{color:#fff;font-size:22pt;line-height:1.05;margin-bottom:6mm}
.banda strong{color:#fff}
.banda li{color:var(--on)}
.banda li::before{background:var(--pale)}
.banda .num{color:var(--pale)}

/* línea de tiempo */
.linea{margin:2mm 0 5mm;break-inside:avoid}
.linea .fila{display:grid;grid-template-columns:30mm 1fr;gap:6mm;padding:2.5mm 0;border-top:1px solid var(--line);align-items:baseline}
.linea .fila:last-child{border-bottom:1px solid var(--line)}
.linea .d{font-size:12.5pt;font-weight:800;letter-spacing:-.03em;color:var(--ink);font-variant-numeric:tabular-nums}
.linea .t{font-size:10.5pt}

/* tablas */
table{border-collapse:collapse;width:100%;margin:2mm 0 5mm;font-size:10pt;break-inside:avoid}
th,td{text-align:left;padding:3.2mm 3mm 3.2mm 0;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--ink);font-weight:700;font-size:8.5pt;letter-spacing:.12em;text-transform:uppercase}
.firmas{display:grid;grid-template-columns:1fr 1fr;gap:8mm;margin-top:2mm}
.firmas .f{background:var(--bg);border-radius:5mm;padding:7mm}
.firmas .f h3{font-size:12pt;margin-bottom:12mm}
.firmas .f p{border-bottom:1px solid var(--soft);padding-bottom:1.5mm;margin:0 0 9mm;font-size:9.5pt;color:var(--mute);max-width:none}
.firmas .f p:last-child{margin-bottom:0}

/* pantallazos */
.shot{background:var(--bg);border-radius:6mm;padding:8mm;margin:1mm 0 6mm}
.shot img{display:block;width:100%;border-radius:3mm;box-shadow:0 1.5mm 6mm rgba(10,18,48,.13),0 0 0 .3mm rgba(10,18,48,.06)}
.sec.foto{break-inside:avoid;display:flex;gap:8mm;align-items:start;border-top:1px solid var(--line);padding-top:6mm;margin-bottom:8mm}
.sec.foto .cabeza h2{font-size:17pt;margin-bottom:4mm}
.sec.foto p,.sec.foto li{font-size:9.8pt}
.sec.foto>.lado>p:first-of-type{font-size:9.8pt}
.sec.foto .lado{width:50mm;flex:none}.sec.foto .shot{margin:0;padding:6mm;flex:1;min-width:0}
`;

const cardsHtml = (tok, simples) => {
  let n = 0;
  return `<div class="cards${simples ? " simples" : ""}">${tok.items.map(it => {
    const sub = it.tokens.find(t => t.type === "list");
    const txt = it.tokens.filter(t => t !== sub).map(t => t.raw).join("").trim();
    const m = txt.match(/^\*\*(.+?)\*\*\s*([\s\S]*)$/) || [null, txt, ""];
    n++;
    return `<div class="card${sub ? " ancha" : ""}">${simples ? "" : `<div class="n">${String(n).padStart(2, "0")}</div>`}<h3>${marked.parseInline(m[1])}</h3>${m[2] ? `<p>${marked.parseInline(m[2])}</p>` : ""}${sub ? marked.parser([sub]) : ""}</div>`;
  }).join("")}</div>`;
};
const pasosHtml = tok => `<div class="pasos">${tok.items.map((it, i) => `<div class="paso"><div class="gran">${i + 1}</div><p>${marked.parseInline(it.text)}</p></div>`).join("")}</div>`;
const lineaHtml = tok => `<div class="linea">${tok.rows.map(r => `<div class="fila"><div class="d">${marked.parseInline(r[0].text)}</div><div class="t">${marked.parseInline(r[1].text)}</div></div>`).join("")}</div>`;
const firmasHtml = tok => {
  const filas = [tok.header, ...tok.rows].filter(r => r.some(c => c.text.trim()));
  return `<div class="firmas">${[0, 1].map(c => `<div class="f"><h3>${marked.parseInline(filas[0][c].text)}</h3>${filas.slice(1).map(r => `<p>${marked.parseInline(r[c].text.replace(/_{3,}/g, ""))}</p>`).join("")}</div>`).join("")}</div>`;
};
const imgs = html => html.replace(/<p><img src="\.\.\/clientia-tech\/src\/img\/([\w-]+\.webp)" alt="([^"]*)"><\/p>/g,
  (_, f, alt) => `<div class="shot"><img src="${dataUri(join(raiz, "clientia-tech", "src", "img", f), "image/webp")}" alt="${alt}"></div>`);

const bloque = (tok, dir) => {
  if (tok.type === "list" && dir?.k === "tarjetas") return cardsHtml(tok, dir.v === "simples");
  if (tok.type === "list" && dir?.k === "pasos") return pasosHtml(tok);
  if (tok.type === "table" && dir?.k === "linea") return lineaHtml(tok);
  if (tok.type === "table" && /Por Clientia Tech/.test(tok.raw)) return firmasHtml(tok);
  if (tok.type === "list" && tok.items.some(i => i.task)) return `<ul class="check">${tok.items.map(i => `<li>${marked.parseInline(i.text)}</li>`).join("")}</ul>`;
  return imgs(marked.parser([tok]));
};

const render = archivo => {
  let t = readFileSync(join(aqui, archivo), "utf8");
  for (const [k, v] of Object.entries(datos)) t = t.split(k).join(v);
  const toks = marked.lexer(t, { gfm: true });
  let portada = null, estilo = "", titulo = "", lead = [], secs = [], cur = null, dir = null, sigSec = {};
  for (const tok of toks) {
    if (tok.type === "space") continue;
    const c = tok.type === "html" && tok.raw.match(/<!--\s*([\w-]+)(?::\s*(.*?))?\s*-->/);
    if (c) {
      const [, k, v = ""] = c;
      if (k === "portada") portada = v;
      else if (k === "estilo") estilo = v;
      else if (k === "banda" || k === "contraportada") sigSec = { ...sigSec, k, v };
      else if (k === "pagina") sigSec = { ...sigSec, pagina: true };
      else dir = { k, v };
      continue;
    }
    if (tok.type === "blockquote" && /^\*\*Nota para Rodrigo/.test(tok.text)) continue;
    if (tok.type === "heading" && tok.depth === 1) { titulo = tok.text; continue; }
    if (tok.type === "heading" && tok.depth === 2) { cur = { titulo: tok.text, html: [], ...sigSec }; secs.push(cur); sigSec = {}; continue; }
    const h = bloque(tok, dir); dir = null;
    (cur ? cur.html : lead).push(h);
  }
  const fant = `<div class="fant">${simbolo}</div>`;
  const leadHtml = lead.join("");
  let out = portada === "no"
    ? `<header class="cab">${fant}${marca()}<h1>${marked.parseInline(titulo)}</h1><div class="lead">${leadHtml}</div></header>`
    : `<section class="portada">${fant}<div class="arriba">${marca()}<span>Casa Digital</span></div>
       <div class="medio"><div class="rotulo">${esc(portada || "")}</div><h1>${marked.parseInline(titulo)}</h1><div class="lead">${leadHtml}</div></div>
       <div class="abajo"><span>Preparado para ${esc(a.restaurante)}</span><span>${mes}</span></div></section>`;
  let n = 0, contra = "";
  for (const s of secs) {
    if (s.k === "contraportada") {
      contra = `<section class="contra">${fant}<div class="medio"><h2>Ningún cliente sin respuesta.</h2><div class="txt"><p><strong>${esc(s.titulo)}</strong></p>${s.html.join("")}</div></div>
        <div class="abajo">${marca()}<span>Casa Digital by Clientia Tech</span></div></section>`;
      continue;
    }
    const num = `<div class="num">${String(++n).padStart(2, "0")}</div>`;
    const cuerpo = s.html.join("");
    const pg = s.pagina ? ' style="break-before:page"' : "";
    if (s.k === "banda") {
      const [big, small] = s.v.split("|").map(x => x.trim());
      out += `<section class="sec"${pg}><div class="banda"><div class="big">${esc(big)}<small>${esc(small || "")}</small></div><div>${num}<h2>${marked.parseInline(s.titulo)}</h2>${cuerpo}</div></div></section>`;
    } else if (estilo.includes("ficha")) {
      const alta = cuerpo.length > 4000 ? " alta" : "";
      out += `<section class="sec${alta}"${pg}><div class="tit">${num}<h2>${marked.parseInline(s.titulo)}</h2></div><div class="cuerpo">${cuerpo}</div></section>`;
    } else {
      const shot = s.html.find(h => h.startsWith('<div class="shot"'));
      out += shot
        ? `<section class="sec foto"${pg}><div class="lado"><div class="cabeza">${num}<h2>${marked.parseInline(s.titulo)}</h2></div>${s.html.filter(h => h !== shot).join("")}</div>${shot}</section>`
        : `<section class="sec"${pg}><div class="cabeza">${num}<h2>${marked.parseInline(s.titulo)}</h2></div>${cuerpo}</section>`;
    }
  }
  // hoja del personal: después de los pasos, las demás secciones van en tres columnas para que quepa en una hoja
  if (estilo.includes("hoja")) out = out.replace(/(<\/section>)(<section class="sec"[\s\S]*)$/, '$1<div class="trio">$2</div>');
  return `<!doctype html><html lang="es"><meta charset="utf-8"><style>${CSS}</style><body class="${estilo}">${out}${contra}</body></html>`;
};

const cartel = async () => {
  if (!waNum) return null;
  const link = `https://wa.me/${waNum}?text=${encodeURIComponent("Hola, quiero hacer un pedido")}`;
  const qr = await QRCode.toString(link, { type: "svg", margin: 0, errorCorrectionLevel: "M", color: { dark: "#0A1230", light: "#0000" } });
  const visible = digitos.length === 8 ? `${digitos.slice(0, 4)}-${digitos.slice(4)}` : "+" + digitos;
  return `<!doctype html><html lang="es"><meta charset="utf-8"><style>
@font-face{font-family:H;src:url(${letra}) format("woff2");font-weight:100 900}
@page{size:Letter;margin:0}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font-family:H,system-ui,sans-serif}
.c{width:215.9mm;height:279.4mm;background:#0A1230;color:#F4F6FA;padding:20mm;display:flex;flex-direction:column;position:relative;overflow:hidden}
.fant{position:absolute;right:-40mm;bottom:-36mm;width:160mm;opacity:.07}.fant svg{width:100%;height:auto}
.r{font-size:11pt;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#9DB6FF}
h1{font-size:76pt;line-height:.9;letter-spacing:-.055em;margin:7mm 0 0;font-weight:800;color:#fff}
.s{font-size:16pt;line-height:1.35;color:#B7C1DD;margin:7mm 0 0;max-width:120mm}
.fila{margin-top:auto;display:flex;align-items:flex-end;gap:12mm;position:relative}
.q{width:88mm;height:88mm;padding:8mm;background:#fff;border-radius:7mm;flex:none}
.q svg{width:100%;height:100%;display:block}
.n{font-size:40pt;font-weight:800;letter-spacing:-.03em;line-height:1;color:#fff}
.p{font-size:12.5pt;line-height:1.45;color:#B7C1DD;margin-top:5mm}
.pie{margin-top:14mm;border-top:1px solid rgba(244,246,250,.18);padding-top:5mm;font-size:9.5pt;color:#B7C1DD;position:relative}
</style><body><div class="c"><div class="fant">${simbolo}</div>
<div class="r">${esc(a.restaurante)}</div>
<h1>Pedí por WhatsApp.</h1>
<p class="s">Te contestamos al instante, a cualquier hora.</p>
<div class="fila"><div class="q">${qr}</div><div><div class="n">${visible}</div><p class="p">Escaneá el código, escogé tu pedido y pasá a recogerlo cuando esté listo.</p></div></div>
<div class="pie">Casa Digital by Clientia Tech</div></div></body></html>`;
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
  // Chromium no siempre respeta break-inside:avoid; aquí se mide cada sección con el ancho de la hoja
  // y se manda a la página siguiente la que no cabe entera donde le toca.
  await p.setViewportSize({ width: Math.round(175.9 * 96 / 25.4), height: 1000 });
  await p.evaluate(alto => {
    const portada = document.querySelector(".portada");
    let tope = portada ? portada.getBoundingClientRect().bottom + scrollY : 0;
    for (const s of document.querySelectorAll("body>section.sec")) {
      const r = s.getBoundingClientRect(), y = r.top + scrollY;
      if (s.style.breakBefore === "page") { tope = y; continue; }
      if (y + r.height > tope + alto && r.height <= alto) { s.style.breakBefore = "page"; tope = y; }
      else if (r.height > alto) tope = y + r.height - ((y + r.height - tope) % alto);
    }
  }, 241.4 * 96 / 25.4);
  await p.pdf({ path: join(salida, nombre + ".pdf"), format: "Letter", printBackground: true, preferCSSPageSize: true });
  if (process.env.HTML) writeFileSync(join(salida, nombre + ".html"), html);
  await p.close();
  console.log("  " + nombre + ".pdf");
};
console.log(`Kit de ${a.restaurante} → ${salida}`);
for (const [nombre, archivo] of docs) await pdf(nombre, render(archivo));
const c = await cartel();
if (c) await pdf("cartel-whatsapp", c); else console.log("  (sin --numero no se hace el cartel con QR)");
await navegador.close();
