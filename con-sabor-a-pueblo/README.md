# Con Sabor a Pueblo · paquete de Casa Digital

Comida tradicional hondureña (TikTok @consaborapueblohn, 45K seguidores, 832 videos). Venden los sábados en dos ciudades con un solo WhatsApp de pedidos, el 3169-9031. El dueño llamó a Rodrigo el 11 de noviembre de 2026 después del segundo mensaje de WhatsApp: es el primero que llama.

## Lo que sabemos, todo de su TikTok (leído el 11 nov 2026)

- **Tegucigalpa:** Col. Palmira, dos cuadras abajo del edificio rojo, frente al edificio Italia. Sábados de 10 a. m. a 4 p. m.
- **San Pedro Sula:** Bazar del Sábado, Expocentro. Sábados de 10 a. m. a 6 p. m. (en octubre decían hasta las 4).
- **Productos, como ellos los escriben:** Chanchito chuko (cerdito horneado desmechado sobre tajadas, repollo, encurtido y aderezos), Chicharrones de panceta (con tortillas y limón; se le agrega guacamole), sopa de gallina india y "pollito" en San Pedro Sula.
- **Navidad:** pierna de cerdo deshuesada para el 24 de diciembre, bajo pedido, en las dos ciudades (video del 11 nov).
- **Apartados:** ya aceptan apartados por WhatsApp. El 7 de noviembre terminaron a las 2 p. m. con las bandejas vacías.
- **Precios:** no los publican. A todos les contestan "Menu y precios 📲3169-9031". **No sabemos ningún precio.**
- **Envíos:** el dueño le dijo a Rodrigo por teléfono (11 nov) que tienen su propio delivery. En TikTok no lo aclaran y varios clientes creen que no hay. Zonas y costo: por confirmar.
- **Lo que pidió el dueño en la llamada (según Rodrigo):** que la toma de pedidos sea automática y llegue a cocina, automatizar su delivery y que se le avise al cliente.
- El video más visto (julio) tiene 985.8K vistas. De 100 comentarios leídos en ese video: 19 preguntan el precio, 15 si hacen envíos o domicilio y 12 dónde están.
- El logo dice 8982-7262, que es el número que antes daban para San Pedro Sula. Hoy publican 3169-9031 para las dos ciudades.

No mencionar: los comentarios de "cuando uno va nunca hay" o "no había nadie", ni la discusión por el nombre "chuco".

## Qué hay aquí

- `con-sabor-a-pueblo-casa-digital-vertical.mp4`: video vertical 1080×1920 de 1:56 en el estilo oscuro de antes, con el outro de Clientia Tech. Se genera en `video/` (ver su README). La pantalla de proveedores es demostración y lo dice; lo del repartidor ya funciona en el bot (los mensajes reales son texto de WhatsApp, no la pantalla del video).
- `kit/`: la propuesta por escrito (`0-carta-de-presentacion.md`), cómo sería el arranque (`1-bienvenida.md`) y la lista de lo que necesitamos (`2-lo-que-necesitamos.md`). Los PDF están en `kit/pdf/`.
- `bot/sabor-pueblo-demo.json`: su menú para el bot, con **precios de ejemplo**. Solo para las capturas; no usar con clientes sin que confirmen menú y precios.
- `redes/tiktok-datos.json`: 13 videos con su transcripción, 138 comentarios y las respuestas de la cuenta.

## Precio que eligió Rodrigo (11 nov 2026)

30 días gratis. Instalación L15,000 en dos pagos (día 30 y día 60) y L2,500 al mes desde el día 31, sin comisión. El acuerdo de servicio no va en este envío: es una plantilla que todavía no revisó un abogado y se firma antes del primer pago.

## El bot de verdad: `bot-restaurante/negocios/con-sabor-a-pueblo.json`

Con lo que el dueño mandó el 11-nov-2026 (por WhatsApp a Rodrigo):
- San Pedro Sula: solo cerdito chuko, L195.
- Apartados: tope de 50 por sábado (puesto por ciudad), hasta la 1:00 p. m. del sábado, con depósito antes de confirmarse. El dueño o la sucursal lo aprueban contestando *OK 1001* al aviso del comprobante.
- A domicilio: se le paga al repartidor al recibir (no paga antes). Costo del envío: por definir.
- Pierna de cerdo deshuesada: L320 la libra, mínimo 5 libras, para el 24 de diciembre, pedidos hasta el 15 de diciembre, apartado con el 50 %.
- Los pedidos llegan a un WhatsApp distinto por ciudad (en `NEGOCIO_PRIVADO`, no en el repositorio).

## Antes de prender el bot con ellos

1. Menú y precios de Tegucigalpa (hoy el bot de Tegus solo ofrece la pierna).
2. La cuenta para los depósitos: sin cuenta, el bot no puede pedir depósito y los apartados quedan sin cobro.
3. El WhatsApp de Tegucigalpa para los avisos y el WhatsApp personal del dueño (el 3169-9031 será el número del bot, no puede recibir sus propios avisos).
4. Si el tope de 50 es por ciudad (así está) o entre las dos.
5. Pierna: cuántas libras caben en total y dónde se entrega el 24 (el puesto es solo los sábados).
6. Repartidores: nombre, WhatsApp y ciudad de cada uno; zonas y costo del envío.
7. La prueba real del bot en WhatsApp (`bot-restaurante/PRUEBA-REAL.md`).

## Regenerar los PDF

```bash
node kit-cliente/generar.mjs --restaurante "Con Sabor a Pueblo" --instalacion "L15,000" --mensual "L2,500" \
  --fuentes con-sabor-a-pueblo/kit --solo carta-de-presentacion,bienvenida,lo-que-necesitamos --salida con-sabor-a-pueblo/kit/pdf
```
