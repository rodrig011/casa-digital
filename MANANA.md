# Mañana, martes 17 de noviembre

Todo está para copiar y pegar. Cambie lo que no suene a usted. Va en orden de importancia: si solo alcanza para una cosa, que sea la primera.

Sale del [plan de 90 días](PLAN-90-DIAS.md), semana 1. Nada de aquí lo contradice.

---

## 1. Don Miguel, Loca Luna (lo primero del día)

Anoche el bot quedó con dos cosas que él preguntó: horario distinto por sucursal y saludar por su nombre al cliente que ya ha pedido antes. Ya se le puede decir que eso está hecho.

**Mensaje para mandar:**

> Buenos días, don Miguel. Le cuento que lo que me preguntó ayer ya quedó listo: el bot maneja el horario de cada sucursal por separado y al cliente que ya ha pedido lo saluda por su nombre.
>
> Para dejárselo armado con sus datos necesito el horario real de cada una de las 5 sucursales, día por día. Me lo puede mandar así nomás, en un mensaje o en una foto.
>
> Y le propongo algo: arrancar el mes gratis en una sola sucursal, la que usted escoja. Así lo ve funcionando con sus clientes sin mover todo de un solo, y cuando esté contento lo pasamos a las demás. El plan y el precio son los mismos de la propuesta que le mandé.
>
> Si le queda bien, lo vemos en una llamada de 20 minutos cuando usted pueda. ¿Le parece?

**Si pregunta el precio otra vez:**

> Es lo que va en el PDF que le mandé, don Miguel: plan Cadena, L15,000 de instalación en dos partes (la mitad el día 30 y la otra el día 60) y L5,500 al mes desde el día 31. Los primeros 30 días no paga nada, no cobramos comisión por pedido y lo puede cancelar cuando quiera.

(Son los precios oficiales de [oferta/PLAN-DE-OFERTA.md](oferta/PLAN-DE-OFERTA.md). No dé otros. Si pide rebaja, se baja la instalación, nunca la mensualidad.)

**Si pregunta cuánto tarda la instalación:**

> Armar el bot con su menú y sus horarios es cosa de pocos días una vez que me los manda. Lo que más tarda es que WhatsApp apruebe el número, y eso lo decide Meta, no nosotros. Por eso le pido los datos de una vez, para ir adelantando.

(Ojo: no le dé una fecha exacta todavía. Nunca hemos conectado un número real y no sabemos cuánto tarda Meta.)

**Si pregunta qué necesita de él:**

> Poquito, don Miguel. El menú con precios ya lo tengo de sus redes y solo le pido que me lo confirme. De usted necesito: el horario y la dirección de cada sucursal, el número de WhatsApp que va a usar el bot, el número donde quiere que le lleguen los avisos, y una foto del RTN y de un recibo de luz o agua del negocio, que eso lo pide WhatsApp para comprobar que el negocio existe.

(La lista completa está en [kit-cliente/2-lo-que-necesitamos.md](kit-cliente/2-lo-que-necesitamos.md).)

**Si pregunta cuántos clientes tenemos:**

> Le soy sincero: estamos empezando y usted sería de los primeros. Por eso el primer mes es gratis y por eso lo atiendo yo personalmente.

- [ ] Mensaje enviado a don Miguel
- [ ] Contestarle el mismo día todo lo que pregunte
- [ ] Anotar sus horarios cuando los mande

---

## 2. Con Sabor a Pueblo

Lo que pidió ya está puesto: el bot atiende solo Tegucigalpa, cerdito chuko a L220 y los chicharrones con sus precios. La fecha del plan para arrancar es el sábado 28 de noviembre.

**Mensaje para mandar:**

