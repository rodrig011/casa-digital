// Seguridad común del servidor (el mismo archivo vive en bot-restaurante/ y steelworks/bot/).
//
//   app.use(cabeceras())      cabeceras de seguridad en todas las respuestas (CSP, HSTS, sin iframes, nosniff)
//   app.use(soloHttps)        si el proxy dice que la visita llegó por http, la manda a https
//   createLimite({ max, minutos }).pasa(numero)   cuántos mensajes acepta por número en una ventana de tiempo
//
// El freno de mensajes protege la cuenta de Twilio y de Claude: alguien que escribe cientos de mensajes
// seguidos (a mano o con un programa) recibe un aviso y luego silencio hasta que pase la ventana.

// Panel, página de entrada y página de pago: todo sale de este servidor, sin scripts de otros sitios.
const CSP = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "connect-src 'self'",
  "font-src 'self' data:",
  "object-src 'none'",
  "base-uri 'none'",
  "form-action 'self'",
  "frame-ancestors 'none'",
].join("; ");

function cabeceras({ csp = CSP } = {}) {
  return (req, res, next) => {
    res.removeHeader("X-Powered-By");
    res.set({
      "Content-Security-Policy": csp,
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      "Referrer-Policy": "same-origin",
      "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
      "Cross-Origin-Opener-Policy": "same-origin",
    });
    if (req.secure) res.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
    next();
  };
}

// Render (y casi todo hosting) contesta https y pasa X-Forwarded-Proto; en local no hay proxy y no se toca nada
function soloHttps(req, res, next) {
  if (String(req.get("X-Forwarded-Proto") || "").split(",")[0].trim() !== "http") return next();
  if (req.method !== "GET" && req.method !== "HEAD") return res.status(403).type("text/plain").send("Use https");
  res.redirect(301, `https://${req.get("host")}${req.originalUrl}`);
}

function createLimite({ max = 40, minutos = 10, ahora = () => Date.now() } = {}) {
  const m = new Map();
  const ventana = minutos * 6e4;
  let limpio = ahora();
  return {
    // true mientras el número no pasó del máximo; avisar = true solo la primera vez que se pasa
    pasa(key) {
      const t = ahora();
      if (t - limpio > ventana) { for (const [k, e] of m) if (e.hasta < t) m.delete(k); limpio = t; }
      let e = m.get(key);
      if (!e || e.hasta < t) { e = { n: 0, hasta: t + ventana }; m.set(key, e); }
      e.n++;
      return e.n <= max;
    },
    primeraVezFuera: key => { const e = m.get(key); return !!e && e.n === max + 1; },
  };
}

module.exports = { cabeceras, soloHttps, createLimite, CSP };
