# Bot de WhatsApp para restaurantes · instalación

Un solo código sirve para todos los restaurantes. Lo que cambia por cliente es un archivo: `negocios/<cliente>.json` (menú, precios, sucursales, horario, apps de domicilio).

Qué hace el bot por WhatsApp, a cualquier hora:

- muestra el menú con precios,
- toma pedidos para recoger (productos, sucursal, hora, nombre) y da el total,
- da direcciones, teléfonos y horario de cada sucursal,
- explica cómo pedir a domicilio (PedidosYa, Bip Bip) si el restaurante no tiene repartidores,
- pasa a una persona cuando el cliente lo pide.

Cada pedido le llega por WhatsApp al dueño y a la sucursal, aparece en el **panel** y en la **pantalla de cocina**. Cuando la cocina toca **Listo**, al cliente le llega "su pedido está listo". Con la clave de Claude, el bot entiende mensajes escritos con sus palabras; sin clave funciona con el menú de opciones.

Para instalarle a un cliente desde EE. UU., ver también [INSTALACION-A-DISTANCIA.md](../INSTALACION-A-DISTANCIA.md).

## Archivos

| Archivo | Qué hace |
|---|---|
| `negocios/ejemplo.json` | Datos de ejemplo. Se copia uno por cliente. |
| `negocio.js` | Lee y revisa el archivo del cliente; busca productos por número o por nombre. |
| `engine.js` | La conversación con menú de opciones. |
| `ia.js` | Modo IA opcional con Claude (precios siempre del archivo del cliente). |
| `server.js` | Webhook de WhatsApp, API de pedidos y panel. |
| `avisos.js` | Avisos al dueño y a la sucursal; "pedido listo" al cliente. |
| `pagos.js` | Pago con tarjeta por pasarela (Tilopay): link por pedido y consulta del pago. |
| `store.js` | Guarda pedidos y conversaciones en `DATA_DIR`. Los pedidos cerrados con más de 30 días pasan a `archivo/pedidos-AAAA-MM.json` para que `pedidos.json` no crezca para siempre. |
| `auth.js`, `usuarios.js` | Entrada al panel con correo y contraseña. |
| `seguridad.js` | Cabeceras de seguridad, https forzado y freno de mensajes por número (ver `SEGURIDAD.md` en la raíz). |
| `panel/panel.html` | Panel: Hoy, Pedidos, Cocina, Por atender, Menú. |
| `test.js` | Pruebas sin Twilio ni internet: `npm test`. |

## 1. Probarlo en la computadora

Necesita Node 22 o más nuevo.

```bash
cd bot-restaurante
npm install
npm test                       # debe decir "pass 12, fail 0"
cp .env.example .env           # poner SKIP_TWILIO_SIGNATURE=true y un PANEL_SECRET
npm run usuario -- agregar yo@correo.com "Rodrigo"
npm start
```

Hablarle sin Twilio:

```bash
curl -X POST localhost:3000/whatsapp -d "From=whatsapp:+50499999999" -d "Body=hola"
```

y abrir `http://localhost:3000/panel`.

## 2. Llenar el archivo del cliente

1. Copiar `negocios/ejemplo.json` a `negocios/<cliente>.json`.
2. Llenar **solo con lo que el cliente confirmó**: nombre exacto de cada producto como en su menú, precio en lempiras, sucursales con dirección y teléfono. Un horario que no confirmó se deja `""` y el bot dice que una persona lo confirma.
   Para un negocio de Guatemala o El Salvador, agregar `"moneda": "GTQ"` (quetzales, Q45) o `"moneda": "USD"` (dólares, $3.50). Sin `moneda` el bot cobra en lempiras. El bot también dice el país correcto al hablar con la IA.
3. `whatsapp` en cada sucursal es opcional: si la sucursal tiene su propio WhatsApp, recibe sus pedidos además del dueño.
4. `npm test` revisa que todos los archivos de `negocios/` estén bien escritos.
5. Para cambiar un precio después: editar el archivo, subirlo a GitHub y Render lo actualiza solo.

## 3. Publicarlo (Render) y conectar WhatsApp (Twilio)

Igual que el bot de Steel Works: ver [steelworks/bot/README.md](../steelworks/bot/README.md), pasos 2 a 6. Lo distinto:

