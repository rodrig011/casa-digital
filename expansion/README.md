# Guatemala y El Salvador

*26 de octubre de 2026 · Casa Digital (Clientia Tech) · Solo investigación: no se le escribió a nadie*

Encontré **66 restaurantes con correo** (34 en Guatemala y 32 en El Salvador) y 12 más que solo atienden por WhatsApp. Allá pasa lo mismo que en Honduras: los restaurantes chicos casi no publican correo. Por eso los saqué de los dos directorios donde los propios restaurantes se inscriben:

- **Guatemala:** el directorio de socios de la Cámara de Comercio de Guatemala (directorio.ccg.gt), que es donde está la Gremial de Restaurantes. Revisé 119 negocios de comida.
- **El Salvador:** el directorio de ARES, la Asociación de Restaurantes de El Salvador (ares.sv). Tiene 125 restaurantes y 35 publican correo.

Después abrí la página web de cada uno para confirmar el correo y sacar su WhatsApp, y leí el TikTok de los más grandes.

**Archivos:**
- [prospectos.csv](prospectos.csv): todos, con correo, WhatsApp, fuente y lo que se puede decir de cada uno.
- [datos.json](datos.json): lo mismo para el panel o un bot.
- [../harvey/entrada/guatemala-el-salvador.csv](../harvey/entrada/guatemala-el-salvador.csv): la lista que usa Harvey para escribirles.
- `herramientas/`: `ccg.py` lee el directorio de la Cámara, `sitio.py` saca correos y WhatsApp de una página, y `armar.py` arma los dos CSV desde `datos.json`.

## Los mejores para empezar

| | Negocio | Dónde | Por qué | Correo |
|---|---|---|---|---|
| 1 | **Castor's Pizza** | Ciudad de Guatemala | 61 mil seguidores en TikTok y dos videos de 1.3 millones de vistas. **Contestaron 1 de 68 comentarios.** Hay quejas sin respuesta: "como 2 horas pa entregar y frías las pizzas". Los pedidos a domicilio entran por teléfono. | informacion@castorspizza.com |
| 2 | **El Adobe** | Guatemala: zona 1, zona 10, Antigua y Naranjo | Comida típica. Su página tiene un correo para cada sucursal y dos WhatsApp. Es el caso perfecto para el panel por sucursal. | restauranteeladobe@gmail.com |
| 3 | **Clavo y Canela** | San Salvador, 6 locales | **Un solo WhatsApp para los seis locales** y un correo solo para domicilio. | domicilio@clavoycanela.com.sv |
| 4 | **La Pampa** | San Salvador, 6 sucursales | Carnes desde 1987. Cada sucursal tiene su propio correo y teléfono. | lapampa.reservaciones@gmail.com |
| 5 | **Restaurantes Acajutla** | El Salvador, 7 sucursales | Mariscos. Siete sucursales y un solo correo para todas. | restaurantesacajutlas@gmail.com |
| 6 | **Don Pavo** | San Salvador, Escalón | Pan con pavo desde 1976. Tienen un correo y un WhatsApp solo para pedidos. | donpavo.pedidos@gmail.com |
| 7 | **Pollos Real** | El Salvador, 10 sucursales | Pollo rostizado y carnitas. | pollosreal@yahoo.com |
| 8 | **Los Churrascos** | Guatemala: zona 17 y San José Pinula | Dos sucursales con teléfonos distintos. En TikTok la gente pregunta precios y piden una sucursal en San Cristóbal. | loschurrascos.gt@gmail.com |
| 9 | **The Boiling Cajún** | Quetzaltenango | Tienen un correo solo para pedidos. | pedidos@theboilingcajun.com |
| 10 | **El Sopón Típico** | San Salvador, Los Héroes | Comida típica, con botón de WhatsApp en su página. | elsopontipico7@gmail.com |

Sin correo, pero con mucha demanda en TikTok: **El Café de Don Pedro** (San Salvador, un video de 245 mil vistas y 1 de 87 comentarios contestados) y **Willy's Wings** (San Salvador, 16 mil seguidores y 1 de 25 contestados). Esos van por WhatsApp o DM.

## La oferta en cada país

Es la misma que en Honduras: 30 días sin pagar nada, sin compromiso, y el precio se habla en la llamada, nunca por escrito. Lo que cambia:

| | Honduras | Guatemala | El Salvador |
|---|---|---|---|
| Moneda del bot y del panel | lempiras (L 150) | quetzales (Q45) | dólares ($3.50) |
| Precio de referencia (igual al de Honduras) | L32,000 + L3,500 al mes | Q9,500 + Q1,050 al mes | $1,200 + $130 al mes |
| Cómo nos pagan a nosotros | Stripe con tarjeta, en dólares | Stripe con tarjeta, en dólares | Stripe con tarjeta, en dólares |
| Cobro a sus clientes en el bot (opcional) | PixelPay, Tilopay (BAC) | por definir (Recurrente o el banco del restaurante) | Wompi (Banco Agrícola) o Pagadito |
| Apps de domicilio que nombra el bot | PedidosYa, Bip Bip | PedidosYa, Uber Eats, Hugo | PedidosYa, Uber Eats, Hugo |

- **Stripe sirve para cobrarles a ellos**, porque lo cobramos nosotros desde Estados Unidos y Stripe acepta tarjetas de cualquier país. Lo que **no** se puede es que un restaurante de Guatemala o El Salvador abra su propia cuenta de Stripe: ninguno de los dos países está en la lista de Stripe (stripe.com/global, revisada hoy). Para que sus clientes paguen dentro del bot hace falta una pasarela local, igual que en Honduras.
- El Salvador ya usa dólares, así que ahí no hay que convertir nada.
- Guatemala y El Salvador tienen la misma hora que Honduras, así que el bot no cambia de horario.
- Los precios de referencia son el de Honduras pasado a quetzales y a dólares. Se ajustan después de las primeras llamadas.

## Lo que ya cambié para vender allá

- **Bot:** cada restaurante ahora lleva `"moneda"` en su archivo (`GTQ` o `USD`), y el bot, los avisos y el panel muestran los precios en esa moneda. Cuando el bot usa IA, dice el país correcto. Sin `moneda` sigue en lempiras, así que Coco Chicken no cambia. Las pruebas pasan.
- **clientiatech.com:** ahora dice "restaurantes de Honduras, Guatemala y El Salvador" y que el bot da el total en lempiras, quetzales o dólares.
- **Harvey:** ya sabe de qué país es cada prospecto. A los de Guatemala y El Salvador les escribe en español neutro, sin palabras hondureñas, nombra Uber Eats y Hugo en vez de Bip Bip, y nunca dice que solo trabajamos en Honduras.

## Lo que no se pudo verificar

- **El correo de 50 de los 66 salió solo del directorio** (columna "verificado_en_su_pagina" = no). Algunos directorios tienen años, así que hay que verificar cada correo antes de mandar y sacar los que reboten. En esos casos el correo no dice "vi en su página".
- Algunos correos son de una persona o de un área (eventos, franquicias, banquetes). Están marcados en la columna "nota".
- **Dueños:** no salen publicados. El primer correo va al equipo y pregunta quién atiende el WhatsApp.
- **Facebook e Instagram** piden iniciar sesión desde aquí. Lo de TikTok son números del 26 de octubre de 2026.
- Las cadenas grandes (Los Cebollines, Pollo Campestre, Pollo Express) están en la lista con prioridad 3, porque seguramente ya tienen proveedor.
