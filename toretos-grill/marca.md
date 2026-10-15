# Toreto's Grill · Propuesta de Casa Digital

*Casa Digital, una línea de Clientia Tech · Investigación del 15 de octubre de 2026 · Nada se ha enviado todavía*

**Video:** [toretos-grill-casa-digital.mp4](toretos-grill-casa-digital.mp4) (horizontal 1920×1080, 2:04, con "Still Buggin", cortes en los compases, cierra con el logo de Clientia Tech)
**Video para celular:** [toretos-grill-casa-digital-vertical.mp4](toretos-grill-casa-digital-vertical.mp4) (vertical 1080×1920, el mismo video acomodado para la pantalla del teléfono; es el que conviene mandar por WhatsApp)
**Panel demo:** [toretos-grill-panel.html](toretos-grill-panel.html) (un solo archivo, funciona en compu y celular; capturas en `capturas-panel/`)

Todo lo que digo del negocio sale de su TikTok @toretosgrills (perfil, 11 videos, 278 comentarios y 49 respuestas del propio negocio) y del video y la captura que mandó rodrigo. Detalle y fuentes en `redes/investigacion-redes.md` (en la carpeta del proyecto). Lo inferido o de ejemplo está marcado.

## 1. Quiénes son

| | |
|---|---|
| Qué venden | Asados (res, chuleta, costilla), almuerzos y cenas, pollo frito con tajadas, taquitos mexicanos |
| Dónde | San Pedro Sula, colonia La Ideal, 6 y 7 calle, 15 avenida, atrás de Megamall (un solo local; antes estaban cerca de la circunvalación) |
| Horario | Lunes a domingo, 11 am a 10:30 pm. Almuerzos de 11 am a 3 pm |
| Contacto | 9612-3466 (WhatsApp) para todo: pedidos, domicilio y reservas |
| Precios publicados | Almuerzo desde L80 (arroz, frijoles, ensalada y carne o pollo). Asados por L180. Pollo frito con tajadas: sus clientes citan L140 |
| Delivery | Propio. Ya no usan PedidosYa ("Ya no estamos con ellos, 9612-3466 pedidos directo con nuestro delivery") |
| Quién sale en los videos | "El Colocho": así lo llaman sus propios videos ("Regresó el COLOCHO 🧑🏻‍🦲", "Ya le creció el pelo al colocho") y los clientes. Sale en todos. Que sea el dueño no está confirmado. Etiquetan a @Farem Cartagena y @jeimi Gonzales (inferido: dueños o equipo) |
| TikTok @toretosgrills | 5,652 seguidores · 55K me gusta · 290 videos. Fijados: 176.8K, 100.2K y 84.7K vistas |
| Instagram / Facebook | @toretosgrillhn / "Toreto's Grill HN" (no se pudieron abrir desde el servidor) |
| Sitio web propio | No encontré ninguno |
| Eventos | "Toreto's Grill Car Meet", sábado 19 de septiembre, con reservas por WhatsApp |

## 2. Lo que de verdad necesitan (sacado de sus propios comentarios)

1. **Nadie puede contestar todo.** Contestan a mano, uno por uno: en los comentarios escribió la misma dirección a mano 10 veces. Y aun así un cliente se quejó: **"No contestan whats"**. Su respuesta: "Pida 9612-3466 yo le contesto". Todo entra por un solo número: pedidos, domicilio, reservas, preguntas de menú y de factura.
2. **El domicilio es suyo.** Dejaron PedidosYa y llevan los pedidos con su propio motorista. Eso significa tomar el pedido, pasarlo a cocina, mandar al motorista, cobrar y cuadrar el efectivo, todo a mano.
3. **Le piden factura con RTN** ("Dan factura con rtn ?", sin respuesta) y vienen grupos de trabajo ("ahí te llego con todos los compañeros de la chamba").
4. **Tienen una meta clara:** "cuando vendamos 1000 almuerzos diarios en sps nos vamos a tegus".

## 3. La propuesta: su WhatsApp que contesta solo + el panel del dueño

**a) Bot en su WhatsApp 9612-3466** (el de verdad, no una ventanita en una página):
- Contesta al instante dirección (con el pin del mapa), horario, menú del día y precios.
- Toma el pedido a domicilio o para recoger, con la dirección, y lo manda a la cocina. Avisa al cliente cuando sale el motorista.
- Pide el RTN cuando quieren factura.
- Toma reservas; los grupos grandes se los pasa al encargado con un aviso al celular.
- Sin códigos de producto en la conversación; habla como ellos.
- Se construye sobre el bot que ya hicimos para Steel Works (`casa-digital/steelworks/bot/`).

