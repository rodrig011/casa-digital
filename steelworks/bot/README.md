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
| `auth.js`, `usuarios.js` | Acceso al panel del dueño con correo y contraseña (ver *Panel del dueño*). |
| `seguridad.js` | Cabeceras de seguridad, https forzado y freno de mensajes por número (ver `SEGURIDAD.md` en la raíz). |
| `panel/` | El panel que se abre en `/panel` después de entrar (lo genera `python3 ../build.py`). |
| `ia.js` | Modo IA opcional con Claude: entiende mensajes libres por WhatsApp (ver *Modo IA*). |
| `test.js` | Pruebas sin Twilio: `npm test`. |
| `.env.example` | Todas las variables, explicadas. |
| `render.yaml`, `Dockerfile` | Para publicarlo en Render o en cualquier servidor con Docker. |

## 1. Probarlo en tu computadora (5 minutos)

Necesitas Node 22 o más nuevo.

```bash
cd steelworks/bot
npm install
npm test                      # simula conversaciones completas; debe decir "pass 9, fail 0"
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
| Modo IA con Claude (opcional, ver *Modo IA*) | ≈ US$0.004 por conversación | ~US$1 |
| **Total** | | **≈ US$25 a 35 al mes** |

El bot manda una sola respuesta por turno (no tres mensajes sueltos), así cada turno cuesta un mensaje.

Fuentes: [Twilio WhatsApp pricing](https://www.twilio.com/en-us/whatsapp/pricing), [Meta: precios de WhatsApp Business](https://developers.facebook.com/docs/whatsapp/pricing), [Render pricing](https://render.com/pricing), [Render free plan](https://render.com/docs/free).

## Modo IA (Claude)

Opcional. Con el modo IA el bot entiende mensajes escritos con las palabras del cliente, por ejemplo *«quiero un portón para mi casa de unos 3 metros, cuánto sale?»*, en vez de solo el menú de botones. Contesta de usted, en mensajes cortos, y:

- da precios **solo** con las tarifas de `engine.js` (las mismas del menú), siempre como *precio estimado* y aclarando que el exacto se da al medir;
- busca piezas del catálogo por nombre y categoría, da direcciones y teléfonos de las sucursales;
- agenda la visita para medir: la ficha se guarda en `leads.json` y le llega al dueño igual que con el menú;
- si el cliente pide una persona o algo que el bot no puede hacer, avisa al dueño ("pidió hablar con una persona").
- No inventa horarios (dice que una persona los confirma), no promete enlaces de pago ni descuentos.

Solo aplica a WhatsApp; las llamadas siguen con el menú de voz. **Si la API de Claude falla o tarda más de 11 segundos, ese mensaje lo contesta el menú de siempre** (queda anotado en los logs como `[ia] error`). Sin clave el bot sigue funcionando con el menú, como hasta ahora.

### Cómo activarlo

1. Crear una cuenta en [console.anthropic.com](https://console.anthropic.com) con el correo de Steel Works y cargar saldo en **Billing** (con US$5 alcanza para miles de conversaciones). Conviene poner un límite de gasto mensual en **Limits**.
2. En **API Keys > Create Key**, ponerle de nombre "bot WhatsApp" y copiar la clave (empieza con `sk-ant-`; solo se muestra una vez).
3. Pegarla en **Render > steelworks-bot > Environment** en `ANTHROPIC_API_KEY` y guardar (Render vuelve a desplegar solo). Para probar en la computadora va en `.env`. **Nunca la mande por chat, correo ni la suba al repositorio**: quien la tenga puede gastar el saldo. Si se filtra, se borra en API Keys y se crea otra.
4. En los logs de Render debe salir `Modo IA activo (claude-haiku-5-5)`.

Para apagarlo sin borrar la clave: `BOT_IA=off`. Para cambiar de modelo: `ANTHROPIC_MODEL` (por defecto `claude-haiku-5-5`, el más barato de Claude).

### Cuánto cuesta

Precios de Claude Haiku 5.5 (octubre de 2026, confirmar en [anthropic.com/pricing](https://www.anthropic.com/pricing)): US$0.10 por millón de tokens de entrada y US$0.50 por millón de salida; lo que se repite en cada mensaje (instrucciones y herramientas) se guarda en caché y cuesta la décima parte. Un token es más o menos media palabra.

Supuesto: una conversación de unos 8 mensajes del cliente, que son unas 12 llamadas a Claude (algunas usan herramientas).

| Parte | Tokens | Costo |
|---|---|---|
| Instrucciones y herramientas, en caché | ~2,000 × 12 = 24,000 (a US$0.01 por millón) + escribir la caché una vez (~2,000 a US$0.125) | US$0.0005 |
| Conversación (lo que va diciendo el cliente y el bot) | ~1,500 × 12 = 18,000 (a US$0.10 por millón) | US$0.0018 |
| Respuestas del bot | ~300 × 12 = 3,600 (a US$0.50 por millón) | US$0.0018 |
| **Por conversación** | | **≈ US$0.004** |

**Unas 100 conversaciones cuestan cerca de US$0.40** (menos de US$1 aunque las conversaciones salgan el doble de largas). Para comparar, Twilio cobra unos US$10 por esas mismas 100 conversaciones. El gasto real se ve en console.anthropic.com > **Usage**.

## Panel del dueño (correo y contraseña)

El panel vive en el mismo servidor del bot: `https://<su-servicio>.onrender.com/panel`. Para verlo hay que entrar con correo y contraseña, y solo entran las personas que usted autorice.

1. **PANEL_SECRET.** El Blueprint lo crea solo. Si lo cambia, se cierran todas las sesiones abiertas.
2. **Dar acceso a alguien.** En Render, abra el servicio, vaya a **Shell** y escriba:
   ```
   npm run usuario -- agregar correo@steelworks.hn "Nombre Apellido"
   ```
   Le pide la contraseña dos veces sin mostrarla. Debe tener al menos 10 caracteres. La persona queda guardada en el disco, en `usuarios.json`, y ya puede entrar.
3. **Quitar acceso.** Escriba `npm run usuario -- quitar correo@steelworks.hn`. Su sesión deja de valer en ese momento. Para ver quién tiene acceso, escriba `npm run usuario -- lista`.
4. **Sin consola.** En su computadora, escriba `npm run usuario -- linea correo "Nombre"`. Eso imprime una línea; péguela en **Environment > PANEL_USUARIOS**, una persona por línea.

Para cambiar una contraseña, vuelva a usar `agregar` con el mismo correo.

**Cómo protege el panel:**
- Las contraseñas no se guardan, solo una huella (scrypt).
- La sesión dura 12 horas. Va en una cookie firmada que el navegador no deja leer a otras páginas (HttpOnly, SameSite=Strict, Secure).
- "Salir" también cierra la sesión en el servidor: si alguien copió la cookie, deja de servirle.
- Después de 5 intentos fallidos, ese correo o esa conexión quedan bloqueados 15 minutos.
- Si falta PANEL_SECRET, el panel no abre.

El archivo `steelworks-panel.html` que se manda para mostrar es solo una demostración. Trae su propia pantalla de entrada (demo@steelworks.hn / hierro2026) y no protege nada.

## Pendiente con Steel Works

- Tarifas reales por m² y por metro de baranda (`TARIFAS` en `engine.js`), precio del motor, horario.
- Qué número usará el bot y quién recibe los avisos (dueño, sucursal Tegucigalpa, sucursal San Pedro Sula).
- Documentos para la verificación del negocio en Meta.
