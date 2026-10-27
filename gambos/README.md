# Gambos · paquete de Casa Digital

Seafood boil "Cajun Style" en Tegucigalpa. TikTok @gambos_hn (7.9K seguidores, 62.4K me gusta, 36 videos; "¿Ya probaste nuestro Seafood Boil Cajun Style?" tiene 2.6M de vistas). Pedidos al WhatsApp +504 8932-4789, que sale como "Gambos by Pacomeralgo". La dueña es una mujer (contestó ella el 26-oct-2026); su nombre todavía no lo sabemos.
No mezclar con material de otros restaurantes de mariscos (Libby's Cajun es de San Pedro Sula y es otro cliente posible).

Lo que dicen ellos mismos (respuestas de la cuenta en TikTok, leídas el 27-oct-2026):
- "Estamos en TGU. Atendemos únicamente por delivery o pickup de jueves a domingo. Los pedidos se deben hacer un dia antes."
- Pickup en Colonia Florencia Norte. No tienen local para comer.
- Venden por cupos y tandas: "no te quedés sin cupo este fin de semana", "todavía tenemos cupos disponibles para los batches de este fin de semana".
- Salsas: Clásica Cajún, Honey Cajún, Lemon Pepper. "Pica levemente".
- En 10 videos se leyeron 209 comentarios: 125 preguntan precio, ubicación, si pica o el número. La cuenta contestó 45, casi siempre con el mismo texto ("Te enviamos nuestro menú").

Menú (catálogo de WhatsApp Business, capturas de Rodrigo del 26-oct-2026, en `redes/catalogo-whatsapp-*.png`): Combo individual (1px) L486, Duo de Mar (2px) L970, Marea x4 (4px) L1,940, Marea x6 L2,910 (5 camarones jumbo y 4 mejillones por persona, más lo demás). Adicionales: Elotes L50, Libra de chorizo L150, Libra de King Crab L300, Libra de camarones L320, Libra de mejillones L210, Cajun Butter Cup L220, Libra de Langosta Small L450, Libra de Langosta Large L600.

- `redes/`: `tiktok-datos.json` (perfil, 10 videos, todos los comentarios leídos y las respuestas de la cuenta), portadas de sus videos, `avatar.jpg` (el logo) y el catálogo.
- `panel/`: panel de la dueña (demo), estilo Salesforce. `python3 panel/build.py` arma `panel/dist/gambos-panel.html`, un solo archivo, publicado en https://clientiatech.com/demos/gambos-panel.html (noindex). Entrada demo: demo@gambos.hn / boil2026. Lo central es **Cupos**: cada pedido de WhatsApp aparta sus cupos solo (un cupo = una persona, como su menú: 1px, 2px, 4px, 6px), cada tanda se llena y el asistente ofrece otra hora o lista de espera, y cada día se cierra la noche anterior. Además: WhatsApp (conversaciones con sus reglas y su menú real), Cocina por tanda con revisión antes de sellar la bolsa, Entregas (delivery y pickup en Florencia Norte), Pagos (transferencias por confirmar; ningún cobro conectado), Clientes con ficha, Campañas ("ya abrimos cupos"), Mariscos e insumos (compra exacta a partir de los cupos vendidos), Reportes por fin de semana, TikTok (datos reales) y Equipo. Menú, precios, ciudad, días, pickup, salsas, fotos y TikTok son reales; tandas, cupos, pedidos, clientes y pagos son de ejemplo y lo dice en pantalla.

- `video/`: video vertical de la propuesta (`python3 video/gen.py`, luego `hyperframes render . -o ...` dentro de `video/build/gambos-vertical`; necesita `src/musica.mp3`, la canción oficial, y `coco-chicken/video/deps`). Listo en `gambos-casa-digital-vertical.mp4` (1:53, 1080x1920). Las capturas del panel en `video/src/` se toman con `node video/shots.js`; si cambia el panel, se vuelven a tomar.

Precio si lo piden: instalación entre L15,000 y L20,000 y mensualidad desde L2,500, sin comisión; 30 días gratis; la instalación se paga en un solo pago el día 30.

## Bot real (listo para prender)

`bot-restaurante/negocios/gambos.json`: su catálogo con los nombres y precios tal cual, las 3 salsas, jueves a domingo, pedidos un día antes, delivery o pickup en Florencia Norte. El bot vende por cupos (ver la sección 5 de `bot-restaurante/README.md`): pregunta la salsa de cada combo, el día y la tanda, aparta los cupos solo, cierra la tanda cuando se llena y lleva la lista de espera. El panel real tiene la vista **Cupos**.

Antes de prenderlo hay que pedirle a Gambos (lo de aquí son ejemplos):
1. Las horas de las tandas y cuántas personas caben en cada una (ahora: 12:00, 2:00, 4:30 y 6:30, 12 por tanda).
2. A qué hora cierran los pedidos el día anterior (ahora: 9:00 p. m.).
3. La dirección exacta del pickup y el enlace de Google Maps.
4. Zonas y costo del envío.
5. Cómo cobran: cuenta para transferencias (banco, tipo, número, a nombre de quién). Con eso el bot cobra antes de apartar el cupo; sin eso el cobro queda apagado.
6. Qué número contesta el bot (el 8932-4789 u otro) y acceso a su Meta Business para conectarlo (ver `INSTALACION-A-DISTANCIA.md`).
7. Quién recibe los avisos de pedidos y quién entra al panel (correos).

## Panel oficial (seguro y cifrado)

Es el panel real del bot (`bot-restaurante/panel`), con su menú y sus cupos, en un servidor solo para Gambos: `bot-restaurante/render-gambos.yaml`.

- Los datos de sus clientes (nombres, teléfonos, direcciones, pedidos, conversaciones) se guardan cifrados con AES-256; sin la llave `DATA_KEY` nadie los puede leer, ni nosotros copiando el disco.
- Para entrar: correo, contraseña y un código de 6 números que le llega por WhatsApp. Puede recordar su teléfono 30 días.
- Vista **Seguridad**: quién tiene acceso, intentos fallidos y quién cambió cada pedido.
- Conexión solo por https; la sesión se cierra sola a las 12 horas.

Para prenderlo, cuando Gambos diga que sí:
1. En Render: New > Blueprint, este repositorio, Blueprint path `bot-restaurante/render-gambos.yaml`. Llenar las claves de Meta (README del bot, sección 3) y `ANTHROPIC_API_KEY`.
2. Copiar `DATA_KEY` y `PANEL_SECRET` (Render > Environment) al gestor de contraseñas.
3. En Render > Shell: `npm run usuario -- agregar correo-de-la-duena "Nombre" 504XXXXXXXX` (su WhatsApp, para el código).
4. En WhatsApp Manager crear la plantilla de Autenticación `codigo_panel` y ponerla en `META_PLANTILLA_CODIGO`.
5. Entrar a `https://gambos-bot.onrender.com/panel` desde su celular y revisar Seguridad.

Capturas: `panel-real/oficial-*.png`.

## Cartas para Gambos (`kit/`)

- `kit/pdf/carta-de-presentacion.pdf`: quiénes somos, lo que vimos, lo que hacemos, precio (L15,000 + L2,500) y siguiente paso.
- `kit/pdf/lo-que-necesitamos.pdf`: la lista para prender el bot (documentos de Meta, menú, cupos y tandas, entrega, pagos, número, panel).
- `kit/pdf/bienvenida.pdf`: para cuando digan que sí.
- `kit/pdf/acuerdo-de-servicio.pdf`: el contrato. Instalación de L15,000 en un solo pago el día 30 (decisión de Rodrigo, 27-oct-2026) y L2,500 al mes desde el día 31. No lo ha revisado un abogado.

Se arman desde los `.md` de `kit/` con el generador del kit:
`CHROMIUM_PATH=/opt/pw-browsers/chromium node kit-cliente/generar.mjs --restaurante "Gambos" --numero "8932-4789" --instalacion "L15,000" --mensual "L2,500" --fuentes gambos/kit --solo carta-de-presentacion,lo-que-necesitamos,bienvenida,acuerdo-de-servicio --salida gambos/kit/pdf`
