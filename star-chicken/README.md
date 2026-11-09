# Star Chicken · paquete de Casa Digital

Cocina oculta en San Pedro Sula (TikTok @starchkn.hn), abrió el 6 de noviembre de 2026. Boneless con salsa Maracuyeahhh, Tenders, Cosmic Burger, Mac & Cheese. Solo delivery y pick up; hoy se pide por Bip Bip, Instagram o pasando a la cocina, sin WhatsApp publicado.

- `PROPUESTA.md`: lo que vimos, la necesidad, la propuesta (solo lo que el bot hace hoy) y el DM de Instagram listo para copiar.
- `redes/`: investigación de su TikTok (datos, comentarios, portadas y logo).
- `bot/star-chicken-demo.json`: su menú para el bot con **precios de ejemplo**. Solo para la demo y las capturas; no usar con clientes sin que confirmen menú y precios.
- `star-chicken-casa-digital-vertical.mp4`: video vertical 1080×1920 con "Stylish" de FASSounds.
- `video/gen.py`: genera el video (misma base que `fusion-food/video/gen.py`). Las capturas `video/src/panel-*.jpg` son del **panel real** (`bot-restaurante/panel`) corriendo en local con `bot/star-chicken-demo.json` y pedidos escritos al bot. Las fotos `video/src/` son cuadros y portadas de sus propios videos de TikTok a su tamaño original.

```bash
cp /mnt/project-files/musica/stylish-fassounds.mp3 star-chicken/video/src/musica.mp3   # no va en el repo
cd star-chicken/video && python3 gen.py && cd build/star-chicken-vertical && hyperframes render . -o ../star-chicken-vertical.mp4 -q high
```
