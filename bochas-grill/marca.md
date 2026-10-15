# Bocha's Grill · Propuesta de Casa Digital

*Casa Digital, una línea de Clientia Tech · Investigación del 15 de octubre de 2026 · Nada se ha enviado todavía*

**Video para celular:** [bochas-grill-casa-digital-vertical.mp4](bochas-grill-casa-digital-vertical.mp4) (vertical 1080×1920, 2:04, "Still Buggin"; el guion sigue el método de preguntas de [metodos-video.md](../../propuestas/metodos-video.md) y la edición es la de los videos verticales anteriores)
**Panel demo:** [bochas-grill-panel.html](bochas-grill-panel.html) (un solo archivo, funciona en compu y celular; capturas en `capturas-panel/`)

Todo lo que digo del negocio sale de su TikTok @bochasgrill (perfil, 13 videos, 214 comentarios) y del TikTok del dueño @bochas10. Detalle y fuentes en [redes/investigacion-redes.md](redes/investigacion-redes.md); comentarios copiados en [redes/tiktok-comentarios.md](redes/tiktok-comentarios.md). Lo inferido o de ejemplo está marcado.

## 1. Quiénes son

| | |
|---|---|
| Qué venden | Asados BBQ: Económicos de Costilla y de Carne, Chicharrones de Carne, parrilladas, con tajadas y "el aderezo de la casa" (lo venden también en bolsa con su marca) |
| Sucursales | 5: San Pedro Sula (Stibys y Calpules), El Progreso, Villanueva y Choloma |
| Dirección publicada | Solo la de Villanueva: Gasolinera Shell, carretera hacia San Manuel, frente a colonia Gracias a Dios |
| Canales | Restaurante, para llevar y Bip Bip (los Chicharrones de Carne son exclusivos de Bip Bip en SPS) |
| TikTok @bochasgrill | 21.8K seguidores · 254K me gusta. Sus videos más vistos: su historia (139K y 91.8K), Villanueva de fiesta (46.2K), Económicos L139 (35.9K) |
| El dueño | "Bocha", @bochas10 en TikTok (70K seguidores). Empezó con una mesa frente a su casa, tiene un máster en gestión de restaurantes en Barcelona y escribió: "mi emprendimiento que hoy en día va hacia una franquicia". Su nombre real no está confirmado |
| Sitio web propio | No encontré ninguno, solo Linktree |
| Contacto | Facebook "Bocha's Grill" muestra 8765-2205 y Bochasgrillhn@gmail.com (según búsqueda; no pude abrirlo para confirmar si ese número es WhatsApp) |

## 2. Lo que de verdad necesitan (sacado de sus propios comentarios)

Con cinco sucursales, el dueño ya no puede estar en todas. Lo que se le escapa aparece después en TikTok:

1. **Preguntas sin respuesta.** 7 personas preguntaron el precio y 6 la dirección o el horario; el negocio no contestó ninguna de precio ("pero cual es el precio", "DIRECCIÓN SPS POR FAVOR... Y HORARIO").
2. **Faltantes en una sucursal.** "Fui al local de Villanueva, y no tenian NI FRIJOLES, NI CARNE ASADA NI INCURTIDO!"
3. **Espera.** "ayer fui a Bonchas Choloma y me dijeron que debía esperar 50 minutos por la orden".
4. **El mismo plato en todas.** "hoy pedí y ni el aderezo me pusieron... en Choloma", "carne tan reseca y dura en la stibys", "Choloma no es asi".
5. **Promos que confunden.** "pues en la app no dice eso" (18 me gusta), "Esos L.139 ya con el envío?".
6. **Su meta: la franquicia.** 9 comentarios piden sucursal en otra ciudad (Siguatepeque 3, La Ceiba 2, Tegucigalpa, Comayagua, Puerto Cortés) y uno pregunta "tienen franquicias ??". Una franquicia solo funciona si cada local hace lo mismo sin que el dueño esté ahí.

## 3. La propuesta: preguntas primero, y cada respuesta es una herramienta

Siguiendo el método de rodrigo, no le vendemos "un sistema": le hacemos 4 preguntas y cada respuesta es una parte del servicio.

| Pregunta | Lo que resolvemos |
|---|---|
| ¿Cuántos le preguntan el precio y se quedan sin respuesta? | **Bot en su WhatsApp** (el de verdad, sin ventanita en una página y sin códigos): contesta precio, sucursal más cercana, horario y la promo vigente con sus condiciones; toma pedidos para recoger en la sucursal que el cliente diga; pasa al dueño lo que no sabe (por ejemplo, franquicias) |
| ¿Se enteró a tiempo de que Villanueva se quedó sin frijoles? | **Inventario por sucursal** con mínimo por insumo; cuando algo baja, el panel le escribe solo al proveedor y sugiere traslado desde otra sucursal |
| ¿Sabe cuánto espera hoy un cliente en Choloma? | **Pedidos y pantalla de cocina por sucursal**, cada pedido con su reloj; la sucursal que pasa de 25 minutos se pone en rojo y el bot avisa a los clientes que esperan |
| ¿Sus cinco sucursales sirven el mismo plato? | **Encuesta después de cada pedido** por WhatsApp ("¿Cómo estuvo?") con quejas por sucursal (aderezo, tajadas, carne, espera, atención) y la **ficha del plato** igual en las cinco cocinas |

