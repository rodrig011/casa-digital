# Tito Wings · paquete de Casa Digital

Alitas en Tegucigalpa (Nova Plaza Belén, Blvd. del Norte). TikTok @titowingss. Domicilio propio de 11 am a 7 pm y cuatro teléfonos.
Investigación completa en `redes/investigacion-redes.md`: menú con precios del 13-oct, combos, 15 comentarios preguntando a qué número pedir (les contestaron con un emoji), "No contestan ningún número", el comentario con más likes de la cuenta (235) es sobre la espera, y pedidos que llegan sin aderezos o sin la salsa ranch.
Ojo: no mezclar con material de otros restaurantes de pollo.

- `panel/`: panel del dueño (demo), estilo Salesforce, al nivel de los otros restaurantes. `panel/dist/tito-wings-panel.html` es un solo archivo para mandar o abrir en el celular; se arma con `python3 panel/build.py`. Secciones: Inicio (ventas, pedidos atrasados, acciones recomendadas, motos), WhatsApp (un solo número en lugar de cuatro, lo que el bot sabe, combos que explica, lo que preguntan en TikTok), Pedidos y cocina (salsa de cada plato, aderezos calculados, hora prometida, revisión antes de salir), Domicilios (motos, entregas, hora prometida), Salsas e insumos (Sweet chili agotada, lista de quienes la esperan, proveedores), Caja, Ventas (por canal, plato y salsa), Opiniones (encuesta del bot después de cada entrega) y TikTok. Dirección, horario, teléfonos, menú, combos, comentarios citados y vistas son reales; ventas, conversaciones, motos, caja e insumos son de ejemplo y lo dice en pantalla.
- `tito-wings-casa-digital-vertical.mp4`: el video vertical 1080×1920 con "Stylish" de FASSounds, un corte por compás con fundidos. Partes: 1 El problema (comentarios preguntando a qué número pedir, cuatro teléfonos saturados, el comentario de la espera con su respuesta), 2 La solución ("Por eso les proponemos esto": las cuatro cosas que el sistema automatiza; los cuatro números se vuelven un WhatsApp en el perfil y en un comentario fijado, porque el bot no contesta comentarios de TikTok; el bot tomando 24 alitas a domicilio con cada salsa, los aderezos y la hora de llegada, al precio real de L520), 3 Su panel (Inicio, Pedidos y cocina con la revisión antes de salir, Salsas e insumos), 4 Por qué nosotros, los 30 días gratis, Casa Digital y Clientia Tech.
- `video/gen.py`: genera el video. Si el panel cambia, volver a sacar `video/src/panel-*.jpg` (390 px de ancho a 2x; la de pedidos con el tablero corrido a "Revisar antes de salir") y revisar las paradas en `SHOTS`. `video/src/food2-4.jpg` son cuadros de sus videos de TikTok a su tamaño original (576 px); `food1.jpg` es su foto del local, reducida.

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
cp /mnt/project-files/musica/stylish-fassounds.mp3 tito-wings/video/src/musica.mp3   # no va en el repo
cd tito-wings/video && python3 gen.py && cd build/tito-wings-vertical && hyperframes render . -o ../tito-wings-vertical.mp4 -q high
```
