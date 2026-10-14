# Coco Chicken · Propuesta de Casa Digital

*Casa Digital, una línea de Clientia Tech · Investigación del 14 de octubre de 2026 · Nada se ha enviado todavía*

![Portada](coco-chicken-portada.png)

**Video:** [coco-chicken-casa-digital.mp4](coco-chicken-casa-digital.mp4) (horizontal 1920×1080, 1 min 41 s, con "Still Buggin" y cortes en los compases, cierra con el logo de Clientia Tech)

Todo lo que digo del negocio sale de sus propias cuentas (TikTok, Facebook y PedidosYa), de las capturas y el video que mandó rodrigo. El detalle está en [redes/investigacion-redes.md](redes/investigacion-redes.md). Lo que es inferido o de ejemplo está marcado.

## 1. Quiénes son

| | |
|---|---|
| Qué venden | Pollo frito con tajadas, alitas, fingers, pollo con papas, combos y refrescos |
| Sucursales | Barrio Cabañas, Colonia Satélite y Barrio Medina (San Pedro Sula, inferido por los barrios; un TikTok agradece a "Gente de Choloma") |
| Horario | Lunes a domingo, 9:00 am a 10:00 pm (bio de TikTok) |
| Contacto | 3189-6607 (Facebook, con botón de WhatsApp) · 9291-3644 (rótulo del local) |
| Lema | "¡Mmm qué sabroso!" (en el logo) |
| TikTok @cocochiken1 | 204.9K seguidores · 3.1M me gusta. Bio: "Pagas 3 El 4 Es Gratis / En Pedidos Ya". Cuentas aparte: @CocoChickenSatelite y @cocochickenfans |
| Facebook "Coco Chicken" | 127K seguidores. Bio: "Pollos Desde 30 lps" |
| PedidosYa | 4.4 ★ con 1,097 opiniones, con entrega |
| Sitio web propio | No encontré ninguno |

**Menú y precios en PedidosYa** (nombres exactos): Pierna y tajadas L75 · Cadera y tajadas L85 · Ala y tajadas L95 · Pierna, cadera y tajadas L140. Categorías: Pollo con tajadas (media porción), Pollo con tajadas (porción completa), Alitas con papas fritas, Fingers con papas, Pollo con papas (media porcion), Combo suly calix, Pollo con papa (porciones), Refrescos.

**Videos que más funcionan:** "¿Pollos A 15 lempiras?" (871.5K vistas), uno fijado en el local con @LaYacuny (933.3K) y "Gracias Por Su Cariño Gente De Choloma" (169.5K). Los videos del día a día quedan entre 600 y 10K.

## 2. Diagnóstico

Coco Chicken ya resolvió lo más difícil: la gente los conoce. El dueño sale en sus videos, tienen botarga, ofertas que se vuelven virales y tres sucursales abiertas todos los días.

Donde se les va el valor es después del video:

1. **El pedido termina en la app de otro.** La bio de TikTok manda a PedidosYa ("Pagas 3 El 4 Es Gratis / En Pedidos Ya"). Cada pedido de ahí paga comisión, y los datos del cliente quedan en la app, no con ellos.
2. **No hay un lugar propio para pedir.** No tienen página. Quien ve el video tiene que buscar la app, buscar la sucursal o escribir a un número.
3. **Tres sucursales, varios números.** En Facebook aparece 3189-6607, en el rótulo también 9291-3644, y la sucursal Satélite tiene su propia cuenta de TikTok. El cliente no sabe a cuál escribir, y el dueño no ve en un solo lugar lo que vende cada sucursal.
4. **La promo no deja clientes propios.** "Pagas 3, el 4 es gratis" atrae, pero vive dentro de PedidosYa. Cuando termina, no les queda una lista de clientes para avisarles de la siguiente.
5. **No aparecen en Google Maps** (no encontré perfiles de las sucursales; confirmar en el celular).

## 3. La propuesta (v2, 14 oct): un panel de operación, no solo una página

**Por qué cambió:** Coco Chicken no tiene repartidores propios. Por eso depende de PedidosYa para entregar, y una página de pedidos sola no les resuelve nada. Lo que les sirve es ordenar la operación de las 3 sucursales, que el dueño no puede vigilar a la vez, y mover a "pasar a recoger" los pedidos que hoy pagan comisión sin necesidad.

**Producto principal: Panel Coco Chicken** → [coco-chicken-panel.html](coco-chicken-panel.html) (demo, un solo archivo, funciona en compu y celular; capturas en `capturas-panel/`). Es el mismo tipo de panel que hicimos para Steel Works, con login real cuando se instale.

