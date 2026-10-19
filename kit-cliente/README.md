# Kit del cliente · Casa Digital

Todo lo que recibe y lo que nos tiene que dar un restaurante cuando dice que sí. Sirve para cualquier restaurante: el generador llena el nombre, el dueño, los precios y el número del bot.

## Qué tiene el kit

| # | Documento | Para quién | Cuándo se manda |
|---|---|---|---|
| 1 | [Bienvenida](1-bienvenida.md) | Dueño | Cuando dice que sí |
| 2 | [Lo que necesitamos](2-lo-que-necesitamos.md) | Dueño | Cuando dice que sí |
| 3 | [Acuerdo de servicio](3-acuerdo-de-servicio.md) | Dueño (se firma) | Día 30, si sigue |
| 4 | [Guía del panel](4-guia-del-dueno.md) | Dueño y gerentes | Después de la capacitación |
| 5 | [Hoja del personal](5-hoja-del-personal.md) | Cocina y caja | Después de la capacitación |
| 6 | Cartel con QR del WhatsApp | Mostrador | Después de la capacitación |
| – | [Mensajes listos y promoción](6-mensajes-y-promocion.md) | Rodrigo (para copiar) | En cada paso |

Ejemplo ya armado con el restaurante de ejemplo, para ver cómo quedan: [ejemplo/](ejemplo/) ([bienvenida](ejemplo/bienvenida.pdf), [lista](ejemplo/lo-que-necesitamos.pdf), [acuerdo](ejemplo/acuerdo-de-servicio.pdf), [guía](ejemplo/guia-del-panel.pdf), [hoja del personal](ejemplo/hoja-del-personal.pdf), [cartel](ejemplo/cartel-whatsapp.pdf)).

## Del sí al día 30 (lo que hace Rodrigo)

1. **Día 0, dice que sí.** Mandar el mensaje "Cuando dice que sí" con la bienvenida y la lista. Pedirle a Claude el kit con su nombre y su número (o correr el generador).
2. **Día 1 y 2, recibir la lista y conectar.** Llenar `bot-restaurante/negocios/<cliente>.json` solo con lo que el cliente confirmó. Videollamada de conexión según [INSTALACION-A-DISTANCIA.md](../INSTALACION-A-DISTANCIA.md), pasos 1 a 3.
3. **Día 3, capacitación.** Videollamada de 30 minutos, grabarla. Mandar la guía, la hoja del personal y el cartel, y los textos de promoción para sus redes.
4. **Primera semana.** Revisar todos los días las conversaciones y corregir respuestas.
5. **Día 23.** Mensaje para cuadrar la reunión del día 30.
6. **Día 30.** Reunión con los números del panel. Si sigue: acuerdo firmado (con sus dos casillas marcadas) + link de Stripe por la primera mitad de la instalación + suscripción de la mensualidad. Si no: apagar el bot, ofrecerle sus pedidos en Excel y salir de su Meta Business.
7. **Día 60.** Segunda mitad de la instalación.

## Decisiones que tomé al armarlo

- **Pagos:** nada en los primeros 30 días. Si sigue, la instalación se paga en dos mitades (día 30 y día 60) y la mensualidad empieza el día 31, por Stripe con tarjeta y cobro automático. Los precios no van fijos en los documentos: se pasan al generador para cada cliente (referencia de Coco Chicken: L32,000 + L3,500 al mes).
- **Soporte:** lunes a sábado, de 8 a. m. a 8 p. m. hora de Honduras, y a cualquier hora si el bot se cae. Cambialo en la bienvenida y en el acuerdo si querés otro horario.
- **Lo que se promete:** solo lo que el bot de [bot-restaurante/](../bot-restaurante/README.md) ya hace (menú, pedidos para recoger, sucursales, domicilio por apps, paso a persona, avisos, panel y cocina). Caja, inventario, proveedores, lealtad y ventas por video van como "se agregan después", porque hoy solo están en los paneles de demostración.
- **Facturas:** recibo de Clientia Tech; la factura con CAI se coordina aparte, porque necesita RTN y contador en Honduras.
- **El acuerdo** es una plantilla sencilla, no la revisó un abogado.

## Generar el kit de un cliente

```bash
cd kit-cliente && npm install && cd ..
node kit-cliente/generar.mjs --restaurante "Nombre exacto" --dueno "Nombre del dueño" \
  --numero "9999-9999" --instalacion "L32,000" --mensual "L3,500" --inicio "20 de octubre de 2026"
```

El diseño sigue la página de Clientia Tech: portada azul marino, Hanken Grotesk, tarjetas y mucho aire. Los `.md` llevan comentarios como `<!-- tarjetas -->` o `<!-- banda: 30 | días gratis -->` que GitHub no muestra y que el generador usa para dibujar cada bloque; la lista completa está al principio de `generar.mjs`.

Solo `--restaurante` es obligatorio. Sin `--numero` el cartel sale como borrador, con el QR marcado como pendiente. Los PDF quedan en `kit-cliente/pdf/<restaurante>/`, que no se sube a GitHub porque lleva datos del cliente. Para cambiar el texto, se edita el `.md` y se vuelve a generar.

## Registro de aceptaciones

Cada vez que un negocio acepta el acuerdo, se apunta una fila en una copia privada de [registro-de-aceptaciones.csv](registro-de-aceptaciones.csv) (fuera de este repositorio, porque es público): fecha y hora, negocio, persona, cómo aceptó (firma a mano, firma electrónica, Stripe o WhatsApp), las dos casillas por separado, la versión (fecha) de los términos y de la privacidad, y dónde está guardada la prueba (PDF firmado, pago de Stripe, captura del chat). En el link de pago de Stripe, activar "Exigir aceptación de los términos de servicio" con el enlace a clientiatech.com/terminos.html: Stripe guarda cuándo se marcó. Se guarda durante el servicio y cinco años después. Lo explica [clientiatech.com/legal.html](https://clientiatech.com/legal.html#registro).
