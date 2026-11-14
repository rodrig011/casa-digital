# Loca Luna · video de propuesta (56 s)

Video vertical 1080×1920 hecho desde cero el 14 nov 2026, para mandárselo directo al dueño.

Archivo final: `../loca-luna-casa-digital-vertical.mp4`. Son competencia de Tito Wings y Alitas de la Alemán: no compartir material entre ellos.

Idea: tres sucursales, un solo WhatsApp. El pedido cae en la cocina de la sucursal que toca y el dueño ve las tres desde su celular.

## Qué dice y de dónde sale cada dato

| En pantalla | Fuente |
|---|---|
| Logo y "Est. 2006" | Su logo, del Linktree linktr.ee/localunahn (1080 px, sin agrandar). |
| Los Castaños, Las Hadas, Choluteca | Las tres que ellos mismos publican (Instagram y TikTok). No se mencionan las que solo nombran clientes. |
| Delivery de 10 am a 10 pm | Su bio de Instagram. |
| Foto de la alita | Portada de su TikTok del 10 ago 2026, a su tamaño original de 540 px. |
| El menú y "11 salsas" | Su menú en PDF (enlazado desde su Linktree), a su ancho original de 1129 px. Las 11 salsas están contadas en ese menú. |
| 12 Alas de Pollo, L 320 | Precio de su menú. La conversación es de ejemplo y lo dice. |
| Los seis pedidos por cocina | De ejemplo y lo dice. Productos y salsas con el nombre de su menú. |
| Pantalla de cocina y panel | Capturas del panel real (`bot-restaurante/panel`) con su menú y pedidos de ejemplo (`capturas.mjs`). Lo dice en pantalla. |

No aparece el precio de nuestro servicio, ninguna promesa de ventas, conteos de comentarios ni quejas.

## Diseño (guías de `.claude/skills`)

- Sus colores: el amarillo exacto de su logo (#FFC928) y negro, en campos planos. Sin degradados, sombras, rótulos encima de titulares ni emojis.
- Una sola familia, Bricolage Grotesque: angosta y pesada para titulares, normal para leer. Distinta a la del video de Alitas de la Alemán.
- Cada escena entra distinto según lo que muestra: los titulares suben renglón por renglón, las burbujas salen de su esquina, los pedidos entran de corrido a su carril. Solo `transform` y `opacity`, con `cubic-bezier(0.23,1,0.32,1)`. Los cortes caen en los compases de la canción (110 BPM).

## Cómo se genera

```bash
cp /mnt/project-files/musica/stylish-fassounds.mp3 src/musica.mp3   # la música no va en el repo
node capturas.mjs          # solo si cambia el panel: src/panel-hoy.jpg y src/panel-cocina.jpg
node render.mjs --hoja     # build/hoja.jpg, un cuadro por escena para revisar
node render.mjs            # build/loca-luna-casa-digital-vertical.mp4
```
