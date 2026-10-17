# Fogos Grill Beer Garden · paquete de Casa Digital

- `panel/panel.html`: panel del dueño con la misma base que el de Coco Chicken (estilo Salesforce): Inicio con acciones recomendadas, Pedidos por WhatsApp con pantalla de cocina, Reservas del beer garden, Caja, Inventario con aviso automático a proveedores, Ventas, Clientes y promos, y ventas por video de TikTok. Un solo local. Reales: dirección, horario, WhatsApp 9844-8314, pollo chuco L130 y las vistas de sus videos; lo demás es de ejemplo y lo dice arriba. `python3 panel/build.py` lo deja en un solo archivo: `panel/dist/fogos-grill-panel.html`.
- `redes/investigacion-redes.md`: investigación de su TikTok @fogosbeergarden (copia de `restaurantes/fogos-grill/redes/` en la carpeta del proyecto).
- `fogos-grill-casa-digital-vertical.mp4`: video de propuesta vertical 1080×1920 (1:49), con la canción "Stylish" (FASSounds, Pixabay, 110 BPM) y cada escena sobre un compás.
- `video/gen.py`: arma el video en HyperFrames con la misma edición de los videos oficiales (Toreto's vertical, Coco Chicken v5, Bocha's v3). Guion: sus propios videos y números → comentarios reales (dirección, menú con precios, envíos, teléfono) → el problema, visto en su perfil: no hay menú con precios, no hay link para pedir y la cuenta contestó 0 de 57 comentarios → la solución: "Por eso le proponemos un sistema automático" en tres partes (su WhatsApp contesta solo, una página con su menú, un panel para usted) → primero, cada video lleva a su WhatsApp (un bot de WhatsApp no contesta comentarios de TikTok) → 1: el bot contesta dirección con mapa, menú con el precio real y aparta mesa → 2: la página del link del perfil → 3: el panel real, leído por partes con capturas de `panel/` (`video/src/pv-*.jpg`, ancho de celular): hoy, pedidos, reservas, proveedores → por qué contratarnos → contacto. Conversación, página y números del panel son de ejemplo y lo dicen en pantalla.

Fotos en `video/src/` (todas de su TikTok, sin agrandar): `logo.png` recortado de su imagen "Cómo llegar" (7689259227897941266), que también es `mapa.jpg`; `local.jpg` su foto de perfil; `plato.jpg` cuadro del video del pollo chuco (7697480736105827600, t=48.3 s); `parrillada.jpg` del video 7694829110433942792 (t=62.5 s, en el beer garden); `entrana.jpg` del video 7690773492207242503 (t=22.5 s). `fogos.mp4` (no subido) son 11.6 s de sus videos: fachada (7693952585778187527, 0-4.2 s), pollo chuco (47.6-49.4 s), beer garden (50.2-53.2 s) y parrilla (7691491565507808520, 0-2.6 s), recodificados a H.264 sin audio.

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
# en fogos-grill/video/src/ van musica.mp3 ("Stylish") y fogos.mp4
cd fogos-grill/video && python3 gen.py --bpm 110 --p0 0.029 && cd build/fogos-grill-vertical && hyperframes render . -o ../fogos-grill-vertical.mp4 -q high
```
