# Steel Works · demo de Casa Digital

Demo de propuesta para Steel Works Honduras (steelworkshn.com): sitio nuevo, asistente de WhatsApp y video.

- `sitio/`: la nueva página (HTML + `hierro.js`, que dibuja portones y piezas con código). Abre `sitio/index.html` directo.
- `bot/engine.js`: motor de conversación del asistente. El mismo archivo corre en el navegador (demo del sitio y de la propuesta) y en Node.
- `bot/server.js`: webhook de WhatsApp para Twilio, sin dependencias. `node server.js` y apuntar el sender a `POST /whatsapp`. `node test.js` recorre los flujos.
- `propuesta/index.html`: página de propuesta (diagnóstico, capturas, bot para probar, plan). `imgs.json` guarda las capturas en base64.
- `fotos/`: fotos reales de Steel Works (recortes de su sitio y catálogo). El sitio, la propuesta y el bot las usan; donde no hay foto se muestra el código de la pieza, nunca un dibujo inventado.
- `logo/`: logo en vectores. `gen_logo.py` genera 3 versiones (horizontal, vertical, símbolo) en 6 colores, cada una en SVG, PDF y PNG. `vista-previa.png` las muestra todas.
- `build.py`: genera `dist/steelworks-sitio.html` y `dist/steelworks-propuesta.html` en un solo archivo cada uno.
- `video/gen.py`: video de propuesta en HyperFrames (1920×1080, 37 compases de "Still Buggin", estilo forja). Ver el encabezado del script para los requisitos.

```bash
python3 build.py
python3 logo/gen_logo.py
cd video && python3 gen.py && cd build && hyperframes render . -o ../steelworks-propuesta.mp4 -q high
```

Precios y códigos vienen del sitio público (octubre 2026). Horario, números de pedido, guías y enlace de pago son datos de ejemplo.
