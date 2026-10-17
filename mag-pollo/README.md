# Mag Pollo · paquete de Casa Digital

Investigación en la carpeta del proyecto: `restaurantes/mag-pollo/redes/investigacion-redes.md` (TikTok @magpollohn, 4 sucursales en SPS, comentarios y respuestas).
Ojo: Mag Pollo y Coco Chicken se pelearon en público (16-oct). Nunca usar material de uno con el otro.

- `mag-pollo-casa-digital-vertical.mp4`: el video, 1:40, con "Stylish" de FASSounds (Pixabay, `/mnt/project-files/musica/stylish-fassounds.mp3`), un corte por compás.
- `video/gen.py`: video vertical 1080×1920 (1:40 con "Stylish"), con el mismo pitch y la misma edición del vertical de Toreto's y de Bocha's: sus platos, comentarios reales, el bloque de sucursales que pegan a mano 16+ veces, link en el perfil y comentario fijado que llevan a un solo WhatsApp (el bot no contesta comentarios de TikTok), el bot con la promo real de L399 y la sucursal más cercana, delivery por sucursal, panel con sus 4 sucursales y promos, su "Prontooo" para El Progreso, Casa Digital y Clientia Tech.
- `video/src/`: logo (foto de perfil de TikTok bajada a 600 px), `food1-4.jpg` (su publicación de fotos 7696215765099318546, 2160×2880 bajadas a 720×960).

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
# mag-pollo/video/src/musica.mp3 no va en el repo. Con otra canción: MUSIC_P0=<primer golpe s> MUSIC_BAR=<compás s> python3 gen.py
cd mag-pollo/video && MUSIC_P0=0.035 MUSIC_BAR=2.181818 python3 gen.py  # "Stylish", 110 BPM && cd build/mag-pollo-vertical && hyperframes render . -o ../mag-pollo-vertical.mp4 -q high
```
