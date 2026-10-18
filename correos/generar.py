"""Genera CORREOS.md y correos.csv a partir de la lista de abajo.
Cada dato que se menciona sale de investigacion-masiva/fichas.md (fuente al lado)."""
import csv, urllib.parse, pathlib

AQUI = pathlib.Path(__file__).parent

FIRMA = """Saludos cordiales,

Rodrigo Herrera
Clientia Tech · https://clientiatech.com
WhatsApp +1 (765) 543-4251"""

OFERTA = ("Le propongo probarlo 30 días gratis con {quien}. Si no le sirve, se quita y no paga nada; "
          "no le pido ni un lempira por adelantado.")

CIERRE = ("¿Tendría 10 minutos esta semana para una llamada? Puede contestarme aquí mismo o escribirme "
          "al WhatsApp de abajo, y lo cuadramos a la hora que le quede mejor.")

# (dia, negocio, correo, asunto, saludo, gancho, propuesta, quien, fuente)
C = [
 (1, "Pollos El Hondureño", "polloselhondurenomaps@gmail.com",
  "Pedidos por WhatsApp para las sucursales de Pollos El Hondureño",
  "Estimada familia Castillo y equipo de Pollos El Hondureño:",
  "Le escribo porque vi en su sitio que tienen 14 sucursales y en la prensa que siguen creciendo, ahora con la de Siguatepeque. También vi que el WhatsApp de pedidos que se publica es uno solo, el 9455-8901, para todas las sucursales.",
  "Yo armo un sistema para eso: ese WhatsApp contesta solo el menú, los precios y la sucursal más cercana, toma el pedido y se lo manda a la sucursal que le toca. Ustedes ven en un panel, desde el celular, las ventas y los pedidos de cada sucursal.",
  "una o dos sucursales",
  "polloselhondureno.hn (acerca-de, atención al cliente); periodismocomercial.hn (Siguatepeque, WhatsApp 9455-8901)"),
 (1, "Basilio's", "servicioalcliente@basilios.hn",
  "Una propuesta para los pedidos de Basilio's",
  "Estimado equipo de Basilio's:",
  "Le escribo a servicio al cliente porque no encontré otro correo; le agradecería mucho pasarle este mensaje a gerencia. Vi que Basilio's ya tiene 29 tiendas, que el año pasado abrieron la segunda en Choluteca, y que en su página de contacto aparece un solo WhatsApp para toda la cadena.",
  "Yo armo un sistema para eso: ese WhatsApp contesta solo horarios, tiendas cercanas y productos, toma los pedidos especiales, como pasteles, y avisa a la tienda que le toca. Gerencia ve en un panel lo que pide la gente en cada tienda.",
  "una o dos tiendas",
  "basilios.hn/contacto, basilios.hn/tiendas; hondudiario.com (2a tienda Choluteca, 2025); forumhnnews (29 tiendas)"),
 (1, "Marcas Astrales (Coco Baleadas)", "capitalhumano@cocobaleadas.com",
  "Para gerencia: los comentarios del TikTok de Coco Baleadas",
  "Estimado equipo de Marcas Astrales:",
  "Le escribo a este correo porque es el único que encontré publicado; le agradecería pasarlo a gerencia general u operaciones. Vi que el video más visto de Coco Baleadas en TikTok pasa de un millón de vistas, y que de casi 200 comentarios en sus dos videos más vistos la cuenta contestó 3. Mucha de esa gente pregunta cosas de alguien que ya quiere comprar.",
  "Yo armo un sistema para eso: un WhatsApp que contesta al instante precios, sucursales y horarios, y toma pedidos para la sucursal que toca, y un panel donde se ven las ventas y los pedidos de cada sucursal desde el celular.",
  "una sucursal",
  "tiktok.com/@cocobaleadas (video 1.1M; 3 de 198 respondidos); multiplaza.com (correo)"),
 (1, "Cholucarnes & Más", "cholucarnesymas@gmail.com",
  "Las preguntas de horario y menú en el TikTok de Cholucarnes",
  "Buenos días, equipo de Cholucarnes & Más:",
  "Vi su TikTok: ya llevan más de 240 videos y uno pasa de 47 mil vistas. En ese video la gente pregunta el horario, el menú y la ubicación, y esas preguntas se quedaron sin respuesta. También vi que ya toman pedidos a domicilio con un formulario de Whataform.",
  "Yo armo un sistema que conecta todo eso: un WhatsApp que contesta solo horario, menú y ubicación, toma el pedido del paquete parrillero o de la carnicería, y un panel donde ustedes ven los pedidos y el inventario de carne.",
  "Cholucarnes",
  "tiktok.com/@cholucarnes (249 videos; video 47.9K, 0 respuestas); whataform.com/SB0DA331594757273"),
 (1, "XpressArte Gourmet Cuisine", "xpressartecomayagua@gmail.com",
  "Las preguntas de precio en los videos de XpressArte",
  "Buenos días, equipo de XpressArte:",
  "Vi sus videos en TikTok y les está yendo muy bien: cinco pasan de 100 mil vistas solo entre septiembre y octubre, y el más visto va por 210 mil. En los comentarios de los dos más vistos la gente pregunta precios, y no vi respuesta de la cuenta. También noté que el horario de Facebook (10 am) no es el mismo que el de Instagram (11 am).",
  "Yo armo un sistema para eso: un WhatsApp que contesta solo el menú, los precios, el horario correcto y la ubicación en Plaza San Blas, y toma reservas o pedidos mientras ustedes cocinan.",
  "XpressArte",
  "tiktok.com/@xpressartecomayag (5 videos >100K, 0 de 20 respondidos); facebook e instagram (horarios)"),
 (1, "Restaurante La Vela", "inv.lavelahnd@gmail.com",
  "Las preguntas de menú en el TikTok de La Vela",
  "Buenos días, equipo de Restaurante La Vela:",
  "Encontré este correo en el directorio de puertocortes.hn; si no es el de la administración, le agradecería pasarlo al encargado. Vi que su video más visto en TikTok va por 48 mil vistas, y que ahí la gente pregunta por el menú y los precios sin que la cuenta haya contestado.",
  "Yo armo un sistema para eso: un WhatsApp que contesta solo el menú, los precios, el horario y cómo llegar a la playa municipal, y toma reservas y pedidos mientras ustedes atienden.",
  "La Vela",
  "tiktok.com/@rest.lavela (video 48.4K, 0 de 16 respondidos); puertocortes.hn/place/la-vela"),
 (1, "Telamar Resort", "info@telamarresort.com",
  "Las preguntas de precio en el TikTok de Telamar",
  "Estimado equipo de Telamar Resort:",
  "Vi que su video más visto en TikTok tiene casi un millón de vistas (964 mil), y que en los comentarios mucha gente pregunta precios y pide información para ir en grupo. De 99 comentarios que leí, la cuenta contestó 11.",
  "Yo armo un sistema para eso: un WhatsApp que contesta al instante precios, paquetes y disponibilidad de los restaurantes y el resort, y le pasa a su equipo de reservas solo a la gente que ya quiere reservar.",
  "Telamar",
  "tiktok.com/@telamarresort (video 964K, 11 de 99 respondidos); telamarresort.com/contacto"),
 (1, "Copantl Hotel & Convention Center", "eventos3@copantlconventioncenter.com",
  "Las preguntas de precio en el TikTok del Copantl",
  "Estimado equipo de eventos del Copantl:",
  "Vi que un video del Copantl en TikTok pasa de 104 mil vistas y que varias personas preguntan \"¿cuál es el precio?\" y \"¿qué cuesta?\". De 26 comentarios que leí, la cuenta contestó 6. Le agradecería pasarle este correo al gerente de alimentos y bebidas si no es su área.",
  "Yo armo un sistema para eso: un WhatsApp que contesta al instante precios del buffet, de La Churrasquería y de eventos, y le pasa a su equipo a la gente que ya quiere reservar o cotizar.",
  "uno de sus restaurantes",
  "tiktok.com/@hotelcopantl (video 104K, 6 de 26 respondidos); copantl.com (correo)"),
 (1, "Tela Marine", "info@telamarine.com",
  "Una idea para el restaurante de Tela Marine",
  "Estimado equipo de Tela Marine, a la atención de la dirección:",
  "Leí en La Prensa que el acuario recibe unos 182 mil visitantes al año, y que además del acuario tienen restaurante, café y eventos. En los comentarios de su TikTok que leí no vi respuestas de la cuenta, y ahí hay gente interesada en ir.",
  "Yo armo un sistema para eso: un WhatsApp que contesta solo horarios, precios de entrada, menú y cómo llegar, y un panel donde ustedes ven en un solo lugar la caja y el inventario del restaurante y el café.",
  "Tela Marine",
  "laprensa.hn (182 mil visitantes); tiktok.com/@telamarine (0 de 10 respondidos)"),
 (1, "Cafetano", "info@cafetano.com",
  "Para Mirko Cuculiza: una idea para las cinco cafeterías",
  "Estimado Mirko Cuculiza:",
  "Felicidades por lo que ha logrado con Cafetano: ver una cafetería hondureña entre las mejores del mundo da orgullo. Vi en su página que ya tienen cinco cafeterías en Tegucigalpa, además de la venta de café empacado.",
  "Yo armo un sistema que le junta todo en un panel en el celular: ventas por cafetería y por canal, inventario de café, y un WhatsApp que contesta solo horarios, ubicaciones y pedidos de café empacado.",
  "una de sus cafeterías",
  "es.cafetano.com/pages/ubicaciones (5); radiohouse.hn (Mirko Cuculiza); laprensa.hn (mejores cafeterías del mundo)"),
 (2, "Panadería y Repostería Moderna", "pedidos@panaderiamoderna.com",
  "Una idea para los pedidos de Panadería Moderna",
  "Estimado equipo de Panadería y Repostería Moderna:",
  "Le escribo a este correo de pedidos; le agradecería pasarlo a la gerencia. Vi la nota de la rosca de reyes más grande de Honduras que hicieron, y que hoy tienen cuatro sucursales en San Pedro Sula y que los pedidos llegan por WhatsApp y por este correo.",
  "Yo armo un sistema para eso: un WhatsApp que contesta solo precios, sabores y tamaños, toma el pedido del pastel con fecha y sucursal de retiro, y un panel donde ustedes ven todos los pedidos de la semana en un solo lugar.",
  "Panadería Moderna",
  "eldiario.hn (rosca de reyes); bakerias.com (4 sucursales); facebook.com/panaderiamoderna (correo y WhatsApp)"),
 (2, "Panadería Los Andes", "pedidos@panlosandes.com",
  "Una idea para los pedidos de pasteles de Los Andes",
  "Estimado equipo de Panadería Los Andes:",
  "Vi en su sitio la página de pasteles y que los pedidos llegan por este correo y por WhatsApp para sus sucursales de la Colonia Trejo y Plaza San Antonio.",
  "Yo armo un sistema para eso: un WhatsApp que contesta solo precios, sabores y tamaños, toma el pedido con fecha y sucursal de retiro, y un panel donde ustedes ven todos los pedidos de la semana en un solo lugar.",
  "Los Andes",
  "panaderialosandes.com; facebook.com/losandespanaderia (correo)"),
 (2, "Welchez Café", "info@welchezcafe.com",
  "Una idea para las sucursales de Welchez Café",
  "Estimada familia Welchez y equipo de Welchez Café:",
  "Vi la noticia de la apertura en La Entrada, su quinta sucursal, y que ahora también ofrecen la marca en franquicia. Con sucursales en San Pedro Sula y Copán, cada local trabaja lejos del otro.",
  "Yo armo un sistema para eso: un panel en el celular donde se ven las ventas y el inventario de cada sucursal y cada franquicia, y un WhatsApp que contesta solo horarios, ubicaciones y pedidos de café.",
  "una de sus sucursales",
  "periodismocomercial.hn (quinta sucursal, La Entrada); franquician.com (franquicia); facebook.com/WelchezCafe (correo)"),
 (2, "Criollos", "contacto@criolloshn.com",
  "Una idea para Criollos",
  "Estimado equipo de Criollos:",
  "Leí en Buen Provecho que Criollos honra la comida hondureña desde 1984, y vi que hoy tienen al menos dos restaurantes, en Plaza Ciudad Nueva y en el Centro Histórico. Le agradecería pasarle este correo al gerente.",
  "Yo armo un sistema para eso: un WhatsApp que contesta solo menú, precios, horario y ubicación de cada restaurante, toma pedidos y reservas, y un panel donde ustedes ven las ventas de las dos sucursales en el celular.",
  "uno de sus restaurantes",
  "buenprovecho.hn (desde 1984); facebook.com/criolloshn y /Criollostegucigalpa (sucursales, correo)"),
 (2, "Alondra Catering", "alondracatering@gmail.com",
  "Una idea para las cotizaciones de Alondra Catering",
  "Buenos días, equipo de Alondra Catering:",
  "Vi en su Facebook que llevan más de 30 años haciendo catering y banquetes, y que las cotizaciones se hacen por teléfono y por Facebook.",
  "Yo armo un sistema para eso: un WhatsApp que pregunta solo la fecha, el número de personas y el tipo de evento, le da al cliente un rango inicial y les deja a ustedes la cotización lista con una alerta, más una agenda de eventos en el celular.",
  "Alondra Catering",
  "facebook.com/alondracateringyeventos"),
 (2, "Flor's Catering", "florcateringhn@gmail.com",
  "Una idea para las cotizaciones de Flor's Catering",
  "Buenos días, equipo de Flor's Catering:",
  "Vi en su Facebook que atienden eventos de empresa, bodas y XV años en San Pedro Sula, y que las cotizaciones llegan por Facebook y por teléfono.",
  "Yo armo un sistema para eso: un WhatsApp que pregunta solo la fecha, el número de personas y el tipo de evento, le da al cliente un rango inicial y les deja a ustedes la cotización lista con una alerta, más una agenda de eventos en el celular.",
  "Flor's Catering",
  "facebook.com/FlorsCateringSPS"),
 (2, "Reuniones Honduras", "reservas@reunioneshonduras.com",
  "Una idea para las reservas de banquetes",
  "Estimado equipo de Reuniones Honduras:",
  "Vi en su sitio que organizan banquetes para bodas, quinceañeras y eventos de empresa, y que pronto abren oficina en Tegucigalpa.",
  "Yo armo un sistema para eso: un WhatsApp que pregunta solo la fecha, el número de invitados y el tipo de evento, da un rango inicial y les deja a ustedes la cotización lista con una alerta, más una agenda de eventos en el celular.",
  "Reuniones Honduras",
  "reunioneshonduras.com/banquetes.html"),
 (2, "Hotel Honduras Maya", "eventos@hondurasmaya.hn",
  "Para alimentos y bebidas del Honduras Maya",
  "Estimado equipo de eventos del Hotel Honduras Maya:",
  "Le agradecería pasarle este correo al gerente de alimentos y bebidas. Revisando su sitio vi que todavía aparece el comunicado de cierre por Covid junto a la información actual, y pensé que a alguien que busca el restaurante o un salón para eventos le puede confundir.",
  "Yo armo un sistema para eso: un WhatsApp que contesta al instante horarios del restaurante, menús de eventos y disponibilidad, y le pasa a su equipo solo a la gente que ya quiere reservar o cotizar.",
  "el restaurante o los eventos",
  "hondurasmaya.hn/contacto, hondurasmaya.hn/comunicado"),
 (2, "Hotel Marina Copán", "eventos@hotelmarinacopan.com",
  "Una idea para el restaurante Glifos",
  "Estimado equipo del Hotel Marina Copán:",
  "Le agradecería pasarle este correo a la gerencia. Revisando su sitio vi que el horario del restaurante Glifos no es el mismo en todas las páginas, y alguien que viene de visita a Copán puede llegar a la hora equivocada.",
  "Yo armo un sistema para eso: un WhatsApp que contesta al instante el horario correcto, el menú y las reservas de Glifos y de los eventos, y le avisa a su equipo de cada reserva nueva.",
  "Glifos",
  "hotelmarinacopan.com (/dining y /es: horarios distintos; correo)"),
 (2, "Hotel Portal del Ángel", "administracion@portaldelangelhn.com",
  "Una idea para el restaurante El Portal",
  "Estimado equipo de administración del Hotel Portal del Ángel:",
  "Vi que su restaurante El Portal ofrece cocina europea y hondureña en la Colonia Palmira, y quería proponerles algo pensado para restaurantes como el suyo.",
  "Yo armo un sistema para eso: un WhatsApp que contesta al instante el menú, el horario y las reservas del restaurante, y le avisa a su equipo de cada reserva nueva, con una agenda en el celular.",
  "El Portal",
  "facebook.com/portaldelangel (correo); travelweekly.com (restaurante)"),
]

