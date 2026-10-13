# Steel Works · demo de Casa Digital

Demo de propuesta para Steel Works Honduras (steelworkshn.com): sitio nuevo, asistente que cotiza conversando y video.

La idea central: el cliente no sabe códigos de pieza. Dice «un portón para la cochera, como de 4 por 2» o manda una foto, elige el estilo viendo obras reales, y el asistente calcula las piezas y agenda la visita para medir.

- `fotos/`: fotos reales recortadas de capturas de su sitio y su catálogo 2022 (obras, piezas, chispas del taller, panel CNC). Todo lo visual sale de aquí; no hay dibujos inventados.
- `sitio/`: la nueva página (`index.html`, estilo galería) y la vista del asistente (`chat.js` + `chat.css`), que comparte la propuesta.
- `bot/engine.js`: motor de conversación. Entiende texto libre con reglas (en producción lo reemplaza un modelo de IA con el catálogo como herramienta). Corre en el navegador y en Node.
- `bot/server.js`: webhook de WhatsApp para Twilio, sin dependencias. `node server.js` y apuntar el sender a `POST /whatsapp`. En texto plano el cliente contesta con el número de la opción. `node test.js` recorre los flujos.
- `propuesta/index.html`: página de propuesta con el asistente para probar. `imgs.json` guarda las capturas del sitio nuevo.
- `build.py`: genera `dist/steelworks-sitio.html` y `dist/steelworks-propuesta.html`, cada uno en un solo archivo con fotos y fuentes incluidas.
- `video/gen.py`: video de propuesta en HyperFrames (1920×1080, 37 compases de "Still Buggin", estilo forja con fotos reales). Ver el encabezado del script para los requisitos.

```bash
node bot/test.js
python3 build.py
cd video && python3 gen.py && cd build && hyperframes render . -o ../steelworks-propuesta.mp4 -q high
```

Precios y códigos vienen del sitio público (octubre 2026). Fechas de visita, números de cotización y enlace de pago son datos de ejemplo.
