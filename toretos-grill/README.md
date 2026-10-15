# Toreto's Grill · paquete de Casa Digital

- `marca.md`: investigación y propuesta (copia de la carpeta del proyecto `restaurantes/toretos-grill/`).
- `panel/`: panel del dueño. `python3 panel/build.py` arma `panel/dist/toretos-grill-panel.html` con el logo adentro.
- `video/gen.py`: video de propuesta en HyperFrames (2:04, "Still Buggin"). Usa los helpers de `coco-chicken/video/` (gen2, gen3, gen6, gen10 y `deps/`).

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
# poner en toretos-grill/video/src/ la música (musica.mp3) y su video fijado (tiktok.mp4), que no se suben
cd toretos-grill/video && python3 gen.py && cd build/toretos-grill && hyperframes render . -o ../toretos-grill.mp4 -q high
```
