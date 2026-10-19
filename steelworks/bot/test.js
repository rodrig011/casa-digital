// Pruebas sin Twilio: npm test   (VERBOSE=1 npm test imprime las conversaciones)
// 1) el motor recorre los flujos principales, 2) el webhook de WhatsApp con un Twilio simulado,
// 3) la llamada de voz con <Gather>, 4) el modo IA con un Claude simulado. Nada sale a internet.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const twilio = require("twilio");
const B = require("./engine");
const { createApp } = require("./server");
const { createIA, MODELO } = require("./ia");

const NOW = new Date("2026-10-13T10:00:00-06:00");
const VERBOSE = !!process.env.VERBOSE;
const CODIGOS = B.CATALOGO.map(p => p.code);
const sinCodigos = (t, ctx) => CODIGOS.forEach(c => assert.ok(!t.includes(c), `código de producto ${c} visible al cliente en: ${ctx}`));

function run(titulo, ...xs) {
  if (VERBOSE) console.log(`\n===== ${titulo} =====`);
  let st = null;
  for (const x of xs) {
    const r = B.handle(st, x, NOW); st = r.state;
    if (VERBOSE) console.log(">> " + x);
    r.messages.forEach(m => { const t = B.toText(m); sinCodigos(t, titulo); if (VERBOSE) console.log(t || "[foto del cliente]"); });
  }
  return st;
}

test("motor: flujos principales y ninguna respuesta muestra códigos", () => {
  const a = run("Portón paso a paso", "hola", "1", "3 x 2.2", "Sí, con motor", "Forjado clásico", "Tegucigalpa", "Agendar visita para medir", "1", "2", "María López");
  assert.equal(a.lead.nombre, "María López");
  assert.match(a.lead.resumen, /Portón con motor/);
  assert.deepEqual(a.lead.rango, [43700, 64300]);
  assert.match(a.lead.cita, /^Visita para medir: Miércoles 14, 10 a 12 m\.$/);
  const b = run("Con sus palabras", "buenas", "cuanto me sale un porton de 4 por 2.5", "no", "el de lanzas", "San Pedro Sula", "que me llamen", "Mañana en la mañana", "soy Carlos");
  assert.equal(b.lead.sucursal, "San Pedro Sula"); assert.equal(b.lead.nombre, "Carlos");
  const c = run("Ventanas sin medidas", "hola", "necesito protecciones para unas ventanas", "no sé", "La Ceiba", "Escribirle a un asesor", "Ana");
  assert.equal(c.lead.rango, null); assert.equal(c.lead.sucursal, "San Pedro Sula");
  const e = run("Ventanas con conteo", "hola", "3 ventanas de 1.2 x 1", "Calado CNC", "Otra ciudad", "Choluteca", "2", "Hoy en la tarde", "Luis");
  assert.match(e.lead.resumen, /3 iguales/);
  const f = run("Baranda con foto", "hola", "4", "8 metros", "📷 Tengo una foto", "Tegucigalpa", "1", "3", "1", "Rosa");
  assert.match(f.lead.resumen, /Baranda/);
  const g = run("Piezas", "hola", "soy herrero busco adornos", "📷 Enviar foto de la pieza", "Tegucigalpa");
  assert.match(g.lead.n, /^PZ-/);
  const h = run("Persona", "hola", "quiero hablar con alguien", "2");
  assert.equal(h.handoff, "San Pedro Sula");
});