Además el panel tiene **Promos** (canal, sucursal y fechas; el bot deja de ofrecerlas cuando terminan) y **Crecimiento** (dónde le piden sucursal, contado de sus comentarios, y qué sucursal ya está lista para copiarse como franquicia).

**Panel Bocha's Grill** (estilo CRM, con login para las personas que ellos autoricen): Inicio con las 5 sucursales lado a lado y acciones de un clic · WhatsApp · Pedidos · Calidad · Inventario · Promos · Crecimiento. Ventas, tiempos, calificaciones e inventario del demo son de ejemplo y lo dice en pantalla. El bot se construye sobre el que ya hicimos para Steel Works (`casa-digital/steelworks/bot/`).

**Lo que no hacemos:** tocar sus videos (ya funcionan), sacarlos de Bip Bip, ni hacer cuentas de comisiones.

## 4. Precio de referencia (por validar)

**L45,000 de instalación (en 2 pagos) + L5,500/mes**, para las 5 sucursales: bot en su WhatsApp, panel con login, inventario y encuesta por sucursal, configuración, capacitación en cada local y soporte. Es mi estimado escalando lo de Coco Chicken (3 sucursales, L32,000 + L3,500); no hay tarifas publicadas de agencias en Honduras para comparar.

**Aparte los paga el restaurante:** los mensajes de WhatsApp (Twilio/Meta) y la IA del bot (~US$0.40 por 100 conversaciones).

## 5. El video (guion de preguntas, edición de antes)

Fondo negro con luces suaves, frases completas que suben palabra por palabra con lo clave en dorado, y la prueba en tarjetas debajo. No abre con sus videos de TikTok. Lo de ejemplo dice "Ejemplo".

1. **Apertura:** Casa Digital, "una propuesta para", su logo y Bocha's Grill.
2. **Lo que no hay que hacer:** "Podríamos empezar así: con lo que hace el sistema." La frase "“Le instalamos el mejor sistema para restaurantes del mundo.”" se tacha. "Pero así no se vende."
3. **"Primero, unas preguntas."** Sobre sus cinco sucursales; que las conteste él.
4. **Pregunta 1 a 4**, cada una con su prueba real: los comentarios que preguntan el precio sin respuesta; la foto de su local de Villanueva con "no tenian NI FRIJOLES"; la espera de 50 minutos en Choloma; la foto de su plato con el aderezo y "ni el aderezo me pusieron".
5. **Puente:** "Si alguna respuesta fue “no sé”, eso es lo que resolvemos."
6. **Respuesta 1 a 4**, en el mismo orden: su WhatsApp contesta solo la pregunta real de los L139 y toma un pedido para recoger en Calpules; el inventario de Villanueva le escribe al proveedor de frijoles; la espera de cada sucursal en vivo (Choloma en rojo, avisando a los clientes); la encuesta que avisa "Faltó el aderezo".
7. **Su meta:** su frase real de @bochas10 sobre la franquicia. "Una franquicia funciona cuando cada local hace lo mismo."
8. **Cierre:** el panel en el celular. "No vendemos un sistema. Primero preguntamos, y resolvemos lo que Bocha's Grill necesita." Luego "Escríbanos y le mostramos exactamente cómo", +1 (765) 543-4251, y by Clientia Tech.

## 6. Contacto (borradores, nada enviado)

Mejor por mensaje directo al TikTok del dueño, @bochas10 (él contesta ahí), o al WhatsApp de su Facebook si se confirma.

**Primer mensaje:**

> Hola Bocha, buenas. Mi nombre es Rodrigo Herrera. Soy hondureño y estudio ingeniería en Estados Unidos, y quiero ayudar a los negocios de mi país con lo que he aprendido. Vi su video de cómo empezó y que Bocha's ya va hacia una franquicia. Le preparé un video corto con 4 preguntas sobre sus cinco sucursales. Si alguna la contesta con "no sé", ahí le puedo ayudar. ¿Se lo puedo mandar?

**Con el video:**

> Aquí está el video para Bocha's Grill. La idea es que usted sepa, desde su celular, qué pasa hoy en cada sucursal: quién preguntó y no le contestaron, qué se está acabando, cuánto espera la gente y si el plato salió como debe. Si le interesa, se lo muestro en 15 minutos con sus sucursales reales. ¿Le queda bien esta semana?

**Seguimiento a los 3 días:**

> Hola Bocha, soy Rodrigo, de Casa Digital. Solo quería saber si pudo ver el video que le hicimos a Bocha's Grill. Si prefiere, se lo explico en una llamada corta. Gracias.

Nuestro WhatsApp: **+1 (765) 543-4251**

## 7. Pendiente de confirmar

- Direcciones y horario de Stibys, Calpules, El Progreso y Choloma (están en su Linktree, que no se pudo abrir; en el panel dicen "Por confirmar").
- Si el 8765-2205 de su Facebook es WhatsApp, y si cada sucursal tiene su propio número.
- Precios actuales (solo están publicados los de las promos de septiembre) y precio de los Chicharrones de Carne.
- El nombre real del dueño (se presenta como "Bocha").
- Si venden también por PedidosYa (lo dice un cliente, no ellos).
