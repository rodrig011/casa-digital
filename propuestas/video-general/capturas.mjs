// Capturas del panel REAL (bot-restaurante/panel/panel.html) con un negocio neutro ("Su Restaurante") y pedidos de EJEMPLO.
// Nada aquí es de un restaurante real: el menú sale de bot-restaurante/negocios/ejemplo.json.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const panel = readFileSync(path.join(HERE, "../../bot-restaurante/panel/panel.html"), "utf8");

const MENU = [
  ["c2", "Combo 2 piezas", "Combos", 115], ["c3", "Combo 3 piezas", "Combos", 150], ["fam", "Combo familiar 8 piezas", "Combos", 420],
  ["papas", "Papas grandes", "Extras", 45], ["ref", "Refresco 2 litros", "Extras", 55],
];
const SUC = [{ id: "principal", nombre: "Principal" }];
const EJ = [
  ["Ana M.", [["c2", 2], ["ref", 1]], "cocina", "domicilio", "Col. Kennedy, bloque 3, casa 12"],
  ["Carlos R.", [["fam", 1]], "nuevo", "recoger", "7:40 pm"],
  ["Familia Zelaya", [["fam", 1], ["papas", 2]], "cocina", "recoger", "7:30 pm"],
  ["Josué P.", [["c3", 2]], "cocina", "domicilio", "Res. El Trapiche, bloque B, casa 4"],
  ["Mariela S.", [["c2", 1], ["papas", 1]], "listo", "recoger", "7:15 pm"],
  ["Óscar L.", [["c3", 1], ["ref", 1]], "entregado", "recoger", "6:50 pm"],
  ["Denis A.", [["fam", 1], ["ref", 1]], "entregado", "domicilio", "Col. Miraflores, casa 2210"],
  ["Karen V.", [["c2", 3]], "entregado", "recoger", "6:40 pm"],
  ["Luis F.", [["c3", 1], ["papas", 1]], "entregado", "recoger", "6:20 pm"],
];
const now = new Date("2026-11-13T19:06:00-06:00").getTime();   // viernes 7:06 pm en Honduras
const ped = EJ.map(([nombre, ls, estado, entrega, donde], i) => {
  const lineas = ls.map(([id, cantidad]) => { const m = MENU.find(x => x[0] === id); return { id, nombre: m[1], precio: m[3], cantidad, subtotal: m[3] * cantidad }; });
  const total = lineas.reduce((a, l) => a + l.subtotal, 0);
  return { tipo: "pedido", n: "PED-" + (1012 - i), nombre, sucursal: "Principal", sucursalId: "principal", lineas, total,
    resumen: lineas.map(l => `${l.cantidad} × ${l.nombre}`).join(" · "), tel: "+5040000" + String(1000 + i),
    ...(entrega === "domicilio" ? { entrega: "domicilio", direccion: donde, hora: "A domicilio, lo antes posible" } : { hora: donde }),
    fecha: new Date(now - (i * 9 + 1) * 60000).toISOString(), estado };
});
const N = { nombre: "Su Restaurante", color: "#1B1B1A", cobro: false, reservaciones: false, cupos: null, sucursales: SUC,
  menu: MENU.map(([id, nombre, categoria, precio]) => ({ id, nombre, categoria, precio })), modoIA: true, usuario: "Dueño" };

const b = await chromium.launch();
const ir = async (vista, w, h, dsf) => {
  const c = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: dsf, locale: "es-HN", timezoneId: "America/Tegucigalpa", colorScheme: "light" });
  const p = await c.newPage(); await p.clock.setFixedTime(new Date(now));
  await p.route("**/*", r => { const u = new URL(r.request().url());
    if (u.pathname === "/panel") return r.fulfill({ contentType: "text/html", body: panel });
    if (u.pathname === "/api/negocio") return r.fulfill({ json: N });
    if (u.pathname === "/api/pedidos") return r.fulfill({ json: ped });
    if (u.pathname === "/api/seguridad") return r.fulfill({ json: { usuarios: [], eventos: [] } });
    return r.fulfill({ status: 404, body: "" }); });
  await p.addInitScript(([v]) => { try { localStorage.setItem("vista", v); localStorage.setItem("suc", ""); localStorage.setItem("tema", "light"); localStorage.setItem("modoPedidos", "tablero"); } catch {} }, [vista]);
  await p.goto("http://panel.local/panel"); await p.waitForTimeout(900);
  return p;
};
const out = n => path.join(HERE, "src", n);
// El panel en un celular (390 x 760) a 3x: se muestra a 690 px de ancho sin agrandar pixeles.
let p = await ir("hoy", 390, 760, 3);
await p.screenshot({ path: out("panel-hoy.jpg"), type: "jpeg", quality: 92 });
// La tarjeta de un pedido en la pantalla de cocina, a 3x.
p = await ir("cocina", 1180, 820, 3);
const cartas = p.locator(".cocina > .card");
for (let i = 0; i < await cartas.count(); i++) if ((await cartas.nth(i).innerText()).includes("Ana")) {
  await cartas.nth(i).screenshot({ path: out("pieza-pedido.png") });
  console.log("boton Listo", JSON.stringify(await cartas.nth(i).evaluate(c => { const r = c.getBoundingClientRect(), q = c.querySelector(".btn.pri").getBoundingClientRect(); return [r.width, r.height, q.x - r.x, q.y - r.y, q.width, q.height]; })));
}
await b.close();