- **Blueprint path:** `bot-restaurante/render.yaml`. Para cada cliente, copie el archivo (`render-<cliente>.yaml`), cambie `name` y `NEGOCIO=negocios/<cliente>.json`. Un servidor por cliente: los datos nunca se mezclan.
- **Webhook de Twilio:** `https://<su-servidor>.onrender.com/whatsapp` (POST).
- **Plantilla de avisos al dueño:** igual que en Steel Works (categoría Utility, variables `{{1}}` y `{{2}}`).
- **El aviso "su pedido está listo"** va como texto normal: el cliente acaba de escribir, así que está dentro de las 24 horas de WhatsApp.
- **Usuarios del panel:** en Render > Shell, `npm run usuario -- agregar correo "Nombre"`.

## 4. Cobrar antes de cocinar (pedidos que nunca llegan)

Si alguien pide para recoger y nunca llega, el pollo se pierde. Para eso está el bloque `cobro` en `negocios/<cliente>.json`:

```json
"cobro": { "desde": 500, "faltas": 1, "transferencia": "Banco …, cuenta de ahorro …, a nombre de …", "tarjeta": "" }
```

- **desde**: pedidos de ese total o más se pagan antes. Vacío = ninguno por monto; 0 = todos.
- **faltas**: cuando la cocina toca **No vino** en el panel, ese número suma una falta. Con esa cantidad de faltas, sus próximos pedidos se pagan antes (y al dueño le sale el aviso "no vino a recoger 1 vez").
- **transferencia**: los datos de la cuenta, tal cual los da el dueño.
- **tarjeta**: el enlace de pago de una pasarela a nombre del restaurante (PixelPay, Tilopay; Stripe no acepta negocios de Honduras). `{n}` y `{total}` se cambian por el número de pedido y el total.

Sin transferencia ni tarjeta el cobro está apagado y todo funciona como antes.

Cómo va un pedido que se paga antes:

1. El bot da el total con los datos de pago y pide la foto del comprobante. El pedido queda **Por pagar**: sale en el panel, no en cocina.
2. El cliente manda la foto: al dueño y a la sucursal les llega con la foto (si la sucursal tiene WhatsApp propio).
3. Alguien revisa que el dinero esté en la cuenta y toca **Pago recibido**. El pedido pasa a cocina y al cliente le llega "recibimos su pago".
4. El cliente puede tocar **Cancelar pedido** mientras no haya pagado.

Con transferencia, la confirmación es a mano en el panel.

**Tarjeta con confirmación automática (Tilopay).** Con `PAGOS_PASARELA=tilopay` y las claves del restaurante en Render (`TILOPAY_API_USER`, `TILOPAY_API_PASSWORD`, `TILOPAY_KEY`, ver `.env.example`):

1. Cada pedido que se paga antes recibe su propio link de un solo uso, por el total exacto, con el número de pedido como referencia.
2. El cliente paga. Tilopay avisa al bot (`/pagos/aviso/<pedido>`) y el cliente vuelve a una página "Pago recibido".
3. El bot no confía en el aviso solo: le pregunta a Tilopay si ese link tiene un pago aprobado por el total. Si sí, el pedido pasa a cocina, al cliente le llega "recibimos su pago" y a la sucursal el pedido con "Pagado con tarjeta".
4. Si el pago fue rechazado, al cliente le llega que no pasó y que puede intentar otra vez.
5. Tilopay manda el aviso una sola vez, así que cada 2 minutos el bot revisa los pedidos con link de las últimas 3 horas.

Pendiente antes del primer cliente real: confirmar con Tilopay que da servicio en Honduras y en lempiras, y hacer un pago de prueba para revisar los campos del pago (el bot acepta `code: "1"` o un estado "aprobado"; Tilopay no publica ese formato). Sin pasarela, `tarjeta` en el archivo del negocio sigue sirviendo para un link fijo, confirmado a mano. Si en Twilio está activada la protección de archivos con clave (HTTP basic auth on media), la foto no se reenvía al dueño: el aviso llega igual sin foto.

## 5. Lo que el dueño puede hacer por WhatsApp

Desde el número de `OWNER_WHATSAPP`, escribirle al bot **pedidos**: le contesta con los pedidos y clientes pendientes.

## Lo que todavía no hace

- Envío a domicilio propio (pedir la dirección y cobrar el envío). Hoy el bot manda a PedidosYa o Bip Bip.
- Pago con tarjeta: el código para Tilopay está hecho pero nunca se probó con una cuenta real (ver la sección 4). PixelPay todavía no está conectado.
- Inventario y aviso automático a proveedores (está en los paneles de demostración, falta conectarlo aquí).
- Nunca se ha probado con Twilio real ni con una clave real de Claude.
