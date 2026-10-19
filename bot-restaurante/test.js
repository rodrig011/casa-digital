// Pruebas sin Twilio ni internet: npm test   (VERBOSE=1 npm test imprime las conversaciones)
// 1) el motor recorre los flujos principales, 2) el webhook de WhatsApp con un Twilio simulado,
// 3) el panel (entrar, cambiar estado, aviso de "listo" al cliente), 4) el modo IA con un Claude simulado.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const twilio = require("twilio");
const { cargarNegocio, preparar } = require("./negocio");
const { createEngine, toText } = require("./engine");
const { createApp } = require("./server");
const { createIA, MODELO } = require("./ia");
const { hashClave } = require("./auth");

const NOW = new Date("2026-10-17T12:00:00-06:00");
const VERBOSE = !!process.env.VERBOSE;
const N = cargarNegocio("negocios/ejemplo.json");
const E = createEngine(N);

function run(titulo, ...xs) {
  if (VERBOSE) console.log(`\n===== ${titulo} =====`);
  let st = null;
  for (const x of xs) {
    const r = E.handle(st, x, NOW); st = r.state;
    if (VERBOSE) { console.log(">> " + x); r.messages.forEach(m => console.log(toText(m))); }
  }
  return st;
}

test("negocio: el archivo de ejemplo es válido y un archivo incompleto se rechaza", () => {
  assert.equal(N.items.length, 5);
  assert.equal(N.item("combo de 3 piezas").id, "c3");
  assert.equal(N.item("el familiar").id, "fam");
  assert.equal(N.item("un combo"), null, "ambiguo: no adivina");
  assert.equal(N.item("pizza"), null);
  assert.throws(() => preparar({ nombre: "X", sucursales: [], menu: [] }), /sucursal/);
  // every file in negocios/ must load
  for (const f of fs.readdirSync(path.join(__dirname, "negocios")).filter(f => f.endsWith(".json"))) assert.ok(cargarNegocio("negocios/" + f).items.length, f);
});

test("motor: pedido, sucursales, domicilio y persona", () => {
  const a = run("Pedido paso a paso", "hola", "2", "1", "1 x2, 4", "1", "2", "María López");
  assert.equal(a.lead.n, "PED-1001");
  assert.equal(a.lead.total, 275);
  assert.equal(a.lead.sucursal, "Centro");
  assert.equal(a.lead.hora, "En 30 minutos");
  assert.deepEqual(a.lead.lineas.map(l => [l.id, l.cantidad]), [["c2", 2], ["papas", 1]]);

  const b = run("Con sus palabras", "buenas", "quiero 2 combos de 3 piezas y unas papas grandes", "Zona Norte", "confirmar", "Otra hora", "6:30 pm", "soy Carlos");
  assert.equal(b.lead.total, 345); assert.equal(b.lead.sucursal, "Zona Norte"); assert.equal(b.lead.nombre, "Carlos"); assert.equal(b.lead.hora, "6:30 pm");

  const c = run("Agregar y empezar de nuevo", "hola", "pedir para recoger", "centro", "5", "Agregar algo más", "papas x3", "Empezar de nuevo", "3", "1", "1", "Ana");
  assert.deepEqual(c.lead.lineas.map(l => [l.id, l.cantidad]), [["fam", 1]]);

  const d = run("Menú y luego pedido", "hola", "cuánto cuesta el combo familiar", "1", "2", "fam", "1", "1", "Luis");
  assert.equal(d.lead.sucursal, "Zona Norte"); assert.equal(d.lead.total, 420);

  let st = E.handle(null, "hola", NOW).state;
  let r = E.handle(st, "dónde quedan?", NOW);
  assert.match(toText(r.messages[0]), /Dirección de ejemplo, Barrio Centro/);
  assert.match(toText(r.messages[0]), /se lo confirma una persona/, "horario vacío: no se inventa");
  r = E.handle(st, "hacen delivery?", NOW);
  assert.match(toText(r.messages[0]), /no tenemos envío propio[\s\S]*PedidosYa[\s\S]*Bip Bip/);

  const h = run("Persona", "hola", "quiero hablar con el encargado", "zona norte");
  assert.equal(h.handoff, "Zona Norte");

  const x = run("No entiende", "hola", "asdf qwer");
  assert.equal(x.step, "inicio"); assert.equal(x.lead, undefined);
});

