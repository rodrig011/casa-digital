# Mensajes de WhatsApp para los prospectos de Honduras (16 nov 2026).
# Correr:  python3 vender/prospectos_hn.py  -> escribe vender/MENSAJES-LISTOS.md y vender/prospectos_hn.json
# Los datos de cada negocio salen de sus propias redes o páginas (investigación de oct-nov 2026,
# ver investigacion-masiva/ y las notas de cada prospecto). Las vistas se dicen con "más de" porque solo suben.
import json, urllib.parse, pathlib

DEMO = "https://clientiatech.com/demos/con-sabor-a-pueblo.html"
QUIEN = "Le escribe Rodrigo Herrera. Somos estudiantes universitarios hondureños y tenemos una empresa, Clientia Tech."
CIERRE = "Si le interesa, con gusto le cuento por aquí mismo cómo funciona. Y si usted no es el dueño, ¿me haría el favor de pasarle este mensaje?"

ARMA = {
 "pedidos":   "Armamos que cada pedido de este WhatsApp quede tomado completo, con el total, y entre solo a una pantalla en la cocina. Y usted ve en el celular lo que vende cada día.",
 "domicilio": "Armamos que cada pedido a domicilio quede tomado completo, con la dirección y el total, y entre solo a una pantalla en la cocina. Y usted ve en el celular lo que vende cada día.",
 "sucursales":"Armamos que cada pedido quede tomado completo, con el total, y entre solo a la cocina de la sucursal que le toca. Y usted ve cada sucursal en el celular.",
 "reservas":  "Armamos que cada reservación quede anotada completa, con día, hora y personas, y a usted solo le toque confirmarla desde el celular. También puede tomar pedidos para recoger.",
 "repartos":  "Armamos que cada pedido quede tomado completo, con la dirección y el total, entre solo a la cocina y se le pase al repartidor que esté libre, y que al cliente le llegue el aviso de que va en camino.",
 "navidad":   "Para diciembre le podemos dejar su WhatsApp tomando solo los encargos del 24 y el 31: anota qué quiere cada cliente y para qué hora, pide el anticipo con la foto del comprobante, lleva la cuenta de cuántos le quedan y le pasa la lista ordenada por día y hora.",
}

def primero(p):
    saludo = "Buenas, ¿cómo está?" + (f" Busco a {p['busco']}." if p.get("busco") else "")
    arma = p.get("arma_texto") or ARMA[p["tipo"]]
    cierre = CIERRE if not p.get("busco") else CIERRE.replace("si usted no es el dueño", f"si usted no es {p['busco_corto']}").replace("pasarle este mensaje", "pasarle este mensaje" )
    return f"{saludo} {QUIEN} Vi {p['hecho']}. {arma} {cierre}"

def seguimiento(p):
    quien = f"{p['busco_corto']} pudo ver" if p.get("busco") else "pudo ver"
    if p["tipo"] == "navidad":
        return f"Buenas tardes, ¿cómo está? Disculpe la insistencia, solo para preguntarle si {quien} mi mensaje. Si le interesa para diciembre, le cuento por aquí mismo cómo funcionaría en {p['nombre']}. Los primeros encargos los puede recibir desde el 1 de diciembre."
    return f"Buenas tardes, ¿cómo está? Disculpe la insistencia, solo para preguntarle si {quien} mi mensaje. Si le interesa, le cuento por aquí mismo cómo funcionaría en {p['nombre']}. Los primeros 30 días no pagan nada."

def ultimo(p):
    return (f"Buenas, ¿cómo está? Le escribo una última vez para no quitarle más tiempo. Por si quiere verlo funcionando, "
            f"aquí hay una demostración que armamos con otro negocio: {DEMO} . Si en algún momento le sirve para {p['nombre']}, "
            f"con gusto se lo armamos con su menú. Muchísimas gracias por leerme y que les vaya muy bien. Rodrigo, de Clientia Tech.")

