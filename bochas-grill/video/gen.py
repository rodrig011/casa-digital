#!/usr/bin/env python3
"""Bocha's Grill pitch video v2 (2026-10-15), vertical 1080x1920 for WhatsApp.

rodrigo liked the question-method pitch from his "sell me this pen" reference but not the reference's
editing (2-word captions, opening on the owner's TikTok clips; see gen-v0-pip.py). So the script follows
/mnt/project-files/propuestas/metodos-video.md and the look is the one he liked: the Toreto's Grill
vertical video (dark, slow, soft lights, full phrases on top with gold keywords, the visual below,
"Still Buggin" with every scene on a bar line, Clientia Tech outro).

Story: Casa Digital -> "we could open with 'the best system in the world'... that's not how you sell" ->
"first, some questions" -> 4 questions, each with real comments from their TikTok (price unanswered,
Villanueva out of beans, 50 minutes in Choloma, the same plate in five branches) -> "if any answer was
'I don't know', that's what we solve" -> 4 answers in the same order (WhatsApp bot, stock + supplier,
live wait per branch, rating after every order) -> his own words about a franchise -> "we don't sell a
system" -> contact -> outro. Conversations, stock, times and ratings are examples, labelled on screen.
Helpers come from coco-chicken/video (gen2, gen3, gen6, gen10) and toretos-grill/video/gen.py.
"""
import importlib.util, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.path.join(HERE, "..", "..", "coco-chicken", "video")
sys.path.insert(0, CC)
import gen3, gen6  # noqa: E402
from gen2 import MARK, words, ribbons, DEPS  # noqa: E402
from gen6 import K, P0, BAR  # noqa: E402

_spec = importlib.util.spec_from_file_location("toretos_gen", os.path.join(HERE, "..", "..", "toretos-grill", "video", "gen.py"))
TG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TG)

SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "build")
SLUG = "bochas-grill-vertical"
SCENES = [("intro", 0, 3), ("nosale", 3, 6), ("secret", 6, 8), ("q1", 8, 11), ("q2", 11, 14), ("q3", 14, 17), ("q4", 17, 20),
          ("bridge", 20, 22), ("bot", 22, 27), ("supply", 27, 30), ("wait", 30, 33), ("rate", 33, 36), ("meta", 36, 40),
          ("close", 40, 43), ("us", 43, 46), ("end", 46, 50)]
TOTAL = K(50)


def gold(t):
    return f'<span class="gold">{words(t)}</span>'


def cm(text, i, pre="cm"):
    return f'<div class="cm" id="{pre}{i}"><div class="cm-h"><i></i>Comentario en su TikTok</div><p>{text}</p></div>'


CSS_B = r'''
/* Bocha's: their logo is a wide badge on white, so it sits on a white card instead of a circle */
.ilogo{width:440px;height:360px;border-radius:40px;background:#FAFCFC;box-shadow:0 0 0 3px rgba(242,181,68,.55),0 30px 90px rgba(216,38,28,.3);display:flex;align-items:center;justify-content:center;}
.ilogo img{width:92%;height:auto;object-fit:contain;object-position:50% 50%;}
.wa-av{background:#fff;}
.wa-av img{object-fit:contain;}
.iname{font-size:92px;}
/* the salesman line, struck out */
.pitchc{position:absolute;left:90px;right:90px;top:930px;padding:56px 50px;border-radius:40px;background:linear-gradient(180deg,#161618,#111113);box-shadow:0 0 0 1px rgba(255,255,255,.08),0 40px 100px rgba(0,0,0,.55);text-align:center;}
.pitchc .k{font-size:22px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#6E6E73;}
.pitchc p{margin-top:22px;font-size:58px;line-height:1.15;font-weight:600;letter-spacing:-.025em;color:#E5E5EA;position:relative;}
.strike{position:absolute;left:30px;right:30px;top:50%;height:9px;border-radius:5px;background:#FF453A;transform-origin:0 50%;box-shadow:0 0 28px rgba(255,69,58,.55);}
/* question number */
.qn{display:inline-flex;align-items:center;gap:14px;margin-bottom:30px;padding:12px 24px;border-radius:40px;background:rgba(242,181,68,.10);box-shadow:0 0 0 1px rgba(242,181,68,.35);font-size:26px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#F2B544;}
/* photos from their own videos */
.photo2{position:absolute;left:90px;width:900px;height:675px;border-radius:36px;overflow:hidden;box-shadow:0 0 0 1px rgba(255,255,255,.1),0 50px 120px rgba(0,0,0,.6);}
.photo2 img{width:100%;height:100%;object-fit:cover;}
.photo2 .cap2{position:absolute;left:24px;bottom:22px;font-size:20px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#fff;background:rgba(0,0,0,.55);padding:10px 16px;border-radius:12px;}
.cm.on-photo{position:absolute;left:130px;right:130px;}
.cm.on-photo p{font-size:40px;}
.bigmin{position:absolute;left:90px;right:90px;top:1360px;display:flex;align-items:baseline;justify-content:center;gap:24px;}
.bigmin b{font-size:240px;font-weight:600;letter-spacing:-.06em;line-height:1;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
.bigmin span{font-size:44px;color:#8E8E93;font-weight:500;}
/* answers: branch wait list and the owner alert reuse the riders/stock cards */
.rd.hot{background:rgba(255,69,58,.10);border-radius:24px;padding-left:20px;padding-right:20px;box-shadow:0 0 0 2px rgba(255,69,58,.45);}
.rd .st.bad{color:#FF6B5E;background:rgba(255,69,58,.12);}
.alert2{position:absolute;left:90px;width:900px;background:linear-gradient(180deg,#161618,#0F0F10);border-radius:36px;padding:30px 36px;display:flex;gap:24px;align-items:center;box-shadow:0 0 0 1px rgba(255,69,58,.4),0 40px 110px rgba(0,0,0,.6);}
.alert2 .ai{width:72px;height:72px;border-radius:20px;background:#D8261C;color:#fff;font-size:44px;font-weight:700;display:flex;align-items:center;justify-content:center;flex:none;}
.alert2 .k{font-size:22px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#8E8E93;}
.alert2 b{display:block;font-size:42px;font-weight:600;letter-spacing:-.02em;margin-top:6px;}
.alert2 span{display:block;font-size:26px;color:#8E8E93;margin-top:4px;}
'''

