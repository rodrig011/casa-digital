# Loca Luna · video de propuesta v4 (54 s)

Cuarta versión, del 15 nov 2026. Rodrigo vio la v3 y dijo que no tenía la calidad de animación del video de referencia (`/mnt/project-files/propuestas/referencia-estilo-lanzamiento-app.mp4`). El mensaje y los datos son los de la v3; lo que cambió es el movimiento. Las versiones anteriores siguen en `../video/`, `../video-v2/` y `../video-v3/`.

Archivo final: `../loca-luna-casa-digital-v4.mp4`. Son competencia de Tito Wings y Alitas de la Alemán: no compartir material entre ellos.

## Qué hace distinto el movimiento

Se revisó la referencia a 10 cuadros por segundo. Lo que la hace verse profesional no es el aspecto sino esto, y es lo que se copió:

- **Desenfoque de movimiento real.** Cada cuadro del video es la mezcla de 6 sub-cuadros sacados a 240 por segundo, como el obturador de una cámara. Todo lo que se mueve rápido deja estela.
- **La cámara nunca se detiene.** Entre escenas no hay fundidos: la cámara barre de lado o hacia arriba, atraviesa un botón o desenfoca. Dentro de cada escena siempre hay un acercamiento lento.
- **La frase en grande.** La cámara se mete en "llegara solo", la recorre a pantalla completa y vuelve a salir.
- **Inundación de color.** El amarillo llena la pantalla, un punto negro crece y se la traga, y de ahí sale la marca.
- **Tarjetas en 3D con rebote.** Llegan giradas, se asientan con un resorte corto y siguen girando despacio.
- **Manchas vivas.** Las manchas del fondo cambian de forma y se desplazan con cada barrido de cámara.
- **Ritmo.** 54 s en vez de 69 s; los cortes y los clics caen en los golpes de la canción (120 BPM).

## De dónde sale cada dato

Igual que la v3 (ver `../video-v3/README.md` y `../video/README.md`): logo, tres sucursales, L 320 y nombres de productos salen de sus redes y de su menú. La conversación y los pedidos son de ejemplo y lo dicen en pantalla. La tarjeta de cocina, el panel y la tabla "Por sucursal" son capturas del panel real (`capturas.mjs`). El aviso al cliente es el texto que manda el bot (`bot-restaurante/avisos.js`), sin el emoji ni el total.

No aparece el precio de nuestro servicio, ninguna promesa de ventas, conteos de comentarios ni quejas.

## Cómo se genera

```bash
cp /mnt/project-files/musica/better-times-are-coming-mixkit.mp3 src/musica.mp3   # la música no va en el repo
node capturas.mjs              # solo si cambia el panel
node render.mjs --hoja         # build/hoja.jpg, cuadros sueltos para revisar
A=10 B=16 node render.mjs      # build/tramo.mp4, solo ese tramo
node render.mjs                # build/loca-luna-casa-digital-v4.mp4 (unos 11 minutos: son 12,900 capturas)
```

Todo el movimiento se calcula por cuadro en `index.html` a partir del tiempo (`window.seek(t)`), sin animaciones CSS, para que los sub-cuadros sean exactos.
