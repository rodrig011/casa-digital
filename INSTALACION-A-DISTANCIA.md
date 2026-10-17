# Cómo instalar el sistema a distancia (desde EE. UU.)

Todo el sistema vive en internet, no en el restaurante: el bot y el panel corren en **Render**, WhatsApp pasa por **Twilio** y **Meta**, y la IA es **Claude**. No hay que ir a Honduras ni instalar nada en las computadoras del cliente. Del cliente solo se necesita: su Facebook, unos documentos del negocio, leer un código que le llega por SMS y una videollamada.

## La decisión de cómo se arma

- **Cuentas a nombre de Clientia Tech** (las paga Rodrigo y van incluidas en la mensualidad): Render, Twilio (una subcuenta por cliente) y Claude. Así el cliente no tiene que poner tarjeta en servicios de EE. UU. y Rodrigo puede arreglar todo sin pedirle nada.
- **Una sola cuenta a nombre del cliente:** su Meta Business (es obligatorio, Meta verifica al negocio). El cliente agrega a Rodrigo como administrador y Rodrigo hace el resto.
- **Un servidor por cliente** en Render (su propia URL y sus propios datos). Nunca se mezclan los datos de dos clientes (por ejemplo Coco Chicken y Mag Pollo).
- **Número de WhatsApp:** usar el número que los clientes ya conocen, en modo *coexistencia* (el dueño sigue usando la app de WhatsApp Business en su celular y el bot contesta en el mismo número). Si Twilio no lo permite para ese número, se saca una línea nueva solo para el bot y se cambia en la bio de TikTok, Facebook y PedidosYa.

## Paso a paso

### 0. Antes del primer cliente (una sola vez, solo Rodrigo)

1. Probar el bot completo con el sandbox de Twilio y una clave real de Claude, de punta a punta. Hasta hoy **nunca se probó con Twilio real ni con clave real**. Guía: [steelworks/bot/README.md](steelworks/bot/README.md), pasos 1 a 6.
2. Llenar el archivo del cliente. El bot de restaurantes ya existe: [bot-restaurante/](bot-restaurante/README.md) (menú, pedidos para recoger, sucursales, panel con pantalla de cocina y aviso de "pedido listo" al cliente). Para cada cliente solo se copia `negocios/ejemplo.json` y se llena con su menú y sucursales confirmados.

### 1. Lo que se le pide al cliente por WhatsApp (día 1)

Mandarle esta lista:

- Foto del **RTN** del negocio y de un **recibo de luz o agua** con la dirección (para la verificación de Meta).
- El **menú con precios**, direcciones y horarios de cada sucursal.
- Qué número usará el bot y a quién le llegan los avisos (dueño, gerente de cada sucursal).
- Correos de las personas que entrarán al panel.

### 2. Videollamada de conexión (día 1 o 2, unos 45 minutos)

Por WhatsApp video o Zoom, con el dueño en su celular o computadora:

1. El dueño entra a [business.facebook.com](https://business.facebook.com) con su Facebook (si no tiene cuenta de negocio, la crea ahí mismo).
2. En **Configuración > Personas > Agregar**, pone el correo de Rodrigo con permiso de **administrador**. Rodrigo acepta la invitación desde EE. UU.
3. Rodrigo, en su consola de Twilio, abre **Messaging > Senders > WhatsApp senders > Create new sender**, escoge la cuenta de Meta del cliente y pone el número.
4. Al número del negocio le llega un **SMS o llamada con un código**. El dueño se lo dice a Rodrigo en la llamada. Listo, el número queda conectado.
5. Rodrigo sube el RTN y el recibo en **Meta > Centro de seguridad > Verificación del negocio**. Meta tarda de unos días a dos semanas; mientras tanto el bot ya funciona, solo con límite de mensajes iniciados por el negocio.

### 3. Rodrigo publica el servidor (mismo día, solo él)

1. En Render: **New > Blueprint**, este repositorio, el `render.yaml` del cliente (copia de `bot-restaurante/render.yaml` con su nombre y su archivo de negocio). Se llena con la subcuenta de Twilio, el número, el celular del dueño y la clave de Claude.
2. Crear la plantilla de avisos al dueño en Twilio (Content Template Builder, categoría Utility) y esperar que Meta la apruebe.
3. Dar de alta a cada persona del panel en **Render > Shell**:
   `npm run usuario -- agregar correo@negocio.hn "Nombre"`
   con una contraseña temporal, que se le manda a cada uno por WhatsApp.
4. Probar: escribirle "hola" al número del negocio desde otro celular, hacer un pedido y revisar que al dueño le llegue el aviso.

### 4. Capacitación (día 3, unos 30 minutos)

Otra videollamada: el dueño abre `https://<su-servidor>.onrender.com/panel` en su celular, entra con su correo, y Rodrigo le enseña cada sección. Si usan pantalla de cocina, basta una tablet o un celular viejo con el navegador abierto en esa misma dirección (la compra el cliente allá). Grabar la llamada y mandársela para que el personal la vea.

### 5. Primera semana

- Rodrigo revisa todos los días los registros de Render y las conversaciones del bot para corregir respuestas.
- Cualquier cambio (precios del menú, horario, una sucursal nueva) se hace desde EE. UU.: se cambia el código, se sube a GitHub y Render lo actualiza solo en un par de minutos.

## Cuánto tarda

| | Tiempo |
|---|---|
| Recibir documentos y menú | 1 a 2 días |
| Conectar número y publicar | 1 día |
| Bot funcionando con clientes reales | día 3 o 4 |
| Verificación completa de Meta | hasta 2 semanas (no detiene el arranque) |

## Lo que todavía hay que confirmar

- Que Twilio permita coexistencia con el número actual del negocio (si no, línea nueva).
- Tarifas de Meta para avisos en Honduras.
- Las llamadas por WhatsApp solo se activan después de la verificación de Meta ([steelworks/bot/LLAMADAS.md](steelworks/bot/LLAMADAS.md)).