1. **Hoy:** ventas, pedidos y pollos vendidos por sucursal en tiempo real, cuánto se va hoy en comisión a PedidosYa, y acciones recomendadas de un clic ("el pollo de Satélite se acaba como a las 9 pm → pedir al proveedor por WhatsApp", "la caja de Cabañas cerró con L300 de menos", "pedido listo hace 40 min → avisar al cliente").
2. **Pedidos para recoger (sin repartidor):** el bot de WhatsApp toma el pedido armado y lo manda a la sucursal; tablero Nuevo → En cocina → Listo → Entregado, con pantalla de cocina. Cuando está listo, el bot le avisa solo al cliente. Esto no necesita motos: el cliente pasa a traer y no se paga comisión.
3. **Cierre de caja:** cada noche el cajero cuenta desde el celular y el panel compara con lo vendido. Faltantes en rojo, historial de 7 días por sucursal. Es el control que el dueño no tiene cuando no está en el local.
4. **Pollo e insumos:** cuánto pollo queda en cada sucursal, a qué hora se acaba, y cuánto pedir para mañana (promedio de los últimos 4 días iguales + 5%), con el pedido al proveedor listo para mandar por WhatsApp. Insumos (plátano, repollo, aceite, papas) con mínimo.
5. **Ventas y comisiones:** ventas por canal (mostrador, PedidosYa, WhatsApp) y por producto, y la comisión pagada a PedidosYa con el % de su contrato (lo escriben ellos; no lo conocemos).
6. **Clientes y promos:** su promo "Pagas 3, el 4 es gratis" como tarjeta de sellos en WhatsApp; lista de clientes y envío de promos a quien no ha vuelto.
7. **¿Qué video vendió?:** cada TikTok lleva un código ("di POLLO15 al pedir"), el bot lo anota y el panel muestra cuánto vendió cada video. Las vistas son las reales de @cocochiken1; los pedidos son de ejemplo.

**¿Y el delivery?** No les vendemos repartidores. Tres caminos, en este orden:
- **PedidosYa se queda para entregas a domicilio.** Ahí está su volumen y la entrega la pone la app.
- **Pasar a recoger** es lo que movemos a su canal propio: sin comisión y sin motos. El panel muestra cuánto se ahorra con cada pedido que pasa.
- **Más adelante, si quieren entregas propias:** pedir un mensajero por app solo para pedidos propios (Uber Flash opera en Tegucigalpa y San Pedro Sula desde mayo 2025; no confirmé que lleve comida) o contratar 1 o 2 motoristas cuando el volumen de WhatsApp lo justifique. En su portada se ve un rótulo de Bip Bip (otra app de delivery); preguntarles si la usan.

La página propia de pedidos (v1) sigue como extra: sirve para el link en la bio y alimenta el mismo tablero.

## 3b. Propuesta v1 (página de pedidos), se mantiene como extra

**Idea central: convertir las vistas de TikTok en pedidos propios, sin comisión.** PedidosYa sigue, como un canal más; lo nuevo es un canal que es de ellos.

1. **Página propia de pedidos** (por ejemplo `cocochicken.hn`, no verifiqué si está libre). Va en la bio de TikTok, Facebook e Instagram. El cliente elige sucursal, ve el menú con sus nombres y precios reales, pide para recoger o a domicilio y paga con tarjeta (pasarela local, a la cuenta del restaurante) o al recibir. El menú y los precios los cambian ellos desde el celular.
2. **Bot de WhatsApp que toma el pedido.** Un solo número para todas las sucursales. El bot pregunta qué quieren y si es para recoger o a domicilio, arma el pedido con el total y lo manda a la cocina de la sucursal más cercana. Contesta a cualquier hora y pasa a una persona cuando hace falta. Se construye sobre el bot que ya hicimos para Steel Works (`casa-digital/steelworks/bot/`).
3. **Su promo, en su propio canal.** Tarjeta digital "Pagas 3, el 4 es gratis" por WhatsApp: cada compra suma un sello. Cada cliente queda en su lista, y la siguiente oferta tipo "¿Pollos a 15 lempiras?" se avisa directo, sin pagarle a nadie.
4. **Panel del dueño.** Pedidos y ventas de las tres sucursales en tiempo real, lo más vendido, clientes nuevos y alertas al celular. Se basa en el panel con login que ya hicimos para Steel Works.
5. **Google Maps.** Un perfil verificado por sucursal, con horario, fotos, menú y el link para pedir.

