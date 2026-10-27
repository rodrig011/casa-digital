// Pruebas sin Twilio ni internet: npm test   (VERBOSE=1 npm test imprime las conversaciones)
// 1) el motor recorre los flujos principales, 2) el webhook de WhatsApp con un Twilio simulado,
// 3) el panel (entrar, cambiar estado, aviso de "listo" al cliente), 4) el modo IA con un Claude simulado.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const twilio = require("twilio");
const { cargarNegocio, preparar, cuenta } = require("./negocio");
const { createEngine, toText } = require("./engine");
const { createApp } = require("./server");
const { createStore } = require("./store");
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

test("moneda: quetzales en Guatemala, dólares en El Salvador, lempiras si no dice", () => {
  const base = JSON.parse(fs.readFileSync(path.join(__dirname, "negocios/ejemplo.json"), "utf8"));
  assert.equal(N.L(1250), "L 1,250"); assert.equal(N.pais, "Honduras");
  const gt = preparar({ ...base, moneda: "GTQ" });
  assert.equal(gt.L(45), "Q45"); assert.equal(gt.pais, "Guatemala");
  const sv = preparar({ ...base, moneda: "USD" });
  assert.equal(sv.L(3.5), "$3.50"); assert.equal(sv.pais, "El Salvador");
  const E2 = createEngine(sv), hola = E2.handle(null, "hola", NOW);
  const menu = E2.handle(hola.state, "1", NOW).messages.map(toText).join("\n");
  assert.match(menu, /\$\d+\.\d\d/);
  assert.doesNotMatch(menu, /L \d/);
  assert.throws(() => preparar({ ...base, moneda: "EUR" }), /moneda desconocida/);
});

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

  // several products and quantities in one sentence, without commas
  const carrito = (...xs) => cuenta(N, run("Una frase", "hola", "Ver el menú y precios", ...xs, "Centro").data.carrito).lineas.map(l => [l.id, l.cantidad]);
  assert.deepEqual(carrito("quiero el combo 1 con 4 papas"), [["c2", 1], ["papas", 4]]);
  assert.deepEqual(carrito("el familiar con 2 refrescos"), [["fam", 1], ["ref", 2]]);
  assert.deepEqual(carrito("quiero 2 combo 1 y 1 refresco"), [["c2", 2], ["ref", 1]]);
  assert.deepEqual(carrito("quiero un combo 3 piezas con 2 refrescos de 2 litros"), [["c3", 1], ["ref", 2]]);
  assert.deepEqual(carrito("dos combos de 3 piezas"), [["c3", 2]]);
  assert.deepEqual(carrito("1 x2, 4"), [["c2", 2], ["papas", 1]]);
  assert.deepEqual(carrito("quiero 3 combos de numero 1 quiero 3 papas y 2 refrescos"), [["c2", 3], ["papas", 3], ["ref", 2]]);
  assert.deepEqual(carrito("dame 3 combos del 1 dame 1 refresco"), [["c2", 3], ["ref", 1]]);

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
  if (negocio.sucursales[1]) negocio.sucursales[1].whatsapp = "+504 8888-1111";
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

test("panel: un correo que no existe recibe el mismo mensaje que una contraseña mala", async () => {
  const ctx = await montar(null);
  const intento = (correo, clave) => fetch(ctx.base + "/panel/entrar", { method: "POST", redirect: "manual", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ correo, clave }) });
  try {
    const a = await intento("dueno@restaurante.hn", "otra-clave-mala"), b = await intento("nadie@gmail.com", "otra-clave-mala");
    assert.equal(a.status, b.status);
    const err = async r => (await r.text()).match(/class="err"[^>]*>([^<]*)/)[1];
    assert.equal(await err(a), await err(b));
  } finally { ctx.srv.close(); }
});