def presentacion(p):
    arma = p.get("arma_texto") or ARMA[p["tipo"]]
    if p["tipo"] == "navidad":
        return (f"Mucho gusto. {QUIEN} Vi {p['hecho']}. {arma} Lo armamos con sus productos, no es una plantilla, y es solo por diciembre: "
                f"en enero, si quiere, se apaga y su WhatsApp queda igual que antes. Si gusta, le mando una demostración para que vea cómo funciona. ¿Le parece?")
    return (f"Mucho gusto. {QUIEN} Vi {p['hecho']}. {arma} Lo armamos con su menú, no es una plantilla. "
            f"Los primeros 30 días no paga nada y, si no le sirve, se apaga y su WhatsApp queda igual que antes. "
            f"Si gusta, le mando una demostración para que vea cómo funciona. ¿Le parece?")

# ---- Prospectos nuevos o por reescribir (estado nuevo) ----
NUEVOS = [
 # Navidad: escribir del 16 al 22 de noviembre
 dict(id="alondra", nombre="Alondra Catering", tipo="navidad", orden=-30, hecho="que llevan más de 30 años en banquetes y que las cotizaciones son por teléfono",
      arma_texto="Para diciembre le podemos dejar su WhatsApp tomando solo los encargos de cenas del 24 y el 31: anota fecha, hora, personas y menú, pide el anticipo con la foto del comprobante y le pasa la lista ordenada por día."),
 dict(id="flors", nombre="Flor's Catering", tipo="navidad", orden=-29, hecho="que hacen eventos de empresa, bodas y quince años",
      arma_texto="Para diciembre le podemos dejar su WhatsApp tomando solo los encargos de cenas y eventos de fin de año: anota fecha, hora, personas y menú, pide el anticipo con la foto del comprobante y le pasa la lista ordenada por día."),
 dict(id="moderna", nombre="Panadería Moderna", tipo="navidad", orden=-28, hecho="que tienen cuatro sucursales en San Pedro y que los pedidos y encargos van por este WhatsApp"),
 dict(id="carnitas", nombre="Carnitas Típicas al Carbón", tipo="domicilio", orden=-12, hecho="que ponen este número en sus publicaciones para los pedidos"),
 # Pollerías, asaderos y comedores con pedidos por WhatsApp
 dict(id="xpressarte", nombre="XpressArte Gourmet", tipo="reservas", orden=20, hecho="que sus videos pasan seguido de las 100 mil vistas y que la gente pregunta el precio en los comentarios"),
 dict(id="lobby", nombre="Restaurante El Lobby", tipo="pedidos", orden=21, hecho="sus videos del pollo chuco y la yuca, y que la gente pregunta la dirección para llegar",
      arma_texto="Armamos que cada pedido para recoger quede tomado completo, con la hora y el total, y entre solo a una pantalla en la cocina, y que al que pregunta la dirección le llegue la ubicación al instante. Y usted ve en el celular lo que vende cada día."),
 dict(id="chinchilete", nombre="Chinchilete", tipo="sucursales", orden=22, hecho="su video de más de 400 mil vistas y que cada sucursal tiene su propio número"),
 dict(id="aurora", nombre="Aurora Café + Cocina", tipo="pedidos", orden=23, hecho="que suben videos casi todos los días y que la gente pregunta si tienen postres para cumpleaños",
      arma_texto="Armamos que cada encargo de postre o pedido quede tomado completo, con día, hora y total, y entre solo a una pantalla en la cocina, para que nada se pierda en el chat. Y usted ve en el celular lo que vende cada día."),
 dict(id="mas-alitas", nombre="MÁS Alitas", tipo="pedidos", orden=24, hecho="sus videos y que la gente pregunta la dirección y el horario"),
 dict(id="melt-plaza-san-rafael", nombre="Melt Plaza San Rafael", tipo="pedidos", orden=25, hecho="que tienen 4.5 estrellas con más de 800 reseñas en Google, y eso no se logra fácil"),
 dict(id="furia", nombre="Pollos Furia", tipo="pedidos", orden=26, hecho="que tienen varios videos de más de un millón de vistas y que ustedes mismos contestan muchísimos comentarios",
      arma_texto="Armamos que los pedidos que entran por este WhatsApp queden tomados completos, con el total, y entren solos a una pantalla en la cocina, igual que los de su página. Y usted ve en el celular lo que vende cada día y lo más pedido."),
 dict(id="la-vela", nombre="Restaurante La Vela", tipo="reservas", orden=27, hecho="su video de casi 50 mil vistas y que la gente pide el menú en los comentarios"),
 # Reservaciones
 dict(id="el-fierro", nombre="El Fierro", tipo="reservas", orden=30, hecho="que las reservaciones van por este número"),
 dict(id="fogao", nombre="Fogão", tipo="reservas", orden=31, hecho="que ponen este número en cada video para reservar"),
 dict(id="solana", nombre="Solana Bistro", tipo="reservas", orden=32, hecho="que el número de su bio es el de reservaciones"),
 dict(id="xunan", nombre="Xunán", tipo="reservas", orden=33, hecho="que sacan menús nuevos seguido, como el de chiles en nogada"),
 dict(id="palco", nombre="PALCO", tipo="reservas", orden=34, hecho="su video de más de 60 mil vistas y que preguntan dónde están en San Pedro",
      arma_texto="Armamos que cada reservación para los partidos quede anotada completa, con día, hora y personas, en la sucursal que le toca, y a usted solo le toque confirmarla desde el celular."),
 dict(id="placita-susy", nombre="La Placita de Susy", tipo="reservas", orden=35, busco="doña Susy", busco_corto="doña Susy", hecho="que la gente les escribe para reservar las cenas y los días especiales"),
 # Cadenas pequeñas (plan Cadena)
 dict(id="tamago", nombre="Tamago", tipo="sucursales", orden=40, hecho="que ya tienen cinco sucursales y que en TikTok la gente pregunta si un producto está en una sucursal o solo en otra"),
 dict(id="criollos", nombre="Criollos", tipo="sucursales", orden=41, hecho="que tienen sucursales en Ciudad Nueva y en el Centro Histórico y que publican todos los días"),
 dict(id="cafetano", nombre="Cafetano", tipo="sucursales", orden=42, busco="don Mirko Cuculiza", busco_corto="don Mirko", hecho="que ya tienen cinco cafeterías y además venden café empacado",
      arma_texto="Armamos que los pedidos para recoger y los de café empacado queden tomados completos, con el total, y entren solos a la cafetería que le toca. Y usted ve cada cafetería en el celular."),
 dict(id="tio-dolmo", nombre="Tío Dolmo", tipo="sucursales", orden=43, busco="don Steven Flores", busco_corto="don Steven", hecho="que tienen sucursales en toda la zona norte y que en TikTok preguntan mucho dónde quedan y el menú"),
]

