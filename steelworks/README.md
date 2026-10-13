# Steel Works · demo de Casa Digital

Demo de propuesta para Steel Works Honduras (steelworkshn.com): sitio nuevo, asistente de WhatsApp y video.

La idea: que ningún cliente que entra a cotizar se quede sin respuesta. El asistente pregunta qué necesita, pide medidas, deja escoger el estilo con fotos de trabajos reales, da un precio estimado y agenda la visita para medir o una llamada. La ficha le llega a la sucursal. Nadie tiene que saberse un código.

- `sitio/`: la nueva página, sobre la base v1 (estilo forja). Abre `sitio/index.html` directo. La portada lleva fotos reales de sus trabajos a su tamaño original (para que se vean nítidas), con animaciones de entrada y respuesta al tocar. `hierro.js` dibuja el boceto del cotizador. La versión v3 («la frase es el diseño») se descartó porque con fotos de 400 a 600 px se veía vacía y borrosa; está en el historial de git.
- `bot/engine.js`: motor de conversación del asistente. Las tarifas por m² (o por metro de baranda) en `TARIFAS` son de ejemplo; Steel Works pone las suyas. El mismo archivo corre en el navegador (demo del sitio y de la propuesta) y en Node.
- `bot/server.js`: webhook de WhatsApp para Twilio, sin dependencias. `node server.js` y apuntar el sender a `POST /whatsapp`. `node test.js` recorre los flujos.
- `propuesta/index.html`: página de propuesta (diagnóstico, capturas, bot para probar, plan). `imgs.json` guarda las capturas en base64.
- `fotos/`: fotos reales de Steel Works (de su sitio y catálogo). `fotos/recortes/` son las mismas fotos de piezas con el fondo quitado. Nada es inventado ni dibujado.
- `logo/`: logo en vectores. `gen_logo.py` genera 3 versiones (horizontal, vertical, símbolo) en 6 colores, cada una en SVG, PDF y PNG. `vista-previa.png` las muestra todas.
- `build.py`: genera `dist/steelworks-sitio.html` y `dist/steelworks-propuesta.html` en un solo archivo cada uno.
- `video/gen.py`: video de propuesta en HyperFrames (1920×1080, 37 compases de "Still Buggin", estilo forja). Ver el encabezado del script para los requisitos.

```bash
python3 build.py
python3 logo/gen_logo.py
cd video && python3 gen.py && cd build && hyperframes render . -o ../steelworks-propuesta.mp4 -q high
```

Los precios de piezas vienen del sitio público (octubre 2026). Las tarifas de fabricación, el horario y los números de cotización son datos de ejemplo. Por confirmar con Steel Works: que el 3265-8800 sea su WhatsApp, el horario, las tarifas y los nombres de las familias de piezas.
