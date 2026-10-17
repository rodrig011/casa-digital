# Mag Pollo · paquete de Casa Digital

Investigación en la carpeta del proyecto: `restaurantes/mag-pollo/redes/investigacion-redes.md` (TikTok @magpollohn, 4 sucursales en SPS, comentarios y respuestas).
Ojo: Mag Pollo y Coco Chicken se pelearon en público (16-oct). Nunca usar material de uno con el otro.

- `panel/`: el panel del dueño (demo), al nivel de los de los otros restaurantes, estilo Salesforce. `panel/dist/mag-pollo-panel.html` es un solo archivo para mandar o abrir en el celular; se arma con `python3 panel/build.py`. Secciones: Inicio (las 4 sucursales, acciones recomendadas, ventas por hora), WhatsApp (un solo número, lo que el bot sabe), Pedidos (cocina y motoristas por sucursal), Caja, Inventario y proveedores (aviso automático), Promos y canales, Nuevas ciudades y TikTok. Sucursales, direcciones, teléfonos, precios publicados y vistas son reales; ventas y conversaciones son de ejemplo y lo dice en pantalla. No usa nada de Coco Chicken.
- `mag-pollo-casa-digital-vertical.mp4`: el video v3, 1:53, con "Stylish" de FASSounds (Pixabay, `/mnt/project-files/musica/stylish-fassounds.mp3`), un corte por compás. Partes: 1 El problema (comentarios reales y el bloque de 4 sucursales pegado a mano 16+ veces), 2 La solución ("Por eso les proponemos esto": las cuatro cosas que el sistema automatiza; link del perfil y comentario fijado a un solo WhatsApp, porque el bot no contesta comentarios de TikTok; el bot con la promo real de L399), 3 Su panel (el panel de verdad, capturas a lo ancho de un celular que bajan despacio: Inicio, WhatsApp, Inventario y proveedores), 4 Por qué nosotros, Casa Digital y Clientia Tech.
- `video/gen.py`: genera el v3 vertical 1080×1920. Si el panel cambia, volver a sacar `video/src/panel-*.jpg` (390 px de ancho a 2x) y revisar las paradas en `SHOTS`.
- Versiones anteriores guardadas: `mag-pollo-casa-digital-v1-vertical.mp4` con `video/gen-v1.py` y `mag-pollo-casa-digital-v2-vertical.mp4` con `video/gen-v2.py`.
- `video/src/`: logo (foto de perfil de TikTok bajada a 600 px), `panel-*.jpg` (capturas del panel), `food1-4.jpg` (su publicación de fotos 7696215765099318546, 2160×2880 bajadas a 720×960).

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
# mag-pollo/video/src/musica.mp3 no va en el repo. Con otra canción: MUSIC_P0=<primer golpe s> MUSIC_BAR=<compás s> python3 gen.py
cd mag-pollo/video && MUSIC_P0=0.035 MUSIC_BAR=2.181818 python3 gen.py  # "Stylish", 110 BPM && cd build/mag-pollo-vertical && hyperframes render . -o ../mag-pollo-vertical.mp4 -q high
```