// ---------- webhook con Twilio simulado ----------
const TOKEN = "token-de-prueba";
const PUBLIC = "https://bot.steelworks.test";
function montar(dir, extra = {}, deps = {}) {
  const sent = [];
  const client = { messages: { create: async m => { sent.push(m); return { sid: "SM" + sent.length }; } } };
  const cfg = {
    port: 0, sid: "AC_test", token: TOKEN, sandbox: false, from: "whatsapp:+14155238886", contentSid: "",
    owner: "+504 9999-0000", branches: { TGU: "", SPS: "+504 8906-9307" }, transfer: { TGU: "", SPS: "" },
    publicUrl: PUBLIC, skipSignature: false, leadsToken: "secreto", dataDir: dir, ttlHours: 24, fotosUrl: "",
    voiceLang: "es-MX", voiceTts: "Polly.Mia", speechModel: "", ...extra,
  };
  const app = createApp(cfg, { client, now: () => NOW, log: () => {}, ...deps });
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

test("webhook: conversación completa por WhatsApp, ficha guardada y aviso al dueño", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "sw-bot-"));
  const ctx = await montar(dir);
  try {
    const cliente = "whatsapp:+50498765432";
    const pasos = ["Hola Steel Works, quiero cotizar un trabajo.", "1", "3 x 2.2", "Sí, con motor", "Forjado clásico", "Tegucigalpa", "Agendar visita para medir", "1", "2", "María López"];
    let ultimo;
    for (const Body of pasos) {
      ultimo = await post(ctx, "/whatsapp", { From: cliente, Body, NumMedia: "0" });
      assert.equal(ultimo.status, 200);
      assert.equal((ultimo.xml.match(/<Message>/g) || []).length, 1, "un solo mensaje por turno");
      sinCodigos(textoDe(ultimo.xml), Body);
      if (VERBOSE) console.log(">> " + Body + "\n" + textoDe(ultimo.xml).trim());
    }
    assert.match(textoDe(ultimo.xml), /Listo, María/);
    assert.match(textoDe(ultimo.xml), /Cotización COT-2215/);
    await ctx.app.locals.idle();

    // aviso al dueño (la sucursal de TGU no tiene número propio en esta prueba)
    assert.equal(ctx.sent.length, 1);
    assert.equal(ctx.sent[0].to, "whatsapp:+50499990000");
    assert.match(ctx.sent[0].body, /Nueva cotización COT-2215 · WhatsApp/);
    assert.match(ctx.sent[0].body, /María López · \+50498765432/);
    assert.match(ctx.sent[0].body, /L 43,700 a L 64,300/);
    assert.match(ctx.sent[0].body, /Visita para medir: Miércoles 14/);

    // leads.json en disco y GET /leads protegido
    const disco = JSON.parse(fs.readFileSync(path.join(dir, "leads.json"), "utf8"));
    assert.equal(disco.length, 1); assert.equal(disco[0].canal, "whatsapp"); assert.equal(disco[0].tel, "+50498765432");
    assert.equal((await fetch(ctx.base + "/leads")).status, 401);
    assert.equal((await fetch(ctx.base + "/leads?token=otro")).status, 401);
    const leads = await (await fetch(ctx.base + "/leads", { headers: { Authorization: "Bearer secreto" } })).json();
    assert.equal(leads[0].n, "COT-2215"); assert.ok(Array.isArray(leads[0].convo));

    // un segundo cliente recibe otro número (la numeración es global)
    for (const Body of ["hola", "quiero hablar con una persona", "San Pedro Sula"]) await post(ctx, "/whatsapp", { From: "whatsapp:+50433331111", Body });
    await ctx.app.locals.idle();
    const persona = ctx.sent.slice(1);
    assert.deepEqual(persona.map(m => m.to).sort(), ["whatsapp:+50489069307", "whatsapp:+50499990000"]);
    assert.match(persona[0].body, /pidió hablar con una persona · WhatsApp/);

    // el dueño pide su agenda
    const ag = await post(ctx, "/whatsapp", { From: "whatsapp:+50499990000", Body: "agenda" });
    assert.match(textoDe(ag.xml), /Últimas fichas/); assert.match(textoDe(ag.xml), /COT-2215/);
  } finally { ctx.srv.close(); }

  // after a restart the leads and the conversations are still there
  const ctx2 = await montar(dir);
  try {
    await post(ctx2, "/whatsapp", { From: "whatsapp:+50477770000", Body: "hola" });
    const r = await post(ctx2, "/whatsapp", { From: "whatsapp:+50477770000", Body: "2" });
    assert.match(textoDe(r.xml), /puerta/i);
    ctx2.app.locals.store.flush();
    const r2 = await (await fetch(ctx2.base + "/leads", { headers: { Authorization: "Bearer secreto" } })).json();
    assert.equal(r2.length, 2);
    assert.equal((await fetch(ctx2.base + "/leads?token=secreto")).status, 401, "la clave nunca va en la URL");
  } finally { ctx2.srv.close(); }
});

