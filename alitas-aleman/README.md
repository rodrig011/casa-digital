# Alitas de la Alemán · paquete de Casa Digital

Restaurante de alitas en Tegucigalpa (TikTok @alitasaleman.hn, Instagram @alitasdelaaleman). Un solo local en Res. Las Colinas, Boulevard Francia. Hoy se pide llamando a cuatro números, por Bip Bip o pasando al restaurante; no publican WhatsApp. **Son competencia directa de Tito Wings: no compartir material entre los dos.**

- `redes/investigacion.md`: lo que vimos en su TikTok (10 nov 2026), el borrador del primer mensaje y lo que no hay que mencionar. `redes/tiktok-datos.json` tiene los 11 videos y 330 comentarios.
- `bot/alitas-aleman-demo.json`: su menú para el bot. El precio de 24 Alitas (L395) lo dieron ellos en un comentario; **los demás precios son de ejemplo**. Solo para la demo y las capturas; no usar con clientes sin que confirmen menú y precios.
- `alitas-aleman-casa-digital-vertical.mp4`: video vertical 1080×1920 con "Stylish" de FASSounds (1:53).
- `video/gen.py`: genera el video (misma base que `star-chicken/video/gen.py`). Las capturas `video/src/panel-*.jpg` son del **panel real** (`bot-restaurante/panel`) corriendo en local con el menú de la demo y pedidos escritos al bot. Las fotos de `video/src/` son cuadros de sus propios videos de TikTok a su tamaño original (576 px de ancho) y su logo del perfil.

Lo que dice el video y de dónde sale:

- "Las originales. Desde 2002": está impreso en el mantel de sus bandejas (se ve en sus videos).
- 274.7K vistas (video del 4 de octubre), 18.7K seguidores y 105.5K me gusta: su perfil, 10 nov 2026.
- 43 comentarios preguntan a qué número o cómo pedir: conteo sobre los 330 comentarios de `redes/tiktok-datos.json`; la mayoría no tiene respuesta de la marca.
- Los comentarios y el texto de los cuatro números van palabra por palabra.
- La conversación del bot es de ejemplo y lo dice en pantalla. No aparece el precio de nuestro servicio.

Tipografía según las guías de `.claude/skills`: un solo color de acento, sin texto con degradado y sin rótulo encima de los titulares.

```bash
cp /mnt/project-files/musica/stylish-fassounds.mp3 alitas-aleman/video/src/musica.mp3   # no va en el repo
cd alitas-aleman/video && python3 gen.py && cd build/alitas-aleman-vertical && hyperframes render . -o ../alitas-aleman-vertical.mp4 -q high
```
