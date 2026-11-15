// Capturas del panel REAL (bot-restaurante/panel/panel.html) con el menú de Loca Luna y pedidos de ejemplo.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const panel = readFileSync(path.join(HERE, "../../bot-restaurante/panel/panel.html"), "utf8");

// Nombres y precios tal como están en su menú (PDF de su Linktree).
const MENU = [
  ["alas12", "Alas de Pollo 12 unid.", "Pollo", 320], ["alas6", "Alas de Pollo 6 unid.", "Pollo", 190],
  ["bon12", "Boneless 12 unid.", "Pollo", 330], ["bon6", "Boneless 6 unid.", "Pollo", 200],
  ["fing6", "Chicken Fingers 6 unid.", "Pollo", 220], ["chuco", "Pollo Chuco", "Pollo", 250],
  ["papasprep", "Papas Preparadas", "Entradas", 200], ["patatas", "Patatas", "Entradas", 250],
  ["aros", "Aros de Cebolla", "Entradas", 130], ["mozza5", "Mozzarella Sticks 5 unid.", "Entradas", 170],
  ["costilla", "Costilla de Cerdo", "Carnes", 350], ["nachosmix", "Nachos Mixto", "Nachos", 280],
  ["lovers", "Chicken Lovers", "Samplers", 620],
];
const SUC = [{ id: "castanos", nombre: "Los Castaños" }, { id: "hadas", nombre: "Las Hadas" }, { id: "choluteca", nombre: "Choluteca" }];
// Pedidos de EJEMPLO: clientes, cantidades y horas inventados para mostrar el panel.
const EJ = [
  ["hadas", "Carlos M.", [["alas12", 1, "Búfalo"]], "cocina", "recoger", "7:40 pm"],
  ["castanos", "Andrea R.", [["bon12", 1, "Honey Mustard"], ["papasprep", 1]], "nuevo", "domicilio", "Col. Lomas del Guijarro, casa 12"],
  ["hadas", "Familia Zelaya", [["lovers", 1], ["aros", 1]], "cocina", "recoger", "7:30 pm"],
  ["choluteca", "Josué P.", [["alas12", 2, "Barbacoa"]], "cocina", "recoger", "7:30 pm"],
  ["castanos", "Mariela S.", [["alas6", 1, "Loca Luna"], ["mozza5", 1]], "cocina", "recoger", "7:20 pm"],
  ["hadas", "Óscar L.", [["costilla", 1], ["patatas", 1]], "listo", "recoger", "7:15 pm"],
  ["castanos", "Denis A.", [["alas12", 1, "Mango Habanero"], ["fing6", 1]], "entregado", "recoger", "6:50 pm"],
  ["choluteca", "Karen V.", [["bon6", 1, "Sweet Chili"], ["nachosmix", 1]], "entregado", "recoger", "6:40 pm"],
  ["castanos", "Luis F.", [["lovers", 1]], "entregado", "domicilio", "Res. El Trapiche, bloque B"],
  ["hadas", "Paola G.", [["alas12", 1, "Búfalo Parmesano"], ["papasprep", 1]], "entregado", "recoger", "6:20 pm"],
  ["castanos", "Ramón E.", [["bon12", 1, "Jack Daniel's"], ["aros", 1]], "entregado", "recoger", "6:05 pm"],
  ["choluteca", "Sofía B.", [["alas6", 2, "Piña Habanero"]], "entregado", "recoger", "5:50 pm"],
];
const now = new Date("2026-11-14T19:42:00-06:00").getTime();   // sábado 7:42 pm en Honduras, para que las horas de ejemplo cuadren
const ped = EJ.map(([sid, nombre, ls, estado, entrega, donde], i) => {
  const lineas = ls.map(([id, cantidad, salsa]) => { const m = MENU.find(x => x[0] === id); return { id, nombre: m[1] + (salsa ? ` · salsa ${salsa}` : ""), precio: m[3], cantidad, subtotal: m[3] * cantidad }; });
  const total = lineas.reduce((a, l) => a + l.subtotal, 0);
  return { tipo: "pedido", n: "PED-" + (1012 - i), nombre, sucursal: SUC.find(s => s.id === sid).nombre, sucursalId: sid, lineas, total,
    resumen: lineas.map(l => `${l.cantidad} × ${l.nombre}`).join(" · "), tel: "+5049999" + String(1000 + i),
    ...(entrega === "domicilio" ? { entrega: "domicilio", direccion: donde, hora: "A domicilio, lo antes posible" } : { hora: donde }),
    fecha: new Date(now - (i * 11 + 2) * 60000).toISOString(), estado };
});
const N = { nombre: "Loca Luna", color: "#FFC629", cobro: false, reservaciones: false, cupos: null, sucursales: SUC,
  menu: MENU.map(([id, nombre, categoria, precio]) => ({ id, nombre, categoria, precio })), modoIA: true, usuario: "Dueño" };

