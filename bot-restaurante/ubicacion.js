// Ubicación del repartidor en tiempo real, sin instalar nada.
//
// Cuando el repartidor contesta SALGO, el bot le manda un link (/r/<código>): lo abre en el celular, toca
// «Compartir mi ubicación» y deja la página abierta. Al cliente le llega otro link (/seguir/<código>) con
// el mapa: ve dónde va el repartidor, cada pocos segundos, hasta que el pedido se entrega.
//
// - Cada link es un código al azar de 128 bits, distinto para el repartidor y para el cliente: con el del
//   cliente nadie puede mover el punto, y sin el código no se ve nada.
// - La ubicación solo vive en la memoria del servidor (no se guarda en el disco) y se borra al entregar.
// - Al entregar o cancelar, los dos links dejan de funcionar.
const crypto = require("crypto");

const VENCE_MIN = 30;   // a position older than this is not shown as "live"

function createUbicacion({ store, negocio, now = () => new Date(), base = "" }) {
  const posiciones = new Map();   // pedido n -> { lat, lng, acc, t }
  const codigo = () => crypto.randomBytes(16).toString("base64url");
  const activo = !!base;

  // the two links for an order that just left with its driver (created once)
  function preparar(p) {
    if (!activo) return p;
    if (p.seguimiento && p.seguimiento.rep && p.seguimiento.cli) return p;
    return store.updatePedido(p.n, { seguimiento: { rep: codigo(), cli: codigo() } });
  }
  const links = p => activo && p.seguimiento ? { rep: `${base}/r/${p.seguimiento.rep}`, cli: `${base}/seguir/${p.seguimiento.cli}` } : null;
  const buscar = (campo, t) => typeof t === "string" && t.length >= 20 ? store.pedidos.findLast(p => p.seguimiento && p.seguimiento[campo] === t) : null;
  const abierto = p => p && ["listo", "en_camino"].includes(p.estado);

  function montar(app, express) {
    const cabeceras = res => res.set({ "Cache-Control": "no-store", "Referrer-Policy": "no-referrer", "X-Robots-Tag": "noindex",
      "Content-Security-Policy": "default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; frame-src https://www.openstreetmap.org; base-uri 'none'; form-action 'none'" });

    // the driver's page: shares the phone's location while it is open
    app.get("/r/:t", (req, res) => {
      const p = buscar("rep", req.params.t);
      cabeceras(res).type("html");
      if (!p) return res.status(404).send(pagina({ titulo: "Link vencido", cuerpo: `<p class="nota">Este link ya no funciona.</p>` }));
      res.send(pagina({ titulo: `${p.n} · Compartir ubicación`, cuerpo: repartidorHTML(p), script: repartidorJS }));
    });
    app.post("/r/:t", express.json({ limit: "1kb" }), (req, res) => {
      const p = buscar("rep", req.params.t);
      cabeceras(res);
      if (!p) return res.status(404).json({ fin: true });
      if (!abierto(p)) { posiciones.delete(p.n); return res.status(410).json({ fin: true, estado: p.estado }); }
      const lat = +req.body.lat, lng = +req.body.lng, acc = Math.min(5000, Math.max(0, +req.body.acc || 0));
      if (!Number.isFinite(lat) || !Number.isFinite(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180) return res.status(400).json({ error: "ubicación inválida" });
      posiciones.set(p.n, { lat: +lat.toFixed(6), lng: +lng.toFixed(6), acc: Math.round(acc), t: now().toISOString() });
      res.json({ ok: true });
    });

    // the customer's page: the map
    app.get("/seguir/:t", (req, res) => {
      const p = buscar("cli", req.params.t);
      cabeceras(res).type("html");
      if (!p) return res.status(404).send(pagina({ titulo: "Link vencido", cuerpo: `<p class="nota">Este link ya no funciona.</p>` }));
      res.send(pagina({ titulo: `Su pedido ${p.n}`, cuerpo: clienteHTML(p, negocio), script: clienteJS }));
    });
    app.get("/seguir/:t/donde", (req, res) => {
      const p = buscar("cli", req.params.t);
      cabeceras(res);
      if (!p) return res.status(404).json({ fin: true });
      const pos = posiciones.get(p.n);
      const viva = pos && now() - new Date(pos.t) < VENCE_MIN * 60e3;
      res.json({ estado: p.estado, repartidor: p.repartidor ? p.repartidor.nombre : "", pos: abierto(p) && viva ? pos : null, fin: !abierto(p) });
    });
  }

  // when the order is closed the position is dropped
  function cerrar(p) { posiciones.delete(p.n); }

  return { activo, preparar, links, montar, cerrar, _posiciones: posiciones };
}

const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function pagina({ titulo, cuerpo, script = "" }) {
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>${esc(titulo)}</title><meta name="theme-color" content="#ffffff">
<style>
*{box-sizing:border-box}body{margin:0;font:400 15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;color:#181818;background:#F3F3F3;-webkit-font-smoothing:antialiased}
main{max-width:520px;margin:0 auto;padding:16px;display:grid;gap:12px}
.card{background:#fff;border:1px solid #E5E5E5;border-radius:12px;padding:16px}
h1{font-size:18px;margin:0}p{margin:0}.sub{color:#706E6B;font-size:13px}
.nota{color:#706E6B;text-align:center;padding:40px 16px}
.estado{display:flex;align-items:center;gap:8px;font-weight:600}.punto{width:10px;height:10px;border-radius:50%;background:#C9C9C9;flex:none}.punto.vivo{background:#2E844A;box-shadow:0 0 0 4px rgba(46,132,74,.18)}
button{width:100%;height:52px;border:0;border-radius:12px;background:#0176D3;color:#fff;font:inherit;font-size:16px;font-weight:600;cursor:pointer}button:disabled{background:#C9C9C9}
button.parar{background:#fff;color:#BA0517;border:1px solid #E5E5E5}
.mapa{height:min(62vh,460px);padding:0;overflow:hidden}.mapa iframe{width:100%;height:100%;border:0;display:block}
.vacio{height:100%;display:grid;place-items:center;color:#706E6B;text-align:center;padding:24px}
</style></head><body><main>${cuerpo}</main><script>${script}</script></body></html>`;
}

function repartidorHTML(p) {
  return `<div class="card"><h1>${esc(p.n)} · ${esc(p.nombre || "Cliente")}</h1><p class="sub">📍 ${esc(p.direccion || "")}</p></div>
<div class="card" style="display:grid;gap:12px">
  <div class="estado"><span class="punto" id="punto"></span><span id="estado">Todavía no comparte su ubicación</span></div>
  <p class="sub">El cliente ve en un mapa dónde va usted mientras esta página esté abierta. Al entregar, deja de compartirse sola.</p>
  <button id="btn">Compartir mi ubicación</button>
</div>`;
}
const repartidorJS = `
const btn=document.getElementById("btn"),est=document.getElementById("estado"),pt=document.getElementById("punto");let id=null,lock=null,ult=0;
function parar(t){if(id!==null)navigator.geolocation.clearWatch(id);id=null;pt.classList.remove("vivo");est.textContent=t;btn.textContent="Compartir mi ubicación";btn.className="";if(lock)lock.release().catch(()=>{});lock=null}
async function mandar(c){const ahora=Date.now();if(ahora-ult<8000)return;ult=ahora;
  try{const r=await fetch(location.pathname,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({lat:c.latitude,lng:c.longitude,acc:c.accuracy})});
    if(r.status===410||r.status===404){btn.disabled=true;return parar("Pedido entregado. Ya no se comparte su ubicación.")}
    pt.classList.add("vivo");est.textContent="Compartiendo · "+new Date().toLocaleTimeString("es-HN",{hour:"numeric",minute:"2-digit"})}catch(e){est.textContent="Sin señal, reintentando…"}}
btn.onclick=async()=>{if(id!==null)return parar("Dejó de compartir su ubicación");
  if(!navigator.geolocation)return est.textContent="Este teléfono no deja compartir la ubicación";
  est.textContent="Pidiendo permiso…";
  id=navigator.geolocation.watchPosition(x=>mandar(x.coords),e=>parar(e.code===1?"Necesita permitir la ubicación en el navegador":"No se pudo leer la ubicación"),{enableHighAccuracy:true,maximumAge:5000,timeout:20000});
  btn.textContent="Dejar de compartir";btn.className="parar";
  try{lock=await navigator.wakeLock.request("screen")}catch(e){}};`;

function clienteHTML(p, negocio) {
  return `<div class="card"><h1>Su pedido ${esc(p.n)}</h1><p class="sub">${esc(negocio ? negocio.nombre : "")}${p.repartidor ? ` · lo lleva ${esc(p.repartidor.nombre)}` : ""}</p></div>
<div class="card"><div class="estado"><span class="punto" id="punto"></span><span id="estado">Buscando al repartidor…</span></div></div>
<div class="card mapa" id="mapa"><div class="vacio">Cuando el repartidor comparta su ubicación, aquí lo verá en el mapa.</div></div>`;
}
const clienteJS = `
const est=document.getElementById("estado"),pt=document.getElementById("punto"),mapa=document.getElementById("mapa");let antes=null,fin=false;
const lejos=(a,b)=>!a||Math.hypot(a.lat-b.lat,(a.lng-b.lng)*Math.cos(b.lat*Math.PI/180))*111000>25;
async function ver(){if(fin)return;try{const r=await fetch(location.pathname.replace(/\\/$/,"")+"/donde",{cache:"no-store"});const d=await r.json();
  if(d.fin){fin=true;pt.classList.remove("vivo");est.textContent=d.estado==="entregado"?"✅ Su pedido fue entregado. ¡Gracias!":"Este seguimiento terminó.";return}
  if(!d.pos){est.textContent=(d.repartidor||"El repartidor")+" todavía no comparte su ubicación";return}
  pt.classList.add("vivo");const h=new Date(d.pos.t);est.textContent=(d.repartidor||"Repartidor")+" va en camino · "+h.toLocaleTimeString("es-HN",{hour:"numeric",minute:"2-digit"});
  if(lejos(antes,d.pos)){antes=d.pos;const z=.006,b=[d.pos.lng-z,d.pos.lat-z*.7,d.pos.lng+z,d.pos.lat+z*.7].join(",");
    mapa.innerHTML='<iframe title="Mapa" src="https://www.openstreetmap.org/export/embed.html?bbox='+b+'&layer=mapnik&marker='+d.pos.lat+','+d.pos.lng+'"></iframe>'}
}catch(e){est.textContent="Sin conexión, reintentando…"}}
ver();setInterval(ver,10000);`;

module.exports = { createUbicacion };