// ---------- webhook con Twilio simulado ----------
const TOKEN = "token-de-prueba";
const PUBLIC = "https://bot.restaurante.test";
const CLAVE = "pollo-frito-2026";
async function montar(dir, extra = {}, deps = {}) {
  const sent = [];
  const client = { messages: { create: async m => { sent.push(m); return { sid: "SM" + sent.length }; } } };
  const cfg = {
    port: 0, negocio: "negocios/ejemplo.json", sid: "AC_test", token: TOKEN, sandbox: false, from: "whatsapp:+14155238886", contentSid: "",
    owner: "+504 9999-0000", publicUrl: PUBLIC, skipSignature: false, leadsToken: "secreto", dataDir: dir, ttlHours: 12,
    panelSecret: "s".repeat(40), panelUsuarios: `dueno@restaurante.hn|Dueño|${await hashClave(CLAVE)}`, ...extra,
  };
  const negocio = deps.negocio || preparar({ ...JSON.parse(fs.readFileSync(path.join(__dirname, "negocios/ejemplo.json"), "utf8")) });
  negocio.sucursales[1].whatsapp = "+504 8888-1111";
  const app = createApp(cfg, { client, now: () => NOW, log: () => {}, negocio, ...deps });
  return new Promise(ok => { const srv = app.listen(0, () => ok({ app, srv, sent, base: `http://127.0.0.1:${srv.address().port}` })); });
}
async function post(ctx, ruta, params, { firmar = true } = {}) {
  const body = new URLSearchParams(params).toString();
  const headers = { "Content-Type": "application/x-www-form-urlencoded" };
  if (firmar) headers["X-Twilio-Signature"] = twilio.getExpectedTwilioSignature(TOKEN, PUBLIC + ruta, params);
  const r = await fetch(ctx.base + ruta, { method: "POST", headers, body });
  return { status: r.status, xml: await r.text() };
}
const textoDe = xml => xml.replace(/<[^>]+>/g, "\n").replace(/&apos;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
async function entrar(ctx) {
  const r = await fetch(ctx.base + "/panel/entrar", { method: "POST", redirect: "manual", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ correo: "dueno@restaurante.hn", clave: CLAVE }) });
  assert.equal(r.status, 303);
  return r.headers.get("set-cookie").split(";")[0];
}

