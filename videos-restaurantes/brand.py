#!/usr/bin/env python3
"""Write marca.md for each restaurant into /mnt/project-files/restaurantes/<slug>/."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = "/mnt/project-files/restaurantes"

EXTRA = {
    "el-patio": dict(
        address="Contiguo a Banco Banpaís, Bulevar Morazán, Tegucigalpa",
        phone="+504 2221-4141", phone_kind="fijo",
        hours="Lun a sáb 11:00 am a 11:30 pm · dom 11:00 am a 11:00 pm",
        online="Sin sitio web propio. En Google aparecen directorios (Wanderlog, Tripadvisor) y fotos de clientes.",
        reviews_note="Google 4.3 (4,642 reseñas) · Tripadvisor 4.2 (394)",
        what_people_say="Porciones generosas, platos típicos, música en vivo y decoración rústica que honra lo hondureño. Quejas: carne a veces muy cocida y servicio lento.",
        opportunity="Es el que más reseñas tiene de los cinco: mucha gente ya los busca y no encuentra un lugar oficial para ver el menú, reservar o pedir. Mucho volumen de familias y turistas, así que reservas para grupos y pedidos para llevar son lo fuerte.",
        concept="**La fiesta catracha.** Un cartel de feria hondureña: letras gruesas, colores de barro, maíz y pino, y la música en vivo como protagonista del sitio (agenda de la semana).",
        voice="Cálida, de casa, orgullosamente hondureña. Habla de \"vos\" solo en frases cortas de cierre; el resto en \"usted\" amable.",
        palette=[("Barro", "primary", "Botones, fondos de héroe"), ("Maíz", "accent", "Destacados, especiales del día"), ("Pino", "deep", "Textos secundarios, pie"), ("Crema", "bg", "Fondo general"), ("Carbón", "ink", "Texto")],
        fonts_desc="Títulos: **Archivo Black** (en mayúsculas, como rótulo pintado). Texto: **Inter**.",
        site=["Inicio con la agenda de música en vivo", "Menú vivo por categorías (desayunos, típicos, parrilla, bebidas)", "Reservas para grupos y celebraciones con depósito", "Pedidos para recoger y a domicilio, pagados en línea", "Cómo llegar y parqueo"],
        sources=["https://wanderlog.com/place/details/2799839/el-patio", "https://wanderlog.com/list/geoCategory/205348/"],
    ),
    "rojo-verde-y-ajo": dict(
        address="Paseo República de Argentina, Tegucigalpa (Plus Code 4R23+5MJ)",
        phone="+504 2232-5653", phone_kind="fijo",
        hours="Lun a mié 12:00 a 10:00 pm · jue a sáb 12:00 a 11:00 pm · domingo cerrado",
        online="Sin sitio web propio. En Google salen Wanderlog, Revista Estilo y Tripadvisor.",
        reviews_note="Google 4.5 (272 reseñas) · Tripadvisor 4.2 (148)",
        what_people_say="Experiencia de alta cocina en ambiente íntimo y relajado, buena carta de vinos, música en vivo. Revista Estilo lo pone en su lista top y menciona a la chef Mandy Bermúdez y un menú de temporada (ceviche de vieiras, filete de res con salsa de vermut).",
        opportunity="Un menú de temporada que cambia es justo lo que un PDF o una foto en Instagram no resuelve. Reservas con depósito para noches de música en vivo y fines de semana.",
        concept="**Tres colores, una cocina.** El nombre ya es la marca: rojo tomate, verde hierba y el marfil del ajo. Un sitio editorial, como carta impresa de restaurante de autor, con la chef al frente.",
        voice="Sobria, sensorial y precisa. Frases cortas que describen el plato y el origen del ingrediente.",
        palette=[("Rojo tomate", "primary", "Héroe, botones"), ("Verde hierba", "accent", "Detalles, estado \"de temporada\""), ("Verde oscuro", "deep", "Textos secundarios"), ("Marfil de ajo", "bg", "Fondo"), ("Tinta", "ink", "Texto")],
        fonts_desc="Títulos: **Fraunces** (serif editorial, itálica para frases). Texto: **Inter**.",
        site=["Inicio con la chef y la carta de temporada", "Menú vivo (la chef cambia platos desde el celular)", "Reservas con depósito para música en vivo y fin de semana", "Carta de vinos", "Tarjetas de regalo y cenas especiales con boleto"],
        sources=["https://wanderlog.com/place/details/2799858/rojo-verde-y-ajo", "https://www.revistaestilo.net/galeria/restaurantes-top-en-tegucigalpa-y-san-pedro-sula-DAES1356500"],
    ),
    "cafe-honore": dict(
        address="Colonia Palmira, Tegucigalpa (Plus Code 4R23+4P7)",
        phone="+504 2239-7566", phone_kind="fijo",
        hours="Todos los días 10:30 am a 10:00 pm",
        online="Solo página de Facebook (facebook.com/cafehonore). Sin sitio ni menú en línea.",
        reviews_note="Google 4.5 (773 reseñas) · Tripadvisor 4.2 (125)",
        what_people_say="Café-deli con aire europeo desde 1993 (según Revista Estilo): jamón de Parma, quesos franceses, ensaladas, sopas, panadería y una tiendita de quesos, embutidos y especias. Terraza con cerveza o vino francés. Quejas: servicio lento en horas pico.",
        opportunity="Tiene tienda gourmet además de restaurante: puede vender quesos, embutidos y canastas de regalo en línea, y recibir pedidos de oficinas para almuerzo (venta B2B). Pedir y pagar en la mesa con QR ayuda con el servicio lento en horas pico.",
        concept="**Una esquina de Europa en Palmira.** Azul de toldo parisino, mantequilla y burdeos. Un sitio que se siente como la vitrina de un deli, con la historia desde 1993.",
        voice="Elegante pero cercana, de barrio. Cuenta la historia y los productos con nombre y origen.",
        palette=[("Azul París", "primary", "Héroe, botones"), ("Oro mantequilla", "accent", "Destacados"), ("Burdeos", "deep", "Detalles de vino y tienda"), ("Crema", "bg", "Fondo"), ("Tinta azul", "ink", "Texto")],
        fonts_desc="Títulos: **Cormorant Garamond** (serif clásica, itálica para frases). Texto: **Inter**.",
        site=["Inicio con la historia desde 1993", "Menú vivo del café", "Tienda deli en línea: quesos, embutidos, canastas de regalo", "Almuerzos para oficinas (pedido y pago antes de las 11 am)", "Pedir y pagar en la mesa por QR"],
        sources=["https://wanderlog.com/place/details/2082958", "https://www.revistaestilo.net/galeria/restaurantes-top-en-tegucigalpa-y-san-pedro-sula-DAES1356500"],
    ),
    "chedrani": dict(
        address="15 Avenida NO, San Pedro Sula",
        phone="+504 2557-5744", phone_kind="fijo",
        hours="Lun, mié, jue y vie 11:00 am a 9:00 pm · mar 11:00 am a 10:00 pm · sáb y dom 11:00 am a 11:00 pm",
        online="Solo página de Facebook (facebook.com/restaurantechedrani). Sin sitio ni menú en línea.",
        reviews_note="Google 4.3 (2,335 reseñas) · Tripadvisor 4.0 (69)",
        what_people_say="Parrilla fresca, mariscos y especialidades locales en porciones generosas a buen precio, área grande al aire libre y hasta lavado de carros mientras uno come. Recomiendan la parrillada.",
        opportunity="Mucho volumen y fines de semana largos (hasta las 11 pm): pedidos para llevar pagados en línea, reservas de mesas grandes y paquetes para grupos o partidos.",
        concept="**Brasa y terraza.** Carbón, naranja de brasa y amarillo de cerveza fría. Letras condensadas tipo rótulo de parrilla, fotos reales de la brasa (nunca de banco de imágenes).",
        voice="Directa, alegre, de amigos. Frases cortas y en mayúsculas para lo importante.",
        palette=[("Brasa", "primary", "Héroe, botones"), ("Cerveza", "accent", "Destacados, promos"), ("Humo", "deep", "Tarjetas"), ("Carbón", "bg", "Fondo"), ("Hueso", "ink", "Texto")],
        fonts_desc="Títulos: **Bebas Neue** (condensada, en mayúsculas). Texto: **Inter**.",
        site=["Inicio con la parrillada y la terraza", "Menú vivo (parrilla, mariscos, bebidas)", "Pedidos para llevar y a domicilio pagados en línea", "Reservas para grupos y eventos", "Promos de fin de semana por WhatsApp a la base de clientes"],
        sources=["https://wanderlog.com/place/details/2800007", "https://wanderlog.com/list/geoCategory/205360"],
    ),
    "el-mezzonite": dict(
        address="2 Calle NO y 24 Avenida, San Pedro Sula",
        phone="+504 9535-8989", phone_kind="celular (puede tener WhatsApp, por confirmar)",
        hours="No publicadas en las fuentes revisadas",
        online="Solo página de Facebook (facebook.com/elmezzonite). Sin sitio ni menú en línea.",
        reviews_note="Google 4.5 (275 reseñas) · Tripadvisor 4.5 (54)",
        what_people_say="Lugar elegante para aniversarios y cumpleaños, buena comida y postres, sangría y cócteles. Tunota destaca pasta fresca (carbonara, ravioli de ricotta y espinaca). Quejas: algunos dicen que es caro y que el servicio a veces no está atento.",
        opportunity="Es el restaurante de las fechas especiales: reservas con depósito, menús de aniversario, tarjetas de regalo y cenas con boleto. Ticket alto, así que pocas reservas extra ya pagan el servicio.",
        concept="**Para las noches que se celebran.** Negro profundo, champaña y vino. Un sitio oscuro y elegante, como la carta de una cena de aniversario.",
        voice="Íntima y elegante, en \"usted\". Habla de ocasiones, no de descuentos.",
        palette=[("Champaña", "primary", "Héroe, botones"), ("Vino", "accent", "Detalles, ocasiones"), ("Noche", "deep", "Tarjetas"), ("Negro", "bg", "Fondo"), ("Marfil", "ink", "Texto")],
        fonts_desc="Títulos: **DM Serif Display** (serif de alto contraste, itálica para frases). Texto: **Inter**.",
        site=["Inicio pensado para ocasiones especiales", "Menú vivo y carta de cócteles", "Reservas con depósito y nota de ocasión (aniversario, cumpleaños)", "Tarjetas de regalo digitales", "Cenas especiales con boleto"],
        sources=["https://wanderlog.com/list/geoCategory/318048", "https://www.tunota.com/honduras-hoy/lugares-para-comer-en-san-pedro-sula-restaurantes-populares-que-puedes-visitar-2023-06-13"],
    ),
}

WA = "+1 (765) 543-4251"


def md(r, x):
    c = r["colors"]
    pal = "\n".join(f"| {n} | `{c[k]}` | {use} |" for n, k, use in x["palette"])
    site = "\n".join(f"{i}. {s}" for i, s in enumerate(x["site"], 1))
    src = "\n".join(f"- {s}" for s in x["sources"])
    first_contact = (
        f"Buenas tardes, ¿hablo con {r['name']}? Mi nombre es Rodrigo, de Casa Digital, una línea de Clientia Tech. "
        f"Le preparé al restaurante un video de 40 segundos con una idea: su propia página con menú, pedidos pagados en línea y reservas, "
        f"sin comisión por pedido. Tienen {r['reviews']} reseñas en Google y muy buena calificación, pero al buscarlos salen directorios y no una página suya. "
        f"¿Me podría compartir el WhatsApp del dueño o de quien ve el marketing para enviárselo?"
    )
    wa_msg = (
        f"Hola, buen día. Soy Rodrigo, de Casa Digital (Clientia Tech). Les hice este video corto con una propuesta para {r['name']}: "
        f"su propia casa digital, con menú que cambian desde el celular, pedidos y pagos con tarjeta directo a su cuenta, y reservas por WhatsApp. "
        f"Cero comisión nuestra por pedido y lista en 14 días.\n\n"
        f"Estamos tomando solo 5 restaurantes con precio de fundador. Si le interesa, le muestro en 15 minutos cómo se vería con su menú real. "
        f"¿Le queda bien esta semana?"
    )
    follow = (
        f"Hola, le escribo de nuevo de Casa Digital. Solo quería saber si pudo ver el video que le hicimos a {r['name']}. "
        f"Si prefiere, se lo explico en una llamada corta. Gracias."
    )
    return f"""# {r['name']} · Archivo de marca

