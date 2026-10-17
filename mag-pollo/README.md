# Mag Pollo · paquete de Casa Digital

Investigación en la carpeta del proyecto: `restaurantes/mag-pollo/redes/investigacion-redes.md` (TikTok @magpollohn, 4 sucursales en SPS, comentarios y respuestas).
Ojo: Mag Pollo y Coco Chicken se pelearon en público (16-oct). Nunca usar material de uno con el otro.

- `mag-pollo-casa-digital-vertical.mp4`: el video v2, 1:53, con "Stylish" de FASSounds (Pixabay, `/mnt/project-files/musica/stylish-fassounds.mp3`), un corte por compás. Va en cuatro partes marcadas: 1 El problema (comentarios reales y el bloque de 4 sucursales pegado a mano 16+ veces), 2 La solución (link en el perfil y comentario fijado llevan a un solo WhatsApp, porque el bot no contesta comentarios de TikTok; el bot con la promo real de L399, la sucursal más cercana y el delivery), 3 Su panel (tres pantallas grandes: ventas de hoy por sucursal y canal, pedidos y clientes esperando, y qué hacer), 4 Por qué nosotros (lo hacemos con su menú y sus 4 sucursales, lo instalamos y actualizamos nosotros, llamada de 15 minutos), Casa Digital y Clientia Tech.
- `video/gen.py`: genera el v2 vertical 1080×1920.
- `mag-pollo-casa-digital-v1-vertical.mp4` y `video/gen-v1.py`: la primera versión (1:40), guardada por si acaso.
- `video/src/`: logo (foto de perfil de TikTok bajada a 600 px), `food1-4.jpg` (su publicación de fotos 7696215765099318546, 2160×2880 bajadas a 720×960).

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
# mag-pollo/video/src/musica.mp3 no va en el repo. Con otra canción: MUSIC_P0=<primer golpe s> MUSIC_BAR=<compás s> python3 gen.py
cd mag-pollo/video && MUSIC_P0=0.035 MUSIC_BAR=2.181818 python3 gen.py  # "Stylish", 110 BPM && cd build/mag-pollo-vertical && hyperframes render . -o ../mag-pollo-vertical.mp4 -q high
```