test("panel: Salir cierra la sesión en el servidor, también después de reiniciar", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rest-salir-"));
  const ctx = await montar(dir);
  let cookie;
  try {
    cookie = await entrar(ctx);
    assert.equal((await fetch(ctx.base + "/api/pedidos", { headers: { Cookie: cookie } })).status, 200);
    const out = await fetch(ctx.base + "/panel/salir", { redirect: "manual", headers: { Cookie: cookie } });
    assert.equal(out.status, 303); assert.match(out.headers.get("set-cookie"), /Max-Age=0/);
    // someone who kept a copy of the cookie is out too
    assert.equal((await fetch(ctx.base + "/api/pedidos", { headers: { Cookie: cookie } })).status, 401);
    assert.equal((await fetch(ctx.base + "/panel", { redirect: "manual", headers: { Cookie: cookie } })).status, 303);
    // a new login still works
    assert.equal((await fetch(ctx.base + "/panel/yo", { headers: { Cookie: await entrar(ctx) } })).status, 200);
  } finally { ctx.srv.close(); }
  const ctx2 = await montar(dir);
  try { assert.equal((await fetch(ctx2.base + "/panel/yo", { headers: { Cookie: cookie } })).status, 401); } finally { ctx2.srv.close(); }
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

test("demo de la página: contesta con IA solo a clientiatech.com, no guarda el pedido y frena el abuso", async () => {
  const claude = claudeFalso([usar("d1", "crear_pedido", { nombre: "Ana", sucursal: "centro", productos: [{ id: "c2", cantidad: 3 }], hora: "ya" }), decir("Listo, Ana: pedido *DEMO-1001*.")]);
  const ctx = await montar(null, { demoIA: true, demoOrigenes: ["https://clientiatech.com"], demoPorVisitante: 2, demoPorDia: 10 }, { demoClient: claude });
  const chat = (body, origin = "https://clientiatech.com") => fetch(ctx.base + "/demo/chat", { method: "POST", headers: { "Content-Type": "application/json", Origin: origin }, body: JSON.stringify(body) });
  try {
    assert.equal((await chat({ sesion: "abcdefgh12", texto: "hola" }, "https://otro.com")).status, 403);
    const r = await chat({ sesion: "abcdefgh12", texto: "3 combos del 1 a nombre de Ana" });
    assert.equal(r.status, 200);
    assert.equal(r.headers.get("access-control-allow-origin"), "https://clientiatech.com");
    const j = await r.json();
    assert.match(j.reply, /DEMO-1001/);
    assert.equal(j.pedido.total, 345); assert.equal(j.pedido.n, "DEMO-1001");
    assert.equal(ctx.app.locals.store.pedidos.length, 0);
    assert.equal(ctx.sent.length, 0);
    assert.equal((await chat({ sesion: "abcdefgh12", texto: "otra" })).status, 502);   // guion agotado: la página usa el menú
    assert.equal((await chat({ sesion: "abcdefgh12", texto: "otra" })).status, 429);
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

// ---------- pago con tarjeta por pasarela (Tilopay simulado) ----------
test("pagos: cliente de Tilopay entra con token, crea un link de un solo uso por pedido y consulta si se pagó", async () => {
  const { createTilopay } = require("./pagos");
  const llamadas = [];
  let pagos = [];
  const fetchFalso = async (url, o = {}) => {
    llamadas.push({ url, ...o, body: o.body ? JSON.parse(o.body) : null });
    const r = url.endsWith("/login") ? { access_token: "jwt1", token_type: "bearer", expires_in: 86400 }
      : url.endsWith("/createLinkPayment") ? { type: "200", message: "Success", url: "https://app.tilopay.com/link/MjMw", id: 77 }
      : { type: "200", message: "Success", detail: { id: 77 }, payments: pagos };
    return { ok: true, status: 200, text: async () => JSON.stringify(r) };
  };
  const t = createTilopay({ usuario: "u", clave: "c", key: "k-1", fetch: fetchFalso });
  const l = await t.crearLink({ n: "PED-1001", total: 420, nombre: "Ana", webhookUrl: "https://bot/pagos/aviso/PED-1001?t=x", volverUrl: "https://bot/pagos/listo/PED-1001?t=x" });
  assert.deepEqual(l, { id: "77", url: "https://app.tilopay.com/link/MjMw" });
  assert.deepEqual(llamadas[0].body, { apiuser: "u", password: "c" });
  const crear = llamadas[1];
  assert.equal(crear.headers.Authorization, "bearer jwt1");
  assert.equal(crear.body.amount, "420.00"); assert.equal(crear.body.currency, "HNL"); assert.equal(crear.body.type, 1);
  assert.equal(crear.body.reference, "PED-1001"); assert.equal(crear.body.key, "k-1"); assert.match(crear.body.webhook_url, /pagos\/aviso\/PED-1001/);
  assert.deepEqual(await t.verificar("77", 420), { pagado: false, monto: 0, pagos: 0 });
  pagos = [{ code: "0", amount: "420.00" }];
  assert.equal((await t.verificar("77", 420)).pagado, false, "rechazado no cuenta");
  pagos = [{ code: "1", amount: "420.00" }];
  assert.equal((await t.verificar("77", 420)).pagado, true);
  assert.match(llamadas.at(-1).url, /getDetailLinkPayment\/77\/k-1$/);
  assert.equal(llamadas.filter(c => c.url.endsWith("/login")).length, 1, "el token se reutiliza");
});

test("webhook: con pasarela cada pedido lleva su link; si el pago sale bien pasa solo a cocina y avisa", async () => {
  let pagado = false, creados = [];
  const pasarela = {
    proveedor: "tilopay",
    crearLink: async a => { creados.push(a); return { id: "L" + creados.length, url: `https://app.tilopay.com/link/${a.n}` }; },
    verificar: async () => ({ pagado, monto: pagado ? 420 : 0 }),
  };
  const ctx = await montar(null, { pagosSecret: "p".repeat(40) }, { negocio: conCobro(), pasarela });
  try {
    const cliente = "whatsapp:+50496665555";
    let r;
    for (const Body of ["hola", "2", "Centro", "3", "Confirmar pedido", "Lo antes posible", "Ana"]) r = await post(ctx, "/whatsapp", { From: cliente, Body, NumMedia: "0" });
    const txt = textoDe(r.xml);
    assert.match(txt, /Con tarjeta:\* https:\/\/app\.tilopay\.com\/link\/PED-1001/);
    assert.match(txt, /entra solo a cocina/); assert.ok(!/LINK_DE_PAGO/.test(txt));
    assert.equal(creados.length, 1); assert.equal(creados[0].total, 420);
    assert.match(creados[0].webhookUrl, /^https:\/\/bot\.restaurante\.test\/pagos\/aviso\/PED-1001\?t=/);
    const st = ctx.app.locals.store;
    assert.equal(st.pedidos[0].pagoLink.id, "L1");
    await ctx.app.locals.idle();
    const ruta = creados[0].webhookUrl.replace(PUBLIC, "");
    const aviso = body => fetch(ctx.base + ruta, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

    // a fake notice without the order's signature is refused; a notice alone never marks it paid
    assert.equal((await fetch(ctx.base + "/pagos/aviso/PED-1001?t=falso", { method: "POST" })).status, 403);
    const antes = ctx.sent.length;
    assert.equal((await aviso({ code: "0", codeDescription: "Fondos insuficientes" })).status, 200);
    await ctx.app.locals.idle();
    assert.equal(st.pedidos[0].estado, "por_pagar");
    assert.equal(ctx.sent.length, antes + 1); assert.equal(ctx.sent.at(-1).to, cliente);
    assert.match(ctx.sent.at(-1).body, /no pasó \(Fondos insuficientes\)/);

    pagado = true;
    await aviso({ code: "1" }); await aviso({ code: "1" });
    await ctx.app.locals.idle();
    const p = st.pedidos[0];
    assert.equal(p.estado, "nuevo"); assert.equal(p.pagado, true); assert.equal(p.metodoPago, "tarjeta"); assert.equal(p.por, "tilopay");
    const nuevos = ctx.sent.slice(antes + 1);
    assert.equal(nuevos.filter(m => m.to === cliente && /Recibimos su pago del pedido \*PED-1001\*/.test(m.body)).length, 1, "un solo aviso aunque lleguen dos");
    assert.ok(nuevos.some(m => m.to === "whatsapp:+50499990000" && /Nuevo pedido PED-1001 · Centro/.test(m.body) && /Pagado con tarjeta/.test(m.body)));

    const vuelta = await fetch(ctx.base + creados[0].volverUrl.replace(PUBLIC, ""));
    assert.equal(vuelta.status, 200); assert.match(await vuelta.text(), /Pago recibido/);
    assert.equal((await fetch(ctx.base + "/pagos/listo/PED-1001?t=malo")).status, 403);
  } finally { ctx.srv.close(); }
});

test("store: los pedidos cerrados de más de 30 días pasan al archivo del mes, sin perder faltas ni numeración", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rest-bot-"));
  let ahora = Date.parse("2026-11-20T15:00:00Z");
  fs.writeFileSync(path.join(dir, "pedidos.json"), JSON.stringify([
    { n: "PED-1001", tel: "+50498765432", fecha: "2026-09-05T18:00:00Z", estado: "entregado" },
    { n: "PED-1002", tel: "+50498765432", fecha: "2026-09-20T18:00:00Z", estado: "no_vino" },
    { n: "PED-1003", tel: "+50411112222", fecha: "2026-10-02T18:00:00Z", estado: "nuevo" },
    { n: "PED-1004", tel: "+50498765432", fecha: "2026-10-03T18:00:00Z", estado: "cancelado" },
    { n: "PED-1005", tel: "+50498765432", fecha: "2026-11-15T18:00:00Z", estado: "no_vino" },
  ]));
  const st2 = createStore(dir, { now: () => ahora });
  assert.equal(st2.faltas("+504 9876-5432"), 2);
  st2.seq = 1006; st2.addPedido({ n: "PED-1006", tel: "+50433334444", fecha: new Date(ahora).toISOString(), estado: "nuevo" });

  const leer = f => JSON.parse(fs.readFileSync(path.join(dir, f), "utf8"));
  // still-open order stays even if old; recent ones stay
  assert.deepEqual(leer("pedidos.json").map(p => p.n), ["PED-1003", "PED-1005", "PED-1006"]);
  assert.deepEqual(leer("archivo/pedidos-2026-09.json").map(p => p.n), ["PED-1001", "PED-1002"]);
  assert.deepEqual(leer("archivo/pedidos-2026-10.json").map(p => p.n), ["PED-1004"]);
  assert.equal(st2.faltas("+50498765432"), 2, "la falta archivada sigue contando");

  // a month later everything closed is archived; after a restart numbering and faltas continue
  st2.updatePedido("PED-1003", { estado: "entregado" }); st2.updatePedido("PED-1006", { estado: "entregado" });
  ahora += 40 * 86400e3;
  st2.updatePedido("PED-1005", { visto: true });
  assert.equal(leer("pedidos.json").length, 0);
  assert.deepEqual(leer("archivo/pedidos-2026-10.json").map(p => p.n), ["PED-1004", "PED-1003"]);
  const st3 = createStore(dir, { now: () => ahora });
  assert.equal(st3.seq, 1006);
  assert.equal(st3.faltas("+50498765432"), 2);
});

test("seguridad: cabeceras, https y freno de mensajes por número", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rest-bot-"));
  const ctx = await montar(dir, { limiteMensajes: 3 });
  try {
    const r = await fetch(ctx.base + "/panel/entrar");
    assert.match(r.headers.get("content-security-policy"), /frame-ancestors 'none'/);
    assert.equal(r.headers.get("x-content-type-options"), "nosniff");
    assert.equal(r.headers.get("x-powered-by"), null);
    const h = await fetch(ctx.base + "/panel", { redirect: "manual", headers: { "X-Forwarded-Proto": "http" } });
    assert.equal(h.status, 301); assert.match(h.headers.get("location"), /^https:\/\//);
    const s = await fetch(ctx.base + "/", { headers: { "X-Forwarded-Proto": "https" } });
    assert.match(s.headers.get("strict-transport-security"), /max-age=31536000/);

    const de = Body => post(ctx, "/whatsapp", { From: "whatsapp:+50490001111", Body, NumMedia: "0" });
    for (let i = 0; i < 3; i++) assert.match(textoDe((await de("hola")).xml), /\S/);
    assert.match(textoDe((await de("hola")).xml), /muchos mensajes seguidos/);
    assert.doesNotMatch((await de("hola")).xml, /<Message>/, "después del aviso, silencio");
    assert.match(textoDe((await post(ctx, "/whatsapp", { From: "whatsapp:+50490002222", Body: "hola", NumMedia: "0" })).xml), /\S/, "otro número sigue normal");
    assert.match(textoDe((await post(ctx, "/whatsapp", { From: "whatsapp:+50499990000", Body: "pedidos", NumMedia: "0" })).xml), /Pendientes|No hay pedidos/);
  } finally { ctx.srv.close(); }
});

const LC = cargarNegocio("negocios/libbys-cajun.json");
test("motor (Libby's Cajun): a domicilio con dirección, y reservación de mesa con ocasión", () => {
  const E3 = createEngine(LC);
  const correr = xs => { let st = null, ult; for (const x of xs) { const r = E3.handle(st, x, NOW); st = r.state; ult = r.messages.map(toText).join("\n"); if (VERBOSE) console.log(">> " + x + "\n" + ult); } return { st, ult }; };
  const hola = E3.handle(null, "hola", NOW);
  assert.deepEqual(hola.messages.at(-1).buttons, ["Ver el menú y precios", "Hacer un pedido", "Reservar una mesa", "Ubicación y horario", "Pedir a domicilio", "Hablar con una persona"]);

  // delivery: asks pickup or delivery, then the address
  let { st, ult } = correr(["hola", "quiero una mariscada catracha y 2 bebidas", "Confirmar pedido", "A domicilio", "Rio", "Col. Trejo, 5 calle, casa blanca frente a la pulpería", "Carla Mejía"]);
  assert.equal(st.lead.tipo, "pedido"); assert.equal(st.lead.entrega, "domicilio");
  assert.match(st.lead.direccion, /Col. Trejo/); assert.equal(st.lead.total, 1570);
  assert.match(ult, /A domicilio: Col. Trejo/); assert.match(ult, /costo del envío/);
  // pickup keeps asking the hour
  ({ st } = correr(["hola", "2", "1 x1", "Confirmar pedido", "Para recoger", "Lo antes posible", "Ana"]));
  assert.equal(st.lead.entrega, undefined); assert.equal(st.lead.hora, "Lo antes posible");

  // reservation: day, hour, people (in words), occasion, name -> waits for the restaurant
  ({ st, ult } = correr(["hola", "quiero reservar para un cumpleaños", "Otro día", "sábado 14 de noviembre", "7:30 p. m.", "somos seis", "Cumpleaños", "me llamo daniela r."]));
  assert.deepEqual({ tipo: st.lead.tipo, dia: st.lead.dia, hora: st.lead.hora, personas: st.lead.personas, ocasion: st.lead.ocasion, estado: st.lead.estado },
    { tipo: "reservacion", dia: "Sábado 14 de noviembre", hora: "7:30 p. m.", personas: 6, ocasion: "Cumpleaños", estado: "por_confirmar" });
  assert.match(ult, /Reservación RES-1001 recibida, Daniela/); assert.match(ult, /le confirmamos/);
  // a big group is flagged; over the limit goes to a person
  ({ st } = correr(["hola", "3", "Hoy", "8 pm", "15", "Ninguna", "Empresa X"]));
  assert.equal(st.lead.grupo, true); assert.equal(st.lead.ocasion, "");
  ({ st } = correr(["hola", "3", "Mañana", "1 pm", "45"]));
  assert.equal(st.lead, undefined); assert.equal(st.handoff, "San Pedro Sula");
});

test("webhook (Libby's Cajun): la reservación llega al dueño, el panel la confirma y al cliente le llega el aviso", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rest-bot-"));
  const ctx = await montar(dir, { negocio: "negocios/libbys-cajun.json" }, { negocio: cargarNegocio("negocios/libbys-cajun.json") });
  try {
    const cliente = "whatsapp:+50495554444";
    for (const Body of ["hola", "3", "Mañana", "8:00 p. m.", "2", "Cena romántica", "Luis Andino"]) await post(ctx, "/whatsapp", { From: cliente, Body });
    await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, 1);
    assert.match(ctx.sent[0].body, /Nueva reservación RES-1001 · San Pedro Sula/);
    assert.match(ctx.sent[0].body, /Mañana, 8:00 p. m./); assert.match(ctx.sent[0].body, /Cena romántica/);
    const pend = await post(ctx, "/whatsapp", { From: "whatsapp:+50499990000", Body: "pendientes" });
    assert.match(textoDe(pend.xml), /RES-1001/);

    const cookie = await entrar(ctx);
    assert.equal((await (await fetch(ctx.base + "/api/negocio", { headers: { Cookie: cookie } })).json()).reservaciones, true);
    const estado = e => fetch(ctx.base + "/api/pedidos/RES-1001/estado", { method: "POST", headers: { "Content-Type": "application/json", Cookie: cookie }, body: JSON.stringify({ estado: e }) });
    assert.equal((await estado("confirmada")).status, 200);
    await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, 2); assert.equal(ctx.sent[1].to, cliente);
    assert.match(ctx.sent[1].body, /Luis, su mesa en \*San Pedro Sula\* queda apartada: Mañana, 8:00 p. m., 2 personas/);
    await estado("confirmada"); await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, 2, "confirmar dos veces no le escribe dos veces");

    // delivery order: the owner sees the address; "listo" tells the customer it is on its way
    for (const Body of ["hola", "2", "1 x1", "Confirmar pedido", "A domicilio", "Col. Jardines del Valle, 3 calle, portón negro", "Marta"]) await post(ctx, "/whatsapp", { From: "whatsapp:+50491112222", Body });
    await ctx.app.locals.idle();
    assert.match(ctx.sent.at(-1).body, /Nuevo pedido PED-1002/); assert.match(ctx.sent.at(-1).body, /A domicilio: Col. Jardines del Valle/);
    await fetch(ctx.base + "/api/pedidos/PED-1002/estado", { method: "POST", headers: { "Content-Type": "application/json", Cookie: cookie }, body: '{"estado":"listo"}' });
    await ctx.app.locals.idle();
    assert.match(ctx.sent.at(-1).body, /Marta, su pedido \*PED-1002\* ya va en camino/);
  } finally { ctx.srv.close(); }
});

