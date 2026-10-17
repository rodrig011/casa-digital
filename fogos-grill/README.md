# Fogos Grill Beer Garden · paquete de Casa Digital

- `redes/investigacion-redes.md`: investigación de su TikTok @fogosbeergarden (copia de `restaurantes/fogos-grill/redes/` en la carpeta del proyecto).
- `fogos-grill-casa-digital-vertical.mp4`: video de propuesta vertical 1080×1920 (1:29), con la canción "Stylish" (FASSounds, Pixabay, 110 BPM) y cada escena sobre un compás.
- `video/gen.py`: arma el video en HyperFrames con la misma edición de los videos oficiales (Toreto's vertical, Coco Chicken v5, Bocha's v3). Guion: sus propios videos y números → comentarios reales (dirección, menú con precios, envíos, teléfono) → paso 1: cada video lleva a su WhatsApp (link en el perfil, comentario fijado, el número en cada video), porque un bot de WhatsApp no contesta comentarios de TikTok → el bot contesta dirección con su mapa, menú con el precio real (pollo chuco L130) y aparta mesa → una página con menú, mapa y reservas → panel con pedidos, reservas y qué video vende → Casa Digital. Conversación, página y números del panel son de ejemplo y lo dicen en pantalla.

Fotos en `video/src/` (todas de su TikTok, sin agrandar): `logo.png` recortado de su imagen "Cómo llegar" (7689259227897941266), que también es `mapa.jpg`; `local.jpg` su foto de perfil; `plato.jpg` cuadro del video del pollo chuco (7697480736105827600, t=48.3 s); `parrillada.jpg` del video 7694829110433942792 (t=62.5 s, en el beer garden); `entrana.jpg` del video 7690773492207242503 (t=22.5 s). `fogos.mp4` (no subido) son 11.6 s de sus videos: fachada (7693952585778187527, 0-4.2 s), pollo chuco (47.6-49.4 s), beer garden (50.2-53.2 s) y parrilla (7691491565507808520, 0-2.6 s), recodificados a H.264 sin audio.

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
# en fogos-grill/video/src/ van musica.mp3 ("Stylish") y fogos.mp4
cd fogos-grill/video && python3 gen.py --bpm 110 --p0 0.029 && cd build/fogos-grill-vertical && hyperframes render . -o ../fogos-grill-vertical.mp4 -q high
```
