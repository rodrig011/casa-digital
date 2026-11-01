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
| `meta.js` | WhatsApp directo con Meta (Cloud API): botones, listas, plantillas y fotos de comprobantes. |
| `avisos.js` | Avisos al dueño y a la sucursal; "pedido listo" al cliente. |
| `pagos.js` | Pago con tarjeta por pasarela (Tilopay): link por pedido y consulta del pago. |
| `cifrado.js` | Cifra en el disco (AES-256-GCM, llave `DATA_KEY`) pedidos, conversaciones, usuarios y bitácora. |
| `bitacora.js` | Anota cada entrada al panel, intento fallido, bloqueo y cambio de pedido; el dueño la ve en Seguridad. |
| `store.js` | Guarda pedidos y conversaciones en `DATA_DIR`. Los pedidos cerrados con más de 30 días pasan a `archivo/pedidos-AAAA-MM.json` para que `pedidos.json` no crezca para siempre. |
| `auth.js`, `usuarios.js` | Entrada al panel con correo, contraseña y código por WhatsApp. |
| `seguridad.js` | Cabeceras de seguridad, https forzado y freno de mensajes por número (ver `SEGURIDAD.md` en la raíz). |
| `panel/panel.html` | Panel: Hoy, Pedidos, Cocina, Por atender, Menú, Seguridad (y Cupos o Reservaciones si el negocio los usa). |
| `test.js` | Pruebas sin Twilio ni internet: `npm test`. |

## 1. Probarlo en la computadora

Necesita Node 22 o más nuevo.