test("webhook: rechaza peticiones sin firma de Twilio", async () => {
  const ctx = await montar(null);
  try {
    assert.equal((await post(ctx, "/whatsapp", { From: "whatsapp:+50411112222", Body: "hola" }, { firmar: false })).status, 403);
    assert.equal((await post(ctx, "/voice", { CallSid: "CA1", From: "+50411112222" }, { firmar: false })).status, 403);
  } finally { ctx.srv.close(); }
  const dev = await montar(null, { skipSignature: true });
  try { assert.equal((await post(dev, "/whatsapp", { From: "whatsapp:+50411112222", Body: "hola" }, { firmar: false })).status, 200); }
  finally { dev.srv.close(); }
});

test("voz: llamada completa con <Gather speech> y aviso al dueño", async () => {
  const ctx = await montar(null);
  try {
    const call = { CallSid: "CA_prueba", From: "+50422334455" };
    let r = await post(ctx, "/voice", call);
    assert.match(r.xml, /<Gather [^>]*input="speech dtmf"[^>]*language="es-MX"/);
    assert.match(r.xml, /Soy el asistente de Steel Works/);
    assert.ok(!/Piezas para herrer/.test(r.xml), "en llamada no se ofrecen piezas (necesitan foto)");
    const pasos = [
      [{ Digits: "1" }, /ancho por alto en metros, por ejemplo: 3 por 2\.2\. O di «no sé las medidas» o marca 1/i],
      [{ SpeechResult: "Tres por dos punto dos." }, /motor eléctrico/],
      [{ SpeechResult: "No." }, /Qué estilo te gusta\? Tenemos tres/],
      [{ SpeechResult: "El forjado." }, /ciudad/],
      [{ SpeechResult: "Tegucigalpa." }, /lempiras/],
      [{ Digits: "1" }, /Qué día/],
      [{ SpeechResult: "El uno." }, /A qué hora/],
      [{ SpeechResult: "", Digits: "" }, /no te escuché/],
      [{ Digits: "3" }, /A nombre de quién/],
    ];
    for (const [p, re] of pasos) {
      r = await post(ctx, "/voice", { ...call, ...p });
      if (VERBOSE) console.log(">> " + JSON.stringify(p) + "\n" + textoDe(r.xml).trim());
      assert.match(textoDe(r.xml), re);
      assert.ok(!/[*📐💰📷]/u.test(textoDe(r.xml)), "la voz no lee emojis ni asteriscos");
    }
    r = await post(ctx, "/voice", { ...call, SpeechResult: "María López." });
    assert.match(r.xml, /<Hangup\/>/);
    assert.match(textoDe(r.xml), /Listo, María.*Su número de cotización es el 2215/s);
    await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, 1);
    assert.match(ctx.sent[0].body, /Nueva cotización COT-2215 · llamada/);
    assert.match(ctx.sent[0].body, /Portón · Medidas: 3 × 2\.2 m · Estilo: Forjado clásico/);
    assert.match(ctx.sent[0].body, /Visita para medir: Miércoles 14, 2 a 4 p\. m\./);
  } finally { ctx.srv.close(); }
});

test("voz: pedir una persona transfiere la llamada a la sucursal", async () => {
  const ctx = await montar(null, { transfer: { TGU: "+50422325628", SPS: "" } });
  try {
    const call = { CallSid: "CA_persona", From: "+50422334455" };
    await post(ctx, "/voice", call);
    let r = await post(ctx, "/voice", { ...call, SpeechResult: "Quiero hablar con una persona." });
    assert.match(textoDe(r.xml), /Con qué sucursal/);
    r = await post(ctx, "/voice", { ...call, Digits: "1" });
    assert.match(r.xml, /<Dial>\+50422325628<\/Dial>/);
    await ctx.app.locals.idle();
    assert.match(ctx.sent[0].body, /pidió hablar con una persona · llamada/);
  } finally { ctx.srv.close(); }
});

// ---------- modo IA con un cliente de Anthropic simulado ----------
// guion: lista de respuestas (o errores) que devuelve messages.create, en orden
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
const usar = (id, name, input) => ({ stop_reason: "tool_use", content: [{ type: "thinking", thinking: "", signature: "x" }, { type: "tool_use", id, name, input }] });
const decir = text => ({ stop_reason: "end_turn", content: [{ type: "text", text }] });
const resultado = (llamada, id) => llamada.body.messages.at(-1).content.find(b => b.type === "tool_result" && b.tool_use_id === id);

