# Plantillas de WhatsApp para Con Sabor a Pueblo

WhatsApp solo deja que el bot le escriba **primero** a alguien (al dueño, a un repartidor, a un cliente después de 24 horas) con una plantilla aprobada por Meta. Son dos, y se crean una sola vez.

**Dónde:** business.facebook.com > portafolio **Con Sabor a Pueblo HN** > WhatsApp Manager > **Administrar plantillas** > **Crear plantilla**.

Antes, en WhatsApp Manager > **Configuración de pago**, agregue la tarjeta de Clientia. Sin tarjeta, Meta no deja mandar las plantillas.

## 1. aviso_pedido (avisos de pedidos, repartidores y clientes)

| Campo | Qué poner |
|---|---|
| Categoría | **Utilidad** |
| Nombre | `aviso_pedido` |
| Idioma | **Español** |
| Encabezado | Ninguno |
| Cuerpo | `Actualización de un pedido en Con Sabor a Pueblo: {{1}}. Detalle: {{2}}. Responda a este mensaje si tiene alguna consulta.` |
| Ejemplo de {{1}} | `Nuevo pedido PED-1003` |
| Ejemplo de {{2}} | `1 Cerdito chuko · A domicilio · Total L 220` |
| Pie de página | `Conteste este mensaje si tiene dudas.` |
| Botones | Ninguno |

## 2. codigo_panel (código para entrar al panel)

| Campo | Qué poner |
|---|---|
| Categoría | **Autenticación** |
| Nombre | `codigo_panel` |
| Idioma | **Español** |
| Método de entrega del código | **Copiar código** |
| Texto del botón | `Copiar código` |
| Extras | Marque "Agregar recomendación de seguridad" y vencimiento en **5 minutos** |

## 3. Cuando Meta las apruebe (minutos u horas)

En Render > con-sabor-a-pueblo-bot > Environment:

- `META_PLANTILLA` = `aviso_pedido`
- `META_PLANTILLA_CODIGO` = `codigo_panel`

Save y **Manual Deploy**.

Si Meta rechaza `aviso_pedido`, casi siempre es porque el cuerpo termina en {{2}} (por eso lleva "Gracias." al final) o porque falta el ejemplo. Deje el texto tal como está arriba.

## 4. Botones aunque Ricardo no haya escrito en 24 h (opcional, recomendado)

Dentro de las 24 h los botones salen solos. Para que también salgan fuera de las 24 h, cree estas dos plantillas.
Son iguales a `aviso_pedido`, con la misma categoría Utilidad, el mismo idioma Español, el mismo cuerpo y los mismos ejemplos. La diferencia es que llevan botones de **respuesta rápida** (Quick reply):

| Nombre | Botones (Quick reply, en este orden) |
|---|---|
| `aviso_listo` | `Listo` · `Pendientes` |
| `aviso_pago` | `Pago recibido` |

Cuerpo: `Actualización de un pedido en Con Sabor a Pueblo: {{1}}. Detalle: {{2}}. Responda a este mensaje si tiene alguna consulta.`

Cuando Meta las apruebe, en Render > Environment:

- `META_PLANTILLA_LISTO` = `aviso_listo`
- `META_PLANTILLA_PAGO` = `aviso_pago`

Save y **Manual Deploy**. Cada botón le dice al bot qué pedido es, así que Ricardo solo toca.
