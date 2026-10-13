# Bot de WhatsApp de Steel Works · instalación

El asistente contesta WhatsApp a cualquier hora: pregunta qué quiere cotizar el cliente, pide medidas, deja escoger el estilo, da un precio estimado y agenda la visita para medir o una llamada. Cada ficha terminada:

- se guarda en `leads.json` (y se puede leer en `GET /leads` para el panel del dueño),
- le llega por WhatsApp al dueño y, si tiene número propio, a la sucursal que la atiende,
- si el cliente pide "hablar con una persona", también se avisa al dueño en ese momento.

La idea es automatizar el proceso y no depender de una secretaria: el dueño recibe los avisos y la agenda, y el taller recibe el trabajo ya anotado.

Para llamadas telefónicas ver [LLAMADAS.md](LLAMADAS.md).

## Archivos

| Archivo | Qué hace |
|---|---|
| `engine.js` | La conversación (el mismo archivo usa la demo del sitio). Las tarifas en `TARIFAS` son de ejemplo. |
| `server.js` | Servidor: `/whatsapp`, `/voice`, `/leads`. Valida la firma de Twilio. |
| `avisos.js` | Arma y manda los avisos al dueño y a la sucursal. |
| `store.js` | Guarda conversaciones y fichas en `DATA_DIR` (`leads.json`, `sessions.json`). |
| `voz.js` | Convierte la conversación a voz para las llamadas. |
| `test.js` | Pruebas sin Twilio: `npm test`. |
| `.env.example` | Todas las variables, explicadas. |
| `render.yaml`, `Dockerfile` | Para publicarlo en Render o en cualquier servidor con Docker. |

## 1. Probarlo en tu computadora (5 minutos)

Necesitas Node 22 o más nuevo.

```bash
cd steelworks/bot
npm install
npm test                      # simula conversaciones completas; debe decir "pass 5, fail 0"
cp .env.example .env          # y llena lo que tengas
npm start                     # "Bot escuchando en :3000"
```

Sin cuenta de Twilio también arranca: los avisos al dueño salen en la consola. Para hablarle sin Twilio pon `SKIP_TWILIO_SIGNATURE=true` en `.env` y:

```bash
curl -X POST localhost:3000/whatsapp -d "From=whatsapp:+50499999999" -d "Body=hola"
```

## 2. Crear la cuenta de Twilio