```bash
cd bot-restaurante
npm install
npm test                       # debe decir "fail 0"
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

## 3. Publicarlo (Render) y conectar WhatsApp directo con Meta

El bot habla con la API de WhatsApp de Meta (Cloud API, `meta.js`), sin Twilio: contestarle a un cliente que escribió primero no cuesta nada. Los menús salen con botones y listas de WhatsApp de verdad. Con `META_TOKEN` y `META_PHONE_ID` el bot usa Meta; sin ellos, Twilio (más abajo).

1. **Render:** New > Blueprint, `bot-restaurante/render.yaml` (copia por cliente, ver abajo). Anotar la URL (`https://<servidor>.onrender.com`).
2. **App de Meta:** en [developers.facebook.com](https://developers.facebook.com) > Mis apps > Crear app > tipo Negocio, ligada al Meta Business del cliente (donde Rodrigo es administrador). Agregar el producto **WhatsApp**.
3. **Número:** WhatsApp > Configuración de la API > Agregar número de teléfono, y el código que llega por SMS. Copiar el **identificador del número de teléfono** a `META_PHONE_ID` y el número a `META_NUMERO`. Para probar antes, Meta da un número de prueba gratis en esa misma pantalla.
4. **Token que no vence:** Configuración del negocio > Usuarios del sistema > Agregar (administrador) > Asignar activos: la app y la cuenta de WhatsApp con control total > Generar token con los permisos `whatsapp_business_messaging` y `whatsapp_business_management`. Va en `META_TOKEN`.
5. **Secreto de la app:** Configuración de la app > Básica > Clave secreta de la app, en `META_APP_SECRET`. Sin esto el bot rechaza todo (así nadie más puede hacerse pasar por Meta).
6. **Webhook:** WhatsApp > Configuración > Webhook: URL `https://<servidor>.onrender.com/meta`, token de verificación = el mismo texto que `META_VERIFY_TOKEN`. Después, en Campos del webhook, suscribirse a **messages**.
7. **Plantilla de avisos:** en el WhatsApp Manager > Plantillas de mensajes > Crear, categoría **Utilidad**, nombre `aviso_pedido`, idioma español, cuerpo: `Aviso de su negocio: {{1}}. Detalle: {{2}}`. Cuando Meta la apruebe, poner el nombre en `META_PLANTILLA`. Con ella le llegan al dueño los pedidos aunque no le haya escrito al bot en 24 horas, y al cliente el "su pedido está listo" de un pedido hecho el día anterior. Esas plantillas sí las cobra Meta (centavos), con la tarjeta que se pone en el WhatsApp Manager.
8. **Probar:** escribirle "hola" al número desde otro celular, hacer un pedido y revisar que al dueño le llegue el aviso. En Render > Logs, `[meta]` dice si algo falló.

Lo demás de Render:

- **Blueprint path:** `bot-restaurante/render.yaml`. Para cada cliente, copie el archivo (`render-<cliente>.yaml`), cambie `name` y `NEGOCIO=negocios/<cliente>.json`. Un servidor por cliente: los datos nunca se mezclan.
- **Con Twilio (respaldo):** igual que el bot de Steel Works ([steelworks/bot/README.md](../steelworks/bot/README.md), pasos 2 a 6), webhook `https://<su-servidor>.onrender.com/whatsapp` (POST) y plantilla de avisos en Twilio. Twilio cobra unos $0.005 por mensaje encima de Meta.
- **Usuarios del panel:** en Render > Shell, `npm run usuario -- agregar correo "Nombre" 504XXXXXXXX`. Con el número de WhatsApp, al entrar le llega un código (ver "Seguridad del panel" abajo).

### Seguridad del panel

- **Datos cifrados:** con `DATA_KEY` (Render la genera) los pedidos, nombres, teléfonos, direcciones, conversaciones, usuarios y bitácora se guardan cifrados con AES-256-GCM. Quien copie el disco no puede leer nada, y si alguien cambia un archivo el servidor lo nota y no arranca. En Render el servidor no arranca sin la llave. **Copie `DATA_KEY` al gestor de contraseñas el día que se crea**: si se pierde, los datos no se pueden abrir. No la cambie después de arrancar.
- **Dos pasos:** contraseña de 10 caracteres o más, y después un código de 6 números al WhatsApp de la persona, que vence en 5 minutos. Cinco códigos malos cortan el intento y bloquean esa conexión 15 minutos. "Recordar este teléfono" evita el código en ese teléfono por 30 días; cambiar la contraseña lo borra.
- **Plantilla del código (Meta):** Meta pide que los códigos salgan con una plantilla de categoría **Autenticación**. En WhatsApp Manager > Plantillas: nueva, categoría Autenticación, nombre `codigo_panel`, idioma español, botón "Copiar código". Cuando la aprueben, póngala en `META_PLANTILLA_CODIGO`. Mientras tanto el código sale como aviso normal (llega si la persona escribió al número en las últimas 24 h, o con `META_PLANTILLA`).
- **Bitácora:** el panel tiene la vista Seguridad (en el celular, tocando las iniciales): cómo está protegido, quién tiene acceso y las últimas entradas, intentos fallidos y cambios de pedido, con hora y equipo.
- **Ya estaba:** https forzado, cabeceras de seguridad, sesión de 12 horas en cookie firmada, "Salir" la anula en el servidor, contraseñas con hash scrypt, 5 contraseñas malas bloquean 15 minutos. Lista completa en [SEGURIDAD.md](../SEGURIDAD.md).

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

## 5. Venta por cupos y tandas (Gambos)

Para negocios que venden por adelantado y cocinan por tandas. En `negocios/<cliente>.json`:

- Cada producto lleva `"cupos"`: cuántas personas son (Combo individual 1, Duo de Mar 2...). Los adicionales van en 0 y no se venden solos.
- `"cupos": { "dias": [...], "tandas": [...], "porTanda": 12, "anticipacion": 1, "cierre": "21:00", "verDias": 7, "salsas": [...] }`.
  `anticipacion: 1` y `cierre: "21:00"` = cada día se puede pedir hasta las 9 de la noche del día anterior (hora de Honduras).

Lo que hace el bot: arma el pedido, pregunta la salsa de cada combo, si lo recoge o se lo llevan, el día (solo los que siguen abiertos) y la tanda (solo las que tienen cupo, con cuántos quedan). Antes de cerrar vuelve a revisar el cupo, por si otro cliente lo tomó mientras tanto. Si no cabe, ofrece otro día o la lista de espera: el pedido queda "Lista de espera" sin cupo y sin cobro. Los cupos se cuentan de los pedidos guardados (todos menos cancelados y lista de espera), así que un pedido cancelado libera sus cupos y al dueño le llega quién está en espera para escribirle. En el panel, **Cupos** muestra cada día con sus tandas y la lista de espera; Cocina solo muestra los pedidos de hoy, en orden de tanda. El modo IA hace lo mismo con la herramienta `ver_cupos`.

## 6. Lo que el dueño puede hacer por WhatsApp

Desde el número de `OWNER_WHATSAPP`, escribirle al bot **pedidos**: le contesta con los pedidos y clientes pendientes.

## 7. Cancelaciones y mensajes repetidos

- El bot **nunca cancela solo** un pedido que ya entró a cocina. Si el cliente escribe "cancelar mi pedido", le avisa a la sucursal de su último pedido ("Quiere cancelar el pedido PED-…") y le dice al cliente que una persona le confirma. Un pedido que todavía espera el pago sí se cancela con el botón **Cancelar pedido**.
- Cuando la sucursal cancela un pedido desde el panel, al cliente le llega un WhatsApp: "*Sucursal* canceló su pedido PED-…". Una sola vez.
- Los mensajes de un mismo cliente se contestan en orden, uno detrás del otro (dos mensajes seguidos ya no se pisan).
- Si el cliente confirma dos veces el mismo pedido en menos de 30 minutos, no se crea otro: se le repite el mismo número.

## 8. Respaldo de los datos

Antes de instalar con un cliente, y después **una vez al día**, baje un respaldo y guárdelo fuera de Render (por ejemplo en su computadora o en Google Drive):

```bash
LEADS_TOKEN=... DATA_KEY=... node respaldo.js bajar https://su-bot.onrender.com     # baja y comprueba que abre
DATA_KEY=... node respaldo.js comprobar respaldo-2026-11-01.json                   # dice cuántos pedidos y usuarios trae
DATA_KEY=... node respaldo.js restaurar respaldo-2026-11-01.json ./datos-nuevos     # solo en una carpeta vacía
```

El respaldo va cifrado con `DATA_KEY`: sin la llave no se puede leer ni restaurar. Guarde la llave en el gestor de contraseñas, nunca en la misma carpeta que los respaldos. Para restaurar en Render: restaure en una carpeta nueva del disco, apunte `DATA_DIR` a esa carpeta y reinicie.

## Lo que todavía no hace

- Envío a domicilio propio (pedir la dirección y cobrar el envío). Hoy el bot manda a PedidosYa o Bip Bip.
- Pago con tarjeta: el código para Tilopay está hecho pero nunca se probó con una cuenta real (ver la sección 4). PixelPay todavía no está conectado.
- Inventario y aviso automático a proveedores (está en los paneles de demostración, falta conectarlo aquí).
- Nunca se ha probado con WhatsApp real (Meta o Twilio) ni con una clave real de Claude. Las pruebas de `npm test` simulan los dos. La prueba real se hace con el número de prueba de Meta, nunca con el número de un negocio.
- El respaldo diario no es automático todavía: hay que correr `respaldo.js bajar` (o programarlo en una computadora).