# vertical positions for the Bocha's scenes (after the Toreto's vertical rules)
CSS_BV = r'''
#nosale .left,#q1 .left,#q2 .left,#q3 .left,#q4 .left{top:100px;height:700px;}
.h1.q{font-size:84px;}
#q1 .cms{top:860px;}
#q2 .photo2{top:860px;} #q2 .cm.on-photo{top:1440px;}
#q3 .cms{top:900px;height:420px;}
#q4 .photo2{top:830px;} #q4 .cm.on-photo{top:1380px;} #q4 #q4c1{top:1620px;}
#wait .riders{top:820px;padding:30px 40px 30px;}
#wait .rd{padding:20px 0;grid-template-columns:1fr 170px 250px;}
#wait .rd.hot{padding:20px;}
#rate .chat2{top:860px;}
#rate .alert2{top:1460px;}
#close .shot{top:840px;}
'''


def build():
    proj = os.path.join(OUT, SLUG)
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    A = lambda *p: os.path.join(proj, "assets", *p)
    shutil.copy(os.path.join(SRC, "musica.mp3"), A("musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), A("gsap.min.js"))
    shutil.copy(os.path.join(DEPS, "@fontsource", "archivo-black", "files", "archivo-black-latin-400-normal.woff2"), A("fonts", "display.woff2"))
    for w in (300, 400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"), A("fonts", f"it-{w}.woff2"))
    for n in ("logo.png", "villa.jpg", "plato.jpg", "panel-m.jpg"):
        shutil.copy(os.path.join(SRC, n), A(n))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "bochas-grill-v2", "name": "Casa Digital x Bocha's Grill"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    # verbatim comments from redes/tiktok-comentarios.md
    q1c = "".join(cm(t, i, "q1c") for i, t in enumerate(["cuanto vale??", "pero cual es el precio", "alguien sabe los precios", "DIRECCIÓN SPS POR FAVOR... Y HORARIO"]))
    head = ('<div class="wa-h"><span class="bk">‹</span><div class="wa-av"><img src="assets/logo.png"></div>'
            '<div><b>Bocha\'s Grill</b><span>en línea</span></div></div>')
    order = ('<div class="oc-in"><div class="oc-k">Pedido #5120</div><div class="oc-t">Para recoger</div>'
             '<div class="oc-s">Bocha\'s Calpules · 7:30 pm</div>'
             '<div class="oc-r"><span>2 × Chicharrones de Carne</span><b>7:30</b></div>'
             '<div class="oc-s" style="margin-top:6px">con tajadas · aderezo de la casa aparte</div></div>')
    msgs = [("m1", '<div class="wb out">Esos L.139 ya con el envío? o hay q sumarle el delivery?<small>7:12 p. m.</small></div>'),
            ("t1", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m2", '<div class="wb in">¡Hola! Los L139 eran el Económico de Costilla o de Carne por Bip Bip, lunes, miércoles y viernes de septiembre. El envío lo cobra Bip Bip aparte.<small>7:12 p. m.</small></div>'),
            ("m3", '<div class="wb in">Hoy tenemos los nuevos Chicharrones de Carne 🔥 ¿Se los aparto para recoger?<small>7:12 p. m.</small></div>'),
            ("m4", '<div class="wb out">si, 2 para recoger en calpules a las 7:30<small>7:13 p. m.</small></div>'),
            ("t2", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m5", f'<div class="ocard">{order}</div>'),
            ("m6", '<div class="wb in">¡Listo! Ya está en la cocina de Calpules. Le aviso cuando esté listo.<small>7:13 p. m.</small></div>')]
    wa = (f'<div class="wa">{head}<div class="wa-msgs">' + "".join(f'<div class="slot" id="{i}">{h}</div>' for i, h in msgs)
          + '</div><div class="wa-in">Mensaje</div></div>')
    waits = [("SPS Stibys", "5 en cocina", "18 min", "ok", "✓ Bien"), ("SPS Calpules", "4 en cocina", "16 min", "ok", "✓ Bien"),
             ("El Progreso", "4 en cocina", "22 min", "ok", "✓ Bien"), ("Villanueva", "3 en cocina", "19 min", "ok", "✓ Bien"),
             ("Choloma", "6 en cocina", "41 min", "bad", "Avisando a 6")]
    wait_rows = "".join(f'<div class="rd{" hot" if c == "bad" else ""}" id="rd{i}"><div class="n">{n}<span>{s}</span></div><div class="c">{m}</div><div class="st {c}" id="rs{i}">{t}</div></div>'
                        for i, (n, s, m, c, t) in enumerate(waits))
    whys = ["Lo armamos con sus 5 sucursales.", "Funciona en su WhatsApp de siempre.", "Soporte por WhatsApp, en español."]
    whys_html = "".join(f'<div class="wy2" id="wy{i}"><i>✓</i><span>{words(t)}</span></div>' for i, t in enumerate(whys))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          <div class="sp sp-red" style="left:260px;top:-520px;width:1400px;height:1400px"></div>
          <div class="sp sp-gold" style="left:560px;top:520px;width:800px;height:800px"></div>
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("una propuesta para")}</div>
            <div class="ilogo" id="ilogo"><img src="assets/logo.png"></div>
            <div class="iname" id="iname">Bocha's Grill</div>
          </div>'''),
        scene("nosale", f'''
          <div class="sp sp-red" style="left:900px;top:-300px;width:1500px;height:1500px"></div>
          <div class="pitchc" id="pitch"><div class="k">Lo que dice cualquier vendedor</div><p>“Le instalamos el mejor sistema para restaurantes del mundo.”<i class="strike" id="strike" style="display:block"></i></p></div>
          <div class="left">
            <div class="lgrp" id="ng1"><div class="eb" id="n0">Podríamos empezar así</div><div class="h1" id="n1">{words("Con lo que")}</div><div class="h1" id="n2">{words("hace el sistema.")}</div></div>
            <div class="lgrp" id="ng2"><div class="h1" id="n3">{words("Pero así")}</div><div class="h1" id="n4">{gold("no se vende.")}</div></div>
          </div>'''),
        scene("secret", f'''
          <div class="sp sp-gold" style="left:260px;top:-300px;width:1400px;height:1400px"></div>
          <div class="center">
            <div class="wa-pill" id="sp0" style="background:rgba(242,181,68,.10);box-shadow:0 0 0 1px rgba(242,181,68,.35);color:#F2B544"><i style="background:#F2B544;box-shadow:0 0 0 6px rgba(242,181,68,.22)"></i>Antes de ofrecerle algo</div>
            <div class="h1" id="se1" style="font-size:124px">{words("Primero,")}</div>
            <div class="h1" id="se2" style="font-size:124px">{gold("unas preguntas.")}</div>
            <div class="sub" id="se3" style="max-width:860px">{words("Sobre sus cinco sucursales. Contéstelas usted.")}</div>
          </div>'''),
        scene("q1", f'''
          <div class="sp sp-gold" style="left:900px;top:-200px;width:1400px;height:1400px"></div>
          <div class="cms">{q1c}</div>
          <div class="left">
            <div class="qn" id="q1n">Pregunta 1</div>
            <div class="h1 q" id="q1a">{words("¿Cuántos le preguntan")}</div>
            <div class="h1 q" id="q1b">{words("el precio y")}</div>
            <div class="h1 q" id="q1d">{gold("nadie les contesta?")}</div>
          </div>
          <div class="foot" id="q1f">Comentarios reales en su TikTok @bochasgrill. Ninguno tiene respuesta del negocio.</div>'''),
        scene("q2", f'''
          <div class="sp sp-red" style="left:900px;top:-300px;width:1500px;height:1500px"></div>
          <div class="photo2" id="q2p"><img src="assets/villa.jpg"><div class="cap2">Bocha's Villanueva · su propio video</div></div>
          {cm("Fui al local de Villanueva, y no tenian NI FRIJOLES, NI CARNE ASADA NI INCURTIDO!", 0, "q2c").replace('class="cm"', 'class="cm on-photo"')}
          <div class="left">
            <div class="qn" id="q2n">Pregunta 2</div>
            <div class="h1 q" id="q2a">{words("¿Se enteró a tiempo")}</div>
            <div class="h1 q" id="q2b">{words("de que Villanueva")}</div>
            <div class="h1 q" id="q2d">{gold("se quedó sin frijoles?")}</div>
          </div>'''),
        scene("q3", f'''
          <div class="sp sp-gold" style="left:900px;top:-200px;width:1400px;height:1400px"></div>
          <div class="cms">{cm("ayer fui a Bonchas Choloma y me dijeron que debía esperar 50 minutos por la orden", 0, "q3c")}</div>
          <div class="bigmin" id="q3m"><b>50</b><span>minutos</span></div>
          <div class="left">
            <div class="qn" id="q3n">Pregunta 3</div>
            <div class="h1 q" id="q3a">{words("¿Sabe cuánto espera")}</div>
            <div class="h1 q" id="q3b">{words("hoy un cliente")}</div>
            <div class="h1 q" id="q3d">{gold("en Choloma?")}</div>
          </div>
          <div class="foot" id="q3f">Comentario real en su TikTok, septiembre 2026.</div>'''),
        scene("q4", f'''
          <div class="sp sp-red" style="left:900px;top:-300px;width:1500px;height:1500px"></div>
          <div class="photo2" id="q4p"><img src="assets/plato.jpg"><div class="cap2">El aderezo de la casa · su propio video</div></div>
          {cm("hoy pedí y ni el aderezo me pusieron", 0, "q4c").replace('class="cm"', 'class="cm on-photo"')}
          {cm("varias veces me e quejado x carne tan reseca y dura en la stibys", 1, "q4c").replace('class="cm"', 'class="cm on-photo"')}
          <div class="left">
            <div class="qn" id="q4n">Pregunta 4</div>
            <div class="h1 q" id="q4a">{words("¿Sus cinco sucursales")}</div>
            <div class="h1 q" id="q4b">{words("sirven")}</div>
            <div class="h1 q" id="q4d">{gold("el mismo plato?")}</div>
          </div>'''),
        scene("bridge", f'''
          <div class="sp sp-gold" style="left:260px;top:-300px;width:1400px;height:1400px"></div>
          <div class="center">
            <div class="h1" id="br1">{words("Si alguna respuesta")}</div>
            <div class="h1" id="br2">{words("fue “no sé”,")}</div>
            <div class="h1" id="br3">{gold("eso es lo que")}</div>
            <div class="h1" id="br4">{gold("resolvemos.")}</div>
          </div>'''),
        scene("bot", f'''
          <div class="sp sp-green" style="left:950px;top:-250px;width:1400px;height:1400px"></div>
          <div class="ph-stage">{gen3.phone(wa, "phw", dark=True)}</div>
          <div class="left">
            <div class="lgrp" id="bg1"><div class="eb g" id="b10">Respuesta 1 · al instante</div><div class="h1" id="b11">{words("Su WhatsApp")}</div><div class="h1" id="b12">{gold("contesta solo.")}</div></div>
            <div class="lgrp" id="bg2"><div class="eb g" id="b20">Con la promo y sus condiciones</div><div class="h1" id="b21">{words("Explica el precio")}</div><div class="h1" id="b22">{gold("sin confusión.")}</div></div>
            <div class="lgrp" id="bg3"><div class="eb g" id="b30">En la sucursal que el cliente diga</div><div class="h1" id="b31">{words("Y toma el pedido")}</div><div class="h1" id="b32">{gold("para recoger.")}</div></div>
          </div>
          <div class="demo" id="bdemo">Conversación de ejemplo · la pregunta y la promo son reales</div>'''),
        scene("supply", f'''
          <div class="sp sp-gold" style="left:900px;top:-300px;width:1400px;height:1400px"></div>
          <div class="stk" id="stk"><div class="k">Inventario · Bocha's Villanueva</div>
            <div class="row"><b>Frijoles</b><span id="pl">4 <small>lb</small></span></div>
            <div class="bar"><i id="plb"></i></div><div class="min">Mínimo: 15 lb</div></div>
          <div class="chat2" id="chat2"><div class="hd"><i>🫘</i><div>Abarrotería<span>proveedor de Villanueva</span></div></div>
            <div class="b out" id="pm1"><div class="tag">Aviso automático</div>Buenas, le escribe Bocha's Grill Villanueva. Nos quedan 4 lb de frijoles. ¿Nos trae 30 lb mañana temprano?<small>6:10 pm <em>✓✓</em></small></div>
            <div class="b in" id="pm2">Claro, mañana a las 9 se los llevo.<small>6:14 pm</small></div></div>
          <div class="left">
            <div class="eb g" id="s0">Respuesta 2 · Inventario</div>
            <div class="h1 m" id="s1">{words("Se acaban los frijoles,")}</div>
            <div class="h1 m" id="s2">{gold("el proveedor ya sabe.")}</div>
            <div class="sub" id="s3">{words("Cada sucursal tiene su mínimo. Cuando algo baja, el panel le escribe solo al proveedor y le avisa a usted.")}</div>
          </div>
          <div class="demo" id="sdemo">Ejemplo</div>'''),
        scene("wait", f'''
          <div class="sp sp-red" style="left:900px;top:-300px;width:1400px;height:1400px"></div>
          <div class="riders" id="riders"><div class="k">Espera ahora · 7:30 pm</div>{wait_rows}</div>
          <div class="left">
            <div class="eb g" id="w0">Respuesta 3 · Cocina</div>
            <div class="h1 m" id="w1">{words("La espera de")}</div>
            <div class="h1 m" id="w2">{words("cada sucursal,")}</div>
            <div class="h1 m" id="w3">{gold("en vivo.")}</div>
            <div class="sub" id="w4">{words("Cada pedido lleva su reloj. Si una sucursal se atrasa, usted lo ve y el bot les avisa a los clientes que esperan.")}</div>
          </div>
          <div class="demo" id="wdemo">Ejemplo</div>'''),
        scene("rate", f'''
          <div class="sp sp-green" style="left:900px;top:-300px;width:1400px;height:1400px"></div>
          <div class="chat2" id="rchat"><div class="hd"><i>⭐</i><div>Cliente de Choloma<span>después de su pedido</span></div></div>
            <div class="b out" id="rm1"><div class="tag">El bot pregunta solo</div>¿Cómo estuvo su pedido de Bocha's Choloma? Del 1 al 5 ⭐<small>8:02 pm <em>✓✓</em></small></div>
            <div class="b in" id="rm2">2. me tocó sin aderezo<small>8:03 pm</small></div></div>
          <div class="alert2" id="ralert"><div class="ai">!</div><div><div class="k">Su panel · Choloma</div><b>Faltó el aderezo</b><span>3 clientes hoy · repasar la ficha con el turno de la noche</span></div></div>
          <div class="left">
            <div class="eb g" id="r0">Respuesta 4 · Calidad</div>
            <div class="h1 m" id="r1">{words("Cada cliente califica,")}</div>
            <div class="h1 m" id="r2">{gold("usted se entera hoy.")}</div>
            <div class="sub" id="r3">{words("Las quejas llegan por sucursal el mismo día, y no semanas después en un comentario.")}</div>
          </div>
          <div class="demo" id="rdemo">Ejemplo</div>'''),
        scene("meta", f'''
          <div class="sp sp-red" style="left:900px;top:-200px;width:1300px;height:1300px"></div>
          <div class="quote" id="quote"><div class="h"><img src="assets/logo.png" style="background:#fff;object-fit:contain">Bocha10, en su TikTok @bochas10</div><p>“Quiero compartirles mi emprendimiento que hoy en día va hacia una franquicia”</p></div>
          <div class="goal" id="goal"><div class="k">Sucursales listas para copiarse</div>
            <div class="row"><b><span id="ng">0</span></b><span>de 5</span></div>
            <div class="bar"><i id="gb"></i></div><div class="s">Misma ficha, mismos tiempos, mismo inventario mínimo.</div></div>
          <div class="left">
            <div class="eb g" id="g0">Su meta</div>
            <div class="h1 m" id="g1">{words("Una franquicia")}</div>
            <div class="h1 m" id="g2">{words("funciona cuando")}</div>
            <div class="h1 m" id="g3">{gold("cada local hace lo mismo.")}</div>
            <div class="sub" id="g4">{words("Sin que usted tenga que estar en las cinco a la vez.")}</div>
          </div>
          <div class="demo" id="gdemo">Cita real · conteo de ejemplo</div>'''),
        scene("close", f'''
          <div class="sp sp-gold" style="left:700px;top:-300px;width:1500px;height:1500px"></div>
          <div class="shot" id="shot"><img src="assets/panel-m.jpg"></div>
          <div class="left">
            <div class="lgrp" id="cg1"><div class="eb g" id="c0">Panel Bocha's Grill</div><div class="h1 m" id="c1">{words("No vendemos")}</div><div class="h1 m" id="c2">{gold("un sistema.")}</div></div>
            <div class="lgrp" id="cg2"><div class="h1 m" id="c3">{words("Primero preguntamos,")}</div><div class="h1 m" id="c4">{words("y resolvemos lo que")}</div><div class="h1 m" id="c5">{gold("Bocha's Grill necesita.")}</div></div>
          </div>
          <div class="demo" id="cdemo">Panel demo · datos de ejemplo</div>'''),
        scene("us", f'''
          <div class="sp sp-gold" style="left:900px;top:-200px;width:1400px;height:1400px"></div>
          <div class="left">
            <div class="eb g" id="u0">Casa Digital</div>
            <div class="h1 m" id="u1">{words("Escríbanos y le mostramos")}</div>
            <div class="h1 m" id="u2">{gold("exactamente cómo.")}</div>
            <div class="whys2">{whys_html}</div>
          </div>
          <div class="cta2" id="cta">
            <div class="ic">{gen3.HOUSE}</div>
            <div class="t">Casa Digital</div>
            <div class="s">Se lo mostramos en 15 minutos.</div>
            <div class="wa2"><span>WhatsApp</span>{gen3.WHATSAPP}</div>
            <div class="who">Rodrigo Herrera</div>
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
          </div>''', "endscene"),
    ])

    css = (gen3.CSS.replace("$heroB", "#2a0806").replace("$hero", "#D8261C").replace("$acc", "#F2B544").replace("$pri", "#F2B544")
           .replace("$washA", "rgba(0,0,0,0)").replace("$washB", "rgba(0,0,0,0)").replace("$sitebg", "#0B141A").replace("$siteink", "#fff")
           .replace("$dweight", "400").replace("$dcase", "uppercase").replace("$dtrack", "-0.01em")
           .replace("$italface", "").replace("$ital", '"Display"').replace("$introsizepx", "112px"))
    css += TG.CSS_BASE + TG.CSS_T + CSS_B + TG.CSS_V + CSS_BV
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    j6 = gen6.JS
    helpers = TG.JS_T[:TG.JS_T.index("// 1 · intro")]
    js = (j6[:j6.index("// 1 · intro")] + helpers + JS_B
          + re.sub(r"K\((\d+(?:\.\d+)?)\)", lambda m: f"K({float(m.group(1)) + 9:g})", j6[j6.index("// 11 · outro"):])
          ).replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = (gen3.HTML.replace("$title", "Casa Digital x Bocha's Grill").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)).replace('data-fade-out="2.5"', 'data-fade-out="4"'))
    html = (html.replace('content="width=1920, height=1080"', 'content="width=1080, height=1920"')
            .replace('data-width="1920" data-height="1080"', 'data-width="1080" data-height="1920"'))
    n = iter(range(100))  # soft lights kept on the narrow frame, alternating high and low
    html = re.sub(r'(<div class="sp sp-\w+") style="[^"]*"', lambda m: m.group(1) + (' style="left:-260px;top:%dpx;width:1600px;height:1600px"' % (-500 if next(n) % 2 == 0 else 700)), html)
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


JS_B = r'''
// 1 · intro
rise("#icd", 0.4, { d: 2 });
rise("#ipres .w", K(.9), { d: 1.6, st: .12 });
tl.fromTo("#ilogo", { opacity: 0, scale: .9, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(1.3));
tl.fromTo("#iname", { opacity: 0, y: 30, filter: "blur(20px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.4, ease: SOFT }, K(1.7));

// 2 · what not to do: the salesman line, struck out
rise("#n0", K(3), { d: 1.2 }); rise("#n1 .w", K(3) + .3); rise("#n2 .w", K(3) + .6);
tl.fromTo("#pitch", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(3) + .4);
tl.fromTo("#strike", { scaleX: 0, rotation: -5 }, { scaleX: 1, rotation: -5, duration: .9, ease: "power3.inOut" }, K(4.3));
tl.to("#pitch p", { color: "#6E6E73", duration: .8 }, K(4.5));
out("#ng1", K(4.7) - .8);
rise("#n3 .w", K(4.7)); rise("#n4 .w", K(4.7) + .45, { d: 1.8 });

// 3 · the refrain
rise("#sp0", K(6), { d: 1.4 });
rise("#se1 .w", K(6) + .3, { d: 1.8, st: .12 });
rise("#se2 .w", K(6.6), { d: 2, st: .12 });
rise("#se3 .w", K(7.1), { st: .03 });

// 4 · question 1: the price, asked and never answered
rise("#q1n", K(8), { d: 1.2 }); rise("#q1a .w", K(8) + .3); rise("#q1b .w", K(8) + .6); rise("#q1d .w", K(8) + .9, { d: 1.8 });
[8.6, 9.0, 9.4, 9.8].forEach((k, i) => rise("#q1c" + i, K(k), { y: 40, d: 1.6 }));
rise("#q1f", K(9.2), { d: 1.2 });

// 5 · question 2: Villanueva out of beans
rise("#q2n", K(11), { d: 1.2 }); rise("#q2a .w", K(11) + .3); rise("#q2b .w", K(11) + .6); rise("#q2d .w", K(11) + .9, { d: 1.8 });
tl.fromTo("#q2p", { opacity: 0, y: 70, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(11.3));
tl.fromTo("#q2p img", { scale: 1.06 }, { scale: 1, duration: K(14) - K(11.3), ease: "none" }, K(11.3));
rise("#q2c0", K(12.2), { y: 40, d: 1.6 });

// 6 · question 3: 50 minutes in Choloma
rise("#q3n", K(14), { d: 1.2 }); rise("#q3a .w", K(14) + .3); rise("#q3b .w", K(14) + .6); rise("#q3d .w", K(14) + .9, { d: 1.8 });
rise("#q3c0", K(14.6), { y: 40, d: 1.6 });
tl.fromTo("#q3m", { opacity: 0, scale: .9, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(15.4));
rise("#q3f", K(15), { d: 1.2 });

// 7 · question 4: the same plate in five branches
rise("#q4n", K(17), { d: 1.2 }); rise("#q4a .w", K(17) + .3); rise("#q4b .w", K(17) + .6); rise("#q4d .w", K(17) + .9, { d: 1.8 });
tl.fromTo("#q4p", { opacity: 0, y: 70, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(17.3));
tl.fromTo("#q4p img", { scale: 1.06 }, { scale: 1, duration: K(20) - K(17.3), ease: "none" }, K(17.3));
rise("#q4c0", K(18.1), { y: 40, d: 1.6 }); rise("#q4c1", K(18.7), { y: 40, d: 1.6 });

// 8 · bridge
rise("#br1 .w", K(20), { d: 1.8, st: .12 }); rise("#br2 .w", K(20.4), { d: 1.8, st: .12 });
rise("#br3 .w", K(21), { d: 2, st: .12 }); rise("#br4 .w", K(21.3), { d: 2, st: .12 });

// 9 · answer 1: their WhatsApp answers the real L139 question and takes a pickup order (5 bars)
tl.fromTo("#phw", { y: 700, rotationY: -16, rotationX: 6 }, { y: 0, rotationY: -6, rotationX: 2, duration: 2.4, ease: SOFT }, K(22));
tl.to("#phw", { rotationY: 4, rotationX: 0, duration: K(27) - K(23), ease: "sine.inOut" }, K(23));
rise("#bdemo", K(22.5), { d: 1.2 });
rise("#b10", K(22), { d: 1.2 }); rise("#b11 .w", K(22) + .3); rise("#b12 .w", K(22) + .6);
show("m1", K(22.5)); show("t1", K(23)); dots("t1", K(23) + .3); hide("t1", K(23.5)); show("m2", K(23.5));
out("#bg1", K(24) - .8);
rise("#b20", K(24), { d: 1.2 }); rise("#b21 .w", K(24) + .3); rise("#b22 .w", K(24) + .6);
show("m3", K(24.3)); show("m4", K(25));
out("#bg2", K(25.4) - .8);
rise("#b30", K(25.4), { d: 1.2 }); rise("#b31 .w", K(25.4) + .3); rise("#b32 .w", K(25.4) + .6);
show("t2", K(25.4)); dots("t2", K(25.4) + .3); hide("t2", K(25.9)); show("m5", K(25.9)); show("m6", K(26.4));

// 10 · answer 2: stock drops, the supplier is told by itself
rise("#s0", K(27), { d: 1.2 }); rise("#s1 .w", K(27) + .3); rise("#s2 .w", K(27) + .6, { d: 1.8 });
rise("#s3 .w", K(28), { st: .03 });
tl.fromTo("#stk", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(27) + .3);
tl.fromTo("#plb", { scaleX: 1 }, { scaleX: .27, duration: 1.6, ease: FINE }, K(27.5));
tl.fromTo("#chat2", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.6, ease: SOFT }, K(28));
rise("#pm1", K(28.3), { y: 20, d: 1.2 });
rise("#pm2", K(29.1), { y: 20, d: 1.2 });
rise("#sdemo", K(27.6), { d: 1.2 });

// 11 · answer 3: wait per branch, live
rise("#w0", K(30), { d: 1.2 }); rise("#w1 .w", K(30) + .3); rise("#w2 .w", K(30) + .6); rise("#w3 .w", K(30) + .9, { d: 1.8 });
rise("#w4 .w", K(31.2), { st: .03 });
tl.fromTo("#riders", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(30) + .3);
[30.6, 30.9, 31.2, 31.5, 31.8].forEach((k, i) => rise("#rd" + i, K(k), { y: 20, d: 1.2 }));
tl.fromTo("#rd4", { scale: 1 }, { scale: 1.025, duration: .5, yoyo: true, repeat: 1, ease: "sine.inOut" }, K(32.3));
rise("#wdemo", K(30.6), { d: 1.2 });

// 12 · answer 4: every customer rates, the owner hears it the same day
rise("#r0", K(33), { d: 1.2 }); rise("#r1 .w", K(33) + .3); rise("#r2 .w", K(33) + .6, { d: 1.8 });
rise("#r3 .w", K(34), { st: .03 });
tl.fromTo("#rchat", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(33) + .3);
rise("#rm1", K(33.5), { y: 20, d: 1.2 });
rise("#rm2", K(34.2), { y: 20, d: 1.2 });
tl.fromTo("#ralert", { opacity: 0, y: 50, scale: .97 }, { opacity: 1, y: 0, scale: 1, duration: 1.4, ease: SOFT }, K(34.9));
rise("#rdemo", K(33.6), { d: 1.2 });

// 13 · his own words: a franchise
rise("#g0", K(36), { d: 1.2 }); rise("#g1 .w", K(36) + .3); rise("#g2 .w", K(36) + .6); rise("#g3 .w", K(36) + .9, { d: 1.8 });
rise("#g4 .w", K(37.4), { st: .03 });
tl.fromTo("#quote", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(36) + .3);
tl.fromTo("#goal", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.8, ease: SOFT }, K(36.8));
tl.fromTo("#gb", { scaleX: 0 }, { scaleX: .4, duration: 2.4, ease: FINE }, K(37.3));
count("ng", 0, 2, K(37.3), n => String(n), 2.4);
rise("#gdemo", K(36.6), { d: 1.2 });

// 14 · we don't sell a system (their real panel)
tl.fromTo("#shot", { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(40) + .2);
tl.fromTo("#shot img", { scale: 1 }, { scale: 1.035, duration: K(43) - K(40), ease: "none", transformOrigin: "30% 30%" }, K(40));
rise("#c0", K(40), { d: 1.2 }); rise("#c1 .w", K(40) + .3); rise("#c2 .w", K(40) + .6, { d: 1.8 });
out("#cg1", K(41.5) - .8);
rise("#c3 .w", K(41.5)); rise("#c4 .w", K(41.5) + .35); rise("#c5 .w", K(41.5) + .7, { d: 1.8 });
rise("#cdemo", K(40.5), { d: 1.2 });

// 15 · Casa Digital, call to action
rise("#u0", K(43), { d: 1.2 }); rise("#u1 .w", K(43) + .3); rise("#u2 .w", K(43) + .7, { d: 1.8 });
[43.9, 44.4, 44.9].forEach((k, i) => rise("#wy" + i + " .w, #wy" + i + " i", K(k), { st: .04, d: 1.3 }));
tl.fromTo("#cta", { opacity: 0, y: 90, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 2.2, ease: SOFT }, K(43.5));
float("#cta", K(44.4), K(46) - K(44.4));

'''

if __name__ == "__main__":
    print(build())
