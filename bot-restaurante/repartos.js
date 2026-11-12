// Repartidores propios del restaurante (negocio.repartidores): el bot reparte los envíos solo, por WhatsApp.
//
// 1. Entra un pedido a domicilio: queda "Esperando envío" (no va a cocina). El bot escoge al repartidor de esa
//    sucursal con menos entregas (si empatan, al que hace más rato no recibe una) y le manda por WhatsApp qué
//    lleva, a dónde, el teléfono del cliente y el mapa, y le pregunta cuánto es el envío.
// 2. El repartidor contesta el precio (60, «son 60», «ENVÍO 60»). Al cliente le llega el precio y el total, y contesta:
//      SÍ        -> el pedido va a cocina (al dueño y a la sucursal les llega como pedido nuevo)
//      RECOGER   -> pasa a ser para recoger, va a cocina y el repartidor queda libre
//      CANCELAR  -> se cancela y se avisa al repartidor y al dueño
//    Si nadie contesta, el dueño o la sucursal pueden poner el precio: "ENVÍO 60 1004".
// 3. La cocina lo marca Listo: al repartidor le llega "pase a recogerlo" y al cliente "lo lleva Carlos".
// 4. El repartidor contesta SALGO (al cliente: "va en camino"), ENTREGADO (al cliente: "gracias") o NO PUEDO
//    (pasa al siguiente repartidor; si no hay otro, avisa al dueño). Con varias entregas: "entregado 1004".
// Los repartidores no instalan nada ni entran al panel. Desde el panel se puede marcar En camino, Entregado
// o pasar el pedido a otro repartidor.
const { waAddr, digits } = require("./avisos");
const { lineaTexto, textoCobro } = require("./negocio");

const EN_CALLE = ["por_envio", "por_pagar", "nuevo", "cocina", "listo", "en_camino"];
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