test("webhook: pedido completo por WhatsApp, aviso al dueño y a la sucursal, cocina lo marca listo y el cliente recibe el aviso", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rest-bot-"));
  const ctx = await montar(dir);
  try {
    const cliente = "whatsapp:+50498765432";
    let ultimo;
    for (const Body of ["Hola, buenas tardes", "2", "Zona Norte", "2 x2, 5", "Confirmar pedido", "Lo antes posible", "María López"]) {
      ultimo = await post(ctx, "/whatsapp", { From: cliente, Body, NumMedia: "0" });
      assert.equal(ultimo.status, 200);
      assert.equal((ultimo.xml.match(/<Message>/g) || []).length, 1, "un solo mensaje por turno");
      if (VERBOSE) console.log(">> " + Body + "\n" + textoDe(ultimo.xml).trim());
    }
    assert.match(textoDe(ultimo.xml), /Listo, María/);
    assert.match(textoDe(ultimo.xml), /PED-1001/);
    assert.match(textoDe(ultimo.xml), /Total: L 355/);
    await ctx.app.locals.idle();

    // owner + the branch's own WhatsApp
    assert.deepEqual(ctx.sent.map(m => m.to).sort(), ["whatsapp:+50488881111", "whatsapp:+50499990000"]);
    assert.match(ctx.sent[0].body, /Nuevo pedido PED-1001 · Zona Norte/);
    assert.match(ctx.sent[0].body, /María López · \+50498765432/);
    assert.match(ctx.sent[0].body, /2 × Combo 3 piezas · L 300/);
    assert.match(ctx.sent[0].body, /Total L 355/);

    const disco = JSON.parse(fs.readFileSync(path.join(dir, "pedidos.json"), "utf8"));
    assert.equal(disco.length, 1); assert.equal(disco[0].estado, "nuevo"); assert.equal(disco[0].tel, "+50498765432");

    // the API needs a session or the token
    assert.equal((await fetch(ctx.base + "/api/pedidos")).status, 401);
    assert.equal((await fetch(ctx.base + "/api/negocio")).status, 401);
    assert.equal((await fetch(ctx.base + "/api/pedidos", { headers: { Authorization: "Bearer secreto" } })).status, 200);
    assert.equal((await fetch(ctx.base + "/api/pedidos/PED-1001/estado", { method: "POST", headers: { "Content-Type": "application/json" }, body: '{"estado":"listo"}' })).status, 401);

    const cookie = await entrar(ctx);
    const neg = await (await fetch(ctx.base + "/api/negocio", { headers: { Cookie: cookie } })).json();
    assert.equal(neg.nombre, "Pollo de Ejemplo"); assert.equal(neg.menu.length, 5); assert.equal(neg.usuario, "Dueño");
    const pan = await fetch(ctx.base + "/panel", { headers: { Cookie: cookie } });
    assert.equal(pan.status, 200); assert.match(await pan.text(), /Pantalla para la cocina/);

    const estado = (e, extra = {}) => fetch(ctx.base + "/api/pedidos/PED-1001/estado", { method: "POST", headers: { "Content-Type": "application/json", Cookie: cookie, ...extra }, body: JSON.stringify({ estado: e }) });
    assert.equal((await estado("volando")).status, 400);
    assert.equal((await estado("listo", { Origin: "https://malo.example" })).status, 403);
    assert.equal((await estado("cocina")).status, 200);
    await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, 2, "pasar a cocina no le escribe al cliente");
    assert.equal((await estado("listo")).status, 200);
    await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, 3);
    assert.equal(ctx.sent[2].to, cliente);
    assert.match(ctx.sent[2].body, /María, su pedido \*PED-1001\* ya está listo/);
    assert.match(ctx.sent[2].body, /Zona Norte/);
    // marking it ready twice does not message the customer twice
    await estado("cocina"); await estado("listo"); await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, 3);
    const p = (await (await fetch(ctx.base + "/api/pedidos", { headers: { Cookie: cookie } })).json())[0];
    assert.equal(p.estado, "listo"); assert.equal(p.por, "dueno@restaurante.hn");

    // another customer asks for a person: owner is told, the order number keeps counting
    for (const Body of ["hola", "5", "Centro"]) await post(ctx, "/whatsapp", { From: "whatsapp:+50433331111", Body });
    await ctx.app.locals.idle();
    assert.equal(ctx.sent.at(-1).to, "whatsapp:+50499990000");
    assert.match(ctx.sent.at(-1).body, /pidió hablar con una persona · Centro/);

    // the owner asks for what is pending
    const pend = await post(ctx, "/whatsapp", { From: "whatsapp:+50499990000", Body: "pedidos" });
    assert.match(textoDe(pend.xml), /Pendientes/); assert.match(textoDe(pend.xml), /\+50433331111/);
    assert.equal(ctx.app.locals.store.pedidos[1].n, "AS-1002");
  } finally { ctx.srv.close(); }

  // after a restart the orders are still there and numbering continues
  const ctx2 = await montar(dir);
  try {
    const st = ctx2.app.locals.store;
    assert.equal(st.pedidos.length, 2); assert.equal(st.seq, 1002);
  } finally { ctx2.srv.close(); }
});

test("webhook: rechaza peticiones sin firma de Twilio", async () => {
  const ctx = await montar(null);
  try { assert.equal((await post(ctx, "/whatsapp", { From: "whatsapp:+50411112222", Body: "hola" }, { firmar: false })).status, 403); }
  finally { ctx.srv.close(); }
});

