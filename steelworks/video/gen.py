#!/usr/bin/env python3
"""Steel Works · video de propuesta, estilo película de producto de Apple (HyperFrames, 1920x1080).

Fondo claro, tipografía grande y limpia, cada frase entra desenfocada y se asienta. Muestra la página
nueva dentro de un MacBook y el asistente de WhatsApp dentro de un iPhone: primero cómo está hoy su
página, luego cómo puede verse. Cierra con el outro de Clientia Tech.

Música: "Clean Cut" (120 BPM). Un compás = 2 s y el primer golpe fuerte cae en 0:08.017, así que
toda escena empieza en T(n) = 0.017 + 2n. Requisitos junto al script: musica-clean.mp3, capturas/
(sitio-web.jpg y sitio-movil.jpg, la página completa), ../fotos y deps/node_modules con gsap@3.14.2
y @fontsource/inter-tight.

    python3 gen.py && cd build && hyperframes render . -o ../steelworks-propuesta.mp4 -q high
"""
import json, os, shutil
from outro import ribbons

HERE = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(HERE, "..", "fotos")
DEPS = os.environ.get("DEPS", os.path.join(HERE, "deps", "node_modules"))
OUT = os.path.join(HERE, "build")
WHATSAPP = "+1 (765) 543-4251"
MARK = json.load(open(os.path.join(HERE, "clientia-mark.json")))
T = lambda n: round(0.017 + 2 * n, 3)
SCENES = [("intro", 0, 4), ("claim", 4, 7), ("hoy", 7, 13), ("mac", 13, 20), ("bot", 20, 25),
          ("both", 25, 28), ("offer", 28, 31), ("cta", 31, 34), ("end", 34, 38)]
TOTAL = T(38)

# where each view of the site starts in the full-page capture (css px at 1440 wide), and its caption
STOPS = [(0, "Su lema y sus trabajos, en la portada."), (971, "Lo que fabrican, con fotos reales."),
         (1877, "El cliente pone su medida y ve el precio."), (2821, "Sus dos sucursales, con horario y WhatsApp.")]
# their real shop listings (steelworkshn.com/tienda, 13 oct 2026) and what a visitor runs into
SHOP = [("p-120-1016", "Adorno Barra 120-1016", "L62.71"), ("p-120-1048", "Adorno Barra 120-1048", "L84.42"),
        ("p-110-702", "Adorno Poste 110-702", "L64.94")]
# a glass card per view of the site, floating over the MacBook's edge (label, value, detail)
CHIPS = [("Portada", "Todo, en hierro.", "Su lema, con sus trabajos reales"),
         ("Galería", "Fotos reales del taller", "Puertas, cercos y protecciones"),
         ("Cotizador", "L 36,300 – 50,100", "Portón forjado · 3.6 × 2.4 m"),
         ("Sucursales", "Tegucigalpa y San Pedro Sula", "Horario, teléfonos y cómo llegar")]
HOY = ["Las piezas solo tienen código, sin nombre ni uso.",
       "Para pedir un portón, solo hay un carrito de piezas.",
       "No se ve cómo queda puesta en un portón.",
       "Google la describe como «Just another WordPress site».",
       "El blog no se actualiza desde agosto de 2021.",
       "Sin horario y el formulario de contacto no funciona."]
CHAT = [("out", "Hola, ¿cuánto me sale un portón de 4 por 2.5?"),
        ("in", 'Perfecto: portón, 4 × 2.5 m. ¿Qué estilo te gusta? Estos son trabajos nuestros:'
               '<div class="gal"><figure><img src="assets/obra-puerta-arco.jpg"><b>Moderno</b></figure>'
               '<figure><img src="assets/obra-cerco.jpg"><b>Forjado</b></figure>'
               '<figure><img src="assets/obra-puerta-cnc.jpg"><b>Calado CNC</b></figure></div>'),
        ("out", "Forjado clásico"),
        ("in", "Precio estimado: <b>L 42,000 a L 58,000</b>. Incluye fabricación, pintura e instalación."),
        ("out", "Agendar visita para medir"),
        ("in", "Listo, Carlos. Visita para medir: jueves, de 8 a 10 a. m. Su ficha ya la tiene la sucursal.")]
