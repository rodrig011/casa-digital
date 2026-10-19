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
| `store.js` | Guarda pedidos y conversaciones en `DATA_DIR`. |
| `auth.js`, `usuarios.js` | Entrada al panel con correo y contraseña. |
| `panel/panel.html` | Panel: Hoy, Pedidos, Cocina, Por atender, Menú. |
| `test.js` | Pruebas sin Twilio ni internet: `npm test`. |

## 1. Probarlo en la computadora

Necesita Node 22 o más nuevo.

```bash
cd bot-restaurante
npm install
npm test                       # debe decir "pass 10, fail 0"
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

La confirmación del pago es a mano, en el panel. Para que se confirme sola con tarjeta hay que conectar el aviso de la pasarela que escoja el restaurante (falta hacerlo). Si en Twilio está activada la protección de archivos con clave (HTTP basic auth on media), la foto no se reenvía al dueño: el aviso llega igual sin foto.

## 5. Lo que el dueño puede hacer por WhatsApp

Desde el número de `OWNER_WHATSAPP`, escribirle al bot **pedidos**: le contesta con los pedidos y clientes pendientes.

## Lo que todavía no hace

- Envío a domicilio propio (pedir la dirección y cobrar el envío). Hoy el bot manda a PedidosYa o Bip Bip.
- Confirmar solo el pago con tarjeta: hoy alguien toca "Pago recibido" en el panel (ver la sección 4).
- Inventario y aviso automático a proveedores (está en los paneles de demostración, falta conectarlo aquí).
- Nunca se ha probado con Twilio real ni con una clave real de Claude.
