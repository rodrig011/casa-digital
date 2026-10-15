# Coco Chicken · video de propuesta

`gen6.py` arma el proyecto de HyperFrames (1920×1080, 1 min 41 s, "Still Buggin", cortes en los compases). Usa los helpers de `gen2.py`/`gen3.py` (copiados de `videos-restaurantes/` en la rama `claude/project-thread-ul4ahh`).

`src/` tiene recortes de las capturas que mandó rodrigo (TikTok, Facebook, PedidosYa) y el logo tomado del último cuadro de su TikTok. Falta `src/tiktok.mp4` (su video "¿Pollos A 15 lempiras?" recodificado, 17 MB, no subido) y `musica2.mp3` + `deps/` junto a los scripts.

```bash
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
python3 gen6.py src && cd videos6/coco-chicken && hyperframes render . -o ../coco-chicken.mp4 -q high
```

## v2 (`gen7.py`, 2026-10-14)

Mismo estilo, música y compases que v1, con otra historia: el domicilio lo ponen PedidosYa y Bip Bip (su bio de TikTok y el letrero de su local), y lo que les falta es ver todo junto. Luego vienen 4 pantallas reales del panel demo (acciones, ventas por app, pedidos para recoger, caja), todas marcadas "Datos de ejemplo". `src/panel/` tiene las capturas a 2x que hace `vshot.js` sobre `coco-chicken/panel/dist/coco-chicken-panel.html`. Ojo: `gen7.py` lee las fuentes de `coco-src/` junto a los scripts.

## v3 (`gen8.py`, 2026-10-14)

rodrigo pidió algo más de lujo que muestre cómo contesta y se conecta el bot. Fondo negro con luces suaves (rojo, dorado, verde WhatsApp) y palabras clave en dorado. Recorrido: su TikTok → comentarios reales ("Incluye refresco ese combo ?", "Y al fin bro dnd Estan ubicados", "Hacen envíos??", "nunca me responden") → "Su WhatsApp, que contesta solo" → conversación completa en un iPhone (precios reales) → teléfono, pantalla de cocina y panel conectados, con el aviso al cliente → panel real → promo y códigos de TikTok → Casa Digital. Usa `coco-src/panel/pv-hoy.png`.

## v4 (`gen9.py`, 2026-10-14)

Es el v3 con dos escenas más, a pedido de rodrigo ("que muestre el beneficio, los números, las comisiones que se ahorra"). **Los números:** 300 pedidos al mes pasan a recoger × L140 × 25% = L10,500 al mes (L126,000 al año). Va marcado como ejemplo con supuestos. **Oportunidades:** de 506 comentarios, 87 piden sucursal en su ciudad, 56 preguntan precio o combo y 25 preguntan dónde están. Dura 2:04 (50 compases). No muestra nuestro precio: eso se habla en la llamada.

## v5 (`gen10.py`, 2026-10-15)

rodrigo no quiso el ejemplo de comisiones ("olvida cuánto cobra PedidosYa, ocupamos algo que de verdad ayude"). Las dos escenas de v4 se cambiaron por: **Cero clientes sin respuesta** (tres preguntas reales de sus comentarios, "Donde están ubicados", "precio?", "cuando para Tegucigalpa", con sus conteos 25/56/87, se contestan una por una y el contador baja a 0) y **Proveedores** (el inventario de Satélite baja del mínimo de plátano y el panel le escribe solo a la Verdulería, que contesta; marcado "Ejemplo"). En el panel, "PedidosYa y Bip Bip, con su comisión" pasó a "WhatsApp, apps y mostrador juntos". Misma duración: 2:04.
