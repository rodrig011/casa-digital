# Plan de 90 días para consolidar Clientia Tech

Del 17 de noviembre de 2026 al 14 de febrero de 2027. Escrito para seguirlo solo, sin ayuda de nadie.

## Dónde estamos hoy, sin adornos

- 0 clientes pagando y 0 pruebas activas.
- Dos tratos vivos: **Con Sabor a Pueblo** (el dueño llamó, probó el bot y ya se le arregló lo que pidió) y **Loca Luna** (don Miguel Majano tiene la propuesta del plan Cadena y está haciendo preguntas).
- El bot nunca se ha probado con WhatsApp y Claude de verdad, solo simulados.
- La empresa no está registrada y el acuerdo de servicio no lo ha visto un abogado.
- De 16 negocios contactados por WhatsApp contestaron 5. Todavía hay negocios de Honduras en la lista sin escribirles.

## Qué significa consolidarnos

Tres cosas, en este orden. Lo demás espera.

1. **Un cliente en vivo y pagando.** Sin eso no hay empresa, hay un proyecto.
2. **Poder cobrar en regla.** Acuerdo revisado, empresa registrada, cuenta donde cae la plata, y Rodrigo y Dylan con lo suyo por escrito.
3. **Que el segundo cliente cueste la mitad del trabajo.** Una lista de instalación probada, un caso real que enseñar y referidos.

Crecer a Guatemala y El Salvador viene después de esto, no antes.

## Quién hace qué

- **Rodrigo:** vende, instala y atiende al dueño.
- **Dylan:** abogado, contador, cuenta del banco, cobros y el registro de la empresa.
- **Los dos:** 30 minutos cada viernes para ver los números de abajo.

## Semana 1 (17 al 22 de noviembre): destrabar la instalación

