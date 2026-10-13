// node test.js · recorre los flujos del asistente en texto plano
const B = require("./engine");
let st = null;
const run = (title, ...xs) => {
  console.log("\n===== " + title);
  st = null;
  for (const x of xs) {
    const r = B.handle(st, x); st = r.state;
    console.log("\n>> " + x);
    r.messages.forEach(m => console.log(m.userImage ? "[foto del cliente]" : B.toText(m)));
  }
  return st;
};
const a = run("Portón dicho con sus palabras", "hola", "Quiero un portón para la cochera de 4 por 2", "clasico", "110-702", "Tegucigalpa", "Jueves en la mañana");
console.assert(a.cot.lines[0].qty === 35 && a.handoff === "Tegucigalpa", "portón");
const b = run("Cerco por número de opción", "hola", "1", "2", "18 metros", "1", "4", "2", "3");
console.assert(b.cot.medidas === "18 m lineales" && b.visita === "Prefiero que me llamen", "cerco");
const c = run("Piezas sin saber códigos", "hola", "busco unas puntas para una reja", "110-721", "25", "Ver mi cotización", "Envío a mi ciudad");
console.assert(c.pedido.total === 25 * 81.27, "piezas");
const d = run("Foto", "hola", "📷 Enviar una foto", "Sí, una puerta así", "No sé, que vengan a medir", "222-2950", "San Pedro Sula", "Viernes en la tarde");
console.assert(d.cot.medidas === "Por medir en visita" && d.handoff === "San Pedro Sula", "foto");
const e = run("Asesor y sucursales", "hola", "dónde están y qué horario tienen", "quiero hablar con una persona", "San Pedro Sula");
console.assert(e.handoff === "San Pedro Sula", "asesor");
console.log("\nOK");