test("panel: sin sesión manda a entrar; contraseña mala no entra", async () => {
  const ctx = await montar(null);
  try {
    const sin = await fetch(ctx.base + "/panel", { redirect: "manual" });
    assert.equal(sin.status, 303); assert.equal(sin.headers.get("location"), "/panel/entrar");
    const pag = await (await fetch(ctx.base + "/panel/entrar")).text();
    assert.match(pag, /Pollo de Ejemplo/); assert.ok(!/Steel Works/.test(pag));
    const mal = await fetch(ctx.base + "/panel/entrar", { method: "POST", redirect: "manual", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ correo: "dueno@restaurante.hn", clave: "otra-clave-mala" }) });
    assert.equal(mal.status, 401);
  } finally { ctx.srv.close(); }
});

// ---------- modo IA con un cliente de Anthropic simulado ----------
function claudeFalso(guion) {
  const llamadas = [];
  return {
    llamadas, guion,
    messages: {
      create: async (body, opts) => {
        llamadas.push({ body: JSON.parse(JSON.stringify(body)), opts });
        const r = guion.shift();
        if (!r) throw new Error("guion agotado");
        if (r instanceof Error) throw r;
        return { id: "msg_" + llamadas.length, type: "message", role: "assistant", model: body.model, usage: { input_tokens: 10, output_tokens: 10 }, ...r };
      },
    },
  };
}
const usar = (id, name, input) => ({ stop_reason: "tool_use", content: [{ type: "tool_use", id, name, input }] });
const decir = text => ({ stop_reason: "end_turn", content: [{ type: "text", text }] });
const resultado = (llamada, id) => JSON.parse(llamada.body.messages.at(-1).content.find(b => b.type === "tool_result" && b.tool_use_id === id).content);

test("ia: toma el pedido con precios del archivo del negocio, lo guarda y avisa", async () => {
  const claude = claudeFalso([
    usar("t1", "ver_menu", {}),
    decir("Claro. El *Combo 3 piezas* cuesta L 150. ¿Cuántos y en qué sucursal lo recoge?"),
    usar("t2", "crear_pedido", { nombre: "ana Pérez", sucursal: "centro", productos: [{ id: "c3", cantidad: 2, nota: "sin chile" }, { id: "ref", cantidad: 1 }], hora: "7:00 p. m." }),
    decir("✅ Listo, Ana. Su pedido es el *PED-1001*, total L 355. Le avisamos por aquí cuando esté listo."),
  ]);
  const ctx = await montar(null, {}, { ia: createIA({ negocio: N, client: claude }) });
  try {
    const cliente = "whatsapp:+50497776666";
    let r = await post(ctx, "/whatsapp", { From: cliente, Body: "cuánto el combo de 3 piezas?" });
    assert.match(textoDe(r.xml), /L 150/);
    const menu = resultado(claude.llamadas[1], "t1").menu;
    assert.deepEqual(menu.find(m => m.id === "c3"), { id: "c3", nombre: "Combo 3 piezas", categoria: "Combos", descripcion: "3 piezas, papas y refresco", precio: "L 150" });
    r = await post(ctx, "/whatsapp", { From: cliente, Body: "2 sin chile y un refresco, centro, a las 7, Ana Pérez" });
    assert.match(textoDe(r.xml), /PED-1001/);
    const tr = resultado(claude.llamadas[3], "t2");
    assert.equal(tr.numero, "PED-1001"); assert.equal(tr.total, "L 355");
    assert.equal(claude.llamadas[0].body.model, MODELO);
    assert.deepEqual(claude.llamadas[0].body.tools.map(t => t.name), ["ver_menu", "sucursales", "crear_pedido", "pasar_a_persona"]);
    assert.match(claude.llamadas[0].body.system[0].text, /Pollo de Ejemplo/);
    assert.match(claude.llamadas[0].body.system[0].text, /No tiene envío propio. A domicilio se pide por PedidosYa, Bip Bip/);
    await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, 1);
    assert.match(ctx.sent[0].body, /Nuevo pedido PED-1001 · Centro/);
    assert.match(ctx.sent[0].body, /Ana Pérez/);
    assert.match(ctx.sent[0].body, /2 × Combo 3 piezas \(sin chile\) · L 300/);
    const p = ctx.app.locals.store.pedidos[0];
    assert.equal(p.total, 355); assert.equal(p.hora, "7:00 p. m.");

    // a product id that is not on the menu is refused, never priced
    const c2 = claudeFalso([usar("t3", "crear_pedido", { nombre: "X", sucursal: "centro", productos: [{ id: "pizza", cantidad: 1 }], hora: "ya" }), decir("Ese producto no lo tenemos.")]);
    const r2 = await createIA({ negocio: N, client: c2 }).turn([], "una pizza", NOW, { numero: () => "PED-9" });
    assert.equal(r2.pedido, null); assert.match(resultado(c2.llamadas[1], "t3").error, /pizza/);
  } finally { ctx.srv.close(); }
});