# ---- Prospectos que no estaban en la página (se agregan) ----
AGREGAR = [
 dict(id="carnitas-mary", nombre="Carnitas Mary", numero="50498469394", ciudad="Tegucigalpa y Comayagüela", tipo="domicilio", orden=-15, prioridad=1, contacto="Carlos",
      busco="a Carlos", busco_corto="Carlos",
      hecho="que tienen dos puntos, en el mercado de Comayagüela y en la Loarque, y que en TikTok mucha gente pregunta dónde quedan y a qué número pedir",
      arma_texto="Armamos que cada pedido de este número, a domicilio o para recoger, quede tomado completo con el total y entre solo al punto que le toca. Y ustedes ven los dos puntos en el celular.",
      nota="Investigado 10 nov. 9846-9394 es el número de domicilio y menú; no está confirmado que tenga WhatsApp (si no abre, mandar DM en TikTok @carnitas_mary). Carlos es la cara del TikTok; que Mary sea la mamá no está confirmado. No mencionar comentarios políticos de la campaña de desayunos."),
 dict(id="super-burras", nombre="Súper Burras", numero="50494690000", ciudad="San Pedro Sula", tipo="domicilio", orden=-14, prioridad=1, contacto="don Adonay Chirinos",
      busco="a don Adonay", busco_corto="don Adonay",
      hecho="que tienen varios puntos en San Pedro, que están contratando para crecer y que el Burra Delivery va todo por este número",
      arma_texto="Armamos que cada pedido del delivery quede tomado completo, con la dirección y el total, y entre solo a la cocina, y que la gente pueda dejar su pedido listo para recoger en el punto que le queda cerca. Y usted ve en el celular lo que vende cada punto.",
      nota="Investigado 10 nov. 9469-0000 es el Burra Delivery; no está confirmado que tenga WhatsApp (si no abre, DM en TikTok @super.burras). Venden de 6 a 10 am: escribir después de las 10:30. No mencionar comentarios de 'caro' ni la queja del queso."),
 dict(id="toretos", nombre="Toreto's Grill", numero="50496123466", ciudad="San Pedro Sula", tipo="repartos", orden=-13, prioridad=1, contacto="",
      hecho="los videos del Colocho y que todo va por este WhatsApp, también el domicilio con sus propios repartidores",
      nota="Investigado 15-19 oct; nunca se le escribió. Farem Cartagena es muy probablemente el dueño (IG farem_cartagena), no confirmado: nunca decir que el Colocho es el dueño. Plan Negocio (repartidores propios)."),
 dict(id="el-pollo-loco", nombre="El Pollo Loco", numero="50497730804", ciudad="Tegucigalpa", tipo="pedidos", orden=-11, prioridad=1, contacto="",
      hecho="que abrieron el local nuevo frente a la Católica y que este número viene en su menú",
      arma_texto="Armamos que los pedidos para recoger de este WhatsApp queden tomados completos, con la hora y el total, y entren solos a una pantalla en la cocina, aparte de los de PedidosYa. Y usted ve en el celular lo que vende cada día.",
      nota="Investigado 17 oct; nunca se le escribió. Domicilio solo por PedidosYa: no hablar mal de PedidosYa ni hacer cuentas de comisión."),
 dict(id="fusion-food", nombre="Fusion Food", numero="50487570555", ciudad="Gracias, Lempira", tipo="domicilio", orden=10, prioridad=2, contacto="",
      hecho="que toman los pedidos a domicilio por este WhatsApp y que el plato del día cambia todos los días",
      nota="Investigado oct; nunca se le escribió. Correo fusionfoodhn@gmail.com. Venden alitas: no mandarle material de otros negocios de alitas."),
 dict(id="mag-pollo", nombre="Mag Pollo", numero="50431548697", ciudad="San Pedro Sula", tipo="sucursales", orden=11, prioridad=2, contacto="don Magdiel",
      busco="a don Magdiel", busco_corto="don Magdiel",
      hecho="que tienen cuatro sucursales en San Pedro y que los pedidos llegan a este número",
      nota="Su WhatsApp ya tiene menú automático por palabras: no decir que no contestan. Nunca mencionar a Coco Chicken ni compartir nada de ellos."),
 dict(id="alitas-aleman", nombre="Alitas de la Alemán", numero="50496036732", ciudad="Tegucigalpa", tipo="pedidos", orden=12, prioridad=2, contacto="",
      hecho="que tienen cuatro números para los pedidos y que en los comentarios mucha gente pregunta a cuál escribir",
      arma_texto="Armamos que un solo WhatsApp tome los pedidos completos, con la salsa, la dirección y el total, y los pase solos a una pantalla en la cocina, para no depender de que alguien conteste el teléfono. Y usted ve en el celular lo que vende cada día.",
      nota="Los 4 números son de llamada; no publican WhatsApp. Si este no abre en WhatsApp, mandar el mismo texto por DM de Instagram. Su video corto ya existe (alitas-aleman/alitas-aleman-corto.mp4): solo a ellos, nunca a Tito Wings ni Loca Luna."),
]