test("ia: estimar_precio usa las tarifas del motor y luego contesta", async () => {
  const claude = claudeFalso([
    usar("tu_1", "estimar_precio", { tipo: "porton", estilo: "forjado", ancho: 3, alto: 2.2, motor: true }),
    decir("Un portón forjado de 3 × 2.2 m con motor anda entre *L 43,700 y L 64,300*. Es un precio estimado; el exacto se lo damos al medir, sin costo."),
  ]);
  const ia = createIA({ client: claude });
  const r = await ia.turn([], "quiero un portón forjado de 3 x 2.2 con motor, cuánto sale?", NOW);
  assert.match(r.reply, /L 43,700 y L 64,300/);
  assert.equal(r.lead, null); assert.equal(r.persona, false);
  assert.equal(claude.llamadas.length, 2);
  const [primera, segunda] = claude.llamadas;
  assert.equal(primera.body.model, MODELO);
  assert.deepEqual(primera.body.system.at(-1).cache_control, { type: "ephemeral" });
  assert.deepEqual(primera.body.tools.map(t => t.name), ["estimar_precio", "buscar_piezas", "sucursales", "agendar_visita", "pasar_a_persona"]);
  assert.ok(primera.opts && primera.opts.signal, "cada llamada lleva un límite de tiempo");
  // el rango sale de engine.js, igual que en el flujo de menú (prueba del motor: [43700, 64300])
  const tr = JSON.parse(resultado(segunda, "tu_1").content);
  assert.equal(tr.rango_lempiras, "L 43,700 a L 64,300");
  assert.match(tr.aviso, /estimado/);
  // el historial queda listo para el siguiente mensaje, sin bloques de pensamiento
  assert.equal(r.history[0].role, "user");
  assert.ok(!JSON.stringify(r.history).includes('"thinking"'));
  assert.equal(r.history.length, 4);
  // las piezas se describen por nombre: el código va aparte, nunca dentro del nombre
  const pz = require("./ia").buscarPiezas({ texto: "llamador" });
  assert.ok(pz.piezas.length > 0);
  pz.piezas.forEach(p => sinCodigos(p.nombre, "buscar_piezas"));
});

test("ia: agendar_visita por WhatsApp guarda la ficha y avisa al dueño", async () => {
  const claude = claudeFalso([
    decir("¡Con gusto! ¿Qué medidas tiene el espacio, más o menos?"),
    usar("tu_a", "agendar_visita", { nombre: "maría López", tipo: "porton", ancho: 3, alto: 2.2, motor: true, estilo: "forjado", acabado: "negro mate", sucursal: "TGU", cuando: "miércoles 14, 10 a 12 m.", zona: "Col. Kennedy, Tegucigalpa" }),
    decir("✅ Listo, María. Su cotización es la *COT-2215*. La sucursal de Tegucigalpa le confirma la visita por este chat."),
  ]);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "sw-bot-ia-"));
  const ctx = await montar(dir, {}, { ia: createIA({ client: claude }) });
  try {
    const cliente = "whatsapp:+50498765432";
    let r = await post(ctx, "/whatsapp", { From: cliente, Body: "quiero un portón para mi casa de unos 3 metros, cuánto sale?", NumMedia: "0" });
    assert.match(textoDe(r.xml), /Qué medidas/);
    r = await post(ctx, "/whatsapp", { From: cliente, Body: "3 x 2.2 forjado con motor, María López, el miércoles en la mañana", NumMedia: "0" });
    assert.equal((r.xml.match(/<Message>/g) || []).length, 1);
    assert.match(textoDe(r.xml), /COT-2215/);
    // el segundo mensaje llevó el historial del primero
    assert.equal(claude.llamadas[1].body.messages.length, 3);
    assert.equal(JSON.parse(resultado(claude.llamadas[2], "tu_a").content).numero, "COT-2215");
    await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, 1);
    assert.equal(ctx.sent[0].to, "whatsapp:+50499990000");
    assert.match(ctx.sent[0].body, /Nueva cotización COT-2215 · WhatsApp/);
    assert.match(ctx.sent[0].body, /María López · \+50498765432/);
    assert.match(ctx.sent[0].body, /Portón con motor · Medidas: 3 × 2\.2 m · Estilo: Forjado clásico · Lugar: Col\. Kennedy, Tegucigalpa · Acabado: negro mate/);
    assert.match(ctx.sent[0].body, /L 43,700 a L 64,300/);
    assert.match(ctx.sent[0].body, /Visita para medir: miércoles 14/);
    const disco = JSON.parse(fs.readFileSync(path.join(dir, "leads.json"), "utf8"));
    assert.equal(disco[0].n, "COT-2215"); assert.equal(disco[0].convo.length, 4);

    // pasar_a_persona: aviso de "pidió hablar con una persona" al dueño y a la sucursal de SPS
    const otro = "whatsapp:+50433331111";
    claude.guion.push(usar("tu_p", "pasar_a_persona", { motivo: "quiere factura a nombre de empresa", sucursal: "SPS" }), decir("Le paso con un asesor de San Pedro Sula, le escribe por aquí."));
    r = await post(ctx, "/whatsapp", { From: otro, Body: "necesito factura a nombre de mi empresa" });
    assert.match(textoDe(r.xml), /asesor/);
    await ctx.app.locals.idle();
    const p = ctx.sent.slice(1);
    assert.deepEqual(p.map(m => m.to).sort(), ["whatsapp:+50489069307", "whatsapp:+50499990000"]);
    assert.match(p[0].body, /pidió hablar con una persona · WhatsApp/);
    assert.match(p[0].body, /factura a nombre de empresa/);
  } finally { ctx.srv.close(); }
});

