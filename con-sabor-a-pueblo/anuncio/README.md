# Con Sabor a Pueblo · anuncio "Haz tu pedido por WhatsApp" (32 s)

Anuncio vertical 1080×1920 para los clientes de Con Sabor a Pueblo (para su TikTok o estados de WhatsApp), hecho el 21 nov 2026. Dice que ahora se pide por WhatsApp al 3169-9031, donde contesta el asistente, y cierra con "Con Sabor a Pueblo trabaja con Clientia Tech".

Archivo final: `../con-sabor-a-pueblo-anuncio-whatsapp.mp4`.

Misma técnica que el video v4 de Loca Luna (`loca-luna/video-v4/`): todo se calcula por cuadro con `window.seek(t)` y `render.mjs` mezcla 8 sub-cuadros por cuadro para el desenfoque de movimiento. Música: la canción oficial `stylish-fassounds.mp3`.

## Escenas

| Tiempo | En pantalla |
|---|---|
| 0–3.5 s | Su logo + video de chicharrón cortado (cámara lenta). "Chicharrones de panceta." |
| 3.5–7 s | Video de chanchito chuko servido. "Chanchito chuko." "Repollo encurtido, aderezos y el cerdito desmechado encima." |
| 7–10 s | El amarillo de su logo llena la pantalla. "Ahora lo pides por WhatsApp." "Sin esperar a que alguien vea el mensaje." |
| 10–16 s | "Te contesta al momento." Conversación de WhatsApp, marcada "Conversación de ejemplo". |
| 16–20 s | "Pedir es así:" 1 Escribe al 3169-9031 · 2 Di qué quieres y si es a domicilio o para recoger · 3 Paga por transferencia y tu pedido pasa a cocina. "El envío se le paga al repartidor." |
| 20–24 s | Video de chicharrón + Sábados, 10 a. m. a 4 p. m. (o hasta que se acabe) · Col. Palmira, Tegucigalpa, frente al edificio Italia · A domicilio o para recoger, apartados hasta el jueves. |
| 24–29 s | Logo, "Haz tu pedido por WhatsApp", 3169-9031 en grande, "Pedidos en Tegucigalpa." |
| 29–32 s | Su logo × Clientia Tech. "by Clientia Tech · clientiatech.com". |

## De dónde sale cada dato

- **Videos**: de su TikTok @consaborapueblohn. Chicharrón: video `7705223553939033351` (1080×1920, 60 cps). Chanchito: video `7706891353715641607` (1080×1920, 60 cps), solo los platos, no la fila de gente (eso es San Pedro Sula). Se recortó una franja de 1080×1000 para que **no salgan sus subtítulos palabra por palabra ni el sticker del número**; se muestra a 960 px de ancho, sin agrandar.
- **Logo**: `bot-restaurante/negocios/con-sabor-a-pueblo-logo.svg` (vectorial, sin el número de SPS).
- **Nombres**: "Chicharrones de panceta" y "Chanchito chuko" como los escriben en TikTok. La descripción del chanchito es la del menú del bot (`bot-restaurante/negocios/con-sabor-a-pueblo.json`).
- **Horario, lugar, envío, transferencia, apartados hasta el jueves**: `con-sabor-a-pueblo.json` (mensaje del dueño del 18 nov y lo que dijo el 11 y el 16 nov).
- **Tegucigalpa solamente**: el bot solo atiende Tegucigalpa; lo de San Pedro Sula se lo pasa al dueño. Por eso el anuncio no menciona SPS.
- **Sin precios**: ellos no publican precios en TikTok. Tampoco aparece el precio de Clientia Tech ni promesas de ventas.

## Cómo se genera

```bash
cd con-sabor-a-pueblo/anuncio
cp /mnt/project-files/musica/stylish-fassounds.mp3 src/musica.mp3     # la música no va en el repo
# los cuadros de video no van en el repo (pesan 47 MB): se sacan de sus TikTok
pip install yt-dlp
yt-dlp -o chicharron.mp4 https://www.tiktok.com/@consaborapueblohn/video/7705223553939033351
yt-dlp -o chanchito.mp4  https://www.tiktok.com/@consaborapueblohn/video/7706891353715641607
mkdir -p src/clips/a src/clips/b src/clips/c
ffmpeg -ss 0.1   -i chicharron.mp4 -t 2.1 -vf "crop=1080:1000:0:375" -q:v 3 src/clips/a/%03d.jpg
ffmpeg -ss 14.6  -i chanchito.mp4  -t 3.2 -vf "crop=1080:1000:0:400" -q:v 3 src/clips/b/%03d.jpg
ffmpeg -ss 15.65 -i chicharron.mp4 -t 3.4 -vf "crop=1080:1000:0:375" -q:v 3 src/clips/c/%03d.jpg
node render.mjs --hoja        # build/hoja.jpg, cuadros sueltos para revisar
node render.mjs               # build/con-sabor-a-pueblo-anuncio-whatsapp.mp4
```

Si cambia la cantidad de cuadros de un clip, actualizar `CLIPS` en `index.html`.