OFFER = [("Página nueva", "Con sus trabajos, su catálogo y precios claros."),
         ("Asistente de WhatsApp", "Cotiza a cualquier hora: medida, estilo, precio y cita."),
         ("Ficha a la sucursal", "Cada cliente llega con lo que pidió y su cita."),
         ("Reporte semanal", "Cuántos cotizaron, cuántas visitas y cuántas ventas.")]


def words(text, cls="w"):
    return " ".join(f'<span class="{cls}">{w}</span>' for w in text.split())


def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    A = os.path.join(OUT, "assets")
    os.makedirs(os.path.join(A, "fonts"))
    shutil.copy(os.path.join(HERE, "musica-clean.mp3"), os.path.join(A, "musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), os.path.join(A, "gsap.min.js"))
    for w in (300, 400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"),
                    os.path.join(A, "fonts", f"it-{w}.woff2"))
    for f in os.listdir(os.path.join(HERE, "capturas")):
        shutil.copy(os.path.join(HERE, "capturas", f), os.path.join(A, f))
    for f in ("obra-puerta-arco", "obra-cerco", "obra-puerta-cnc", "logo-actual") + tuple(p for p, _, _ in SHOP):
        shutil.copy(os.path.join(FOTOS, f + ".jpg"), os.path.join(A, f + ".jpg"))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(OUT, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "steelworks-propuesta", "name": "Casa Digital x Steel Works"}, open(os.path.join(OUT, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{T(s)}" data-duration="{round(T(e) - T(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    def mac(mid, img):
        return (f'<div class="mac" id="{mid}"><div class="lid"><div class="scr"><img class="page" id="{mid}-pg" src="assets/{img}"></div>'
                f'<i class="cam-dot"></i></div><div class="base"><i></i></div></div>')

    def phone(pid, inner):
        return f'<div class="phone" id="{pid}"><div class="pscr">{inner}</div><i class="island"></i></div>'

    hoy = "".join(f'<div class="hrow" id="hr{i}"><i>{i % 3 + 1}</i><b>{t}</b></div>' for i, t in enumerate(HOY))
    tiles = "".join(f'<div class="tile"><img src="assets/{p}.jpg"><span>{n}</span><b>{pr}</b><em>Añadir al carrito</em></div>'
                    for p, n, pr in SHOP)
    caps = "".join(f'<div class="chip c{i}" id="mc{i}"><span>{a}</span><b>{b}</b><i>{c}</i></div>' for i, (a, b, c) in enumerate(CHIPS))
    chat = "".join(f'<div class="bub {s}" id="cb{i}">{h}<time>9:41</time></div>' for i, (s, h) in enumerate(CHAT))
    wa = (f'<div class="wa"><div class="wa-top"><div class="av"><img src="assets/simbolo.svg"></div><div><b>Steel Works</b><span>en línea</span></div></div>'
          f'<div class="wa-body"><div class="wa-scroll" id="wsc">{chat}</div></div></div>')
    shutil.copy(os.path.join(HERE, "..", "logo", "simbolo", "steelworks-logo-simbolo-naranja.svg"), os.path.join(A, "simbolo.svg"))
    offer = "".join(f'<div class="of" id="of{i}"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(OFFER))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          <div class="center">
            <div class="kick" id="ik">{words("Casa Digital presenta")}</div>
            <div class="h1" id="it">{words("Para Steel Works.")}</div>
            <div class="sub" id="is">{words("Más de 40 años haciendo hierro.")}</div>
          </div>''', "dark"),
        scene("claim", f'''
          <div class="center">
            <div class="h1" id="c1">{words("Su trabajo es de primera.")}</div>
            <div class="h1 grey" id="c2">{words("Su página también debería serlo.")}</div>
          </div>'''),
        scene("hoy", f'''
          <div class="hoy-l"><div class="h1" id="hh">Hoy.</div><div class="sub" id="hs">{words("Lo que ve un cliente en su página.")}</div>
            <div class="hlist">{hoy}</div></div>
          <div class="old" id="old"><div class="obar"><i></i><i></i><i></i><span id="ourl">steelworkshn.com/tienda</span></div>
            <div class="ov" id="ov1"><div class="omenu"><img src="assets/logo-actual.jpg"><span>TIENDA</span><span>GALERÍA</span><span>NOSOTROS</span><span>BLOG</span><span>CONTACTO</span></div>
              <div class="stitle">TIENDA</div><div class="tiles">{tiles}</div>
              <i class="pin" id="pn0" style="left:40px;top:520px">1</i><i class="pin" id="pn1" style="left:560px;top:592px">2</i><i class="pin" id="pn2" style="left:850px;top:190px">3</i></div>
            <div class="ov" id="ov2"><div class="omenu"><img src="assets/logo-actual.jpg"><span>TIENDA</span><span>GALERÍA</span><span>NOSOTROS</span><span>BLOG</span><span>CONTACTO</span></div>
              <div class="gres"><span>steelworkshn.com</span><b>STEEL WORKS</b><p>Just another WordPress site</p></div>
              <div class="gres blog"><span>steelworkshn.com/blog</span><b>Blog</b><p>Última entrada: agosto de 2021</p></div>
              <div class="gres form"><span>Contacto</span><b>Formulario de contacto</b><p class="err">El formulario no envía el mensaje.</p></div>
              <i class="pin" id="pn3" style="left:62px;top:184px">1</i><i class="pin" id="pn4" style="left:62px;top:334px">2</i><i class="pin" id="pn5" style="left:62px;top:483px">3</i></div></div>'''),
        scene("mac", f'''
          <div class="mtitle" id="mt">{words("Así puede verse.")}</div>
          {mac("m1", "sitio-web.jpg")}
          {caps}'''),
        scene("bot", f'''
          <div class="bot-l">
            <div class="h2" id="bh">{words("Un asistente que cotiza por ustedes.")}</div>
            <div class="sub" id="bs">{words("Medida, estilo, precio y cita. A cualquier hora, por WhatsApp.")}</div>
          </div>
          {phone("p1", wa)}'''),
        scene("both", f'''
          <div class="btitle" id="bt">{words("En cualquier pantalla.")}</div>
          {mac("m2", "sitio-web.jpg")}
          {phone("p2", '<img class="page" id="p2-pg" src="assets/sitio-movil.jpg">')}'''),
        scene("offer", f'''
          <div class="otitle" id="ot">{words("Lo que construimos para Steel Works.")}</div>
          <div class="offers">{offer}</div>'''),
        scene("cta", f'''
          <div class="center">
            <div class="h1" id="k1">{words("La demo ya está lista.")}</div>
            <div class="h1 grey" id="k2">{words("Se la mostramos en 15 minutos.")}</div>
            <div class="wa-num" id="k3">WhatsApp {WHATSAPP}</div>
            <div class="sig" id="k4">Rodrigo Herrera · Casa Digital</div>
          </div>'''),
        scene("end", f'''
          <div class="endglow" id="eglow"></div>
          <div class="ribwrap">{ribbons("re", ["#3E7BFA", "#8E7CFF", "#5AC8FA", "#FFFFFF", "#BF5AF2", "#64D2FF"])}</div>
          <div class="center">
            <div class="mark-wrap" id="mwrap">
              <svg class="mark" viewBox="{MARK["viewBox"]}">
                <defs>
                  <linearGradient id="sweepg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
                  <linearGradient id="markfill" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#C9D6FF"/><stop offset=".55" stop-color="#FFFFFF"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
                  <clipPath id="mclip">{mark_paths}</clipPath>
                </defs>
                <g id="mstroke" fill="none" stroke="#fff" stroke-width="1.6" stroke-linejoin="round">{mark_paths}</g>
                <g id="mfill" fill="url(#markfill)">{mark_paths}</g>
                <g clip-path="url(#mclip)"><rect id="msweep" x="-200" y="0" width="160" height="600" fill="url(#sweepg)" transform="rotate(20)"/></g>
              </svg>
            </div>
            <div class="lockup"><span class="by" id="lby">by</span> <span class="ct">{"".join(f'<span class="lt">{ch if ch != " " else "&nbsp;"}</span>' for ch in "Clientia Tech")}</span></div>
          </div>''', "black"),
    ])

    js = (JS.replace("$SCENES", json.dumps([[i, T(a), T(b)] for i, a, b in SCENES])).replace("$TOTAL", str(TOTAL))
          .replace("$STOPS", json.dumps([y for y, _ in STOPS])).replace("$NCHAT", str(len(CHAT))))
    html = (HTML.replace("$body", body).replace("$css", CSS).replace("$js", js)
            .replace("$total", str(TOTAL)).replace("$title", "Casa Digital x Steel Works"))
    open(os.path.join(OUT, "index.html"), "w").write(html)
    return OUT


HTML = r'''<!doctype html>
<html lang="es" data-resolution="landscape">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>$title</title>
<script src="assets/gsap.min.js"></script>
<style>$css</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="$total" data-width="1920" data-height="1080">
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="$total" data-fade-out="3" data-track-index="1"></audio>
$body
</div>
<script>$js</script>
</body>
</html>
'''

CSS = r'''
@font-face{font-family:"IT";src:url("assets/fonts/it-300.woff2") format("woff2");font-weight:300;}
@font-face{font-family:"IT";src:url("assets/fonts/it-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"IT";src:url("assets/fonts/it-500.woff2") format("woff2");font-weight:500;}
@font-face{font-family:"IT";src:url("assets/fonts/it-600.woff2") format("woff2");font-weight:600;}
@font-face{font-family:"IT";src:url("assets/fonts/it-700.woff2") format("woff2");font-weight:700;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1920px;height:1080px;overflow:hidden;background:#F5F5F7;}
#root{position:relative;width:1920px;height:1080px;background:#F5F5F7;color:#1D1D1F;font-family:"IT",sans-serif;-webkit-font-smoothing:antialiased;}
.scene{position:absolute;inset:0;overflow:hidden;background:#F5F5F7;}
.scene.dark{background:#000;color:#F5F5F7;}
.scene.black{background:#000;color:#F5F5F7;}
.cam{position:absolute;inset:0;transform-origin:50% 50%;}
.center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 160px;}
.w{display:inline-block;}
.kick{font:500 34px/1.2 "IT";color:#86868B;margin-bottom:26px;}
.h1{font:600 112px/1.04 "IT";letter-spacing:-.035em;}
.h1.grey{color:#86868B;margin-top:8px;}
.h2{font:600 84px/1.04 "IT";letter-spacing:-.035em;}
.sub{margin-top:30px;font:400 40px/1.3 "IT";color:#6E6E73;letter-spacing:-.01em;}
.dark .sub{color:#86868B;}
/* hoy */
.hoy-l{position:absolute;left:130px;top:170px;width:640px;}
.hoy-l .h1{font-size:140px;}
.hoy-l .sub{font-size:34px;margin-top:18px;}
.hlist{position:relative;margin-top:56px;height:420px;}
.hrow{position:absolute;left:0;right:0;display:flex;gap:22px;align-items:flex-start;}
.hrow:nth-child(3n+1){top:0}.hrow:nth-child(3n+2){top:130px}.hrow:nth-child(3n){top:260px}
.hrow i,.pin{flex:none;width:44px;height:44px;border-radius:50%;background:#FF3B30;color:#fff;font:600 22px/44px "IT";text-align:center;font-style:normal;}
.hrow b{font:500 33px/1.25 "IT";color:#1D1D1F;letter-spacing:-.012em;}
.old{position:absolute;right:120px;top:170px;width:980px;height:740px;border-radius:22px;background:#FFFFFF;overflow:hidden;box-shadow:0 40px 90px rgba(0,0,0,.10);}
.obar{height:52px;background:#ECECEE;display:flex;align-items:center;gap:10px;padding:0 22px;}
.obar i{width:14px;height:14px;border-radius:50%;background:#D1D1D6;}
.obar span{margin:0 auto;font:500 20px "IT";color:#86868B;}
.ov{position:absolute;left:0;right:0;top:52px;bottom:0;}
.pin{position:absolute;box-shadow:0 0 0 8px rgba(255,59,48,.18);}
.omenu{display:flex;align-items:center;gap:26px;padding:22px 40px;border-bottom:1px solid #EEE;font:600 15px Arial,sans-serif;color:#2B4F8C;}
.omenu img{width:150px;margin-right:auto;}
.stitle{padding:26px 40px 12px;font:700 26px Arial,sans-serif;color:#333;}
.tiles{display:flex;gap:24px;padding:0 40px;}
.tile{flex:1;font-family:Arial,sans-serif;text-align:center;}
.tile img{width:100%;height:360px;object-fit:contain;background:#fff;display:block;}
.tile span{display:block;margin-top:10px;font-size:17px;color:#333;}
.tile b{display:block;margin-top:6px;font-size:17px;color:#2B4F8C;}
.tile em{display:inline-block;margin-top:12px;padding:9px 16px;background:#2B4F8C;color:#fff;font:600 13px Arial,sans-serif;font-style:normal;}
.gres{margin:60px 40px 0 140px;font-family:Arial,sans-serif;}
.gres span{font-size:17px;color:#4D5156;}
.gres b{display:block;margin-top:6px;font:400 32px Arial,sans-serif;color:#1A0DAB;}
.gres p{margin-top:8px;font-size:20px;color:#4D5156;}
.gres p.err{color:#C0392B;}
/* MacBook */
.mac{position:absolute;left:50%;width:1240px;margin-left:-620px;transform-origin:50% 100%;}
.lid{position:relative;background:#0B0B0C;border-radius:26px 26px 0 0;padding:20px 20px 26px;box-shadow:inset 0 0 0 2px #2C2C2E;}
.cam-dot{position:absolute;left:50%;top:7px;width:7px;height:7px;margin-left:-3px;border-radius:50%;background:#2C2C2E;}
.scr{position:relative;width:1200px;height:750px;overflow:hidden;border-radius:6px;background:#141516;}
.scr .page{position:absolute;left:0;top:0;width:1200px;height:auto;display:block;}
.base{position:relative;height:30px;margin:0 -90px;background:linear-gradient(#E3E3E8,#B9B9BF 70%,#9E9EA4);border-radius:0 0 24px 24px;}
.base i{position:absolute;left:50%;top:0;width:220px;height:12px;margin-left:-110px;background:#C7C7CC;border-radius:0 0 12px 12px;}
#m1{top:150px;}
.mtitle{position:absolute;left:0;right:0;top:40px;text-align:center;font:600 72px/1 "IT";letter-spacing:-.035em;}
.chip{position:absolute;z-index:5;opacity:0;padding:22px 28px;border-radius:22px;background:rgba(255,255,255,.74);-webkit-backdrop-filter:blur(24px) saturate(1.6);backdrop-filter:blur(24px) saturate(1.6);box-shadow:0 1px 0 rgba(255,255,255,.9) inset,0 30px 70px rgba(0,0,0,.14);}
.chip span{display:block;font:600 18px "IT";color:#FF6A13;letter-spacing:.02em;text-transform:uppercase;}
.chip b{display:block;margin-top:6px;font:600 38px/1.1 "IT";letter-spacing:-.025em;color:#1D1D1F;}
.chip i{display:block;margin-top:6px;font:400 22px "IT";font-style:normal;color:#6E6E73;}
.chip.c0{left:1270px;top:250px;}.chip.c1{left:150px;top:560px;}.chip.c2{left:1300px;top:520px;}.chip.c3{left:130px;top:780px;}
/* iPhone */
.phone{position:absolute;width:430px;height:900px;border-radius:72px;background:#0B0B0C;padding:14px;box-shadow:inset 0 0 0 2px #3A3A3C,0 50px 100px rgba(0,0,0,.18);}
.pscr{width:100%;height:100%;border-radius:58px;overflow:hidden;position:relative;background:#fff;}
.pscr .page{position:absolute;left:0;top:0;width:402px;height:auto;}
.island{position:absolute;left:50%;top:30px;width:126px;height:36px;margin-left:-63px;border-radius:20px;background:#000;}
#p1{left:1220px;top:90px;}
.bot-l{position:absolute;left:150px;top:330px;width:900px;}
.wa{position:absolute;inset:0;background:#EFEAE2;display:flex;flex-direction:column;}
.wa-top{height:150px;background:#F7F7F7;display:flex;align-items:flex-end;gap:14px;padding:0 24px 18px;border-bottom:1px solid #E5E5EA;}
.wa-top .av{width:54px;height:54px;border-radius:50%;background:#131415;display:grid;place-items:center;}
.wa-top .av img{height:30px;}
.wa-top b{display:block;font:600 24px "IT";}
.wa-top span{font:400 17px "IT";color:#86868B;}
.wa-body{flex:1;position:relative;overflow:hidden;}
.wa-scroll{position:absolute;left:0;right:0;top:0;padding:18px 16px;display:flex;flex-direction:column;gap:12px;}
.bub{max-width:86%;padding:12px 14px 8px;border-radius:16px;font:400 21px/1.35 "IT";color:#111B21;background:#fff;align-self:flex-start;opacity:0;box-shadow:0 1px 1px rgba(0,0,0,.08);}
.bub.out{background:#D9FDD3;align-self:flex-end;}
.bub time{display:block;text-align:right;font-size:14px;color:#8696A0;margin-top:2px;}
.gal{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px;}
.gal figure{margin:0;}
.gal img{width:100%;aspect-ratio:3/4;object-fit:cover;border-radius:8px;display:block;}
.gal b{display:block;font:500 15px "IT";margin-top:4px;}
/* both */
.btitle{position:absolute;left:0;right:0;top:60px;text-align:center;font:600 72px/1 "IT";letter-spacing:-.035em;}
#m2{top:250px;margin-left:-860px;transform:scale(.78);transform-origin:0 0;}
#p2{left:1300px;top:200px;transform:scale(.86);transform-origin:0 0;}
/* offer */
.otitle{position:absolute;left:150px;top:150px;font:600 84px/1.04 "IT";letter-spacing:-.035em;}
.offers{position:absolute;left:150px;right:150px;top:390px;display:grid;grid-template-columns:1fr 1fr;gap:80px 120px;}
.of b{display:block;font:600 52px/1.1 "IT";letter-spacing:-.03em;}
.of span{display:block;margin-top:14px;font:400 34px/1.35 "IT";color:#6E6E73;}
/* cta */
.wa-num{margin-top:70px;font:600 64px/1 "IT";letter-spacing:-.02em;color:#1D1D1F;}
.sig{margin-top:26px;font:400 32px "IT";color:#86868B;}
/* end */
.endglow{position:absolute;width:1300px;height:1300px;left:310px;top:-110px;border-radius:50%;background:radial-gradient(closest-side,rgba(90,130,255,.30),rgba(0,0,0,0));}
.ribwrap{position:absolute;left:420px;top:-420px;width:1080px;height:1920px;transform:rotate(90deg);}
.rib{position:absolute;inset:0;mix-blend-mode:screen;transform-origin:50% 50%;}
.rl{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible;}
.glowl{filter:blur(42px);opacity:.9;}
.corel{filter:blur(1.5px);}
.mark-wrap{width:330px;height:390px;}
.mark{width:100%;height:100%;overflow:visible;}
.lockup{margin-top:60px;font:600 64px "IT";letter-spacing:-.025em;white-space:nowrap;}
.by{font-weight:300;color:#86868B;display:inline-block;}
.ct{color:#F5F5F7;}
.lt{display:inline-block;}
'''

JS = r'''
const tl = gsap.timeline({ paused: true });
const T = n => +(0.017 + 2 * n).toFixed(3);
const SOFT = "expo.out";
function rise(sel, t, o) {
  o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y || 40, filter: "blur(" + (o.blur || 18) + "px)" },
    { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d || 1.4, ease: SOFT, stagger: o.st || 0.07 }, t);
}
function out(sel, t, d) { tl.to(sel, { opacity: 0, filter: "blur(14px)", duration: d || .6, ease: "power2.in" }, t); }
const SC = $SCENES;
SC.forEach(([id, s, e]) => tl.fromTo("#cam-" + id, { scale: 1.0 }, { scale: 1.025, duration: e - s, ease: "none" }, s));

// 1 · intro, on black
rise("#ik .w", T(0) + .4, { d: 1.6 });
rise("#it .w", T(1), { st: .12, d: 1.6 });
rise("#is .w", T(2.5), { st: .06 });
out("#cam-intro .center", T(4) - .6);

// 2 · the claim
rise("#c1 .w", T(4), { st: .08 });
rise("#c2 .w", T(5), { st: .08 });
out("#cam-claim .center", T(7) - .6);

// 3 · today: their site as a customer sees it
rise("#hh", T(7), {});
rise("#hs .w", T(7) + .3, { st: .05 });
tl.fromTo("#old", { opacity: 0, y: 60, scale: .97 }, { opacity: 1, y: 0, scale: 1, duration: 1.6, ease: SOFT }, T(7) + .2);
tl.set("#ov2", { opacity: 0 }, 0);
[0, 1, 2].forEach(i => { rise("#hr" + i, T(7.6) + i * 1.1, { y: 24, blur: 10, d: 1.1 });
  tl.fromTo("#pn" + i, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: .6, ease: "back.out(2)" }, T(7.6) + i * 1.1); });
tl.to(["#hr0", "#hr1", "#hr2", "#ov1"], { opacity: 0, duration: .6, ease: "power2.in" }, T(10) - .5);
tl.to("#ov2", { opacity: 1, duration: .8, ease: SOFT }, T(10));
tl.set("#ourl", { textContent: "steelworkshn.com" }, T(10));
[3, 4, 5].forEach((n, i) => { rise("#hr" + n, T(10.2) + i * 1.1, { y: 24, blur: 10, d: 1.1 });
  tl.fromTo("#pn" + n, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: .6, ease: "back.out(2)" }, T(10.2) + i * 1.1); });
out("#cam-hoy", T(13) - .6);

// 4 · how it can look: the MacBook opens onto the new site and scrolls through it
const PX = 1200 / 1440;  // css px of the capture -> px on the MacBook screen
const STOPS = $STOPS;
rise("#mt .w", T(13), { st: .08 });
tl.fromTo("#m1", { opacity: 0, y: 220, rotationX: 28, transformPerspective: 2200 }, { opacity: 1, y: 0, rotationX: 0, duration: 2.4, ease: SOFT }, T(13) + .2);
STOPS.forEach((y, i) => {
  const t = T(14 + i * 1.5);
  if (i) tl.to("#m1-pg", { y: -y * PX, duration: 1.6, ease: "power3.inOut" }, t - .6);
  const side = i % 2 ? -1 : 1;  // chips alternate sides; the laptop turns a few degrees toward each one
  tl.to("#m1", { rotationY: i ? -side * 4 : 0, duration: 1.6, ease: "power3.inOut" }, t - .6);
  if (!i) return;  // the front page already carries its own glass cards
  tl.fromTo("#mc" + i, { opacity: 0, x: side * 60, y: 10, scale: .96, filter: "blur(12px)" }, { opacity: 1, x: 0, y: 0, scale: 1, filter: "blur(0px)", duration: 1.1, ease: SOFT }, t - .1);
  tl.to("#mc" + i, { y: -8, duration: 2, ease: "sine.inOut" }, t + 1);
  if (i < STOPS.length - 1) tl.to("#mc" + i, { opacity: 0, x: side * 30, filter: "blur(8px)", duration: .5, ease: "power2.in" }, T(14 + (i + 1) * 1.5) - .7);
});
out("#cam-mac", T(20) - .6);

// 5 · the assistant in an iPhone
rise("#bh .w", T(20), { st: .07 });
rise("#bs .w", T(20.5), { st: .04 });
tl.fromTo("#p1", { opacity: 0, y: 160, rotationY: -16, transformPerspective: 2200 }, { opacity: 1, y: 0, rotationY: -4, duration: 2, ease: SOFT }, T(20) + .2);
tl.to("#p1", { rotationY: 4, duration: 8, ease: "sine.inOut" }, T(21));
const wsc = document.getElementById("wsc"), wbody = wsc.parentNode, bubs = [...wsc.children];
for (let i = 0; i < $NCHAT; i++) {
  const t = T(21) + i * 0.9;
  tl.fromTo("#cb" + i, { opacity: 0, y: 24, scale: .97 }, { opacity: 1, y: 0, scale: 1, duration: .55, ease: "back.out(1.5)" }, t);
  const bottom = bubs[i].offsetTop + bubs[i].offsetHeight + 24, shift = Math.max(0, bottom - wbody.clientHeight);
  if (shift > 0) tl.to(wsc, { y: -shift, duration: .55, ease: "power2.out" }, t - .1);
}
out("#cam-bot", T(25) - .6);

// 6 · any screen: desktop and phone scroll together
rise("#bt .w", T(25), { st: .08 });
tl.fromTo("#m2", { opacity: 0, x: -120 }, { opacity: 1, x: 0, duration: 1.8, ease: SOFT }, T(25) + .2);
tl.fromTo("#p2", { opacity: 0, x: 120 }, { opacity: 1, x: 0, duration: 1.8, ease: SOFT }, T(25) + .35);
tl.to("#m2-pg", { y: -971 * PX, duration: 4, ease: "power2.inOut" }, T(26));
tl.to("#p2-pg", { y: -1527, duration: 4, ease: "power2.inOut" }, T(26));
out("#cam-both", T(28) - .6);

// 7 · what we build
rise("#ot .w", T(28), { st: .06 });
[0, 1, 2, 3].forEach(i => rise("#of" + i, T(28.5) + i * .35, { y: 30, d: 1.2 }));
out("#cam-offer", T(31) - .6);

// 8 · CTA
rise("#k1 .w", T(31), { st: .08 });
rise("#k2 .w", T(31.75), { st: .08 });
rise("#k3", T(32.5), { d: 1.2 });
rise("#k4", T(32.5) + .4, { d: 1.2 });

// 9 · Clientia Tech: outline draws, locks on the next bar
function trails(rid, t0, dur, spin) {
  for (let i = 0; i < 6; i++) {
    const st = t0 + i * 0.22, len = 480 + (i % 3) * 170;
    tl.fromTo("." + rid + "-p" + i, { strokeDasharray: len + " 2000", strokeDashoffset: len }, { strokeDashoffset: -1000, duration: dur - i * 0.15, ease: "power2.inOut" }, st);
  }
  tl.fromTo("#" + rid, { rotation: spin[0], scale: spin[2], opacity: 0 }, { rotation: spin[1], scale: spin[3], opacity: 1, duration: dur, ease: "power1.inOut" }, t0);
}
const E0 = T(34), E1 = T(35);
document.querySelectorAll("#mstroke path").forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
trails("re", E0 - 0.2, 2.6, [20, -8, 1.6, 0.9]);
tl.to("#re", { scale: 3.2, opacity: 0, duration: 1.1, ease: "expo.out" }, E1);
tl.to("#mstroke path", { strokeDashoffset: 0, duration: 1.8, ease: "power2.inOut" }, E0 + .1);
tl.fromTo("#mfill", { opacity: 0 }, { opacity: 1, duration: .5, ease: "power2.out" }, E1);
tl.to("#mstroke", { opacity: 0, duration: .5 }, E1);
tl.fromTo("#mwrap", { scale: .92 }, { scale: 1, duration: 2.4, ease: SOFT }, E0);
tl.fromTo("#mwrap", { filter: "drop-shadow(0 0 0px rgba(140,170,255,0))" }, { filter: "drop-shadow(0 0 60px rgba(140,170,255,.65))", duration: .35, ease: "power2.out", yoyo: true, repeat: 1 }, E1);
tl.fromTo("#eglow", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: 1.6, ease: SOFT }, E1);
tl.fromTo("#msweep", { x: -200 }, { x: 900, duration: 1.4, ease: "power2.inOut" }, E1 + .5);
rise("#lby", E1 + .5, { d: 1.2 });
rise(".lt", E1 + .7, { d: 1.2, st: .035, y: 40, blur: 12 });
tl.to("#end .center, #eglow", { opacity: 0, duration: 1.4, ease: "power2.in" }, $TOTAL - 1.6);

window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
tl.seek(0);
'''

if __name__ == "__main__":
    print(build())