test("ia (Libby's Cajun): crear_reservacion pide la mesa sin darla por confirmada; domicilio lleva dirección", () => {
  const { ejecutar, tools, system } = require("./ia");
  assert.ok(tools(LC).some(t => t.name === "crear_reservacion"));
  assert.ok(!tools(N).some(t => t.name === "crear_reservacion"));
  assert.match(system(LC), /Cómo toma una reservación/); assert.doesNotMatch(system(LC), /No prometa envíos/);
  assert.match(system(N), /No prometa envíos, ni reservaciones/);
  const ctx = { numero: (pre = "PED") => pre + "-7" };
  const r = ejecutar(LC, "crear_reservacion", { nombre: "sofía", dia: "viernes", hora: "7 pm", personas: 4, ocasion: "Aniversario" }, ctx);
  assert.equal(r.numero, "RES-7"); assert.match(r.nota, /no está confirmada/);
  assert.equal(ctx.reservacion.estado, "por_confirmar"); assert.equal(ctx.reservacion.nombre, "Sofía");
  assert.match(ejecutar(LC, "crear_reservacion", { nombre: "x", dia: "hoy", hora: "1", personas: 80 }, {}).error, /pasar_a_persona/);
  const c2 = {};
  ejecutar(LC, "crear_pedido", { nombre: "Ana", productos: [{ id: "sopa", cantidad: 1 }], hora: "ya", direccion: "Col. Trejo, casa 5" }, c2);
  assert.equal(c2.pedido.entrega, "domicilio"); assert.equal(c2.pedido.hora, "A domicilio");
});