1. **Montar hoy el panel real de Con Sabor a Pueblo en Render.** Es la sección "Atajo" de [PUESTA-EN-MARCHA.md](con-sabor-a-pueblo/PUESTA-EN-MARCHA.md), son 20 minutos y no necesita a Meta.
2. **Resolver lo de Meta con fecha límite.** Probar desde el celular y con otro navegador. Si el miércoles 18 sigue bloqueado, abrir la cuenta de desarrollador con el Facebook de Dylan. Si el viernes 20 tampoco, se arranca con Twilio y se cambia a Meta después. No se pasa otra semana esperando.
3. **Hacer la prueba real** de [PRUEBA-REAL.md](bot-restaurante/PRUEBA-REAL.md) con el número de prueba, paso por paso, anotando lo que falle.
4. **Contestarle a don Miguel el mismo día** cada pregunta, corto y con lo que el bot hace hoy. Proponerle una llamada de 20 minutos y arrancar el mes gratis en una sola sucursal, la que él escoja. El precio del plan Cadena no se toca.
5. **Ventas, 30 minutos diarios:** los mensajes de Navidad a los negocios de carne y encargos (10 por día, hasta el 22), los seguimientos pendientes en la [página de WhatsApp](https://claude.ai/artifact/SUV15bH8BrWtgiokUBPc59), y contestarle a Carnes El Argentino.
6. **Cambiar la contraseña del correo** de clientiatech.com, que quedó pegada en un chat.

**Listo cuando:** el panel real abre en Render, la prueba real pasó completa (o hay lista de fallas), y don Miguel tiene todas sus respuestas.

## Semana 2 (23 al 29 de noviembre): primer cliente en vivo

1. **Videollamada de 45 minutos con el dueño de Con Sabor a Pueblo** (parte 4 de la guía). Ahí se le repite el precio y lo que incluye, antes de empezar el mes gratis: L15,000 de instalación en dos mitades y L2,500 al mes.
2. **Mandarle el kit y que acepte el acuerdo por escrito** (un "acepto" por WhatsApp sirve). Anotarlo en `kit-cliente/registro-de-aceptaciones.csv`.
3. **Conectar su número** (parte 5 de la guía) y **estar pendiente del WhatsApp todo el sábado 28**, que es su día de venta.
4. **Dylan:** conseguir un abogado en Honduras y mandarle [el acuerdo de servicio](kit-cliente/3-acuerdo-de-servicio.md). Tiene que estar revisado antes del primer cobro, que cae a finales de diciembre.
5. **Navidad:** si para el miércoles 25 nadie dijo que sí, se guarda la oferta hasta Semana Santa y no se le mete más tiempo.

**Listo cuando:** entró por lo menos un pedido de un cliente de verdad por el bot y le llegó al dueño.

Si la instalación se atrasa una semana, todo lo de abajo se corre una semana. No se salta ningún paso.

## Semanas 3 y 4 (30 de noviembre al 13 de diciembre): que funcione de verdad

1. **Cada sábado en la noche anotar:** cuántos pedidos entraron por el bot, cuántos tuvo que arreglar el dueño a mano, qué falló y qué preguntó la gente que el bot no supo.
2. **Arreglar solo fallas.** Si el dueño pide algo nuevo, se apunta y se le dice cuándo. Nada de funciones nuevas por iniciativa nuestra.
3. **Escribirle al dueño cada lunes:** "¿cómo le fue el sábado?". Que sienta que hay alguien detrás.
4. **Loca Luna:** llegar a un sí o a un no claro. Si es sí, instalar la primera sucursal con la misma guía.
5. **Sacar la lista de instalación.** Copiar la guía de Con Sabor a Pueblo a `kit-cliente/INSTALACION.md` quitando lo que es solo de ellos y agregando lo que salió mal. Eso es lo que hace repetible el negocio.
6. **Ventas:** 10 mensajes nuevos por día de lunes a viernes con [MENSAJES-LISTOS.md](vender/MENSAJES-LISTOS.md), y seguimiento al día 3 y al día 7 a cada uno. Todo anotado en `campana/registro-campana.csv`.

**Listo cuando:** dos sábados seguidos sin que Rodrigo tenga que meter mano, y existe la lista de instalación.

## Semanas 5 y 6 (14 al 27 de diciembre): cobrar y poner la casa en orden

1. **Una semana antes del día 30, hablar con el dueño:** enseñarle sus propios números del mes y preguntarle si sigue. No esperar a que venza.
2. **Cobrar.** La primera mitad de la instalación y la primera mensualidad, por enlace de Stripe o transferencia. Dylan lleva el control en una hoja: qué se cobró, cuándo y qué falta.
3. **Acuerdo entre Rodrigo y Dylan, por escrito y firmado.** Una página: qué porcentaje tiene cada uno, quién hace qué, cómo se reparte lo que entra y qué pasa si uno se sale. Es gratis y evita el pleito más común entre socios.
4. **Registro de la empresa.** Preguntarle al abogado y a un contador, antes de registrar nada:
   - Una LLC de dos dueños en Estados Unidos declara impuestos distinto que una de un solo dueño. Que expliquen qué le toca presentar a cada uno.
   - Si Dylan está con visa de estudiante, qué puede y qué no puede hacer dentro de la empresa. Esto se pregunta, no se asume.
   - En Honduras: RTN y facturas con CAI en el SAR, y cuenta en lempiras para los clientes que no pagan con tarjeta.
5. **Revisar el costo real.** Con la primera factura de Render y de Claude, ver cuánto cuesta el cliente al mes. El cálculo de L650 a L900 es estimado.

**Listo cuando:** entró el primer pago, hay acuerdo de socios firmado y hay fecha para registrar la empresa.

Si el dueño dice que no sigue, preguntarle por qué y apuntarlo tal cual. Esa respuesta vale más que cualquier idea nuestra, y con ella se corrige la oferta antes de seguir vendiendo.

## Semanas 7 a 9 (28 de diciembre al 17 de enero): el caso y los referidos

1. **Escribir el caso de Con Sabor a Pueblo en una página**, con permiso del dueño y solo con sus números reales: pedidos por sábado, qué cambió para él, y una frase suya si la quiere dar. Sin inflar nada.
2. **Pedirle referidos:** "¿conoce a otro dueño al que le serviría?". Por cada negocio que se quede, un mes gratis para él.
3. **Cambiar el primer mensaje** de la lista para mencionar el caso: un negocio hondureño con nombre que ya lo usa pesa más que cualquier video.
4. **Cobrar la segunda mitad** de la instalación en el día 60.
5. **Seguir con los 10 mensajes diarios.** Cuando se acabe la lista de Honduras, buscar más negocios del mismo tipo que el cliente que sí compró.

**Listo cuando:** el caso está publicado en clientiatech.com y se pidieron referidos.

## Semanas 10 a 13 (18 de enero al 14 de febrero): repetir

1. **Instalar al segundo y al tercer cliente** con la lista de instalación, midiendo las horas que toma cada uno. Si el tercero no toma menos que el primero, se arregla la lista antes de vender más.
2. **Registrar la empresa** como dijeron el abogado y el contador, y pasar Stripe y la cuenta del banco a nombre de la empresa.
3. **Revisar precios con datos:** cuánto cuesta atender a cada cliente en plata y en horas. Se baja la instalación si hace falta, nunca la mensualidad.
4. **Decidir lo de Guatemala y El Salvador.** Solo si hay clientes pagando en Honduras y atenderlos no se come toda la semana. Si no, se espera otros 90 días.

**Listo cuando:** hay más de un cliente pagando, la empresa está registrada y hay una decisión escrita sobre expandirse.

## Cómo generar confianza

Un dueño que le va a pagar a dos estudiantes que viven fuera revisa estas cosas, más o menos en este orden. Para cada una: qué hay hoy y qué falta.

**1. "¿Quiénes son ustedes?"** Quiere ver una cara y un nombre, no una marca.
- Ya hay: la página [Quiénes somos](https://clientiatech.com/#quien) con Rodrigo y Dylan, el correo con dominio propio y la página de LinkedIn de la empresa.
- Hacer esta semana: perfil de WhatsApp Business completo (nombre Clientia Tech, logo, sitio, horario de atención y descripción de una línea), foto real de Rodrigo en su WhatsApp, y el LinkedIn personal de cada uno enlazado desde Quiénes somos.
- En la primera llamada, cámara encendida. Eso solo quita la mitad de la duda.

**2. "¿Esto sirve o es puro cuento?"** No cree en videos, cree en lo que prueba.
- Ya hay: el bot de demostración que puede probar desde su propio celular, y los 30 días gratis.
- Regla: que lo pruebe él antes de hablar de precio. Con Sabor a Pueblo avanzó cuando el dueño lo probó.
- Falta, y es lo que más pesa: un cliente hondureño con nombre que ya lo usa. Sale en las semanas 7 a 9.

**3. "¿Y si me dejan botado?"** Es el miedo más grande y casi nunca lo dicen.
- Ya hay: el [acuerdo de servicio](kit-cliente/3-acuerdo-de-servicio.md), que deja cancelar cuando quiera, el horario de soporte y los respaldos del bot.
- Decirlo antes de que pregunte: el número de WhatsApp es suyo y siempre lo va a ser, sus pedidos y clientes son suyos y se los entregamos si se va, y no paga nada el primer mes.
- Falta: el acuerdo revisado por abogado (semana 2) y cumplir el horario de soporte sin fallar. Un mensaje del dueño sin contestar en un sábado de venta borra todo lo demás.

**4. "¿Esta empresa existe?"**
- Ya hay: el sitio con términos, privacidad y reembolsos, y Stripe a nombre de Clientia Tech.
- Falta: la empresa registrada y poder dar factura (semanas 5 a 13). Mientras tanto se da recibo y se dice así, "recibo". No decir "factura" ni "empresa registrada" hasta que sea cierto.

**5. "¿Con quién hablo aquí en Honduras?"**
- Hoy el número es de Estados Unidos. No se esconde: "estudiamos en Estados Unidos, somos hondureños y atendemos en horario de Honduras".
- Falta: un número +504 para atender clientes. Se saca la próxima vez que uno de los dos esté en Honduras. Dylan, que es de allá, puede ser el contacto para cobros.

**6. "¿Qué pasa con los datos de mis clientes?"**
- Ya hay: [SEGURIDAD.md](SEGURIDAD.md) y la página de privacidad.
- Si pregunta, contestar en dos líneas sencillas: los datos van cifrados, solo él y su personal entran al panel con su usuario, y no se le venden ni se le pasan a nadie.

**7. Lo pequeño que se nota**
- Contestar el mismo día, siempre. Es lo que más distingue a una empresa seria de un muchacho con una idea.
- El mismo nombre, logo y firma en WhatsApp, correo, PDF y sitio. La firma del correo ya está hecha en `clientia-tech/firma/`: usarla siempre.
- Todo lo que se acuerde por llamada se manda después por escrito en un mensaje corto.
- Cumplir las fechas que uno mismo dio. Si no se va a llegar, avisar antes, no después.

**Qué decir cuando pregunten cuántos clientes tenemos.** La verdad, que además vende: "Estamos empezando y usted sería de los primeros. Por eso el primer mes es gratis y por eso lo atiendo yo personalmente." Un dueño perdona que seamos nuevos. No perdona que le mintamos.

**Lo que nunca se hace:** testimonios inventados, logos de negocios que no son clientes, "más de tantos clientes", certificaciones que no tenemos, ni fotos de oficina que no existe. En Honduras los dueños se conocen entre ellos y una mentira se sabe rápido.

## Los números de cada viernes

Rodrigo y Dylan los ven juntos. Si no están anotados, esa semana no cuenta.

| Qué | Dónde se anota |
|---|---|
| Mensajes nuevos enviados y seguimientos | `campana/registro-campana.csv` |
| Cuántos contestaron y cuántos preguntaron precio | `campana/registro-campana.csv` |
| Llamadas con dueños | `campana/registro-campana.csv` |
| Pruebas activas y clientes pagando | hoja de cobros de Dylan |
| Plata que entró y plata que salió | hoja de cobros de Dylan |
| Pedidos por el bot y fallas, por cliente | panel de cada cliente |

## Revisión del día 45 (31 de diciembre)

Si para esa fecha no hay ningún cliente en vivo, el problema ya no es el producto ni los mensajes. Se para todo y se llama por teléfono a los dueños que contestaron alguna vez, para preguntarles una sola cosa: qué les faltó para decir que sí. Con esas respuestas se rehace la oferta.

## Lo que no se hace en estos 90 días

- Paneles, videos, rediseños o funciones nuevas que ningún dueño pidió.
- Nada a la medida antes de que el dueño diga que sí.
- Prometer ventas o "más pedidos". Se promete lo que el bot hace.
- Empezar una prueba gratis sin que el dueño sepa el precio de después.
- Buscar prospectos nuevos mientras haya negocios sin contactar en la lista.
- Meterle horas a Harvey. Se deja como está, solo Honduras.

## Lo que ya existe (no rehacerlo)

| Para | Archivo |
|---|---|
| Precios y planes | [oferta/PLAN-DE-OFERTA.md](oferta/PLAN-DE-OFERTA.md) |
| Cómo vender y qué contestar | [vender/GUIA-DE-VENTA.md](vender/GUIA-DE-VENTA.md) |
| Mensajes listos por negocio | [vender/MENSAJES-LISTOS.md](vender/MENSAJES-LISTOS.md) |
| Instalar a Con Sabor a Pueblo | [con-sabor-a-pueblo/PUESTA-EN-MARCHA.md](con-sabor-a-pueblo/PUESTA-EN-MARCHA.md) |
| Prueba real del bot | [bot-restaurante/PRUEBA-REAL.md](bot-restaurante/PRUEBA-REAL.md) |
| Kit del cliente (bienvenida, acuerdo, guías) | [kit-cliente/](kit-cliente/) |
| Seguridad de cada cliente | [SEGURIDAD.md](SEGURIDAD.md) |