function createRepartos({ negocio, store, avisos, now, log = console.log, track = x => x, ubicacion = null }) {
  const links = p => ubicacion ? ubicacion.links(p) : null;
  const lista = negocio.repartidores || [];
  const activo = lista.length > 0;
  const nom = p => (p.nombre || "Hola").split(" ")[0];
  const num = p => p.n.replace(/\D/g, "");
  const deTel = from => lista.find(r => r.tel === digits(from)) || null;
  const deRep = p => p.repartidor && lista.find(x => x.id === p.repartidor.id);
  const enCalle = r => store.pedidos.filter(p => p.repartidor && p.repartidor.id === r.id && EN_CALLE.includes(p.estado));
  const aDueno = (p, titulo, lineas) => Promise.all(avisos.destinos(p.sucursal).map(to => avisos.enviar(to, `🛵 *${titulo}*\n\n${lineas.join("\n")}`, { titulo, lineas })));
  const aRep = (r, body) => r && track(avisos.enviar(waAddr(r.tel), body, { titulo: `Entregas · ${negocio.nombre}`, lineas: [body.replace(/\*/g, "").replace(/\n+/g, " · ")] }));

  function fichaRepartidor(p, r) {
    const cotiza = p.estado === "por_envio";
    const titulo = `${cotiza ? "Envío por cotizar" : "Entrega"} ${p.n} · ${p.sucursal}`;
    const lineas = [
      `👤 ${p.nombre || "Sin nombre"} · +${digits(p.tel)}`,
      `📍 ${p.direccion}`,
      ...(p.lineas || []).map(l => lineaTexto(l, negocio.L)),
      p.pagado || p.pagaAntes ? `💰 Comida ${negocio.L(p.total)} (se paga por transferencia)${p.envio != null ? ` · usted cobra solo el envío: ${negocio.L(p.envio)}` : ""}` : `💰 Comida ${negocio.L(p.total)}${p.envio != null ? ` + envío ${negocio.L(p.envio)} = cobrar ${negocio.L(p.total + p.envio)}` : ""}`,
      `Mapa: ${mapa(p, negocio)}`,
      `Cliente: https://wa.me/${digits(p.tel)}`,
    ];
    const pide = cotiza
      ? `¿Cuánto es el envío? Conteste solo el precio, por ejemplo *60*. El cliente lo acepta y entonces pasa a cocina. Si no puede llevarlo, conteste *NO PUEDO*.`
      : `Conteste *SALGO* cuando salga, *ENTREGADO* cuando lo entregue o *NO PUEDO* para pasárselo a otro.`;
    const body = `🛵 *${r.nombre}, ${cotiza ? "nuevo envío" : "tiene una entrega"}: ${p.n}*\n\n${lineas.join("\n")}\n\n${pide}`;
    return { titulo, lineas: [...lineas, cotiza ? "Conteste el precio del envío (por ejemplo 60) o NO PUEDO" : "Conteste SALGO, ENTREGADO o NO PUEDO"], body };
  }

  // the free-est driver of the order's branch; ties go to whoever waited longest for a delivery
  function escoger(p, excluir = []) {
    const b = negocio.sucursales.find(s => s.nombre === p.sucursal);
    const ok = lista.filter(r => !excluir.includes(r.id) && (!r.sucursal || (b && r.sucursal === b.id)));
    const ultima = r => Math.max(0, ...store.pedidos.filter(x => x.repartidor && x.repartidor.id === r.id).map(x => new Date(x.t_asignado || 0).getTime()));
    return ok.map(r => [r, enCalle(r).length, ultima(r)]).sort((a, b) => a[1] - b[1] || a[2] - b[2])[0]?.[0] || null;
  }

  // a new delivery order (estado por_envio: the driver quotes the delivery first), a ready one without a driver,
  // or the owner / a driver asking for another driver
  function asignar(n, { excluir = [], por = "bot" } = {}) {
    const p = store.getPedido(n);
    if (!p || p.entrega !== "domicilio" || !activo) return null;
    const r = escoger(p, excluir);
    if (!r) {
      store.updatePedido(n, { repartidor: null });
      log(`[${n}] sin repartidor disponible`);
      track(aDueno(p, `${p.n} no tiene repartidor`, [`📍 ${p.direccion}`, p.estado === "por_envio" ? `Nadie ha dicho el precio del envío. Escríbale a un repartidor, o conteste *ENVÍO 60 ${num(p)}* con el precio.` : "Ningún repartidor lo pudo llevar. Escríbale a uno o asígnelo desde el panel."]));
      return null;
    }
    const antes = p.repartidor;
    const q = store.updatePedido(n, { repartidor: { id: r.id, nombre: r.nombre, tel: "+" + r.tel }, t_asignado: now().toISOString(), rechazos: excluir, asignadoPor: por });
    const f = fichaRepartidor(q, r);
    log(`[${n}] asignado a ${r.nombre}${antes ? ` (antes ${antes.nombre})` : ""}`);
    track(avisos.enviar(waAddr(r.tel), f.body, f));
    const previo = antes && antes.id !== r.id && por !== "repartidor:" + antes.id && lista.find(x => x.id === antes.id);
    if (previo) aRep(previo, `ℹ️ ${previo.nombre}, la entrega *${q.n}* se le pasó a ${r.nombre}. Ya no tiene que llevarla.`);
    if (!antes && q.estado === "listo") track(avisos.enviar(waAddr(q.tel), `✅ ¡${nom(q)}, su pedido *${q.n}* ya está listo! Lo lleva *${r.nombre}*; le avisamos por aquí cuando salga.`));
    track(aDueno(q, q.estado === "por_envio" ? `${q.n}: ${r.nombre} cotiza el envío` : `${q.n} asignado a ${r.nombre}`, [`📍 ${q.direccion}`, `💰 Comida ${negocio.L(q.total)}`,
      antes ? `${antes.nombre} no lo pudo llevar.` : q.estado === "por_envio" ? "Cuando el cliente acepte el precio del envío, le llega el pedido para cocina." : "Se le avisó por WhatsApp."]));
    return q;
  }

  // the price of the delivery, from the driver ("ENVÍO 60") or the owner ("ENVÍO 60 1004"): the customer accepts it before cooking
  function fijarEnvio(p, precio, por) {
    const cotiza = p.estado === "por_envio";
    const q = store.updatePedido(p.n, { envio: precio, envioPor: por, t_envio: now().toISOString() });
    const total = negocio.L(q.total + precio);
    track(avisos.enviar(waAddr(q.tel), cotiza
      ? (q.pagaAntes
        ? `🛵 ${nom(q)}, el envío de su pedido *${q.n}* a ${q.direccion} cuesta *${negocio.L(precio)}*: se le paga al repartidor al recibir.\nLa comida (${negocio.L(q.total)}) se paga por transferencia antes de cocina.\n\n¿Lo confirmamos? Conteste *SÍ* y le mandamos los datos para pagar, *RECOGER* si prefiere pasar por él, o *CANCELAR*.`
        : `🛵 ${nom(q)}, el envío de su pedido *${q.n}* a ${q.direccion} cuesta *${negocio.L(precio)}*.\nTotal: *${total}* (comida ${negocio.L(q.total)} + envío), se paga al recibir.\n\n¿Lo confirmamos? Conteste *SÍ* para mandarlo a cocina, *RECOGER* si prefiere pasar por él, o *CANCELAR*.`)
      : `🛵 ${nom(q)}, el envío de su pedido *${q.n}* cuesta *${negocio.L(precio)}*. Total a pagarle al repartidor: *${total}*.`));
    log(`[${q.n}] envío ${precio} (${por})`);
    return q;
  }

  // the customer's answer to the delivery price -> the reply, or null if this number has no quote waiting
  function respuestaCliente(from, text) {
    const p = store.pedidos.findLast(x => x.estado === "por_envio" && x.envio != null && digits(x.tel) === digits(from));
    if (!p) return null;
    const t = norm(text), r = deRep(p);
    const si = /^(si|sí|ok|okey|okay|dale|va|esta bien|confirm|de acuerdo|claro|perfecto|listo)\b/.test(t) || t === "1";
    const recoger = /recog|recoj|paso yo|yo paso|voy yo|yo voy|paso por|pasar por/.test(t) || t === "2";
    const cancelar = /cancel|no gracias|muy caro|caro|^no\b/.test(t) || t === "3";
    const t0 = now().toISOString();
    // it pays before: accepted -> waiting for the transfer, the kitchen gets it when the payment is confirmed
    const cobrar = (q, que) => {
      track(avisos.ficha(q));
      const monto = q.anticipo || q.total;
      return `✅ Listo, ${nom(q)}. ${que}\n\nPara mandarlo a cocina, la comida se paga antes:\n${textoCobro(negocio, q.n, q.total, monto)}\n\nEn cuanto revisemos el pago, entra a cocina y le avisamos por aquí.`;
    };
    if (si && !recoger && !cancelar && p.pagaAntes) {
      const q = store.updatePedido(p.n, { estado: "por_pagar", envioAceptado: true });
      aRep(r, `✅ El cliente aceptó el envío de *${q.n}* (${negocio.L(q.envio)}). Está pagando la comida; cuando la cocina lo tenga listo le avisamos para que pase a recogerlo.`);
      log(`[${q.n}] envío aceptado, esperando pago`);
      return cobrar(q, `Envío de ${negocio.L(q.envio)} aceptado para *${q.n}*: se le paga al repartidor al recibir.`);
    }
    if (recoger && p.pagaAntes) {
      const q = store.updatePedido(p.n, { estado: "por_pagar", entrega: "recoger", envio: null, repartidor: null, hora: p.diaFecha ? p.hora : "Lo antes posible" });
      aRep(r, `ℹ️ ${r ? r.nombre : ""}, el cliente de *${q.n}* mejor pasa a recogerlo. Ya no tiene que llevarlo.`);
      return cobrar(q, `Su pedido *${q.n}* lo recoge en *${q.sucursal}*.`);
    }
    if (si && !recoger && !cancelar) {
      const q = store.updatePedido(p.n, { estado: "nuevo", t_nuevo: t0, envioAceptado: true });
      track(avisos.ficha(q));
      aRep(r, `✅ El cliente aceptó el envío de *${q.n}* (${negocio.L(q.envio)}). Ya va a cocina; le avisamos cuando esté listo para recoger.`);
      log(`[${q.n}] envío aceptado`);
      return `✅ Listo, ${nom(q)}. Su pedido *${q.n}* ya va a cocina. Total: *${negocio.L(q.total + q.envio)}* con envío. Le avisamos por aquí cuando salga.`;
    }
    if (recoger) {
      const b = negocio.sucursales.find(s => s.nombre === p.sucursal);
      const q = store.updatePedido(p.n, { estado: "nuevo", t_nuevo: t0, entrega: "recoger", envio: null, repartidor: null, hora: p.diaFecha ? p.hora : "Lo antes posible" });
      track(avisos.ficha(q));
      aRep(r, `ℹ️ ${r ? r.nombre : ""}, el cliente de *${q.n}* mejor pasa a recogerlo. Ya no tiene que llevarlo.`);
      return `✅ Listo, ${nom(q)}. Su pedido *${q.n}* ya va a cocina y lo recoge en *${q.sucursal}*${b && b.direccion ? ` (${b.direccion})` : ""}. Total: *${negocio.L(q.total)}*. Le avisamos cuando esté listo.`;
    }
    if (cancelar) {
      const q = store.updatePedido(p.n, { estado: "cancelado", t_cancelado: t0, por: "cliente:envio" });
      aRep(r, `ℹ️ El cliente de *${q.n}* canceló el pedido. Ya no tiene que llevarlo.`);
      track(aDueno(q, `${q.n} cancelado por el cliente`, [`No aceptó el envío de ${negocio.L(q.envio)}.`, `Responder: https://wa.me/${digits(q.tel)}`]));
      return `Listo, cancelamos su pedido *${q.n}*. Si quiere, puede pedir para recoger. ¡Gracias por escribirnos!`;
    }
    return `¿Confirmamos su pedido *${p.n}* con envío de ${negocio.L(p.envio)} (total ${negocio.L(p.total + p.envio)})? Conteste *SÍ*, *RECOGER* si prefiere pasar por él, o *CANCELAR*.`;
  }

  // the kitchen marked it ready: the driver who quoted it goes for it (or one is picked now)
  function listo(p) {
    const r = deRep(p);
    if (!r) return asignar(p.n, { por: "cocina" });
    aRep(r, `🍽️ *${p.n} ya está listo* en ${p.sucursal}. Pase a recogerlo.\n📍 Para: ${p.nombre || "el cliente"}, ${p.direccion}\n💰 ${p.pagado ? `La comida ya está pagada: cobre solo el envío, ${negocio.L(p.envio || 0)}` : `Cobrar ${negocio.L(p.total + (p.envio || 0))}`}\n\nCuando salga, conteste *SALGO*.`);
    track(avisos.enviar(waAddr(p.tel), `✅ ¡${nom(p)}, su pedido *${p.n}* ya está listo! Lo lleva *${r.nombre}*; le avisamos por aquí cuando salga.`));
    return p;
  }

  // what the customer hears when the order leaves or arrives (from the driver's WhatsApp or the panel)
  function enCamino(p) {
    const quien = p.repartidor ? ` con *${p.repartidor.nombre}*` : "";
    const l = links(p);
    return avisos.enviar(waAddr(p.tel), `🛵 ¡${nom(p)}, su pedido *${p.n}* ya va en camino${quien}! ${p.pagado ? `La comida ya está pagada${p.envio ? `; el envío (${negocio.L(p.envio)}) se le paga a ${p.repartidor ? p.repartidor.nombre : "el repartidor"} al recibir` : ""}.` : `Total: ${negocio.L(p.total + (p.envio || 0))}${p.envio ? ` (con envío de ${negocio.L(p.envio)})` : ""}.`}${l ? `\n\n📍 Vea dónde va, en tiempo real: ${l.cli}` : ""}`);
  }
  function entregado(p) {
    return avisos.enviar(waAddr(p.tel), `✅ ${nom(p)}, su pedido *${p.n}* fue entregado. ¡Gracias por su compra en *${negocio.nombre}*!`);
  }

  // "ENVÍO 60 1004" from the owner or a branch
  function envioNegocio(text, por) {
    const m = norm(text).match(/^envio\s*(?:de\s*)?(?:l\.?\s*)?(\d{1,4})\s+(?:ped-?\s*)?(\d{3,})$/);
    if (!m) return null;
    const p = store.pedidos.findLast(x => x.n.replace(/\D/g, "").endsWith(m[2]));
    if (!p || p.entrega !== "domicilio" || ["entregado", "cancelado"].includes(p.estado)) return `No encuentro un envío abierto con el número ${m[2]}.`;
    fijarEnvio(p, +m[1], por);
    return `👍 Le avisamos al cliente que el envío de ${p.n} es ${negocio.L(+m[1])}.`;
  }

  // a message from a driver's number -> the bot's replies, or null if it is not a driver
  function mensaje(from, text) {
    const r = deTel(from);
    if (!r) return null;
    const t = norm(text);
    const mios = enCalle(r).sort((a, b) => new Date(a.t_asignado) - new Date(b.t_asignado));
    const lista = () => mios.map(p => `• *${p.n}* · ${ESTADO[p.estado]} · ${p.nombre || "Sin nombre"} · ${p.direccion}`).join("\n");
    if (!mios.length) return [{ text: `Hola, ${r.nombre}. No tiene entregas pendientes. Cuando haya una, le llega por aquí.` }];
    // "ENVÍO 60" (or "envío 60 1004" with several)
    // also just "120", "son 120", "L 120", "120 lempiras", "120 1004" while a quote is pending
    const pendientes = mios.filter(x => x.estado === "por_envio" && x.envio == null);
    const limpio = t.replace(/\b(el|la|envio|es|son|cuesta|vale|precio|seria|sale|le|cobro|cobra|de|lps?|lempiras|l)\b\.?/g, " ").replace(/[.,:]/g, " ").replace(/\s+/g, " ").trim();
    const m = limpio.match(/^(\d{1,4})(?:\s+(?:ped-?\s*)?(\d{3,}))?$/);
    const conPalabra = /\benvio\b/.test(t);
    const env = m && (conPalabra || (pendientes.length && +m[1] >= 10 && +m[1] <= 999)) ? m : null;
    if (conPalabra && !env && /^envio\b/.test(t)) return [{ text: `Escriba solo el precio del envío en números, por ejemplo *60*.` }];
    if (env) {
      const precio = +env[1], porCotizar = pendientes;
      const cual = env[2] ? mios.filter(x => num(x).endsWith(env[2])) : porCotizar.length === 1 ? porCotizar : mios.length === 1 ? mios : [];
      if (cual.length !== 1) return [{ text: `${r.nombre}, ¿de cuál entrega? Escriba el precio y el número, por ejemplo *${precio} ${num(mios[0])}*:\n${lista()}` }];
      const q = fijarEnvio(cual[0], precio, "repartidor:" + r.id);
      return [{ text: q.estado === "por_envio"
        ? `👍 Le preguntamos al cliente si acepta el envío de ${negocio.L(precio)} para *${q.n}*. Si dice que sí, le avisamos y pasa a cocina.`
        : `👍 Le avisamos al cliente que el envío de *${q.n}* es ${negocio.L(precio)}: en total cobra ${negocio.L(q.total + precio)}.` }];
    }
    const accion = t === "1" || /\bsalgo\b|\bsali\b|\bvoy\b|en camino/.test(t) ? "salgo"
      : t === "2" || /entregad|\bentregue\b|\blisto\b/.test(t) ? "entregado"
      : t === "3" || /no puedo|no lo puedo|no voy|otro/.test(t) ? "nopuedo" : null;
    if (!accion) return [{ text: `${r.nombre}, sus entregas:\n${lista()}`, buttons: BOTONES }];
    // which order: the number in the message, else the only one that fits. SALGO with several ready takes them all.
    const numero = (text.match(/\d{3,}/) || [])[0];
    const listos = mios.filter(x => x.estado === "listo"), saliendo = mios.filter(x => x.estado === "en_camino");
    const ps = numero ? mios.filter(x => num(x).endsWith(numero))
      : accion === "salgo" ? listos
      : accion === "entregado" ? (saliendo.length === 1 ? saliendo : saliendo.length ? [] : listos.length === 1 ? listos : [])
      : mios.length === 1 ? mios : listos.length === 1 ? listos : [];
    if (accion === "salgo" && !numero && !ps.length) return [{ text: `${r.nombre}, todavía no hay ninguna lista para salir. Le avisamos por aquí cuando la cocina la tenga.\n${lista()}` }];
    if (ps.length !== 1 && !(accion === "salgo" && ps.length)) {
      const verbo = accion === "entregado" ? "ENTREGADO" : accion === "salgo" ? "SALGO" : "NO PUEDO";
      return [{ text: `${r.nombre}, ${numero ? `no encuentro la entrega ${numero} entre las suyas` : "tiene varias entregas"}. Escriba el número, por ejemplo *${verbo} ${num(mios[0])}*:\n${lista()}` }];
    }
    const t0 = now().toISOString();
    const p = ps[0];
    if (accion === "salgo") {
      const van = ps.filter(x => x.estado === "listo");
      if (!van.length) return [{ text: p.estado === "en_camino" ? `${p.n} ya estaba en camino. Cuando lo entregue, conteste *ENTREGADO*.` : `${p.n} todavía no está listo. Le avisamos por aquí cuando lo esté.`, buttons: p.estado === "en_camino" ? ["Entregado"] : undefined }];
      for (const x of van) {
        let q = store.updatePedido(x.n, { estado: "en_camino", t_en_camino: t0, por: "repartidor:" + r.id });
        if (ubicacion) q = ubicacion.preparar(q);
        track(enCamino(q));
        log(`[${x.n}] en camino con ${r.nombre}`);
      }
      const det = van.map(x => { const l = links(store.getPedido(x.n)); return `*${x.n}* · ${x.nombre || "Sin nombre"}\n📍 ${x.direccion}\nMapa: ${mapa(x, negocio)}${l ? `\n📡 Compartir su ubicación con el cliente (deje la página abierta): ${l.rep}` : ""}`; }).join("\n\n");
      return [{ text: `👍 Listo, ${r.nombre}. Le avisamos ${van.length > 1 ? "a los clientes" : "al cliente"} que va en camino.\n\n${det}\n\nCuando ${van.length > 1 ? "entregue cada uno, conteste *ENTREGADO* con el número" : "lo entregue, conteste *ENTREGADO*"}.`, buttons: ["Entregado"] }];
    }
    if (accion === "entregado") {
      if (!["listo", "en_camino"].includes(p.estado)) return [{ text: `${p.n} todavía no ha salido. Le avisamos cuando esté listo.` }];
      const q = store.updatePedido(p.n, { estado: "entregado", t_entregado: t0, por: "repartidor:" + r.id });
      if (ubicacion) ubicacion.cerrar(q);
      track(entregado(q));
      track(aDueno(q, `${q.n} entregado por ${r.nombre}`, [`💰 ${negocio.L(q.total + (q.envio || 0))}${q.envio ? ` (con envío de ${negocio.L(q.envio)})` : ""}`, `📍 ${q.direccion}`]));
      log(`[${p.n}] entregado por ${r.nombre}`);
      const quedan = mios.filter(x => x.n !== p.n);
      return [{ text: `✅ Gracias, ${r.nombre}. *${p.n}* quedó entregado.${quedan.length ? `\n\nLe quedan:\n${quedan.map(x => `• *${x.n}* · ${ESTADO[x.estado]} · ${x.direccion}`).join("\n")}` : ""}` }];
    }
    // can't take it: next driver, never back to the ones who already said no
    if (p.estado === "en_camino") return [{ text: `${p.n} ya salió con usted. Si hay un problema, llame a la sucursal.` }];
    const q = asignar(p.n, { excluir: [...(p.rechazos || []), r.id], por: "repartidor:" + r.id });
    return [{ text: q ? `Entendido. *${p.n}* se le pasó a ${q.repartidor.nombre}.` : `Entendido. Le avisamos al negocio que *${p.n}* necesita otro repartidor.` }];
  }

  return { activo, lista, asignar, listo, mensaje, respuestaCliente, envioNegocio, enCamino, entregado, deTel, enCalle };
}

const ESTADO = { por_envio: "esperando su precio de envío", por_pagar: "esperando el pago del cliente", nuevo: "en cocina", cocina: "en cocina", listo: "lista para recoger", en_camino: "en camino" };

module.exports = { createRepartos, prepararRepartidores };
