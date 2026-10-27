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

Precio si lo piden: instalación entre L15,000 y L20,000 y mensualidad desde L2,500, sin comisión; 30 días gratis; la instalación se paga en dos partes, día 30 y día 60.
