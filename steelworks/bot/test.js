// Recorre las conversaciones principales: node test.js
const B = require("./engine");
const NOW = new Date("2026-10-13T10:00:00-06:00");
function run(titulo, ...xs) {
  console.log(`\n===== ${titulo} =====`);
  let st = null;
  for (const x of xs) {
    const r = B.handle(st, x, NOW); st = r.state;
    console.log(">> " + x);
    r.messages.forEach(m => console.log(B.toText(m) || "[foto del cliente]"));
  }
  return st;
}
const a = run("Portón paso a paso", "hola", "1", "3 x 2.2", "Sí, con motor", "Forjado clásico", "Tegucigalpa", "Agendar visita para medir", "1", "2", "María López");
const b = run("Con sus palabras", "buenas", "cuanto me sale un porton de 4 por 2.5", "no", "el de lanzas", "San Pedro Sula", "que me llamen", "Mañana en la mañana", "soy Carlos");
const c = run("Ventanas sin medidas", "hola", "necesito protecciones para unas ventanas", "no sé", "La Ceiba", "Escribirle a un asesor", "Ana");
const e = run("Ventanas con conteo", "hola", "3 ventanas de 1.2 x 1", "Calado CNC", "Otra ciudad", "Choluteca", "2", "Hoy en la tarde", "Luis");
const f = run("Baranda con foto", "hola", "4", "8 metros", "📷 Tengo una foto", "Tegucigalpa", "1", "3", "1", "Rosa");
run("Piezas", "hola", "soy herrero busco adornos", "📷 Enviar foto de la pieza", "Tegucigalpa");
run("Persona", "hola", "quiero hablar con alguien", "2");
console.log("\nfichas:", [a, b, c, e, f].map(s => s.lead));
