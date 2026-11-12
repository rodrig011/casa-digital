# Con Sabor a Pueblo: poner el bot en vivo

Lista de lo que falta para pasar de la demo al WhatsApp real del negocio. Cada paso dice quién lo hace y cuánto cuesta.
Lo que ya está hecho y probado (43 pruebas): bot con IA, pedidos a cocina, apartados con tope, pago con comprobante,
repartidores con ubicación, panel del dueño con menú, equipo y configuración editables, respaldo cifrado.

## 1. Lo que el dueño tiene que confirmar (una llamada de 10 minutos)

| Dato | Por qué | Dónde se pone |
|---|---|---|
| Precio del cerdito en Tegucigalpa y si ahí venden algo más | El bot cobra lo que dice el menú | El dueño en el panel, Menú |
| Si el tope de 50 apartados es por ciudad o entre las dos | Hoy está 50 en cada ciudad | El dueño en el panel, Configuración |
| Cuenta para los depósitos | Ya la tenemos (BAC). Que confirme que es esa | Archivo privado, nunca en el repositorio |
| El WhatsApp que va a usar el bot | Ver el paso 3 | Meta |
| Nombre y WhatsApp de cada repartidor y su ciudad | Para mandarles los envíos | El dueño en el panel, Repartidores |
| Cuántas libras de pierna caben y dónde se entrega el 24 | Encargo de Navidad | Archivo del negocio |

## 2. Servidor (Render)

- La demo vive en el plan gratis de Render. **Para un cliente real no sirve**: el plan gratis se duerme y no guarda archivos, así que los pedidos y la configuración del panel se perderían al reiniciar.
- Hace falta el plan Starter con un disco de 1 GB: unos **$7.25 al mes**. Sale de la mensualidad del cliente (L2,500).
- El disco va en `DATA_DIR=/var/data`, con `DATA_KEY` puesta para que todo quede cifrado.
- Respaldo: `node respaldo.js bajar https://<bot>.onrender.com` una vez por semana. Ya incluye menú, repartidores y configuración.

## 3. WhatsApp (Meta)

- Rodrigo no fue aprobado como desarrollador en Meta. Opciones, en orden:
  1. Que **Dylan** cree la cuenta de desarrollador y la app (developers.facebook.com, con su Facebook). Es socio y dueño de Clientia Tech.
  2. Que Rodrigo lo vuelva a intentar verificando su teléfono y su identidad en la cuenta de Facebook.
- El negocio da de alta su número en **su propio** Meta Business (el número es de ellos, no de Clientia Tech). Nosotros quedamos como socios con acceso.
- Ojo con el número: si se pasa entero a la API, deja de funcionar en la app de WhatsApp Business del celular. Meta tiene una forma de usar el mismo número en la app y en la API ("coexistencia"); se confirma en la pantalla de registro antes de pasar el número. Si no se puede, conviene un número nuevo solo para pedidos.
- Costo: contestar a un cliente que escribió primero es gratis dentro de las 24 horas. Los avisos a repartidores o al dueño fuera de esa ventana usan plantillas que Meta cobra por mensaje (centavos de dólar).

## 4. Claude (la IA)

- Clave de la API en console.anthropic.com, solo en Render (`ANTHROPIC_API_KEY`), nunca en el chat.
- Modelo Haiku con caché y un tope diario por número: unos **$10 a $15 al mes** con el volumen de un negocio así. Si la IA falla, contesta el menú.

## 5. Prueba antes de prenderlo

Seguir `bot-restaurante/PRUEBA-REAL.md` con el número de prueba de Meta y celulares nuestros, nunca con el del negocio.
Agregar a la prueba: el dueño pausa los pedidos en Configuración y el bot lo dice; baja el máximo de apartados y el bot ofrece otro día.

## 6. El día que se prende

1. El dueño entra al panel con su correo y contraseña (se crean con `npm run usuario`), revisa Menú y Configuración.
2. Se pone en pausa hasta el viernes en la noche y se abre para los apartados del sábado.
3. El sábado Rodrigo o Dylan miran el panel en vivo y contestan lo que el bot pase a una persona.

## Costo mensual por cliente (estimado)

| Qué | Costo |
|---|---|
| Render Starter + disco | ~$7.25 |
| Claude (Haiku) | ~$10 a $15 |
| WhatsApp (Meta) | casi $0 si los clientes escriben primero |
| **Total** | **~$20 a $25 al mes** frente a L2,500 que paga el cliente |
