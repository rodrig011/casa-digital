# Bocha's Grill · paquete de Casa Digital

- `marca.md`: investigación y propuesta (copia de la carpeta del proyecto `restaurantes/bochas-grill/`). `redes/investigacion-redes.md`: fuentes y conteos de sus comentarios.
- `panel/`: panel del dueño para las 5 sucursales. `python3 panel/build.py` arma `panel/dist/bochas-grill-panel.html` con el logo adentro.
- `video/gen.py`: video vertical 1080×1920 (2:04), con el mismo pitch y la misma edición del video vertical de Toreto's (frases completas, fondo negro con luces): su historia, comentarios reales, bot de WhatsApp, inventario, espera por sucursal, encuesta, panel, franquicia y contacto.
- `video/gen-v2-preguntas.py`: la versión con el guion de preguntas; rodrigo la rechazó, queda de registro. Usa `coco-chicken/video/` (gen2, gen3, gen6, clientia-mark.json y `deps/`) y `toretos-grill/video/gen.py`.
- `video/gen-v0-pip.py`: primera versión con ventana de sus TikTok y subtítulos cortos; rodrigo rechazó esa edición, queda solo de registro.

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
# en bochas-grill/video/src/ van musica.mp3 ("Still Buggin"); las fotos hist*.jpg, villa.jpg, plato.jpg y panel-m.jpg ya están en el repo
cd bochas-grill/video && python3 gen.py && cd build/bochas-grill-vertical && hyperframes render . -o ../bochas-grill-vertical.mp4 -q high
```


Fotos: `villa.jpg` es un cuadro de su video 7678006702586776840 (t=10.3 s) y `plato.jpg` de 7674047952360443143 (t=4.3 s), recortados a 1080×810 de videos de 1080×1920, sin agrandar. `panel-m.jpg` es la captura móvil de Inicio del panel.
`hist1/2/4/5.jpg` son 4 de las 5 fotos de su publicación de TikTok 7674032833983302920 ("Empezamos con una idea..."), de 2160×2700 bajadas a 720×900.