// ---------- Gambos: cupos por día y tanda ----------
const GB = cargarNegocio("negocios/gambos.json");
const GBCUP = JSON.parse(fs.readFileSync(path.join(__dirname, "negocios/gambos.json"), "utf8")).cupos;
const gambosCon = cambios => preparar({ ...JSON.parse(fs.readFileSync(path.join(__dirname, "negocios/gambos.json"), "utf8")), ...cambios });

test("negocio (Gambos): nombres del catálogo, cupos por producto y días que todavía se pueden pedir", () => {
  const { fechasCupos } = require("./negocio");
  assert.equal(GB.item("marea x4").id, "marea4"); assert.equal(GB.item("marea x6").id, "marea6");
  assert.equal(GB.item("la marea de 4").id, "marea4"); assert.equal(GB.item("duo de mar").id, "duo");
  assert.equal(GB.item("marea"), null, "ambiguo: no adivina");
  assert.deepEqual(GB.items.filter(i => i.cupos).map(i => i.cupos), [1, 2, 4, 6]);
  const E4 = createEngine(GB);
  assert.deepEqual(E4.leerPedido("marea x6 x2, una libra de camarones").encontrados, [{ id: "marea6", cantidad: 2 }, { id: "camarones", cantidad: 1 }]);
  // NOW = sábado 17 de octubre al mediodía: el domingo todavía se puede (cierra hoy a las 9 pm), el sábado de hoy no
  assert.deepEqual(fechasCupos(GB, NOW).map(f => f.etiqueta), ["domingo 18 de octubre", "jueves 22 de octubre", "viernes 23 de octubre", "sábado 24 de octubre"]);
  assert.equal(fechasCupos(GB, new Date("2026-10-17T21:30:00-06:00"))[0].etiqueta, "jueves 22 de octubre", "después del cierre ya no entra el domingo");
  assert.throws(() => gambosCon({ cupos: { dias: ["lunes"], tandas: [], porTanda: 5 } }), /cupos.tandas/);
  assert.throws(() => gambosCon({ cupos: { dias: ["feriado"], tandas: ["1"], porTanda: 5 } }), /cupos.dias/);
});

