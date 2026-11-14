# Loca Luna · video de propuesta v2 (74 s)

Segunda versión, del 14 nov 2026, hecha con lo que pidió Rodrigo: más profesional, otra canción, el panel visto en pantalla grande (al estilo de un sistema de restaurantes como Toast) y una parte "de hondureños, para hondureños". La v1 sigue en `../video/` y `../loca-luna-casa-digital-vertical.mp4`.

Archivo final: `../loca-luna-casa-digital-v2.mp4`. Son competencia de Tito Wings y Alitas de la Alemán: no compartir material entre ellos.

## Qué cambió frente a la v1

- **Panel:** en vez de la vista de celular, se ve el panel real en tamaño tablet (barra oscura a la izquierda, botones naranja, tablero de pedidos por columnas) y la cámara se acerca a los pedidos de Las Hadas, a los números del día, a la tabla "Por sucursal" y al tablero. No es un diseño aparte: es `bot-restaurante/panel/panel.html` tal como está.
- **Canción:** "Better Times are Coming" de Mixkit (`https://mixkit.co/free-stock-music/`, archivo 173), 120 BPM exactos, un corte cada 2 s. Licencia gratuita de música de Mixkit; conviene que Rodrigo la lea una vez en https://mixkit.co/license/ antes de usar el video en anuncios pagados.
- **De hondureños, para hondureños:** escena nueva con la bandera dibujada, los nombres de los dos fundadores, precios en lempiras y atención en español en horario de Honduras.
- **Tono:** fondos negro y hueso, el amarillo de su logo solo como acento y en el cierre; titulares un poco menos pesados.

## De dónde sale cada dato

Igual que la v1 (ver `../video/README.md`): logo, tres sucursales, delivery de 10 am a 10 pm, 11 salsas y L 320 salen de sus redes y de su menú. Conversación, pedidos y cifras del panel son de ejemplo y lo dicen en pantalla. Rodrigo Herrera y Dylan Jiménez son los dueños de Clientia Tech. El horario de atención es el del kit de cliente (lunes a sábado, 8 am a 8 pm, hora de Honduras).

No aparece el precio de nuestro servicio, ninguna promesa de ventas, conteos de comentarios ni quejas.

## Cómo se genera

```bash
cp /mnt/project-files/musica/better-times-are-coming-mixkit.mp3 src/musica.mp3   # la música no va en el repo
node capturas.mjs          # solo si cambia el panel: src/panel-hoy.jpg, panel-pedidos.jpg, panel-cocina.jpg
node render.mjs --hoja     # build/hoja.jpg, cuadros sueltos para revisar
node render.mjs            # build/loca-luna-casa-digital-v2.mp4
```