def cuerpo(c):
    _, _, _, _, saludo, gancho, prop, quien, _ = c
    return "\n\n".join([
        saludo,
        "Mi nombre es Rodrigo Herrera, de Clientia Tech. Soy hondureño y hago sistemas para que los negocios de Honduras atiendan mejor a sus clientes sin depender de contestar todo a mano.",
        gancho, prop, OFERTA.format(quien=quien), CIERRE, FIRMA])

def mailto(c):
    q = urllib.parse.urlencode({"subject": c[3], "body": cuerpo(c)}, quote_via=urllib.parse.quote)
    return f"mailto:{c[2]}?{q}"

md = ["# Correos listos para mandar · Clientia Tech",
      "",
      "*20 correos, uno por negocio con correo verificado en `investigacion-masiva/`. Cada dato que se menciona tiene su fuente. Nada se ha enviado todavía.*",
      "",
      "**Cómo mandarlos desde el celular:** tocá \"Abrir en mi correo\" y se abre tu app de correo con el destinatario, el asunto y el texto ya escritos. Revisalo y mandalo.",
      "",
      "- **Día 1:** los 10 primeros, entre 9 y 11 am de Honduras.",
      "- **Día 2:** los otros 10, a la misma hora.",
      "- Mandalos de uno en uno, con un par de minutos entre cada uno, para que el correo no los marque como spam.",
      "- Si alguien contesta, la meta es la llamada de 10 minutos. Sin precios por escrito y sin mandar el video antes de la llamada.",
      "- No están Coco Chicken, Mag Pollo ni Fogos (ya se les escribió por WhatsApp).",
      "",
      "| # | Día | Negocio | Correo |", "|---|---|---|---|"]
for i, c in enumerate(C, 1):
    md.append(f"| {i} | {c[0]} | {c[1]} | {c[2]} |")
for i, c in enumerate(C, 1):
    md += ["", "---", "", f"## {i}. {c[1]}", "",
           f"**Para:** {c[2]}  ", f"**Asunto:** {c[3]}  ", f"**Día:** {c[0]}", "",
           f"[📧 Abrir en mi correo]({mailto(c)})", "", "```", cuerpo(c), "```", "",
           f"<sub>Fuente de los datos: {c[8]}</sub>"]
(AQUI / "CORREOS.md").write_text("\n".join(md) + "\n")

with open(AQUI / "correos.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["dia", "negocio", "correo", "asunto", "cuerpo", "fuente", "enviado"])
    for c in C: w.writerow([c[0], c[1], c[2], c[3], cuerpo(c), c[8], ""])
print(len(C), "correos")
