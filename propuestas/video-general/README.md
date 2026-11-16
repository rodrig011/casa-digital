# Casa Digital · video corto general (38 s)

Video vertical 1080×1920 del 15 nov 2026. Sirve para **cualquier restaurante**: no lleva el nombre, las fotos ni los datos de ningún negocio. Es el que se manda cuando alguien contesta el primer mensaje por WhatsApp, para no tener que hacer un video a la medida antes de que el dueño lo pida.

Archivo final: `../casa-digital-video-corto.mp4`.

## Qué dice

1. Viernes, 7 de la noche. El WhatsApp no para.
2. ¿Quién contesta, anota el pedido y le avisa a la cocina? Y mientras tanto, el cliente esperando.
3. Eso puede hacerse solo.
4. El pedido se toma completo por WhatsApp.
5. Llega ordenado a la cocina. Y al cliente le llega el aviso.
6. Y usted ve el día desde su celular.
7. Todo esto queda automático: tomar el pedido, mandarlo a la cocina, avisarle al cliente, sumar la venta del día.
8. ¿Lo vemos con su menú? Rodrigo Herrera, por WhatsApp, +1 (765) 543-4251. Casa Digital by Clientia Tech.

El mensaje es "los pedidos llegan ordenados a la cocina y el dueño ve todo en un panel", no "un bot que contesta".

## De dónde sale cada cosa

| En pantalla | Qué es |
|---|---|
| Los seis mensajes del inicio | Mensajes de ejemplo; lo dice en pantalla. |
| La conversación | De ejemplo; lo dice en pantalla. Los productos y precios son los de `bot-restaurante/negocios/ejemplo.json`. |
| La tarjeta de cocina y el panel | Capturas del panel real (`bot-restaurante/panel/panel.html`) con el negocio "Su Restaurante" y pedidos de ejemplo (`capturas.mjs`). Lo dice en pantalla. |
| "¡Ana, su pedido PED-1012 ya va en camino!" | El texto que manda el bot (`bot-restaurante/avisos.js`), sin el emoji ni el total. |

No aparece el precio de nuestro servicio, ningún cliente, testimonio, cifra de resultados ni promesa de ventas.

## Diseño (guías de `.claude/skills`)

- **taste-skill**: sin rótulos encima de los titulares, sin degradados, sin manchas ni figuras de adorno, sin palabra de acento en los titulares; solo texto y pedazos reales de interfaz.
- **impeccable**: una sola familia (Archivo) en dos anchos, condensada pesada para titulares y normal para leer; un solo color de acento, el naranja del panel real; fondos planos, tinta y papel gris.
- **emil-design-eng / animate**: las cosas entran con resorte corto y se quedan quietas; solo `transform`, `opacity` y desenfoque; cada escena empieza en un compás de la canción (110 BPM) y los mensajes caen en los golpes.
- El movimiento es el de Loca Luna v4: desenfoque de movimiento real (6 sub-cuadros por cuadro) y la cámara que barre, atraviesa o desenfoca entre escenas.

## Cómo se genera

```bash
cp /mnt/project-files/musica/stylish-fassounds.mp3 src/musica.mp3   # la música no va en el repo
node capturas.mjs              # solo si cambia el panel
node render.mjs --hoja         # build/hoja.jpg, cuadros sueltos para revisar (T="1,2.5,..." elige los tiempos)
A=10 B=16 node render.mjs      # build/tramo.mp4, solo ese tramo
node render.mjs                # build/casa-digital-video-corto.mp4 (unos 10 minutos)
```
