// Adaptador de voz: el mismo motor de cotización, hablado por teléfono con Twilio <Gather input="speech">.
// Convierte lo que dice el motor a frases para leer en voz alta, y lo que dice el cliente a texto
// que el motor entiende ("tres por dos punto dos" -> "3 por 2.2", "uno" -> la primera opción).
const norm = s => (s || "").toString().trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");

// on a call there is no photo to send and no chat to write in
const SIN_VOZ = /📷|Escribirle a un asesor|Piezas para herrer/;

const FRASES = [
  [/Estos son trabajos nuestros:/, "Tenemos tres."],
  [/Toca uno de los estilos, o mándame una foto de uno que te guste\./, "Dime uno de los estilos."],
  [/Puedes tocar una opción o escribirme con tus palabras/, "Puedes decirme una opción con tus palabras"],
  [/Escríbeme solo/g, "Dime solo"], [/Escríbelas así/g, "Dímelas así"], [/No logré leer/g, "No logré entender"],
  [/por aquí mismo/g, "por WhatsApp a este número"],
  [/Cotización COT-(\d+)/g, "Su número de cotización es el $1"],
  [/L (\d[\d,.]*)/g, "$1 lempiras"],
  [/12 m\./g, "12 del mediodía"], [/a\. m\./g, "de la mañana"], [/p\. m\./g, "de la tarde"],
  [/(\d) ?[×x] ?(\d)/g, "$1 por $2"], [/(\d) m\b/g, "$1 metros"],
  [/\s*\(ejemplo, por confirmar\)/g, ""],
];

// text for <Say>: no emoji, no *bold*, words a voice can read
function hablar(text) {
  let s = (text || "").replace(/\*/g, "");
  for (const [a, b] of FRASES) s = s.replace(a, b);
  return s.replace(/[\u{1F000}-\u{1FFFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, "").replace(/\n+/g, ". ").replace(/\s*\.\s*\./g, ".").replace(/\s{2,}/g, " ").trim();
}

// engine messages -> { texto, opciones } for one turn of the call
function turno(messages) {
  let opciones = [], detalle = {};
  const partes = [];
  for (const m of messages) {
    if (m.image) continue;
    if (m.text) partes.push(hablar(m.text));
    if (m.buttons) {
      opciones = m.buttons.filter(b => !SIN_VOZ.test(b));
      detalle = {};
      (m.gallery || []).forEach(g => (detalle[g.title] = g.sub));
    }
  }
  let texto = partes.filter(Boolean).join(" ");
  if (opciones.length === 1) texto += ` O di «${opciones[0].toLowerCase()}» o marca 1.`;
  else if (opciones.length) texto += " Dime la opción o marca su número: " + opciones.map((o, i) => `${i + 1}, ${hablar(o).replace(/\.$/, "")}${detalle[o] ? ", " + detalle[o].toLowerCase() : ""}`).join(". ") + ".";
  return { texto, opciones };
}

// Spanish number words -> digits, so the engine can read measures and counts
const U = { cero: 0, un: 1, uno: 1, una: 1, dos: 2, tres: 3, cuatro: 4, cinco: 5, seis: 6, siete: 7, ocho: 8, nueve: 9, diez: 10, once: 11, doce: 12, trece: 13, catorce: 14, quince: 15, dieciseis: 16, diecisiete: 17, dieciocho: 18, diecinueve: 19, veinte: 20, veintiuno: 21, veintiun: 21, veintidos: 22, veintitres: 23, veinticuatro: 24, veinticinco: 25, veintiseis: 26, veintisiete: 27, veintiocho: 28, veintinueve: 29 };
const D = { treinta: 30, cuarenta: 40, cincuenta: 50, sesenta: 60, setenta: 70, ochenta: 80, noventa: 90 };
const W = "(?<!\\p{L})(\\p{L}+)(?!\\p{L})";               // a whole word, accents included
function aTexto(speech) {
  let s = String(speech || "").replace(/[¿?¡!]/g, "").trim().replace(/\.$/, "");
  s = s.replace(new RegExp(W + " y " + W, "gu"), (m, a, b) => (norm(a) in D && U[norm(b)] < 10 ? String(D[norm(a)] + U[norm(b)]) : m));
  s = s.replace(new RegExp(W + "\\s+(metros?|ventanas?|puertas?|port[oó]n)", "giu"), (m, a, b) => (/^un[oa]?$/.test(norm(a)) ? "1 " + b : m));
  s = s.replace(new RegExp(W, "gu"), w => { const k = norm(w); return k in D ? String(D[k]) : k in U && !/^un[a]?$/.test(k) ? String(U[k]) : w; });
  return s.replace(/(\d)\s*(?:punto|coma)\s*(\d)/gi, "$1.$2").replace(/(\d+) y medio/gi, "$1.5");
}

// what the caller said or pressed -> the text we hand to the engine
function entrada({ SpeechResult, Digits }, opciones) {
  const n = Digits ? parseInt(Digits, 10) : NaN;
  if (n && opciones[n - 1]) return opciones[n - 1];
  if (!SpeechResult) return Digits || "";
  const t = aTexto(SpeechResult);
  const k = /^(?:el |la |opci[oó]n |n[uú]mero )?(\d)$/i.exec(t);
  if (k && opciones[+k[1] - 1]) return opciones[+k[1] - 1];
  return t;
}

module.exports = { hablar, turno, aTexto, entrada };
