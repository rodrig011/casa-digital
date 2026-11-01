# Campaña de venta: registro y revisión

Actualizado el 1 de noviembre de 2026.

## Cómo va (contando negocios, no mensajes)

| | Negocios |
|---|---|
| Contactados (WhatsApp) | 15 |
| Contactados (correo) | 0 (el primer envío de Harvey es el lunes 2-nov) |
| Rebotes | 0 |
| Respondió una persona | 4 (Coco Chicken, Gambos, Libby's Cajun, Carnes El Argentino) |
| Respuestas automáticas | 0 registradas |
| Mostraron interés | 3 (Coco Chicken, Gambos, Libby's Cajun) |
| Llamadas o demos en vivo | 0 (a 3 se les mandó video y panel demo; no hubo llamada) |
| Pruebas activas | 0 |
| Pagos | 0 |

Hoy: Gambos rechazó; Coco Chicken y Libby's Cajun dejaron de responder. Carnes El Argentino contestó ("hable amigo") el 26-oct y no hay registro de que se le haya mandado la presentación.

## Archivos

- `registro-campana.csv`: una fila por negocio contactado, con lo que pasó.
- `revision-contactos-2026-11-01.csv`: los 87 correos de Harvey (83 en cola y 4 inválidos), revisados uno por uno.

## Reglas para contar

- **Un negocio es una fila**, aunque se le manden tres correos o se le escriba por WhatsApp y por correo.
- **Respuesta automática no es respuesta.** "Gracias por escribirnos", "fuera de la oficina", el saludo automático de WhatsApp Business o el asistente de Meta van en `respuesta_automatica`, no en `respondio_persona`.
- **Interesado** = una persona pregunta el precio, pide más información, propone hablar o pide la prueba.
- **Prueba activa** = el dueño ya conoce por escrito el precio de después y lo que incluye, aceptó, y el bot está conectado a su número. Antes de eso no cuenta.
- **Pago** = dinero recibido en la cuenta, no una promesa.
- Un "no" o un "no me escriban" se anota y se respeta para siempre: ese negocio no vuelve a recibir nada por ningún canal.

## Revisión de los 83 contactos de Harvey (1-nov)

Cómo se revisó: para cada correo se comprobó que su dominio recibe correo (registro MX) y se abrió la página del negocio para ver si el correo aparece ahí. **Verificado** quiere decir que el correo aparece en la página del propio negocio hoy. Que salga en un directorio (Cámara de Comercio de Guatemala, ARES de El Salvador, Facebook) no lo hace verificado. Ningún buzón se comprobó enviando un correo.

| Estado | Cuántos | Qué hacer |
|---|---|---|
| ok (verificado en su página) | 17 | Se pueden aprobar. |
| sin verificar | 53 | El dominio recibe correo, pero el correo sale de un directorio o de Facebook. Pueden rebotar. |
| revisar | 4 | Su página muestra otro correo (Clavo y Canela, Panadería Los Andes, Hotel Marina Copán) o la frase "vi en su página" no está comprobada (El Adobe). |
| dudoso | 8 | Buzón de Recursos Humanos, franquicias, quejas o atención al cliente, o correo que no se parece al negocio. |
| duplicado | 1 | Cholucarnes ya recibió WhatsApp el 28-oct. |
| no enviar | 4 | Dominio inexistente o sin correo (ya marcados inválidos por Harvey). |

**De los 5 aprobados para el lunes, solo Castor's Pizza está verificado en su página.** El Adobe y Clavo y Canela están en "revisar"; La Pampa y Restaurantes Acajutla salen solo del directorio ARES.

No hay rechazos ni bajas registradas en la lista de correo (todavía no se ha enviado nada). Gambos, Libby's Cajun y Coco Chicken no están en la cola de Harvey. "Coco Baleadas" (Marcas Astrales) sí está, pero es otro negocio.
