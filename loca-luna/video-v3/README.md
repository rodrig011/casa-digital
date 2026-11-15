# Loca Luna · video de propuesta v3 (69 s)

Tercera versión, del 14 nov 2026. Rodrigo mandó un video de referencia (el lanzamiento de una app, visto en TikTok) y pidió ese estilo, otras letras ("esas letras se ven muy AI") y que quede claro que la propuesta es automatizar procesos. Las versiones 1 y 2 siguen en `../video/` y `../video-v2/`.

Archivo final: `../loca-luna-casa-digital-v3.mp4`. Son competencia de Tito Wings y Alitas de la Alemán: no compartir material entre ellos.

## Qué se tomó de la referencia

- Fondo claro con manchas suaves del color de la marca (aquí el amarillo de su logo) que se mueven despacio, alternado con escenas oscuras con un resplandor.
- Letras medianas y limpias, centradas, que aparecen palabra por palabra enfocándose. Tipografía Outfit, un solo peso para titulares.
- Una frase que cruza la pantalla en grande antes de asentarse.
- Pedazos de interfaz en tarjetas que llegan giradas en 3D, un cursor que hace clic y la cámara que entra al botón.
- Cada escena entra y sale con desenfoque.

La referencia es horizontal; este video sigue vertical (1080×1920) porque se manda por WhatsApp.

## El mensaje: automatizar el proceso

El video sigue un pedido de punta a punta: el cliente escribe por WhatsApp, el asistente toma el pedido completo, lo manda solo a la cocina que toca, la cocina toca Listo y al cliente le llega el aviso, y el dueño ve las tres sucursales en un panel. Después una lista: tomar el pedido, mandarlo a su cocina, avisarle al cliente, asignar al repartidor, sumar la venta por sucursal. Todo eso lo hace hoy `bot-restaurante`.

## De dónde sale cada dato

Logo, tres sucursales, 11 salsas y L 320 salen de sus redes y de su menú (ver `../video/README.md`). La conversación y los pedidos son de ejemplo y lo dicen en pantalla. La tarjeta de cocina, el panel y la tabla "Por sucursal" son capturas del panel real (`capturas.mjs`). El aviso "¡Carlos, su pedido PED-1012 ya está listo! Puede pasar a recogerlo a Las Hadas." es el texto que manda el bot (`bot-restaurante/avisos.js`), sin el emoji ni el total.

No aparece el precio de nuestro servicio, ninguna promesa de ventas, conteos de comentarios ni quejas.

## Cómo se genera

```bash
cp /mnt/project-files/musica/better-times-are-coming-mixkit.mp3 src/musica.mp3   # la música no va en el repo
node capturas.mjs          # solo si cambia el panel
node render.mjs --hoja     # build/hoja.jpg, cuadros sueltos para revisar
node render.mjs            # build/loca-luna-casa-digital-v3.mp4
```
