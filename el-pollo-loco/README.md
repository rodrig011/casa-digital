# El Pollo Loco · paquete de Casa Digital

Pollo chuco en Tegucigalpa (Plaza Paseo Verde, frente a la Universidad Católica). TikTok @elpolloloco504.
Investigación completa en `redes/investigacion-redes.md`: menú impreso con precios, 10 comentarios pidiendo un número para pedir (ninguno recibió uno), la fila (su video de la espera tiene 172K vistas), PedidosYa que no llega a Palmira, Villa Olímpica y la UNAH.
Ojo: es pollero como otros prospectos (rivales entre sí). Nunca usar material de uno con otro.

- `panel/`: panel del dueño (demo), estilo Salesforce, al nivel de los otros restaurantes. `panel/dist/el-pollo-loco-panel.html` es un solo archivo para mandar o abrir en el celular; se arma con `python3 panel/build.py`. Secciones: Inicio (ventas, la fila, acciones recomendadas, ventas por hora), WhatsApp (el bot en el 9773-0804, lo que el bot sabe, lo que preguntan en TikTok), Pedidos y cocina (comandas de caja y de WhatsApp en la pantalla de cocina, ventanilla para recoger sin fila), Piezas y proveedores (piezas que quedan, a qué hora se acaban, marcar agotada para que el bot deje de ofrecerla, aviso automático al proveedor), Caja, Ventas, Zonas que piden y TikTok. Dirección, horario, teléfono, precios del menú, comentarios citados y vistas son reales; ventas, conversaciones, fila y piezas son de ejemplo y lo dice en pantalla.
- `el-pollo-loco-casa-digital-vertical.mp4`: el video vertical 1080×1920 con "Stylish" de FASSounds (`/mnt/project-files/musica/stylish-fassounds.mp3`), un corte por compás con fundidos. Partes: 1 El problema (comentarios pidiendo un número, la fila y su propia respuesta "vamos a mejorar en eso"), 2 La solución ("Por eso les proponemos esto": las cuatro cosas que el sistema automatiza; perfil y comentario fijado mandan al WhatsApp del menú, porque el bot no contesta comentarios de TikTok; el bot tomando un pedido para recoger con el precio real de L140), 3 Su panel (capturas del panel de verdad: Inicio, Pedidos y cocina, Piezas), 4 Por qué nosotros, Casa Digital y Clientia Tech.
- `video/gen.py`: genera el video. Si el panel cambia, volver a sacar `video/src/panel-*.jpg` (390 px de ancho a 2x) y revisar las paradas en `SHOTS`. `video/src/food1-4.jpg` son cuadros de sus videos de TikTok a su tamaño original (576 px), sin agrandar.

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm init -y && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
cp /mnt/project-files/musica/stylish-fassounds.mp3 el-pollo-loco/video/src/musica.mp3   # no va en el repo
cd el-pollo-loco/video && python3 gen.py && cd build/el-pollo-loco-vertical && hyperframes render . -o ../el-pollo-loco-vertical.mp4 -q high
```
