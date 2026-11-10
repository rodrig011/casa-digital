# Alitas de la Alemán · video corto (38 s)

Video vertical 1080×1920 hecho desde cero el 10 nov 2026. Es para mandarlo en frío: dura 38 segundos en vez de 1:53.

Archivo final: `../alitas-aleman-corto.mp4`. Son competencia directa de Tito Wings: no compartir material entre los dos.

## Qué dice y de dónde sale cada dato

| En pantalla | Fuente |
|---|---|
| 274.7K vistas en un solo video | Su TikTok @alitasaleman.hn, video del 4 de octubre (leído el 10 nov 2026). |
| Las fotos | Cuadros de sus propios videos, a su tamaño original de 576 px, sin agrandar. |
| Los cuatro números | Los que ellos mismos publican para domicilio. |
| Los dos comentarios | Copiados palabra por palabra de `../redes/tiktok-datos.json`. |
| "20+ comentarios piden el número o preguntan cómo pedir" | Conteo sobre los 347 comentarios guardados: 21 distintos piden el número o preguntan cómo pedir. No se cuentan los que preguntan por PedidosYa ni las quejas. |
| 24 Alitas, L 395 | Precio que ellos dieron en un comentario. La conversación es de ejemplo y lo dice. |
| Las dos pantallas del panel | Capturas del panel real (`bot-restaurante/panel`) con pedidos de ejemplo; lo dice en pantalla. |

No aparece el precio de nuestro servicio, ninguna promesa de ventas ni quejas de calidad.

## Decisiones de diseño (guías de `.claude/skills`)

- **taste-skill**: sin rótulos encima de los titulares, sin degradados, sin emojis ni figuras de adorno; solo fotos reales y pedazos reales de interfaz.
- **impeccable**: una sola familia tipográfica (Archivo) en dos anchos, condensada pesada para titulares y normal para leer; un solo color de acento, el rojo de su logo; fondo papel claro en vez del negro con brillos.
- **emil-design-eng**: todo entra con `cubic-bezier(0.23,1,0.32,1)`, desde 0.97 de escala y 28 px, animando solo `transform` y `opacity`; los cortes caen en los compases de la canción (110 BPM).

## Cómo se genera

No usa HyperFrames. `index.html` es el video (`window.seek(t)` pone cualquier instante) y `render.mjs` saca los cuadros con Playwright y los une con ffmpeg.

```bash
cp /mnt/project-files/musica/stylish-fassounds.mp3 src/musica.mp3   # la música no va en el repo
node render.mjs --hoja     # build/hoja.jpg, un cuadro por escena para revisar
node render.mjs            # build/alitas-aleman-corto.mp4
```

Para otro restaurante: copiar la carpeta, cambiar fotos, textos y capturas del panel en `index.html`, y revisar cada dato contra sus propias redes.