*Casa Digital, una línea de Clientia Tech · Investigación del 12 de octubre de 2026*

![Portada]({r['slug']}-portada.png)

**Video:** [{r['slug']}-casa-digital.mp4]({r['slug']}-casa-digital.mp4) (vertical 1080×1920, 40 s, con la música y cortes en los golpes, cierra con \"by Clientia Tech\")

## 1. Datos públicos del negocio

| | |
|---|---|
| Tipo | {r['kind']} |
| Ciudad | {r['city']} |
| Dirección | {x['address']} |
| Teléfono público | {x['phone']} ({x['phone_kind']}) |
| Horario | {x['hours']} |
| Reseñas | {x['reviews_note']} |
| Presencia en línea | {x['online']} |

Solo usé información pública del negocio (directorios y prensa). Las cifras de reseñas vienen de Wanderlog, que copia Google y Tripadvisor; hay que confirmarlas en Google antes de mencionarlas.

**Lo que dice la gente:** {x['what_people_say']}

## 2. Diagnóstico

{x['opportunity']}

## 3. Concepto de marca digital

{x['concept']}

**Frase guía:** *{r['tagline']}*

**Voz:** {x['voice']}

### Paleta

| Color | Hex | Uso |
|---|---|---|
{pal}

### Tipografía

{x['fonts_desc']} Todas son de licencia libre (Google Fonts / Fontsource).

### Reglas

- Fotos reales del restaurante y sus platos, tomadas por nosotros. Nada de imágenes de banco ni hechas con IA.
- Primero el celular: todo se diseña para pantalla vertical.
- Menú editorial: nombres de platos con su descripción corta, sin saturar.

## 4. Sitio propuesto

Dominio sugerido: `{r['domain']}` (no verifiqué si está libre).

{site}

Los platos que aparecen en el video ({', '.join(r['dishes'])}) salen de reseñas públicas y son de ejemplo; el menú real se toma con el restaurante.

## 5. Contacto (borradores, nada enviado)

**Primer contacto por teléfono o mensaje directo en Facebook/Instagram:**

> {first_contact}

**Mensaje de WhatsApp con el video** (cuando den el número del dueño):

> {wa_msg}

**Seguimiento a los 3 días si no responden:**

> {follow}

Nuestro WhatsApp para respuestas: **{WA}**

## 6. Pendiente de verificar

- Que el restaurante siga abierto con el mismo horario y dirección.
- Calificación y número de reseñas actuales en Google.
- Nombre del dueño o encargado de marketing.
- Si el dominio sugerido está libre.

## Fuentes

{src}
"""


if __name__ == "__main__":
    data = json.load(open(os.path.join(HERE, "restaurants.json")))
    for r in data:
        d = os.path.join(DEST, r["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "marca.md"), "w") as fh:
            fh.write(md(r, EXTRA[r["slug"]]))
        print(d)
