# ¿El asistente puede contestar llamadas? Análisis

Octubre de 2026. Precios en dólares, tomados de las páginas públicas de Twilio, OpenAI y Meta. Lo marcado *(por confirmar)* no se pudo verificar.

## Recomendación

**Sí se puede, y ya quedó listo un primer paso funcionando.** `server.js` tiene `POST /voice`: el cliente llama, el asistente le habla en español, entiende lo que dice (o lo que marca en el teclado) y recorre la misma cotización que en WhatsApp: tipo de trabajo, medidas, estilo, ciudad, precio estimado y visita o llamada. Al colgar, al dueño le llega la ficha por WhatsApp igual que con un chat. Si el cliente pide una persona, se le pasa la llamada a la sucursal (o se avisa al dueño).

Orden sugerido:

1. **Ahora: WhatsApp primero.** Ahí escribe la mayoría de los clientes en Honduras y cuesta centavos. La opción "Que me llamen" ya deja agendada la llamada en la ficha, sin pagar minutos.
2. **Paso 2 (1 o 2 días de trabajo): el bot contesta las llamadas que nadie atiende.** Un número de Twilio de EE. UU. con `/voice`, y en las líneas de las sucursales se activa el **desvío cuando no contestan o están ocupadas** y fuera de horario. El cliente sigue marcando el número de siempre; el bot solo agarra lo que hoy se pierde. Cuando Meta verifique el negocio, se activan también las **llamadas por WhatsApp** al número del bot, que llegan al mismo `/voice` y no pasan por la compañía de teléfono.
3. **Paso 3 (solo si entran muchas llamadas): voz con IA conversacional.** Twilio ConversationRelay o la API Realtime de OpenAI, para que el cliente hable libre en vez de seguir un menú. El motor `engine.js` se queda como la herramienta que calcula los precios, para que la IA no invente cifras.

## Opciones

| Opción | Cómo funciona | Costo por minuto | Calidad en español | Esfuerzo |
|---|---|---|---|---|
| **A. Twilio `<Gather input="speech">` + motor actual** (ya hecho) | Twilio lee la pregunta (voz Polly es-MX), escucha la respuesta, la manda a `/voice` y el motor decide qué sigue | ~US$0.08 (ver abajo) | Buena para respuestas cortas ("portón", "tres por dos", "Tegucigalpa"); el teclado cubre lo que no entienda | Hecho, con pruebas |
| **B. Twilio ConversationRelay + un modelo de IA** | Twilio hace voz a texto y texto a voz (Deepgram, Google, Amazon, ElevenLabs) y nos manda el texto por WebSocket; una IA conversa y usa `engine.js` para los precios | ~US$0.09 + el modelo | Muy natural; el cliente puede interrumpir | 1 a 2 semanas |
| **C. OpenAI Realtime por Twilio Media Streams** | El audio va directo al modelo de voz (gpt-realtime-2.1 o su versión mini) | ~US$0.03 a 0.11 | La más natural y rápida; voz con acento neutro | 1 a 2 semanas, más pruebas para que no invente |
| **D. Llamadas por WhatsApp** (WhatsApp Business Calling) | El cliente toca "llamar" en el chat del bot; Twilio la entrega a `/voice` como una llamada normal | Twilio cobra por minuto *(tarifa por confirmar)*; Meta no cobra las que inicia el cliente *(por confirmar)* | Igual que A, B o C | Configuración; requiere verificación de Meta |

Todas usan el mismo `/voice` o uno parecido: A y D ya funcionan con el código actual.

### El número

- **Número hondureño (+504) en Twilio:** la guía regulatoria de Twilio para Honduras solo lista números gratuitos +504 800 y la página de precios no muestra números locales *(confirmar en la consola o con Twilio si hay +504 locales, y su precio)*.
- **Número de EE. UU. de Twilio + desvío (recomendado):** US$1.15 al mes. El cliente marca el número de Steel Works y la compañía (Tigo, Claro o Hondutel) desvía la llamada al número de Twilio. **El desvío a un número internacional lo cobra la compañía por minuto**: hay que preguntarle a su operador cuánto cuesta y si se puede desviar solo "si no contesto". Ese costo puede ser mayor que todo lo de Twilio.
- **Troncal SIP con un proveedor hondureño que dé números +504** (BYOC en Twilio, US$0.004 por minuto): evita el desvío internacional, pero hay que contratar y configurar ese proveedor. Para después, si el volumen lo justifica.
- **Llamadas por WhatsApp:** no necesitan número de teléfono nuevo ni desvío; el cliente llama al mismo WhatsApp del bot.

## Costos

Una llamada típica de cotización: unos 3 minutos y unas 10 respuestas del cliente.

