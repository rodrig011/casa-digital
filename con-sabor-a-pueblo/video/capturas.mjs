import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
const { chromium } = createRequire(import.meta.url)("playwright");
const panel = readFileSync(new URL("../../bot-restaurante/panel/panel.html", import.meta.url), "utf8");
const cfg = JSON.parse(readFileSync(new URL("../bot/sabor-pueblo-demo.json", import.meta.url), "utf8"));
let ped = JSON.parse(readFileSync(new URL("./src/pedidos-ejemplo.json", import.meta.url), "utf8"));
const est = { "PED-1001": "entregado", "PED-1002": "entregado", "PED-1003": "entregado", "PED-1004": "cocina", "PED-1005": "cocina", "PED-1006": "cocina" };
const now = Date.now();
ped = ped.map((p, i) => ({ ...p, estado: est[p.n] || p.estado, fecha: new Date(now - (i * 9 + 3) * 60000).toISOString() }));
const N = { nombre: cfg.nombre, color: cfg.color, cobro: false, reservaciones: false, cupos: null, sucursales: cfg.sucursales.map(({ id, nombre }) => ({ id, nombre })), menu: cfg.menu.flatMap(c => c.items.map(i => ({ id: i.id, nombre: i.nombre, categoria: c.categoria, precio: i.precio }))), modoIA: true, usuario: "Dueño" };
const OUT = process.argv[2];
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, locale: "es-HN", timezoneId: "America/Tegucigalpa" });
const page = await ctx.newPage();
await page.route("**/*", r => {
  const u = new URL(r.request().url());
  if (u.pathname === "/panel") return r.fulfill({ contentType: "text/html", body: panel });
  if (u.pathname === "/api/negocio") return r.fulfill({ json: N });
  if (u.pathname === "/api/pedidos") return r.fulfill({ json: ped });
  if (u.pathname === "/api/seguridad") return r.fulfill({ json: { usuarios: [], eventos: [] } });
  return r.fulfill({ status: 404, body: "" });
});
// pantallas de demostración: mismo panel, con una vista que todavía no existe en el sistema real
const DEMO = {
  repartidor: { titulo: "Entregas", base: "cocina", html: `
    <p class="ayuda">Lo que ve el repartidor en su celular: qué lleva, a dónde va y cuánto cobra. Al tocar <b>Entregado</b>, el pedido se cierra en el panel.</p>
    ${[["PED-1004", "Luis Fúnez", ["1 × Chicharrones de panceta", "1 × Chanchito chuko"], "L 330", "Tegucigalpa", "Col. Miraflores, calle principal, casa esquina color crema", "En camino"],
       ["PED-1001", "Karla Mejía", ["2 × Chanchito chuko"], "L 300", "Tegucigalpa", "Col. Kennedy, bloque 12, casa 4, portón verde", "Por salir"],
       ["PED-1005", "Familia Reyes", ["4 × Chanchito chuko", "2 × Sopa de gallina india"], "L 920", "San Pedro Sula", "Col. Trejo, 5 calle, casa blanca frente a la pulpería", "Por salir"]]
      .map(([n, nom, ls, tot, suc, dir, e], i) => `<div class="card ped ${i ? "nuevo" : "cocina-e"}">
        <div class="l1">${n} · ${nom}<span>${e}</span></div>
        <ul>${ls.map(l => `<li>${l}</li>`).join("")}</ul>
        <div class="l3"><span><b>Cobrar ${tot}</b> · ${suc}</span><span>Efectivo</span></div>
        <div class="l3"><span>🛵 ${dir}</span></div>
        <div class="acc"><button class="btn pri">${i ? "Salgo con este" : "Entregado"}</button><button class="btn">Abrir mapa</button><button class="btn">Llamar</button></div></div>`).join("")}` },
  proveedores: { titulo: "Proveedores", base: "hoy", html: `
    <div class="card frase">Para el sábado faltan <b>2 insumos</b>. El sistema ya le escribió a cada proveedor por WhatsApp.</div>
    <div class="card"><table><thead><tr><th>Insumo</th><th>Hay</th><th>Mínimo</th><th>Estado</th></tr></thead><tbody>
      <tr><td>Pierna de cerdo</td><td>18 lb</td><td>40 lb</td><td><span class="tag t-por_pagar">Pedido enviado</span></td></tr>
      <tr><td>Plátano</td><td>2 cajas</td><td>3 cajas</td><td><span class="tag t-por_pagar">Pedido enviado</span></td></tr>
      <tr><td>Repollo</td><td>14</td><td>8</td><td><span class="tag t-comp">Bien</span></td></tr>
      <tr><td>Tortillas</td><td>300</td><td>200</td><td><span class="tag t-comp">Bien</span></td></tr>
      <tr><td>Bandejas</td><td>250</td><td>150</td><td><span class="tag t-comp">Bien</span></td></tr>
    </tbody></table></div>
    <div class="card ped nuevo"><div class="l1">Proveedor de cerdo<span>WhatsApp · hace 5 min</span></div>
      <ul><li style="font-weight:400">“Buenas, de parte de Con Sabor a Pueblo. Para el sábado necesitamos 25 lb de pierna de cerdo. ¿Me confirma si la tiene?”</li></ul>
      <div class="l3"><span><span class="tag t-por_pagar">Esperando respuesta</span></span><span>Entrega: viernes</span></div></div>
    <div class="card ped listo"><div class="l1">Proveedor de plátano<span>WhatsApp · hace 5 min</span></div>
      <ul><li style="font-weight:400">“Buenas, de parte de Con Sabor a Pueblo. Para el sábado necesitamos 1 caja de plátano. ¿Me confirma?”</li></ul>
      <div class="l3"><span><span class="tag t-comp">Confirmado</span></span><span>“Sí, se la llevo el viernes”</span></div></div>` },
};
for (const v of ["hoy", "pedidos", "cocina", "repartidor", "proveedores"]) {
  const d = DEMO[v];
  await page.setViewportSize({ width: 390, height: 844 });
  await page.addInitScript(v => { try { localStorage.setItem("vista", v); } catch {} }, d ? d.base : v);
  await page.goto("http://panel.local/panel");
  await page.waitForTimeout(900);
  if (d) await page.evaluate(d => {
    document.querySelector("#titulo").textContent = d.titulo;
    document.querySelector("#vista").innerHTML = d.html;
    document.querySelectorAll(".nav[aria-current]").forEach(n => n.removeAttribute("aria-current"));
    document.querySelector("#suc").style.display = d.titulo === "Entregas" ? "" : "none";
  }, d);
  // sin la barra de abajo (queda fija a media captura) y sin el aviso "sonido"
  await page.addStyleTag({ content: ".tabs{display:none!important}" });
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  await page.setViewportSize({ width: 390, height: h });
  await page.waitForTimeout(200);
  await page.screenshot({ path: `${OUT}/panel-${v}.jpg`, type: "jpeg", quality: 90 });
  console.log(v, h);
}
await b.close();
