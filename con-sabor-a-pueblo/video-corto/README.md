# Con Sabor a Pueblo · video corto (43 s)

Video vertical 1080×1920 hecho el 11 nov 2026 con la misma base que `alitas-aleman/video-corto`. Archivo final: `../con-sabor-a-pueblo-corto.mp4`.

## Qué dice y de dónde sale cada dato

| En pantalla | Fuente |
|---|---|
| 985.8K vistas en un solo video | Su TikTok @consaborapueblohn, video de julio (leído el 11 nov 2026). |
| Las fotos | Cuadros de sus propios videos, a su tamaño original de 576 px, sin agrandar. |
| ¿Precio? 19, ¿Hacen envíos? 15, ¿Dónde están? 12 | Conteo nuestro sobre los 100 comentarios leídos de ese video (`../redes/tiktok-datos.json`). |
| Las tres citas | Su respuesta habitual, un comentario del 16 de octubre y la respuesta de ellos, palabra por palabra. |
| La conversación | De ejemplo y lo dice. No lleva precio porque ellos no publican ninguno; la dirección de Col. Palmira es la que dan en sus videos. |
| Las dos pantallas del panel | Capturas del panel real (`bot-restaurante/panel`) con pedidos escritos al bot usando `../bot/sabor-pueblo-demo.json`. Pedidos, nombres y precios son de ejemplo y lo dice en pantalla. |
| Las piernas del 24 | Ellos anunciaron el 11 de noviembre que van bajo pedido. Foto de ese video. |

No aparece el precio de nuestro servicio ni ninguna promesa de ventas.

## Diseño

Fondo oscuro con el amarillo de su logo como único acento, y el cierre invertido en ese amarillo. Una sola familia (Archivo) en dos anchos. Todo entra con `cubic-bezier(0.23,1,0.32,1)` animando solo `transform` y `opacity`, y los cortes caen en los compases de la canción (110 BPM).

## Cómo se genera

```bash
cp /mnt/project-files/musica/stylish-fassounds.mp3 src/musica.mp3   # la música no va en el repo
node render.mjs --hoja     # build/hoja.jpg, un cuadro por escena para revisar
node render.mjs            # build/con-sabor-a-pueblo-corto.mp4
```