test("motor (Gambos): salsa por combo, día, tanda con cupos, lista de espera y adicionales solos", () => {
  const ocup = {};
  const E4 = createEngine(gambosCon({ cupos: { ...GBCUP, dias: ["domingo", "jueves"], porTanda: 4 } }));
  const correr = xs => { let st = null, ult = ""; for (const x of xs) { const r = E4.handle(st, x, NOW, { ocupados: (f, t) => ocup[f + " " + t] || 0 }); st = r.state; ult = r.messages.map(toText).join("\n"); if (VERBOSE) console.log(">> " + x + "\n" + ult); } return { st, ult }; };

  let { st, ult } = correr(["hola", "quiero un duo de mar y 2 elotes", "Confirmar pedido"]);
  assert.match(ult, /Qué salsa para el \*Duo de Mar \(2px\)\*/); assert.match(ult, /Honey Cajún/);
  ({ st, ult } = correr(["hola", "quiero un duo de mar y 2 elotes", "Confirmar pedido", "honey", "Para recoger"]));
  assert.match(ult, /Para qué día\? Su pedido usa 2 cupos/);
  assert.deepEqual(st.offer, ["Domingo 18 de octubre", "Jueves 22 de octubre", "Lista de espera"]);
  ocup["2026-10-18 12:00 p. m."] = 4; ocup["2026-10-18 2:00 p. m."] = 3;   // 12:00 llena, 2:00 con 1 libre
  ({ st, ult } = correr(["hola", "quiero un duo de mar y 2 elotes", "Confirmar pedido", "honey", "Para recoger", "domingo"]));
  assert.deepEqual(st.offer, ["4:30 p. m. · quedan 4", "6:30 p. m. · quedan 4"]);
  ({ st, ult } = correr(["hola", "quiero un duo de mar y 2 elotes", "Confirmar pedido", "honey", "Para recoger", "domingo", "6:30", "daniela paz"]));
  assert.deepEqual({ cupos: st.lead.cupos, diaFecha: st.lead.diaFecha, tanda: st.lead.tanda, hora: st.lead.hora, estado: st.lead.estado },
    { cupos: 2, diaFecha: "2026-10-18", tanda: "6:30 p. m.", hora: "Domingo 18 de octubre, 6:30 p. m.", estado: undefined });
  assert.equal(st.lead.lineas[0].nota, "Salsa Honey Cajún"); assert.equal(st.lead.total, 1070);
  assert.match(ult, /Domingo 18 de octubre, tanda de 6:30 p\. m\. · 2 cupos apartados/); assert.match(ult, /Recoge en \*Pickup en Colonia Florencia Norte\*/);

  // the batch fills while the customer types the name: it offers the others again
  const a = correr(["hola", "1 x2", "si", "clasica", "Para recoger", "domingo", "4:30"]);
  ocup["2026-10-18 4:30 p. m."] = 3;
  const r = E4.handle(a.st, "Ana", NOW, { ocupados: (f, t) => ocup[f + " " + t] || 0 });
  assert.equal(r.state.lead, undefined); assert.match(toText(r.messages[0]), /se llenó esa tanda/); assert.equal(r.state.step, "tanda");

  // a Marea x6 does not fit anywhere: full days are named, the waiting list takes it, with nothing to pay yet
  ({ st, ult } = correr(["hola", "una marea x6", "si", "lemon", "A domicilio", "Col. Palmira, casa 12 portón negro", "domingo"]));
  assert.match(ult, /ya no tiene 6 cupos libres/); assert.ok(st.offer.includes("Lista de espera"));
  ({ st, ult } = correr(["hola", "una marea x6", "si", "lemon", "A domicilio", "Col. Palmira, casa 12 portón negro", "domingo", "Lista de espera", "Carlos"]));
  assert.equal(st.lead.estado, "en_espera"); assert.equal(st.lead.cupos, 6); assert.equal(st.lead.tanda, undefined);
  assert.match(ult, /lista de espera/); assert.match(ult, /Todavía no tiene que pagar nada/);

  // extras alone go with a combo
  ({ ult } = correr(["hola", "2 elotes", "si"]));
  assert.match(ult, /Los adicionales van con un combo/);
});

