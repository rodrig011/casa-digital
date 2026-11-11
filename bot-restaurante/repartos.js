// Repartidores propios del restaurante (negocio.repartidores): el bot reparte los envíos solo, por WhatsApp.
//
// 1. Cuando la cocina marca Listo un pedido a domicilio, el bot escoge al repartidor de esa sucursal que menos
//    entregas tiene en la calle (si empatan, al que hace más rato no recibe una) y le manda por WhatsApp
//    qué lleva, a dónde, cuánto cobra, el teléfono del cliente y el mapa.
// 2. Al cliente le llega "su pedido está listo, lo lleva Carlos"; al dueño y a la sucursal, a quién se asignó.
// 3. El repartidor contesta en el mismo WhatsApp del negocio:
//      SALGO      -> el pedido pasa a "En camino" y al cliente le llega "va en camino con Carlos"
//      ENTREGADO  -> el pedido se cierra y al cliente le llega "entregado, gracias"
//      NO PUEDO   -> el bot se lo pasa al siguiente repartidor (si no hay otro, avisa al dueño)
//      cualquier otra cosa -> le recuerda sus entregas pendientes
//    Con dos o más entregas puede decir el número: "entregado 1004".
// Los repartidores no necesitan instalar nada ni entrar al panel. Desde el panel se puede marcar En camino,
// Entregado o pasar el pedido a otro repartidor.
const { waAddr, digits } = require("./avisos");
const { lineaTexto } = require("./negocio");

const EN_CALLE = ["listo", "en_camino"];
const BOTONES = ["Salgo con el pedido", "Entregado", "No puedo llevarlo"];
const norm = s => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();

// "repartidores": [{ "id": "carlos", "nombre": "Carlos", "whatsapp": "+504 9999-0000", "sucursal": "tegucigalpa" }]
// sucursal es opcional: sin ella, el repartidor lleva pedidos de todas las sucursales.
function prepararRepartidores(rs, sucursales) {
  if (!rs) return [];
  if (!Array.isArray(rs)) throw new Error("repartidores: debe ser una lista");
  const ids = new Set(), tels = new Set(), errores = [];
  const out = rs.map((r, i) => {
    const id = String(r.id || "").trim() || `r${i + 1}`, d = digits(r.whatsapp), tel = d.length === 8 ? "504" + d : d;
    if (!r.nombre) errores.push(`repartidor ${id}: falta nombre`);
    if (d.length < 8) errores.push(`repartidor ${id}: falta su WhatsApp`);
    if (ids.has(id)) errores.push(`repartidor repetido: ${id}`);
    if (tels.has(tel)) errores.push(`dos repartidores con el mismo WhatsApp: ${r.whatsapp}`);
    if (r.sucursal && !sucursales.some(s => s.id === r.sucursal)) errores.push(`repartidor ${id}: la sucursal "${r.sucursal}" no existe`);
    ids.add(id); tels.add(tel);
    return { id, nombre: String(r.nombre || "").trim(), tel, sucursal: r.sucursal || "" };
  });
  if (errores.length) throw new Error(errores.join("; "));
  return out;
}

const mapa = (p, negocio) => {
  const b = negocio.sucursales.find(s => s.nombre === p.sucursal);
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${p.direccion}, ${b ? b.nombre : ""}, ${negocio.pais}`)}`;
};

