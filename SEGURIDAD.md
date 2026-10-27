# Seguridad para nuestros clientes

Regla: ningún proyecto se entrega a un cliente sin pasar la lista de abajo. GitHub la revisa en parte solo
(`.github/workflows/seguridad.yml`: claves en el historial, dependencias y pruebas en cada cambio y cada lunes);
el resto se revisa a mano antes de entregar.

## Lista para cada proyecto nuevo

**Claves y datos**
- [ ] Ninguna clave, contraseña o token en el código, en el HTML ni en git. Solo en las variables de Render (o `.env` local, que nunca se sube).
- [ ] La revisión "Seguridad" de GitHub sale en verde (sin claves en el historial, sin vulnerabilidades altas).
- [ ] Ningún dato real de clientes de nuestros clientes en el repositorio (pedidos, teléfonos, conversaciones, comprobantes). El repositorio solo lleva datos públicos del negocio o de ejemplo.
- [ ] Una subcuenta de Twilio por cliente y claves propias por cliente: si una se filtra, se cambia solo esa.

**Entrar al panel**
- [ ] El panel real se sirve desde el servidor con correo y contraseña (`auth.js`): contraseñas con hash scrypt de al menos 10 caracteres, cookie HttpOnly + SameSite=Strict + Secure, 12 horas, "Salir" la invalida, 5 intentos fallidos bloquean 15 minutos.
- [ ] Cada pedido de datos (`/api/...`) revisa la sesión en el servidor. Un login hecho solo en el navegador no protege nada: las demos HTML tienen login falso y nunca llevan datos reales.
- [ ] Solo entran las personas que el dueño autoriza (`npm run usuario -- agregar|quitar`).
- [ ] Entrada en dos pasos: cada persona se registra con su WhatsApp (`npm run usuario -- agregar correo "Nombre" 504XXXXXXXX`) y al entrar le llega un código de 6 números que vence en 5 minutos.
- [ ] Datos cifrados en el disco con `DATA_KEY` (`cifrado.js`, AES-256-GCM): pedidos, clientes, conversaciones, usuarios y bitácora. En Render el servidor no arranca sin la llave. Guardar una copia de la llave en el gestor de contraseñas.
- [ ] Bitácora (`bitacora.js`): cada entrada, intento fallido, bloqueo y cambio de pedido queda anotado; el dueño la ve en Seguridad.

**Lo que entra de afuera**
- [ ] El webhook de WhatsApp solo acepta mensajes firmados por Twilio (`SKIP_TWILIO_SIGNATURE=false` en producción).
- [ ] Freno por número (`seguridad.js`): 40 mensajes cada 10 minutos y 80 respuestas con IA al día; protege la cuenta de Twilio y de Claude.
- [ ] Precios, totales y estados se calculan en el servidor, nunca se aceptan del cliente ni de la IA. Un pago con tarjeta se confirma consultando a la pasarela, no creyendo su aviso.
- [ ] Todo texto que escribe un cliente se escapa antes de mostrarse en el panel (`esc()`), y se corta a un largo máximo.
- [ ] El servidor no recibe archivos subidos; las fotos de comprobantes se quedan en Twilio.

**Servidor**
- [ ] Solo https (Render lo da; `soloHttps` manda a https y HSTS lo fija en el navegador).
- [ ] Cabeceras de seguridad en todas las respuestas (`cabeceras()`: CSP sin scripts de otros sitios, sin iframes, nosniff).
- [ ] Las respuestas de la API llevan solo lo que el panel necesita.
- [ ] Los registros (logs) no muestran contraseñas ni claves; solo los ve quien tiene la cuenta de Render.

**Cuentas**
- [ ] Verificación en dos pasos en GitHub, Render, Twilio, Anthropic, Meta Business y Stripe.
- [ ] Límite de gasto mensual en la consola de Anthropic y alerta de saldo en Twilio.

## Los 20 puntos del video y dónde estamos (19 de octubre de 2026)

Video: "Me faltó algo?" de @nicofrancken en TikTok (lista de seguridad para apps hechas con IA).

| # | Punto | Estado |
|---|---|---|
| 1 | Ocultar las API keys | Cumple: solo en variables de Render; el navegador nunca las ve. |
| 2 | Eliminar secretos del historial de git | Cumple: gitleaks no encontró nada en los 100 cambios guardados del repositorio; ahora se revisa en cada cambio. |
| 3 | Usar la key pública para la base de datos | No aplica: no usamos Supabase ni Firebase; los datos los lee solo el servidor. |
| 4 | Activar Row Level Security | No aplica por lo mismo. Si un proyecto usa Supabase/Firebase, RLS es obligatorio. |
| 5 | Encriptar datos sensibles | Cumple: contraseñas con scrypt, todo viaja por https, tarjetas solo en la pasarela. |
| 6 | Autenticación del lado del servidor | Cumple en el panel real. Las demos HTML tienen login falso y solo datos de ejemplo. |
| 7 | Restringir el acceso a los registros | Cumple: logs solo en la cuenta de Render, sin claves. |
| 8 | Bloquear la manipulación de campos | Cumple: precios y totales salen del menú en el servidor; estados validados. |
| 9 | Proteger las cookies de sesión | Cumple: HttpOnly, SameSite=Strict, Secure, firmada, 12 h. |
| 10 | Hashear las contraseñas | Cumple: scrypt con sal. |
| 11 | Rate limiting en el login | Cumple: 5 intentos por correo y por IP, 15 min. Mejorado: limpia la memoria si atacan con miles de correos. |
| 12 | Protección contra bots | Mejorado: además de la firma de Twilio, freno por número y tope diario de IA. |
| 13 | Parametrizar las queries | No aplica: no hay SQL. |
| 14 | Validar todos los inputs | Cumple: mensajes cortados a 1000 caracteres, cuerpos de máximo 20 KB, cantidades de 1 a 99. |
| 15 | Sanitizar el contenido del usuario | Cumple: el panel escapa nombres, notas y mensajes. |
| 16 | Restringir los archivos que se pueden subir | Cumple: no se suben archivos al servidor. |
| 17 | Solo los datos necesarios en la API | Cumple: `/api/negocio` filtra campos; pedidos solo con sesión o token. |
| 18 | Security headers | Nuevo: CSP, HSTS, X-Frame-Options, nosniff, Referrer-Policy, Permissions-Policy. |
| 19 | Forzar https | Nuevo en los bots. Página de Clientia: activar "Enforce HTTPS" en GitHub Pages. |
| 20 | Escanear dependencias | Nuevo: `npm audit` en cada cambio y cada lunes (hoy: 0 vulnerabilidades). |

Además: en Steel Works la clave de `/leads` ya no se acepta en la URL (las URLs quedan guardadas en registros).

## Pendiente de Rodrigo (no se puede hacer desde el código)

1. Hacer privado el repositorio: tiene investigación de prospectos y el material de Coco Chicken y Mag Pollo, que son rivales. Ojo: GitHub Pages en un repositorio privado pide GitHub Pro (US$4 al mes), o mover la página a Netlify/Cloudflare Pages.
2. Verificación en dos pasos en todas las cuentas de la lista.
3. Límite de gasto en Anthropic y alerta de saldo en Twilio antes de encender el bot de Coco Chicken.
4. GitHub > Settings > Pages > "Enforce HTTPS" para clientiatech.com.