test("webhook (Gambos): los pedidos llenan la tanda, el panel ve los cupos y al cancelar avisa a quién está en espera", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rest-bot-"));
  const G = gambosCon({ cupos: { ...GBCUP, porTanda: 4 } });
  const ctx = await montar(dir, { negocio: "negocios/gambos.json" }, { negocio: G });
  try {
    const pedir = async (From, xs) => { let r; for (const Body of xs) r = await post(ctx, "/whatsapp", { From, Body }); return textoDe(r.xml); };
    await pedir("whatsapp:+50491110001", ["hola", "marea x4", "si", "honey", "Para recoger", "domingo", "12", "Rosa"]);
    await ctx.app.locals.idle();
    assert.match(ctx.sent.at(-1).body, /Nuevo pedido PED-1001/);
    assert.match(ctx.sent.at(-1).body, /Domingo 18 de octubre · tanda de 12:00 p\. m\. · 4 cupos/);
    assert.match(ctx.sent.at(-1).body, /Marea x4 \(4px\) \(Salsa Honey Cajún\)/);
    // the next customer no longer sees the 12:00 batch
    const t = await pedir("whatsapp:+50491110002", ["hola", "duo de mar", "si", "clasica", "Para recoger", "domingo"]);
    assert.doesNotMatch(t, /12:00/); assert.match(t, /2:00 p\. m\. · quedan 4/);
    // a full weekend for a Marea x6 (6 > 4 per batch) goes to the waiting list
    await pedir("whatsapp:+50491110003", ["hola", "marea x6", "si", "lemon", "Para recoger", "Lista de espera", "Carlos"]);
    await ctx.app.locals.idle();
    assert.match(ctx.sent.at(-1).body, /Lista de espera PED-1002/);

    const cookie = await entrar(ctx);
    const n = await (await fetch(ctx.base + "/api/negocio", { headers: { Cookie: cookie } })).json();
    assert.deepEqual(n.cupos.tandas, G.cupos.tandas); assert.equal(n.cupos.porTanda, 4);
    assert.equal(n.cupos.dias[0].fecha, "2026-10-17"); assert.equal(n.cupos.dias[0].abierto, false); assert.equal(n.cupos.dias[1].abierto, true);
    const antes = ctx.sent.length;
    const r = await fetch(ctx.base + "/api/pedidos/PED-1001/estado", { method: "POST", headers: { "Content-Type": "application/json", Cookie: cookie }, body: '{"estado":"cancelado"}' });
    assert.equal(r.status, 200); await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, antes + 2, "al dueño y al WhatsApp de Gambos");
    assert.match(ctx.sent.at(-1).body, /Se liberaron 4 cupos · domingo 18 de octubre, 12:00 p\. m\./); assert.match(ctx.sent.at(-1).body, /Carlos · 6 cupos/);
    const t2 = await pedir("whatsapp:+50491110004", ["hola", "duo de mar", "si", "clasica", "Para recoger", "domingo"]);
    assert.match(t2, /12:00 p\. m\. · quedan 4/, "el cupo cancelado vuelve a estar libre");
  } finally { ctx.srv.close(); }
});