**b) Panel Toreto's Grill** (estilo CRM, con login para las personas que ellos autoricen):
1. **Inicio:** ventas de hoy, almuerzos vendidos, WhatsApp sin contestar (0) y domicilios en camino. Acciones de un clic ("la carne no llega a la cena → escribirle a la carnicería", "pedido lleva 32 min en camino → avisarle al cliente"). Medidor de su meta de 1,000 almuerzos al día.
2. **WhatsApp:** cada conversación, si la contestó el bot o pasó al dueño, y lo que el bot sabe (dirección, horario, menú de hoy, costo de envío), editable.
3. **Pedidos y motoristas:** tablero Nuevo → En cocina → En camino → Entregado y pantalla de cocina. Cada entrega queda anotada con lo que cobró el motorista; al volver, el efectivo se cuadra con un clic.
4. **Inventario y proveedores:** carne, chuleta, costilla, pollo, chorizo, carbón, gas, plátano, lechuga, arroz, frijoles, tortillas. Cuando algo baja del mínimo, el bot le escribe solo al proveedor.
5. **Facturas:** con RTN, ISV 15%, se mandan por WhatsApp. Demo sin valor fiscal; las reales necesitan el CAI del SAR.
6. **Reservas y eventos:** grupos, cumpleaños y eventos como el Car Meet.
7. **TikTok:** cuánto vendió cada video con un código ("diga COLOCHO80 al pedir"). Vistas reales; pedidos de ejemplo.

**Lo que no hacemos:** tocar sus videos (ya funcionan), inventar fotos ni volver a meterlos a una app de delivery.

## 4. Precio de referencia (por validar)

**L24,000 de instalación (en 2 pagos) + L2,800/mes**, todo incluido: el bot en su WhatsApp, el panel con login, la configuración, la capacitación y el soporte. Es mi estimado para un solo local (a Coco Chicken, con 3 sucursales, le pusimos L32,000 + L3,500); no hay tarifas publicadas de agencias en Honduras para comparar.

**Aparte los paga el restaurante:** los mensajes de WhatsApp (Twilio/Meta) y la IA del bot (~US$0.40 por 100 conversaciones).

## 5. El video

Escenas: intro con su logo → "El Colocho ya tiene a la gente" con su video fijado (el que mandó rodrigo) → 4 comentarios reales ("donde estan ubicados?", "y pa domicilio", "Dan factura con rtn ?", "No contestan whats") y "Y él contesta uno por uno" → "Su WhatsApp, que contesta solo" → conversación en un iPhone (dirección, horario y almuerzo de L80 reales; pedido a domicilio de ejemplo) → teléfono, cocina y panel conectados, con el aviso "su pedido va en camino con el motorista" → el panel real → "Cero clientes sin respuesta" → sus motoristas con el efectivo de cada uno cuadrado (ejemplo) → el carbón se acaba y el proveedor ya sabe → su meta de 1,000 almuerzos al día, con su frase real → Casa Digital → by Clientia Tech. Lo de ejemplo está marcado en pantalla.

## 6. Contacto (borradores, nada enviado)

Mejor por mensaje directo en TikTok (él mismo contesta ahí) o por WhatsApp al 9612-3466.

**Primer mensaje:**

> Hola, buenas. Mi nombre es Rodrigo Herrera. Soy hondureño y estudio ingeniería en Estados Unidos, y quiero ayudar a los negocios de mi país con lo que he aprendido. Vi sus videos del almuerzo de 80 lempiras y vi que ustedes mismos le contesta a cada persona que pregunta dónde están o si llevan a domicilio. Les preparé un video corto con una idea: que su WhatsApp conteste y tome los pedidos solo, y un panel donde usted vea pedidos, motoristas, inventario y facturas. ¿Se lo puedo mandar?

**Con el video:**

> Aquí está el video para Toreto's Grill. La idea es que ningún cliente se quede sin respuesta mientras usted está en la parrilla, y que cada motorista vuelva con las cuentas claras. Si le interesa, se lo muestro en 15 minutos con su menú real. ¿Le queda bien esta semana?

**Seguimiento a los 3 días:**

> Hola, soy Rodrigo, de Casa Digital. Solo quería saber si pudo ver el video que le hicimos a Toreto's Grill. Si prefiere, se lo explico en una llamada corta. Gracias.

Nuestro WhatsApp: **+1 (765) 543-4251**

## 7. Pendiente de confirmar

- Precio exacto del pollo frito con tajadas, los asados y los taquitos (solo están publicados el almuerzo de L80 y el asado de L180).
- Costo del envío a domicilio (un cliente dice L150; no lo confirmó el negocio) y cuántos motoristas tienen.
- Quién es el dueño (el que sale en los videos es "el Colocho", pero no dice que sea el dueño; etiquetan a Farem Cartagena, inferido).
- Si tienen RTN y CAI para facturar.
- Instagram y Facebook (no se pudieron abrir desde el servidor; si rodrigo manda capturas, se agregan).
