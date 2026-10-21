# Fusión Food · paquete de Casa Digital

"The King of Wings", comida a domicilio en Gracias, Lempira. Facebook /fusionfoodhn (3.8K) e Instagram @fusionfoodhn (1,884). Pedidos por WhatsApp (Línea Fusión 8757-0555) y por DM; delivery propio en Gracias.
Investigación completa en `redes/investigacion-redes.md`: bio, textos de sus últimas 5 publicaciones con sus reacciones, nombres de platos (Alitas, Chicken fingers, hamburguesas, papas, Tacos Mexicanos, Plato del Día). No se encontraron precios ni nombre del dueño.
Ojo: no mezclar con material de otros restaurantes.

- `panel/`: panel del dueño (demo), estilo Salesforce, al nivel de los otros restaurantes. `panel/dist/fusion-food-panel.html` es un solo archivo para mandar o abrir en el celular; se arma con `python3 panel/build.py`. Secciones: Inicio, Mensajes (WhatsApp, Messenger e Instagram en una bandeja con bot), Pedidos y cocina (revisión antes de salir), Domicilios (motos, hora prometida), Menú del día e insumos (plato del día, avisos a clientes, proveedores), Caja, Ventas, Clientes (frecuentes y encuesta) y Facebook e Instagram (ventas por publicación con código). Ciudad, teléfono, correo, nombres de platos, fotos y publicaciones son reales; precios, ventas, conversaciones, motos, zonas, caja e insumos son de ejemplo y lo dice en pantalla.
- `fusion-food-casa-digital-vertical.mp4`: video vertical 1080×1920, 1:53, "Stylish" de FASSounds, un corte por compás con fundidos. 1 El problema (piden por tres canales, con sus propios textos; las 5 publicaciones mandan a la Línea Fusión y no se sabe cuál vendió), 2 La solución ("Por eso les proponemos esto", lo que el sistema automatiza, tres canales en una bandeja que contesta sola, el bot ofreciendo el plato del día y tomando un pedido), 3 Su panel (Inicio, Mensajes, Menú del día e insumos), 4 Por qué nosotros, 30 días gratis, Casa Digital y Clientia Tech.
- `video/gen.py`: genera el video. Si el panel cambia, volver a sacar `video/src/panel-*.jpg` (390 px de ancho a 2x, página completa) y revisar las paradas en `SHOTS`. `video/src/food1-4.jpg` son fotos de su Facebook a su tamaño original (~520 px).

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
cp /mnt/project-files/musica/stylish-fassounds.mp3 fusion-food/video/src/musica.mp3   # no va en el repo
cd fusion-food/video && python3 gen.py && cd build/fusion-food-vertical && hyperframes render . -o ../fusion-food-vertical.mp4 -q high
```