# ---- Ya recibieron la pregunta por el dueño y no tienen seguimiento nuevo ----
SEGUIMIENTO_NUEVO = {
 "camino-valle": dict(nombre="Pupusería Camino del Valle", tipo="sucursales", hecho="en su página que tienen 13 sucursales y que cada una tiene su propio WhatsApp"),
 "carniceros": dict(nombre="Carniceros", tipo="reservas", hecho="los videos del tomahawk y del almuerzo catracho, y que las reservaciones son por este número",
      arma_texto="Para diciembre armamos que cada reservación de grupo o cena de fin de año quede anotada completa, con día, hora y personas, y al gerente solo le toque confirmarla desde el celular."),
 "cholucarnes": dict(nombre="Cholucarnes & Más", tipo="navidad", hecho="que hacen envíos y que la gente les pregunta horarios, menú y si mandan a Tegus"),
}

def seguimiento_completo(p):
    arma = p.get("arma_texto") or ARMA[p["tipo"]]
    return f"Buenas tardes, ¿cómo está? Disculpe la insistencia: le escribí hace unos días y no le conté para qué era. {QUIEN} Vi {p['hecho']}. {arma} {CIERRE}"

# ---- Recuperar conversaciones que quedaron colgadas ----
ARGENTINO = ("Buenas, ¿cómo está? Le pido disculpas por no haberle contestado antes: usted me dijo \"hable amigo\" y se me quedó pendiente. "
  f"{QUIEN} Vi su video de más de 4 millones de vistas y que los pedidos van a dos números distintos. "
  "Armamos que los pedidos de los dos números queden tomados completos, con el total, y entren solos a una pantalla en el food truck, y que el dueño vea en el celular lo que se vendió cada día. "
  "Para diciembre también puede tomar encargos con anticipo. Lo armamos con su menú y los primeros 30 días no paga nada. "
  "Si le interesa, con gusto le cuento por aquí mismo cómo funciona o le mando una demostración. Y si usted no es el dueño, ¿me haría el favor de pasarle este mensaje?")