const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1180, height: 820 }, deviceScaleFactor: 2, locale: "es-HN", timezoneId: "America/Tegucigalpa", colorScheme: "light" });
const page = await ctx.newPage();
await page.clock.setFixedTime(new Date(now));
await page.route("**/*", r => {
  const u = new URL(r.request().url());
  if (u.pathname === "/panel") return r.fulfill({ contentType: "text/html", body: panel });
  if (u.pathname === "/api/negocio") return r.fulfill({ json: N });
  if (u.pathname === "/api/pedidos") return r.fulfill({ json: ped });
  if (u.pathname === "/api/seguridad") return r.fulfill({ json: { usuarios: [], eventos: [] } });
  return r.fulfill({ status: 404, body: "" });
});
// Pantalla completa en tamaño tablet (1180 x 820) y, aparte, cada pieza a 3x para mostrarla grande sin agrandar pixeles.
const ir = async (vista, suc, dsf) => {
  const c = await b.newContext({ viewport: { width: 1180, height: 820 }, deviceScaleFactor: dsf, locale: "es-HN", timezoneId: "America/Tegucigalpa", colorScheme: "light" });
  const p = await c.newPage(); await p.clock.setFixedTime(new Date(now));
  await p.route("**/*", r => { const u = new URL(r.request().url());
    if (u.pathname === "/panel") return r.fulfill({ contentType: "text/html", body: panel });
    if (u.pathname === "/api/negocio") return r.fulfill({ json: N });
    if (u.pathname === "/api/pedidos") return r.fulfill({ json: ped });
    if (u.pathname === "/api/seguridad") return r.fulfill({ json: { usuarios: [], eventos: [] } });
    return r.fulfill({ status: 404, body: "" }); });
  await p.addInitScript(([v, s]) => { try { localStorage.setItem("vista", v); localStorage.setItem("suc", s); localStorage.setItem("tema", "light"); localStorage.setItem("modoPedidos", "tablero"); } catch {} }, [vista, suc]);
  await p.goto("http://panel.local/panel"); await p.waitForTimeout(900);
  return p;
};
const out = n => path.join(HERE, "src", n);
let p = await ir("hoy", "", 2); await p.screenshot({ path: out("panel-hoy.jpg"), type: "jpeg", quality: 90 });
p = await ir("hoy", "", 3);
await p.locator(".grid2 > .card").nth(1).screenshot({ path: out("pieza-sucursal.png") });
p = await ir("cocina", "hadas", 3);
const cartas = p.locator(".cocina > .card");
for (let i = 0; i < await cartas.count(); i++) if ((await cartas.nth(i).innerText()).includes("Carlos")) {
  await cartas.nth(i).screenshot({ path: out("pieza-pedido.png") });
  console.log("boton Listo", JSON.stringify(await cartas.nth(i).evaluate(c => { const r = c.getBoundingClientRect(), q = c.querySelector(".btn.pri").getBoundingClientRect(); return [r.width, r.height, q.x - r.x, q.y - r.y, q.width, q.height]; })));
}
await b.close();