> Buenos días. Ya quedaron los cambios que me pidió: el bot atiende solo Tegucigalpa, el cerdito chuko a L220 y los chicharrones a L320 la libra o L160 la media, con sus tortillas y limón. Lo de San Pedro se lo pasa a usted directo.
>
> ¿Lo pudo volver a probar? Si ve algo raro, me dice y lo arreglo hoy mismo.
>
> Si ya lo ve bien, le propongo que arranquemos el sábado 28. Antes de eso hacemos una videollamada de unos 45 minutos esta semana o la otra para dejar listo el menú, los horarios y sus repartidores. ¿Qué día le queda mejor?

(En esa videollamada se le repite el precio antes de empezar el mes gratis: L15,000 de instalación en dos mitades y L2,500 al mes. Así dice el plan.)

**Lo que le toca a usted:**

- [ ] Montar el panel real en Render: sección "Atajo" de [PUESTA-EN-MARCHA.md](con-sabor-a-pueblo/PUESTA-EN-MARCHA.md). Son 20 minutos y no necesita a Meta.
- [ ] Si el servidor ya estaba arriba: en Render, botón **Manual Deploy > Deploy latest commit**, para que los cambios de anoche lleguen al servidor.
- [ ] Meta: probar la cuenta de desarrollador desde el celular y desde otro navegador.
- [ ] **Miércoles 18:** si sigue bloqueado, abrirla con el Facebook de Dylan.
- [ ] **Viernes 20:** si tampoco, se arranca con Twilio y se cambia a Meta después. No se espera otra semana.
- [ ] Hacer la prueba real de [PRUEBA-REAL.md](bot-restaurante/PRUEBA-REAL.md) y anotar lo que falle.

---

## 3. Los que dejaron de contestar

**Seguimiento (una sola vez, a los 3 días de silencio):**

> Buenas, le escribo otra vez por si el mensaje se le fue para abajo. Soy Rodrigo, de Clientia Tech. Lo que hacemos es que el pedido del cliente por WhatsApp le llegue completo a la cocina, con el total ya sacado, sin que nadie tenga que estar pegado al teléfono. Si quiere se lo enseño funcionando, lo prueba desde su propio celular y me dice. Y si no es el momento, no hay problema, solo dígame y no le vuelvo a escribir.

**Último mensaje (7 días después, y ahí se deja):**

> Buenas, este es el último mensaje que le mando para no molestar. Si más adelante quiere ver cómo funciona lo de los pedidos por WhatsApp, aquí queda mi número. Que le vaya muy bien con el negocio.

Ninguno de los dos lleva precio. El precio se habla cuando el dueño ya lo probó o lo pregunta.

- [ ] Abrir la [página de WhatsApp](https://claude.ai/artifact/SUV15bH8BrWtgiokUBPc59): todavía hay negocios de Honduras sin escribirles, y ya tienen puesto el primer mensaje nuevo (el directo, sin preguntar por el dueño). Máximo 10 nuevos por día.
- [ ] Mandar los seguimientos que la página marque como pendientes.
- [ ] Contestarle a Carnes El Argentino, que escribió "hable amigo" y nunca se le respondió.
- [ ] Anotar todo en `campana/registro-campana.csv`.

---

## 4. Lo que solo usted puede hacer (10 minutos cada uno)

- [ ] **Google Search Console:** entrar a search.google.com/search-console, agregar `clientiatech.com`, verificar y en "Sitemaps" pegar `https://clientiatech.com/sitemap.xml`.
- [ ] **Perfil de Negocio en Google:** crearlo en business.google.com con el nombre Clientia Tech, el sitio y el WhatsApp.
- [ ] **Perfil de WhatsApp Business:** nombre Clientia Tech, logo, sitio clientiatech.com, horario de atención y una línea de descripción. Foto suya de verdad en su WhatsApp.
- [ ] **Cambiar la contraseña del correo** de clientiatech.com, que quedó pegada en un chat.

---

## Para no olvidar

- Contestar el mismo día, siempre.
- Lo que se acuerde por llamada se manda después por escrito, en un mensaje corto.
- No prometer ventas, ni fechas que dependan de Meta, ni funciones que el bot no tiene hoy.
- Se dice "recibo", no "factura", hasta que la empresa esté registrada.