ARGENTINO_SEG = ("Buenas tardes, ¿cómo está? Solo para preguntarle si pudo ver mi mensaje sobre los pedidos de Carnes El Argentino. "
  f"Por si le sirve verlo, aquí está una demostración que armamos con otro negocio: {DEMO}")
FOGOS = ("Buenas tardes, ¿cómo está? Le escribe Rodrigo Herrera, de Clientia Tech. Hablamos en octubre sobre Fogos y le pido disculpas por desaparecerme. "
  "Desde entonces terminamos el sistema: cada pedido de WhatsApp queda tomado completo con el total, entra solo a una pantalla en la cocina y al cliente le llega el aviso cuando está listo. "
  "Lo armamos con su menú y los primeros 30 días no pagan nada. Si le interesa, con gusto se lo cuento por aquí mismo o le mando una demostración. ¿Me haría el favor de comentárselo al dueño?")
FOGOS_SEG = f"Buenas tardes, ¿cómo está? Solo para dejarle la demostración por si la quiere ver con calma: {DEMO} . Si le sirve para Fogos, me avisa y se lo armamos con su menú."

def wa(numero, texto):
    return f"https://wa.me/{numero}?text={urllib.parse.quote(texto)}"

if __name__ == "__main__":
    out = {"nuevos": {}, "agregar": {}, "seguimiento": {}, "ultimo_todos": ultimo}
    for p in NUEVOS + AGREGAR:
        p.setdefault("busco_corto", None)
        if p.get("busco") and p["busco"].startswith("a "):
            p["busco"] = p["busco"][2:]
        p["msgs"] = dict(primero=primero(p), seguimiento=seguimiento(p), ultimo=ultimo(p), presentacion=presentacion(p))
    for k, p in SEGUIMIENTO_NUEVO.items():
        p["msgs"] = dict(seguimiento=seguimiento_completo(p), ultimo=ultimo(p))
    data = {"nuevos": {p["id"]: p for p in NUEVOS}, "agregar": {p["id"]: p for p in AGREGAR}, "seguimiento": SEGUIMIENTO_NUEVO,
            "argentino": [ARGENTINO, ARGENTINO_SEG], "fogos": [FOGOS, FOGOS_SEG], "demo": DEMO}
    pathlib.Path(__file__).with_name("prospectos_hn.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print("ok", len(NUEVOS), len(AGREGAR), len(SEGUIMIENTO_NUEVO))

NUMEROS = {"alondra":"50494482267","flors":"50497903488","moderna":"50433295152","carnitas":"50432515476","xpressarte":"50488738716",
 "lobby":"50433248847","chinchilete":"50493503003","aurora":"50499580608","mas-alitas":"50493811886","melt-plaza-san-rafael":"50498059681",
 "furia":"50489190689","la-vela":"50492562140","el-fierro":"50488771011","fogao":"50498375285","solana":"50499900394","xunan":"50497242787",
 "palco":"50431857304","placita-susy":"50431719613","tamago":"50494565677","criollos":"50498152006","cafetano":"50494880328","tio-dolmo":"50496062672",
 "camino-valle":"50487391718","carniceros":"50487908323","cholucarnes":"50494538798"}
CIUDAD = {"alondra":"Tegucigalpa","flors":"San Pedro Sula","moderna":"San Pedro Sula","carnitas":"Danlí","xpressarte":"Comayagua","lobby":"Siguatepeque",
 "chinchilete":"Tegucigalpa y Santa Lucía","aurora":"San Pedro Sula","mas-alitas":"San Pedro Sula","melt-plaza-san-rafael":"Tegucigalpa","furia":"San Pedro Sula",
 "la-vela":"Puerto Cortés","el-fierro":"San Pedro Sula","fogao":"Siguatepeque","solana":"Tegucigalpa","xunan":"Tegucigalpa","palco":"San Pedro Sula y El Progreso",
 "placita-susy":"Santa Lucía","tamago":"Tegucigalpa y San Pedro Sula","criollos":"Tegucigalpa","cafetano":"Tegucigalpa","tio-dolmo":"Zona norte",
 "camino-valle":"Tegucigalpa","carniceros":"San Pedro Sula","cholucarnes":"Choluteca"}
NOTAS = {"la-vela":"Facebook lo marcaba como cerrado: confirmar que sigue abierto antes de escribir.",
 "placita-susy":"El número lo publicó un cliente, no el negocio.","furia":"Ya tienen página de pedidos.",
 "carniceros":"Es del grupo Meat House: puede que ya tengan proveedor.","cholucarnes":"También tiene correo en Harvey: no mandar las dos cosas el mismo día.",
 "chinchilete":"Otro número: 9559-3803.","criollos":"Ciudad Nueva: 3382-3618.","melt-plaza-san-rafael":"El dato sale de Google Maps.",
 "camino-valle":"Número de la Col. 21 de Octubre."}
PLAN = {"navidad":"Navidad","pedidos":"Pedidos","domicilio":"Pedidos","reservas":"Pedidos","sucursales":"Cadena","repartos":"Negocio"}

def bloque(nombre, numero, ciudad, plan, nota, msgs, etiquetas):
    tel = f"+{numero[:3]} {numero[3:7]}-{numero[7:]}"
    out = [f"### {nombre}", f"{ciudad} · {tel} · plan probable: **{plan}**" + (f"  \n{nota}" if nota else ""), ""]
    for (titulo, texto) in zip(etiquetas, msgs):
        out += [f"**{titulo}** · [Abrir en WhatsApp]({wa(numero, texto)})", "", f"> {texto}", ""]
    return out

def escribir_md():
    L = ["# Mensajes listos por negocio · Honduras", "",
         "16 de noviembre de 2026. Los mismos mensajes que tiene la [página de WhatsApp](https://claude.ai/artifact/SUV15bH8BrWtgiokUBPc59), por si la página no abre. "
         "Cada botón abre WhatsApp con el texto puesto: revisalo y mandalo. Qué contestar después: [GUIA-DE-VENTA.md](GUIA-DE-VENTA.md).", "",
         "**Cuándo va cada uno:** el primero cuando te toque (máximo 10 nuevos por día). El seguimiento a los 3 días si no contestan. El último 7 días después. Después de eso, no se insiste.", "",
         "**Antes de mandar:** abrí su TikTok o Facebook un minuto y confirmá que el dato del mensaje sigue siendo cierto. Los datos salen de sus propias redes o páginas, revisados entre el 17 de octubre y el 10 de noviembre.", "",
         "## 1. Mandar ya: conversaciones que se quedaron colgadas", ""]
    L += bloque("Carnes El Argentino", "50499292592", "Tegucigalpa (food truck)", "Pedidos o Negocio",
                "Contestó \"hable amigo\" el 26 de octubre y nunca se le contestó. Otro número: 9880-8505.", [ARGENTINO, ARGENTINO_SEG], ["Mensaje de hoy", "Si no contesta en 3 días"])
    L += bloque("Fogos Grill", "50498448314", "San Pedro Sula", "Pedidos",
                "La encargada contestó el 17 de octubre (\"Dígame, soy la encargada\") y se le mandó el video con el logo equivocado. No mencionar los comentarios de \"carne de papel bond\".", [FOGOS, FOGOS_SEG], ["Mensaje de hoy", "Si no contesta en 3 días"])
    L += ["## 2. Ya les escribiste en octubre y falta el seguimiento", "", "Recibieron solo la pregunta por el dueño. Este seguimiento ya les cuenta para qué era.", ""]
    for k, p in SEGUIMIENTO_NUEVO.items():
        L += bloque(p["nombre"], NUMEROS[k], CIUDAD[k], PLAN[p["tipo"]], NOTAS.get(k, ""), [seguimiento_completo(p), ultimo(p)], ["Seguimiento", "Último (7 días después)"])
    L += ["Los otros que esperan seguimiento (Hijo de Pupa, David's Crab, El Inge del Taco, Legato, Asados Mary, La Cacerola, Pollos Mamavila, Condys Grill, Típicos Nicolle) "
          "ya tienen su seguimiento escrito en la página; ahí aparecen solos cuando les toca.", "",
          "## 3. Primeros mensajes nuevos, en este orden", "",
          "Arriba de todos van los 8 que ya tenían el mensaje nuevo desde el 10 de noviembre y todavía no se mandaron (Home Food HN, Típicos Olanchanos, La Esquina del Sabor Garífuna, Pollos Sierra's, The Soul Chkn Club, Tato's Wings, Cric Cric Burger y Asados Marina): están en la página.", ""]
    todos = []
    for p in AGREGAR: todos.append((p["orden"], p["nombre"], p["numero"], p["ciudad"], PLAN[p["tipo"]], p["nota"], p["msgs"]))
    for p in NUEVOS: todos.append((p["orden"], p["nombre"], NUMEROS[p["id"]], CIUDAD[p["id"]], PLAN[p["tipo"]], NOTAS.get(p["id"], ""), p["msgs"]))
    todos.sort(key=lambda t: t[0])
    secc = None
    for orden, nombre, numero, ciudad, plan, nota, m in todos:
        s = "Navidad: mandar del 16 al 22 de noviembre" if plan == "Navidad" else ("Pollerías, asaderos y comedores" if orden < 40 else "Cadenas pequeñas")
        if s != secc:
            L += [f"#### {s}", ""]; secc = s
        L += bloque(nombre, numero, ciudad, plan, nota, [m["primero"], m["seguimiento"], m["ultimo"]], ["Primer mensaje", "Seguimiento (día 3)", "Último (día 10)"])
    L += ["## 4. A quién no escribirle", "",
          "- Hoteles, glamping y resorts (Copantl, Honduras Maya, Marina Copán, Tela Marine, Telamar, ThauRana, Granja D'Elia).",
          "- Franquicias y cadenas grandes (Pollos El Hondureño, Tapachula, Café Welchez, Basilio's).",
          "- Gambos (rechazó) y Con Sabor a Pueblo (ya es conversación de cliente, no de campaña).",
          "- Tito Wings mientras se trabaja con Loca Luna y Alitas de la Alemán (son rivales).",
          "- Guatemala y El Salvador, hasta tener el primer cliente en Honduras.", ""]
    pathlib.Path(__file__).with_name("MENSAJES-LISTOS.md").write_text("\n".join(L))

if __name__ == "__main__":
    escribir_md()