| Concepto | Precio público | Por llamada de 3 min |
|---|---|---|
| Número de EE. UU. de Twilio | US$1.15 al mes | — |
| Llamada entrante a número de EE. UU. | US$0.0085 por minuto | US$0.03 |
| Reconocimiento de voz de `<Gather>` | US$0.02 por cada vez que habla el cliente (US$0.025 con Deepgram o Google v2) | US$0.20 |
| Voz que lee las preguntas (Polly) | centavos *(por confirmar)* | ~US$0.01 |
| **Opción A, total** | | **≈ US$0.25** |
| ConversationRelay | US$0.07 por minuto + el modelo de IA | ≈ US$0.27 + IA |
| Media Streams (opción C) | US$0.0044 por minuto | US$0.01 |
| OpenAI gpt-realtime-2.1 (audio: US$32 entrada / US$64 salida por millón de tokens) | ≈ US$0.04 a 0.10 por minuto (estimado de terceros) | US$0.12 a 0.30 |
| OpenAI gpt-realtime-2.1 mini (US$10 / US$20 por millón) | ≈ US$0.013 a 0.03 por minuto (estimado) | US$0.04 a 0.09 |
| Desvío desde la línea hondureña | lo cobra el operador *(por confirmar)* | ? |

Ejemplo: 100 llamadas al mes con la opción A ≈ US$25 de Twilio, más el desvío del operador.

## Latencia y calidad

- **Opción A:** el cliente habla, Twilio espera la pausa (`speechTimeout="auto"`), nuestro servidor contesta en milisegundos y Twilio empieza a leer. En la práctica es un turno de 1 a 2 segundos *(estimado; medirlo en la prueba)*. Se siente como un menú bien hecho, no como una persona. El cliente puede interrumpir la pregunta respondiendo antes.
- **Opciones B y C:** respuestas de menos de un segundo y conversación libre. Cuestan más y hay que vigilar que la IA no prometa precios o fechas: por eso el precio lo sigue calculando `engine.js`.
- **Español de Honduras:** `es-MX` y `es-US` entienden bien el acento para palabras y números cortos. Fallan más con nombres propios, direcciones y medidas dichas raro ("dos cincuenta"). Por eso el bot ofrece marcar con el teclado, confirma lo que entendió y se queda con el número de teléfono de quien llama.

## Riesgos

- **Costo del desvío** internacional del operador: es el número que más puede cambiar el costo. Preguntar antes.
- **Clientes que cuelgan con un robot.** Mitigación: usarlo solo cuando nadie contesta o fuera de horario, decir desde el inicio que es el asistente y ofrecer siempre "hablar con una persona".
- **Ruido** (taller, calle, carro): bajan los aciertos. El teclado y los reintentos ("no te escuché") ayudan; a la tercera, el bot se despide y pide escribir por WhatsApp.
- **Número oculto:** si el cliente llama con número privado, la ficha queda sin teléfono.
- **Teléfono fijo:** quien llama de un fijo no recibe la confirmación por WhatsApp; el asesor tiene que devolverle la llamada.
- **Llamadas por WhatsApp:** requieren verificar el negocio en Meta y un límite de mensajes alto (2,000 conversaciones al día). El soporte de `<Gather>` en esas llamadas está *por confirmar* en una prueba real.
- **Grabaciones:** el bot no graba. Si después se quiere grabar, hay que avisarle al cliente al inicio.

## Cómo activarlo (opción A)

1. En Twilio, comprar un número de EE. UU. con voz (Phone Numbers > Buy a number).
2. En el número, *A call comes in*: Webhook `https://TU-URL/voice`, POST.
3. Variables (ver `.env.example`): `VOICE_TRANSFER_TGU` y `VOICE_TRANSFER_SPS` con el teléfono de cada sucursal para pasar la llamada cuando piden una persona. `VOICE_LANG=es-MX` y `VOICE_TTS=Polly.Mia` vienen por defecto.
4. Llamar al número y hacer una cotización completa: al dueño le llega "Nueva cotización … · llamada".
5. Pedirle al operador el desvío "si no contesto / ocupado" de las líneas de las sucursales hacia ese número (después de confirmar el costo).

Lo que hace `/voice` hoy: en llamada no ofrece "Piezas para herrería", que necesitan foto. Si alguien pide piezas, se deja una ficha para escribirle por WhatsApp. Al terminar la cotización lee el resumen y el número de cotización, avisa al dueño y cuelga. Lo prueba `npm test` (llamada completa y transferencia a una persona).

## Siguientes pasos

1. Preguntarle a Steel Works cuántas llamadas reciben al día y cuántas se pierden (no contestadas o fuera de horario).
2. Preguntar a su operador el costo del desvío a un número internacional.
3. Hacer 10 llamadas de prueba con personas de Tegucigalpa y San Pedro Sula, y medir aciertos y tiempo por turno.
4. Si hay volumen y el menú se siente rígido, hacer el piloto de la opción B o C con `engine.js` como herramienta de precios.

Fuentes: [Twilio Voice, precios EE. UU.](https://www.twilio.com/en-us/voice/pricing/us), [Twilio Voice, precios Honduras](https://www.twilio.com/en-us/voice/pricing/hn), [Twilio, guía regulatoria Honduras](https://www.twilio.com/en-us/guidelines/hn/regulatory), [TwiML `<Gather>`](https://www.twilio.com/docs/voice/twiml/gather), [ConversationRelay](https://www.twilio.com/docs/voice/conversationrelay), [WhatsApp Business Calling en Twilio](https://www.twilio.com/docs/voice/whatsapp-business-calling), [Twilio WhatsApp pricing](https://www.twilio.com/en-us/whatsapp/pricing), [OpenAI API pricing](https://openai.com/api/pricing/), [Estimado por minuto de OpenAI Realtime (aireiter.com)](https://aireiter.com/blog/openai-realtime-api-pricing).
