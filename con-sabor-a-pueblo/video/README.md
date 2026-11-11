# Con Sabor a Pueblo · video de la propuesta (1:56)

Video vertical 1080×1920 en el estilo oscuro de antes (misma base que `alitas-aleman/video/gen.py`), con el outro de Clientia Tech. Hecho el 11 nov 2026 con lo que el dueño pidió por teléfono: pedidos tomados solos y mandados a cocina, su delivery propio, el aviso al cliente, lo que ve el repartidor, el panel del dueño y el contacto con proveedores.

Archivo final: `../con-sabor-a-pueblo-casa-digital-vertical.mp4`.

## Qué es real y qué es demostración

| En pantalla | Qué es |
|---|---|
| 985.8K vistas, 45K seguidores, 479.5K me gusta | Su TikTok @consaborapueblohn, leído el 11 nov 2026. |
| Fotos | Cuadros de sus propios videos, a 576 px, sin agrandar. |
| Comentarios y sus respuestas | Palabra por palabra (`../redes/tiktok-datos.json`). 34 de los 138 comentarios leídos preguntan el precio. |
| Conversación de WhatsApp | De ejemplo y lo dice. Sin precio: ellos no publican ninguno. |
| Cocina y panel "Hoy" | **Panel real** (`bot-restaurante/panel`) con pedidos escritos al bot usando `../bot/sabor-pueblo-demo.json`. Pedidos, nombres y precios de ejemplo. |
| Avisos al cliente | Los textos que manda el bot de verdad ("Listo…", "ya va en camino"). |
| **Entregas (repartidor)** | **Demostración.** El bot real todavía no tiene pantalla de repartidor. Lo dice en pantalla. |
| **Proveedores** | **Demostración.** El bot real todavía no avisa a proveedores. Insumos, cantidades y proveedores son de ejemplo. Lo dice en pantalla. |

No aparece el precio de nuestro servicio ni ninguna promesa de ventas.

## Cómo se genera

```bash
cd coco-chicken/video && mkdir -p deps && cd deps && npm i gsap @fontsource/archivo-black @fontsource/inter-tight
npm i -g hyperframes@0.8.150
cp /mnt/project-files/musica/stylish-fassounds.mp3 con-sabor-a-pueblo/video/src/musica.mp3   # la música no va en el repo
node con-sabor-a-pueblo/video/capturas.mjs con-sabor-a-pueblo/video/src   # solo si cambia el panel
cd con-sabor-a-pueblo/video && python3 gen.py
node shots.mjs 10,40,70        # cuadros de revisión en build/rev.jpg, sin renderizar todo
cd build/con-sabor-a-pueblo-vertical && hyperframes render . -o ../con-sabor-a-pueblo-vertical.mp4 -q high
```