test("ia: si la API falla, contesta el menú de opciones", async () => {
  const logs = [];
  const claude = claudeFalso([new Error("529 overloaded")]);
  const ctx = await montar(null, {}, { ia: createIA({ negocio: N, client: claude }), log: (...a) => logs.push(a.join(" ")) });
  try {
    const r = await post(ctx, "/whatsapp", { From: "whatsapp:+50455556666", Body: "hola" });
    assert.match(textoDe(r.xml), /Gracias por escribirle a \*Pollo de Ejemplo\*/);
    assert.equal(logs.filter(l => /^\[ia\] error/.test(l)).length, 1);
  } finally { ctx.srv.close(); }
});

// ---------- cobro antes de cocinar y "No vino" ----------
const conCobro = () => preparar({ ...JSON.parse(fs.readFileSync(path.join(__dirname, "negocios/ejemplo.json"), "utf8")), cobro: { desde: 400, faltas: 1, transferencia: "Banco de ejemplo · Cuenta 0000 · A nombre de Pollo de Ejemplo", tarjeta: "https://pagos.example/link?ref={n}&monto={total}" } });

test("motor: pedido grande o de un número que no vino se paga antes; el cliente puede cancelar", () => {
  const NC = conCobro(), EC = createEngine(NC);
  const correr = (ctx, ...xs) => { let st = null, r; for (const x of xs) { r = EC.handle(st, x, NOW, ctx); st = r.state; } return { st, txt: r.messages.map(toText).join("\n") }; };
  const grande = correr({}, "hola", "2", "Centro", "3", "Confirmar pedido", "1", "Ana");
  assert.equal(grande.st.lead.estado, "por_pagar"); assert.equal(grande.st.step, "pago");
  assert.match(grande.txt, /https:\/\/pagos\.example\/link\?ref=PED-1001&monto=420/);
  assert.match(grande.txt, /Banco de ejemplo/); assert.match(grande.txt, /foto del comprobante/);
  assert.ok(!/Listo, Ana/.test(grande.txt));
  let r = EC.handle(grande.st, "ya pagué", NOW);
  assert.match(toText(r.messages[0]), /foto del comprobante/);
  r = EC.handle(r.state, "Cancelar pedido", NOW);
  assert.equal(r.state.cancelar, "PED-1001");

  const chico = correr({}, "hola", "2", "Centro", "1", "Confirmar pedido", "1", "Ana");
  assert.equal(chico.st.lead.estado, undefined); assert.match(chico.txt, /Listo, Ana/);
  const fallo = correr({ faltas: 1 }, "hola", "2", "Centro", "1", "Confirmar pedido", "1", "Ana");
  assert.equal(fallo.st.lead.estado, "por_pagar");
  // without payment details the bot never asks for payment
  const sinDatos = run("Sin cobro", "hola", "2", "Centro", "3", "Confirmar pedido", "1", "Ana");
  assert.equal(sinDatos.lead.estado, undefined);
});