**Lo que no hacemos:** quitarles PedidosYa, tocar su contenido de TikTok (que ya funciona) ni inventar fotos. Usamos sus fotos y videos reales.

## 4. Números (de referencia, por validar)

- **Panel + bot de WhatsApp para recoger, 3 sucursales (v2):** propongo L32,000 de instalación (en 2 pagos) + L3,500/mes, con el login, la pantalla de cocina y el cierre de caja. Es mi estimado, sin tarifas publicadas para comparar.

- **Precio fundador**, como en la oferta de restaurantes: L19,900 de instalación (en 2 pagos) + L2,200/mes por la página de pedidos y los 3 perfiles de Google.
- **Bot de WhatsApp + tarjeta de sellos + panel:** propongo sumar L12,000 de instalación + L1,500/mes. Es mi estimado: no hay tarifas publicadas de agencias en Honduras para comparar.
- **Costos que paga el restaurante aparte:** comisión de la pasarela de pago (PixelPay, BAC o Pagadito; tarifa sin confirmar), mensajes de WhatsApp por Twilio/Meta y la IA del bot (~US$0.40 por 100 conversaciones).
- **Ejemplo de ahorro (supuestos, no datos de ellos):** si pasan 300 pedidos al mes de PedidosYa a su canal, con un pedido promedio de L140 y una comisión de 25%, se ahorran unos L10,500 al mes. La comisión real de PedidosYa en Honduras no está confirmada (en Latinoamérica ronda 20 a 30%).
- **Garantía** (como en la oferta general): 50 pedidos pagados en línea en 90 días, o seguimos trabajando gratis hasta llegar.

## 5. El video

Escenas: intro → "Ya tienen lo más difícil: la atención" con su TikTok fijado reproduciéndose y sus números → "Tres sucursales. Todos los días." con la foto de su local → "Hoy, para pedir: el video lleva a PedidosYa" con su bio y su menú de PedidosYa → "Ustedes ponen el pollo y la fama. La app cobra cada pedido." → las 4 partes de la propuesta → por qué nosotros + WhatsApp → by Clientia Tech.

El diseño de la página, la conversación del bot y las cifras del panel están marcados en pantalla como "Diseño de muestra", "Conversación de ejemplo" y "Datos de ejemplo".

## 6. Contacto (borradores, nada enviado)

El mejor canal es el WhatsApp de Facebook (3189-6607) o un mensaje directo en TikTok, porque el dueño maneja sus redes.

**Primer mensaje:**

> Hola, buenas. Mi nombre es Rodrigo Herrera. Soy hondureño y estudio ingeniería en Estados Unidos, y quiero ayudar a los negocios de mi país con lo que he aprendido. Sigo a Coco Chicken en TikTok: el video de "¿Pollos a 15 lempiras?" pasó de 870 mil vistas, y eso es algo que muy pocos negocios logran. Les preparé un video corto con una idea para que esas vistas se conviertan en pedidos propios, sin comisión: su página para pedir, un WhatsApp que toma el pedido y lo manda a la sucursal, y su promo "pagas 3, el 4 es gratis" en su propio canal. ¿Le puedo mandar el video al dueño?

**Con el video:**

> Aquí está el video para Coco Chicken. PedidosYa se queda como un canal más; lo nuevo es un canal que es de ustedes, con la lista de sus clientes y las ventas de las tres sucursales en un solo panel. Estamos tomando solo 5 restaurantes con precio de fundador. Si le interesa, se lo muestro en 15 minutos con su menú real. ¿Le queda bien esta semana?

**Seguimiento a los 3 días:**

> Hola, soy Rodrigo, de Casa Digital. Solo quería saber si pudo ver el video que le hicimos a Coco Chicken. Si prefiere, se lo explico en una llamada corta. Gracias.

Nuestro WhatsApp: **+1 (765) 543-4251**

## 7. Pendiente de confirmar

- Ciudad y dirección exacta de cada sucursal (los barrios apuntan a San Pedro Sula).
- Si los dos números (3189-6607 y 9291-3644) son de sucursales distintas.
- Si también venden por Bip Bip (en la portada se ve un rótulo con ese logo).
- Comisión real que pagan a PedidosYa y cuántos pedidos les llegan por ahí.
- Si tienen perfiles en Google Maps.
- Nombre del dueño (probablemente quien sale en los videos, inferido).
