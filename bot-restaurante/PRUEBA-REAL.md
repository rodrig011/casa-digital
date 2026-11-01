# Prueba real del bot (WhatsApp y Claude de verdad)

Hasta el 1-nov-2026 el bot solo se ha probado con WhatsApp y Claude simulados (`npm test`, 32 pruebas). Esta es la prueba con servicios reales. **Nunca con el número de un negocio**: se usa el número de prueba que Meta regala.

## Lo que hace falta

| Qué | Quién | Costo |
|---|---|---|
| Cuenta de desarrollador de Meta y una app de WhatsApp (developers.facebook.com, con el Facebook de Rodrigo). Meta da un **número de prueba** gratis que puede escribir a hasta 5 teléfonos registrados. | Rodrigo (10 min) | Gratis |
| Su celular agregado como destinatario de prueba (Meta manda un código). Ese celular hace de cliente, y un segundo celular (por ejemplo el de Dylan) de dueño/sucursal. | Rodrigo | Gratis |
| Clave de la API de Claude (console.anthropic.com) con crédito. | Rodrigo | Compra mínima de crédito (unos $5). La prueba entera gasta centavos con Haiku. |
| Una dirección https pública para el webhook: la PC de Rodrigo con un túnel gratis de Cloudflare (`cloudflared tunnel --url http://localhost:3000`), o Render. | Claude, en la PC de Rodrigo | Gratis |

Las claves las escribe Rodrigo en `.env` en su PC, nunca en el chat.

## Guion de la prueba (marcar cada paso)

1. El celular "cliente" escribe "hola" al número de prueba: contesta el menú o la IA.
2. Pide con sus palabras: "quiero 2 combos de 3 piezas para recoger en Zona Norte a las 7, a nombre de Ana".
3. Confirma: el bot da número de pedido y total; al "dueño" le llega el aviso con la sucursal correcta.
4. Manda "sí confirmo" otra vez: no se crea un segundo pedido.
5. Manda dos mensajes seguidos rápido: el bot contesta los dos en orden, sin olvidar el primero.
6. En el panel (`/panel`), el pedido aparece; la cocina lo pasa a "cocina" y luego a "listo": al cliente le llega "su pedido está listo".
7. Otro pedido: el cliente escribe "cancelar mi pedido": a la sucursal le llega el aviso con el número; el pedido no se cancela solo.
8. La sucursal lo cancela en el panel: al cliente le llega "canceló su pedido" una sola vez.
9. Se baja el respaldo (`node respaldo.js bajar ...`), se restaura en una carpeta nueva y el bot arranca con los mismos pedidos.
10. Se apaga la clave de Claude (`BOT_IA=off`) y se repite el paso 2: contesta el menú.

Lo que salga mal se anota aquí con la fecha y se corrige antes de instalar con un cliente.