test("webhook: pedido por pagar, comprobante al dueño, pago recibido a cocina, No vino y la próxima vez paga antes", async () => {
  const ctx = await montar(null, {}, { negocio: conCobro() });
  try {
    const cliente = "whatsapp:+50492223333";
    let r;
    for (const Body of ["hola", "2", "Centro", "3", "Confirmar pedido", "Lo antes posible", "Ana"]) r = await post(ctx, "/whatsapp", { From: cliente, Body, NumMedia: "0" });
    assert.match(textoDe(r.xml), /Pedido PED-1001 apartado/);
    await ctx.app.locals.idle();
    const st = ctx.app.locals.store;
    assert.equal(st.pedidos[0].estado, "por_pagar");
    assert.match(ctx.sent[0].body, /Pedido por pagar PED-1001 · Centro/); assert.match(ctx.sent[0].body, /no va a cocina/);

    r = await post(ctx, "/whatsapp", { From: cliente, Body: "", NumMedia: "1", MediaUrl0: "https://api.twilio.com/media/ME1" });
    assert.match(textoDe(r.xml), /Recibimos su comprobante del pedido \*PED-1001\*/);
    await ctx.app.locals.idle();
    assert.match(ctx.sent.at(-1).body, /Comprobante de pago PED-1001/); assert.deepEqual(ctx.sent.at(-1).mediaUrl, ["https://api.twilio.com/media/ME1"]);
    assert.equal(st.pedidos[0].comprobante, true);

    const cookie = await entrar(ctx);
    const estado = (n, e) => fetch(ctx.base + `/api/pedidos/${n}/estado`, { method: "POST", headers: { "Content-Type": "application/json", Cookie: cookie }, body: JSON.stringify({ estado: e }) });
    assert.equal((await (await fetch(ctx.base + "/api/negocio", { headers: { Cookie: cookie } })).json()).cobro, true);
    const antes = ctx.sent.length;
    assert.equal((await estado("PED-1001", "nuevo")).status, 200);
    await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, antes + 1); assert.equal(ctx.sent.at(-1).to, cliente);
    assert.match(ctx.sent.at(-1).body, /Recibimos su pago del pedido \*PED-1001\*/);
    assert.equal(st.pedidos[0].pagado, true);
    await estado("PED-1001", "listo"); await estado("PED-1001", "no_vino"); await ctx.app.locals.idle();
    assert.equal(st.pedidos[0].estado, "no_vino");

    // the same number orders something small: now it pays first, and the owner is warned
    for (const Body of ["hola", "2", "Centro", "1", "Confirmar pedido", "Lo antes posible", "Ana"]) r = await post(ctx, "/whatsapp", { From: cliente, Body, NumMedia: "0" });
    await ctx.app.locals.idle();
    assert.equal(st.pedidos[1].estado, "por_pagar"); assert.equal(st.pedidos[1].faltas, 1);
    assert.match(ctx.sent.at(-1).body, /no vino a recoger 1 vez/);
    r = await post(ctx, "/whatsapp", { From: cliente, Body: "1", NumMedia: "0" });   // "1. Cancelar pedido"
    assert.match(textoDe(r.xml), /cancelamos ese pedido/);
    assert.equal(st.pedidos[1].estado, "cancelado"); assert.equal(st.pedidos[1].por, "cliente");

    // a photo with nothing to pay goes to the conversation as before
    r = await post(ctx, "/whatsapp", { From: "whatsapp:+50411110000", Body: "", NumMedia: "1", MediaUrl0: "https://api.twilio.com/media/ME2" });
    assert.ok(!/comprobante/.test(textoDe(r.xml)));
  } finally { ctx.srv.close(); }
});

test("ia: con cobro, crear_pedido deja el pedido por pagar y devuelve los datos de pago", () => {
  const { ejecutar } = require("./ia");
  const NC = conCobro(), ctx = { numero: () => "PED-7", faltas: 0 };
  const r = ejecutar(NC, "crear_pedido", { nombre: "Ana", sucursal: "centro", productos: [{ id: "fam", cantidad: 1 }], hora: "ya" }, ctx);
  assert.equal(ctx.pedido.estado, "por_pagar"); assert.match(r.cobro, /ref=PED-7&monto=420/); assert.match(r.nota, /NO va a cocina/);
  const ctx2 = { numero: () => "PED-8", faltas: 0 };
  assert.equal(ejecutar(NC, "crear_pedido", { nombre: "Ana", sucursal: "centro", productos: [{ id: "c2", cantidad: 1 }], hora: "ya" }, ctx2).cobro, undefined);
  assert.equal(ctx2.pedido.estado, undefined);
});
