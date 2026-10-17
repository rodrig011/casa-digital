# Toreto's Grill · paquete de Casa Digital

- `marca.md`: investigación y propuesta (copia de la carpeta del proyecto `restaurantes/toretos-grill/`).
- `panel/`: panel del dueño. `python3 panel/build.py` arma `panel/dist/toretos-grill-panel.html` con el logo adentro.
- `video/gen_v4.py`: video oficial (v4, vertical, 1:51, "Stylish" de FASSounds en `src/musica-stylish.mp3`, que no se sube). Cuatro partes marcadas y la escena de solución; usa las capturas `src/pv4-*.jpg` del panel nuevo. Salida: `toretos-grill-casa-digital-v4-vertical.mp4`.
- `video/gen.py`: la versión anterior (2:04, "Still Buggin"; `--vertical` para celular). Usa los helpers de `coco-chicken/video/` (gen2, gen3, gen6, gen10 y `deps/`). Mag Pollo también la importa, no borrarla.

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
# poner en toretos-grill/video/src/ la música (musica.mp3) y su video fijado (tiktok.mp4), que no se suben
cd toretos-grill/video && python3 gen.py && cd build/toretos-grill && hyperframes render . -o ../toretos-grill.mp4 -q high
cd toretos-grill/video && python3 gen_v4.py && cd build/toretos-grill-v4 && hyperframes render . -o ../toretos-grill-v4.mp4 -q high
```