test("ia: si la API falla, contesta el menú de siempre y lo anota en el log", async () => {
  const Anthropic = require("@anthropic-ai/sdk");
  const logs = [];
  const claude = claudeFalso([new Anthropic.APIConnectionTimeoutError(), new Error("529 overloaded")]);
  const ctx = await montar(null, {}, { ia: createIA({ client: claude }), log: (...a) => logs.push(a.join(" ")) });
  try {
    const cliente = "whatsapp:+50455556666";
    let r = await post(ctx, "/whatsapp", { From: cliente, Body: "hola, quiero un portón" });
    assert.equal(r.status, 200);
    assert.match(textoDe(r.xml), /Soy el asistente de \*Steel Works\*/);
    assert.match(textoDe(r.xml), /Qué te gustaría cotizar/);
    // the next message also fails over, and the menu flow keeps its place
    r = await post(ctx, "/whatsapp", { From: cliente, Body: "1" });
    assert.match(textoDe(r.xml), /Cuánto mide el espacio/);
    assert.equal(logs.filter(l => /^\[ia\] error/.test(l)).length, 2);
    assert.match(logs[0], /APIConnectionTimeoutError/);
    await ctx.app.locals.idle();
    assert.equal(ctx.sent.length, 0);
  } finally { ctx.srv.close(); }
});

