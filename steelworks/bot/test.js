// Pruebas sin Twilio: npm test   (VERBOSE=1 npm test imprime las conversaciones)
// 1) el motor recorre los flujos principales, 2) el webhook de WhatsApp con un Twilio simulado,
// 3) la llamada de voz con <Gather>. Nada sale a internet.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const twilio = require("twilio");
const B = require("./engine");
const { createApp } = require("./server");

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
function montar(dir, extra = {}) {
  const sent = [];
  const client = { messages: { create: async m => { sent.push(m); return { sid: "SM" + sent.length }; } } };
  const cfg = {
    port: 0, sid: "AC_test", token: TOKEN, sandbox: false, from: "whatsapp:+14155238886", contentSid: "",
    owner: "+504 9999-0000", branches: { TGU: "", SPS: "+504 8906-9307" }, transfer: { TGU: "", SPS: "" },
    publicUrl: PUBLIC, skipSignature: false, leadsToken: "secreto", dataDir: dir, ttlHours: 24, fotosUrl: "",
    voiceLang: "es-MX", voiceTts: "Polly.Mia", speechModel: "", ...extra,
  };
  const app = createApp(cfg, { client, now: () => NOW, log: () => {} });
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
    const r2 = await (await fetch(ctx2.base + "/leads?token=secreto")).json();
    assert.equal(r2.length, 2);
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