1. Entra a [twilio.com/try-twilio](https://www.twilio.com/try-twilio) y crea la cuenta (pide verificar un correo y un celular).
2. En la consola copia **Account SID** y **Auth Token** a `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN`.
3. Pasa la cuenta a pago (Upgrade) cuando vayan a usar el número propio. La prueba gratis sirve para el sandbox.

## 3. Probar con el sandbox de WhatsApp (gratis, el mismo día)

El sandbox es un número de Twilio (+1 415 523 8886) para probar antes de tener el número propio aprobado.

1. Consola de Twilio > **Messaging > Try it out > Send a WhatsApp message**.
2. Desde tu WhatsApp manda al +1 415 523 8886 el código que te muestra (`join palabra-palabra`). Cada persona que vaya a probar, **incluido el dueño**, tiene que hacer esto una vez.
3. En **Sandbox settings**, en *When a message comes in*, pon `https://TU-URL/whatsapp` (método POST). La URL sale del paso 5. Para probar desde tu computadora sirve un túnel, por ejemplo `npx localtunnel --port 3000` o ngrok.
4. En `.env`: `TWILIO_SANDBOX=true`, `OWNER_WHATSAPP=+504 ...` (el celular del dueño) y `PUBLIC_URL=https://TU-URL`.
5. Escríbele "hola" al sandbox y sigue la conversación. Al terminar, al celular del dueño le llega la ficha.

En el sandbox el aviso al dueño solo llega si el dueño le escribió al sandbox en las últimas 24 horas (regla de WhatsApp). El dueño puede escribir **agenda** al bot: le contesta con las últimas fichas y deja la ventana abierta.

## 4. Pasar a WhatsApp Business con el número de Steel Works

1. **Escoger el número.** Puede ser una línea de Steel Works (fija o celular) que reciba un SMS o una llamada para el código de verificación. Ojo: un número que hoy está en la app de WhatsApp o WhatsApp Business pasa a ser del bot y deja de funcionar en la app. Meta tiene un modo "coexistencia" para usar la app y el bot en el mismo número; hay que confirmar con Twilio si lo permite para ese número. Lo más simple es una línea nueva solo para el bot.
2. **Meta Business.** Crear (o usar) la cuenta de Meta Business de Steel Works en [business.facebook.com](https://business.facebook.com). Conviene hacer la **verificación del negocio** (RTN o escritura, recibo de servicios con la dirección y el sitio web): sin ella hay límites bajos de mensajes iniciados por el negocio, y es obligatoria para las llamadas por WhatsApp.
3. **Registrar el número en Twilio.** Consola > **Messaging > Senders > WhatsApp senders > Create new sender**. Twilio abre el registro de Meta (Embedded Signup): se escoge la cuenta de Meta Business, el nombre que verá el cliente ("Steel Works Honduras") y se verifica el número. Meta revisa el nombre; suele tardar de horas a un par de días.
4. En el sender, *Webhook URL for incoming messages*: `https://TU-URL/whatsapp` (POST).
5. **Plantilla para los avisos al dueño.** Consola > **Messaging > Content Template Builder > Create**: tipo texto, categoría **Utility**, idioma español. Texto sugerido:

   ```
   🔔 {{1}}

   {{2}}

   Respóndale al cliente desde el enlace de arriba.
   ```

   Mandar a aprobación de WhatsApp. Cuando quede aprobada copia su **Content SID** (empieza con `HX`) a `TWILIO_ALERT_CONTENT_SID`. Con plantilla, los avisos llegan aunque el dueño no le haya escrito al bot en 24 horas.
6. Cambiar las variables: `TWILIO_SANDBOX=false`, `TWILIO_WHATSAPP_FROM=+504...` (el número nuevo del bot).

## 5. Publicarlo en Render

1. Crear cuenta en [render.com](https://render.com) entrando con GitHub.
2. **New > Blueprint**, escoger este repositorio y en *Blueprint path* poner `steelworks/bot/render.yaml`.
3. Render pide los valores marcados como secretos: SID, token, números. `LEADS_TOKEN` lo genera Render solo (cópialo para el panel).
4. Al terminar, Render da la URL (por ejemplo `https://steelworks-bot.onrender.com`). Ponla en `PUBLIC_URL` (sin `/` al final) y vuelve a desplegar.
5. Abre esa URL en el navegador: debe decir "Steel Works bot activo".

El blueprint usa el plan pagado más pequeño con un disco de 1 GB para `leads.json`. El plan gratis no sirve: se duerme a los 15 minutos, tarda cerca de un minuto en despertar (Twilio espera 15 segundos y el primer mensaje del cliente se pierde) y borra los archivos al reiniciar.

Sin Render, en cualquier servidor con Docker:

```bash
docker build -t steelworks-bot .
docker run -d -p 3000:3000 --env-file .env -v $PWD/data:/data steelworks-bot
```

## 6. Poner la URL del webhook y probar

1. Sandbox o sender de WhatsApp: *When a message comes in* = `https://TU-URL/whatsapp`, POST.
2. Escribir "hola" desde un celular (si es sandbox, después del `join`).
3. Completar una cotización: al dueño le llega "Nueva cotización COT-…" con nombre, teléfono, medidas, precio estimado, cita y enlace para responderle.
4. Escribir "quiero hablar con una persona": al dueño le llega el aviso.
5. Ver las fichas: `curl -H "Authorization: Bearer TU_LEADS_TOKEN" https://TU-URL/leads`.
6. Si algo falla: Render > Logs, y en Twilio > Monitor > Logs > Errors (error 11200 = el bot no contestó; 63016 = aviso fuera de la ventana de 24 h sin plantilla).

## 7. Cambiar el número de los botones del sitio

Los botones de WhatsApp del sitio nuevo apuntan hoy al número de demo **+1 765 543 4251**. Antes de publicar el sitio hay que cambiarlo por el número de WhatsApp del bot de Steel Works en `steelworks/sitio/index.html`:

```js
const WA = "17655434251";   // -> por ejemplo "50432658800" (solo dígitos, con 504)
```

y volver a generar `dist/` con `python3 build.py`.

## Costos aproximados por mes

Precios públicos consultados en octubre de 2026, en dólares. Confirmar antes de cotizarle al cliente.

| Concepto | Precio | Ejemplo: 200 clientes al mes |
|---|---|---|
| Render, plan pagado más pequeño + disco 1 GB | ~US$7 + US$0.25 | US$7.25 |
| Twilio, por cada mensaje de WhatsApp (entra o sale) | US$0.005 | ~10 mensajes del cliente + 10 respuestas = US$0.10 por cliente → US$20 |
| Meta, respuestas dentro de las 24 h que abrió el cliente | gratis | US$0 |
| Meta, avisos al dueño con plantilla Utility | gratis si el dueño escribió en las últimas 24 h; si no, tarifa "Rest of Latin America" (por confirmar en la tabla de Meta, centavos de dólar) | US$0 a ~US$3 |
| Número | el de Steel Works no cuesta en Twilio; un número de EE. UU. de Twilio, US$1.15 | US$0 a 1.15 |
| **Total** | | **≈ US$25 a 35 al mes** |

El bot manda una sola respuesta por turno (no tres mensajes sueltos), así cada turno cuesta un mensaje.

Fuentes: [Twilio WhatsApp pricing](https://www.twilio.com/en-us/whatsapp/pricing), [Meta: precios de WhatsApp Business](https://developers.facebook.com/docs/whatsapp/pricing), [Render pricing](https://render.com/pricing), [Render free plan](https://render.com/docs/free).

## Pendiente con Steel Works

- Tarifas reales por m² y por metro de baranda (`TARIFAS` en `engine.js`), precio del motor, horario.
- Qué número usará el bot y quién recibe los avisos (dueño, sucursal Tegucigalpa, sucursal San Pedro Sula).
- Documentos para la verificación del negocio en Meta.