function createRepartos({ negocio, store, avisos, now, log = console.log, track = x => x }) {
  const lista = negocio.repartidores || [];
  const activo = lista.length > 0;
  const nom = p => (p.nombre || "Hola").split(" ")[0];
  const deTel = from => lista.find(r => r.tel === digits(from)) || null;
  const enCalle = r => store.pedidos.filter(p => p.repartidor && p.repartidor.id === r.id && EN_CALLE.includes(p.estado));
  const aDueno = (p, titulo, lineas) => Promise.all(avisos.destinos(p.sucursal).map(to => avisos.enviar(to, `🛵 *${titulo}*\n\n${lineas.join("\n")}`, { titulo, lineas })));

  function fichaRepartidor(p, r) {
    const titulo = `Entrega ${p.n} · ${p.sucursal}`;
    const lineas = [
      `👤 ${p.nombre || "Sin nombre"} · +${digits(p.tel)}`,
      `📍 ${p.direccion}`,
      ...(p.lineas || []).map(l => lineaTexto(l, negocio.L)),
      `💰 Cobrar ${negocio.L(p.total)}${p.pagado ? " (ya pagó)" : ""}`,
      `Mapa: ${mapa(p, negocio)}`,
      `Cliente: https://wa.me/${digits(p.tel)}`,
    ];
    const body = `🛵 *${r.nombre}, tiene una entrega: ${p.n}*\n\n${lineas.join("\n")}\n\nConteste *SALGO* cuando salga, *ENTREGADO* cuando lo entregue o *NO PUEDO* para pasárselo a otro.`;
    return { titulo, lineas: [...lineas, "Conteste SALGO, ENTREGADO o NO PUEDO"], body };
  }

  // the free-est driver of the order's branch; ties go to whoever waited longest for a delivery
  function escoger(p, excluir = []) {
    const b = negocio.sucursales.find(s => s.nombre === p.sucursal);
    const ok = lista.filter(r => !excluir.includes(r.id) && (!r.sucursal || (b && r.sucursal === b.id)));
    const ultima = r => Math.max(0, ...store.pedidos.filter(x => x.repartidor && x.repartidor.id === r.id).map(x => new Date(x.t_asignado || 0).getTime()));
    return ok.map(r => [r, enCalle(r).length, ultima(r)]).sort((a, b) => a[1] - b[1] || a[2] - b[2])[0]?.[0] || null;
  }

  // the kitchen marked a delivery order ready (or the owner asks for another driver)
  function asignar(n, { excluir = [], por = "bot" } = {}) {
    const p = store.getPedido(n);
    if (!p || p.entrega !== "domicilio" || !activo) return null;
    const r = escoger(p, excluir);
    if (!r) {
      store.updatePedido(n, { repartidor: null });
      log(`[${n}] sin repartidor disponible`);
      track(aDueno(p, `${p.n} no tiene repartidor`, [`📍 ${p.direccion}`, "Ningún repartidor lo pudo llevar. Escríbale a uno o asígnelo desde el panel."]));
      return null;
    }
    const antes = p.repartidor;
    const q = store.updatePedido(n, { repartidor: { id: r.id, nombre: r.nombre, tel: "+" + r.tel }, t_asignado: now().toISOString(), rechazos: excluir, asignadoPor: por });
    const f = fichaRepartidor(q, r);
    log(`[${n}] asignado a ${r.nombre}${antes ? ` (antes ${antes.nombre})` : ""}`);
    track(avisos.enviar(waAddr(r.tel), f.body, f));
    const previo = antes && antes.id !== r.id && por !== "repartidor:" + antes.id && lista.find(x => x.id === antes.id);
    if (previo) track(avisos.enviar(waAddr(previo.tel), `ℹ️ ${previo.nombre}, la entrega *${q.n}* se le pasó a ${r.nombre}. Ya no tiene que llevarla.`));
    if (!antes) track(avisos.enviar(waAddr(q.tel), `✅ ¡${nom(q)}, su pedido *${q.n}* ya está listo! Lo lleva *${r.nombre}*; le avisamos por aquí cuando salga.`));
    track(aDueno(q, `${q.n} asignado a ${r.nombre}`, [`📍 ${q.direccion}`, `💰 ${negocio.L(q.total)}`, antes ? `${antes.nombre} no lo pudo llevar.` : "Se le avisó por WhatsApp."]));
    return q;
  }

  // what the customer hears when the order leaves or arrives (from the driver's WhatsApp or the panel)
  function enCamino(p) {
    const quien = p.repartidor ? ` con *${p.repartidor.nombre}*` : "";
    return avisos.enviar(waAddr(p.tel), `🛵 ¡${nom(p)}, su pedido *${p.n}* ya va en camino${quien}! Total: ${negocio.L(p.total)}.`);
  }
  function entregado(p) {
    return avisos.enviar(waAddr(p.tel), `✅ ${nom(p)}, su pedido *${p.n}* fue entregado. ¡Gracias por su compra en *${negocio.nombre}*!`);
  }

  // a message from a driver's number -> the bot's replies, or null if it is not a driver
  function mensaje(from, text) {
    const r = deTel(from);
    if (!r) return null;
    const t = norm(text);
    const mios = enCalle(r).sort((a, b) => new Date(a.t_asignado) - new Date(b.t_asignado));
    const lista = () => mios.map(p => `• *${p.n}* · ${ESTADO[p.estado]} · ${p.nombre || "Sin nombre"} · ${p.direccion}`).join("\n");
    const accion = t === "1" || /\bsalgo\b|\bsali\b|\bvoy\b|en camino/.test(t) ? "salgo"
      : t === "2" || /entregad|\bentregue\b|\blisto\b/.test(t) ? "entregado"
      : t === "3" || /no puedo|no lo puedo|no voy|otro/.test(t) ? "nopuedo" : null;
    if (!mios.length) return [{ text: `Hola, ${r.nombre}. No tiene entregas pendientes. Cuando haya una, le llega por aquí.` }];
    if (!accion) return [{ text: `${r.nombre}, sus entregas:\n${lista()}`, buttons: BOTONES }];
    // which order: the number in the message, else the only one that fits. SALGO with several ready takes them all.
    const num = (text.match(/\d{3,}/) || [])[0];
    const listos = mios.filter(x => x.estado === "listo"), saliendo = mios.filter(x => x.estado === "en_camino");
    let ps = num ? mios.filter(x => x.n.replace(/\D/g, "").endsWith(num))
      : accion === "salgo" ? (listos.length ? listos : mios)
      : accion === "entregado" ? (mios.length === 1 ? mios : saliendo.length === 1 ? saliendo : [])
      : listos.length === 1 ? listos : mios.length === 1 ? mios : [];
    if (ps.length !== 1 && !(accion === "salgo" && ps.length)) {
      const verbo = accion === "entregado" ? "ENTREGADO" : accion === "salgo" ? "SALGO" : "NO PUEDO";
      return [{ text: `${r.nombre}, ${num ? `no encuentro la entrega ${num} entre las suyas` : "tiene varias entregas"}. Escriba el número, por ejemplo *${verbo} ${mios[0].n.replace(/\D/g, "")}*:\n${lista()}` }];
    }
    const t0 = now().toISOString();
    const p = ps[0];
    if (accion === "salgo") {
      const van = ps.filter(x => x.estado === "listo");
      if (!van.length) return [{ text: `${p.n} ya estaba en camino. Cuando lo entregue, conteste *ENTREGADO*.`, buttons: ["Entregado"] }];
      for (const x of van) {
        const q = store.updatePedido(x.n, { estado: "en_camino", t_en_camino: t0, por: "repartidor:" + r.id });
        track(enCamino(q));
        log(`[${x.n}] en camino con ${r.nombre}`);
      }
      const det = van.map(x => `*${x.n}* · ${x.nombre || "Sin nombre"}\n📍 ${x.direccion}\nMapa: ${mapa(x, negocio)}`).join("\n\n");
      return [{ text: `👍 Listo, ${r.nombre}. Le avisamos ${van.length > 1 ? "a los clientes" : "al cliente"} que va en camino.\n\n${det}\n\nCuando ${van.length > 1 ? "entregue cada uno, conteste *ENTREGADO* con el número" : "lo entregue, conteste *ENTREGADO*"}.`, buttons: ["Entregado"] }];
    }
    if (accion === "entregado") {
      const q = store.updatePedido(p.n, { estado: "entregado", t_entregado: t0, por: "repartidor:" + r.id });
      track(entregado(q));
      track(aDueno(q, `${q.n} entregado por ${r.nombre}`, [`💰 ${negocio.L(q.total)}`, `📍 ${q.direccion}`]));
      log(`[${p.n}] entregado por ${r.nombre}`);
      const quedan = mios.filter(x => x.n !== p.n);
      return [{ text: `✅ Gracias, ${r.nombre}. *${p.n}* quedó entregado.${quedan.length ? `\n\nLe quedan:\n${quedan.map(x => `• *${x.n}* · ${x.direccion}`).join("\n")}` : ""}` }];
    }
    // can't take it: next driver, never back to the ones who already said no
    if (p.estado === "en_camino") return [{ text: `${p.n} ya salió con usted. Si hay un problema, llame a la sucursal.` }];
    const q = asignar(p.n, { excluir: [...(p.rechazos || []), r.id], por: "repartidor:" + r.id });
    return [{ text: q ? `Entendido. *${p.n}* se le pasó a ${q.repartidor.nombre}.` : `Entendido. Le avisamos al negocio que *${p.n}* necesita otro repartidor.` }];
  }

  return { activo, lista, asignar, mensaje, enCamino, entregado, deTel, enCalle };
}

const ESTADO = { listo: "por recoger", en_camino: "en camino" };

module.exports = { createRepartos, prepararRepartidores };