test("ia (Gambos): ver_cupos y crear_pedido con día, tanda, salsa en la nota y lista de espera", () => {
  const { ejecutar, tools, system } = require("./ia");
  assert.ok(tools(GB).some(t => t.name === "ver_cupos")); assert.ok(!tools(N).some(t => t.name === "ver_cupos"));
  const crear = tools(GB).find(t => t.name === "crear_pedido").input_schema;
  assert.ok(crear.required.includes("fecha")); assert.deepEqual(crear.properties.tanda.enum, GB.cupos.tandas);
  assert.match(system(GB), /Cómo funcionan los cupos/); assert.match(system(GB), /Clásica Cajún, Honey Cajún, Lemon Pepper/);
  const ocupados = (f, t) => (f === "2026-10-18" && t === "6:30 p. m." ? 11 : 0);
  const base = { numero: () => "PED-9", now: NOW, ocupados };
  const v = ejecutar(GB, "ver_cupos", {}, base);
  assert.equal(v.dias[0].fecha, "2026-10-18"); assert.equal(v.dias[0].tandas.find(x => x.tanda === "6:30 p. m.").libres, 1);
  const prod = [{ id: "duo", cantidad: 1, nota: "Salsa Honey Cajún" }];
  assert.match(ejecutar(GB, "crear_pedido", { nombre: "a", productos: prod, fecha: "2026-10-18", tanda: "6:30 p. m." }, { ...base }).error, /1 cupos libres y el pedido usa 2/);
  assert.match(ejecutar(GB, "crear_pedido", { nombre: "a", productos: prod, fecha: "2026-10-17", tanda: "6:30 p. m." }, { ...base }).error, /ya no se puede pedir/);
  assert.match(ejecutar(GB, "crear_pedido", { nombre: "a", productos: [{ id: "elotes", cantidad: 2 }], fecha: "2026-10-18", tanda: "2:00 p. m." }, { ...base }).error, /adicionales van con un combo/);
  const c = { ...base };
  const ok = ejecutar(GB, "crear_pedido", { nombre: "ana", productos: prod, fecha: "2026-10-18", tanda: "2:00 p. m.", direccion: "Col. Kennedy, casa 4" }, c);
  assert.equal(ok.tanda, "2:00 p. m."); assert.equal(ok.cupos, 2);
  assert.deepEqual({ diaFecha: c.pedido.diaFecha, tanda: c.pedido.tanda, cupos: c.pedido.cupos, hora: c.pedido.hora, entrega: c.pedido.entrega },
    { diaFecha: "2026-10-18", tanda: "2:00 p. m.", cupos: 2, hora: "Domingo 18 de octubre, 2:00 p. m.", entrega: "domicilio" });
  const c2 = { ...base };
  const e = ejecutar(GB, "crear_pedido", { nombre: "luis", productos: [{ id: "marea6", cantidad: 1 }], fecha: "2026-10-18", lista_espera: true }, c2);
  assert.equal(c2.pedido.estado, "en_espera"); assert.match(e.nota, /lista de espera/); assert.equal(c2.pedido.tanda, undefined);
});