test("panel: solo entra quien tiene correo y contraseña autorizados", async () => {
  const { hashClave, verificarClave, COOKIE } = require("./auth");
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "sw-panel-"));
  const linea = `dueno@steelworks.hn|Dueño|${await hashClave("hierro-forjado-40")}`;
  assert.ok(await verificarClave("hierro-forjado-40", linea.split("|")[2]));
  assert.ok(!(await verificarClave("otra-clave-larga", linea.split("|")[2])));
  await assert.rejects(hashClave("corta"), /al menos 10/);

  // without PANEL_SECRET the panel stays closed
  const cerrado = await montar(dir, { panelSecret: "", panelUsuarios: linea });
  try { assert.equal((await fetch(cerrado.base + "/panel", { redirect: "manual" })).status, 503); } finally { cerrado.srv.close(); }

  const ctx = await montar(dir, { panelSecret: "s".repeat(40), panelUsuarios: linea });
  const entrar = (correo, clave, extra = {}) => fetch(ctx.base + "/panel/entrar", { method: "POST", redirect: "manual", headers: { "Content-Type": "application/x-www-form-urlencoded", ...extra }, body: new URLSearchParams({ correo, clave }) });
  try {
    // no session: sent to the login page, and the panel file is not served
    const sin = await fetch(ctx.base + "/panel", { redirect: "manual" });
    assert.equal(sin.status, 303); assert.equal(sin.headers.get("location"), "/panel/entrar");
    assert.match(await (await fetch(ctx.base + "/panel/entrar")).text(), /Entrar al panel/);
    assert.equal((await fetch(ctx.base + "/panel/yo")).status, 401);

    // wrong password, unknown email
    const mal = await entrar("dueno@steelworks.hn", "no-es-esta-clave");
    assert.equal(mal.status, 401); assert.match(await mal.text(), /incorrectos/); assert.equal(mal.headers.get("set-cookie"), null);
    assert.equal((await entrar("otro@gmail.com", "hierro-forjado-40")).status, 401);
    // another site cannot post the login form
    assert.equal((await entrar("dueno@steelworks.hn", "hierro-forjado-40", { Origin: "https://malo.example" })).status, 403);

    // right password (email in any case): cookie, then the panel and /leads open
    const ok = await entrar("  Dueno@SteelWorks.hn ", "hierro-forjado-40");
    assert.equal(ok.status, 303); assert.equal(ok.headers.get("location"), "/panel");
    const sc = ok.headers.get("set-cookie");
    assert.match(sc, new RegExp(`^${COOKIE}=`)); assert.match(sc, /HttpOnly/); assert.match(sc, /SameSite=Strict/);
    const cookie = sc.split(";")[0];
    const pan = await fetch(ctx.base + "/panel", { headers: { Cookie: cookie } });
    assert.equal(pan.status, 200); assert.match(await pan.text(), /PANEL_MODO = "servidor"/); assert.equal(pan.headers.get("cache-control"), "no-store");
    assert.deepEqual(await (await fetch(ctx.base + "/panel/yo", { headers: { Cookie: cookie } })).json(), { correo: "dueno@steelworks.hn", nombre: "Dueño" });
    assert.equal((await fetch(ctx.base + "/leads", { headers: { Cookie: cookie } })).status, 200);

    // a tampered cookie does not work
    const [v, f] = cookie.split("=")[1].split(".");
    const otro = Buffer.from(JSON.stringify({ ...JSON.parse(Buffer.from(v, "base64url")), e: "otro@gmail.com" })).toString("base64url");
    assert.equal((await fetch(ctx.base + "/panel", { redirect: "manual", headers: { Cookie: `${COOKIE}=${otro}.${f}` } })).status, 303);

    // log out clears the cookie
    const out = await fetch(ctx.base + "/panel/salir", { redirect: "manual", headers: { Cookie: cookie } });
    assert.equal(out.status, 303); assert.match(out.headers.get("set-cookie"), /Max-Age=0/);
    // ...and ends the session on the server: a copy of the old cookie no longer opens anything
    assert.equal((await fetch(ctx.base + "/panel", { redirect: "manual", headers: { Cookie: cookie } })).status, 303);
    assert.equal((await fetch(ctx.base + "/panel/yo", { headers: { Cookie: cookie } })).status, 401);
  } finally { ctx.srv.close(); }

  // a password change ends old sessions; 5 wrong tries lock the email
  const ctx2 = await montar(dir, { panelSecret: "s".repeat(40), panelUsuarios: linea });
  try {
    const r = await fetch(ctx2.base + "/panel/entrar", { method: "POST", redirect: "manual", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ correo: "dueno@steelworks.hn", clave: "hierro-forjado-40" }) });
    const cookie = r.headers.get("set-cookie").split(";")[0];
    ctx2.srv.close();
    const nueva = `dueno@steelworks.hn|Dueño|${await hashClave("clave-nueva-2026")}`;
    const ctx3 = await montar(dir, { panelSecret: "s".repeat(40), panelUsuarios: nueva });
    try {
      assert.equal((await fetch(ctx3.base + "/panel", { redirect: "manual", headers: { Cookie: cookie } })).status, 303, "la sesión vieja ya no vale");
      const intento = clave => fetch(ctx3.base + "/panel/entrar", { method: "POST", redirect: "manual", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ correo: "dueno@steelworks.hn", clave }) });
      for (let i = 0; i < 5; i++) assert.equal((await intento("mala-clave-" + i)).status, 401);
      assert.equal((await intento("clave-nueva-2026")).status, 429, "bloqueado aunque ahora acierte");
    } finally { ctx3.srv.close(); }
  } finally { ctx2.srv.close(); }
});
