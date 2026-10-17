#!/usr/bin/env python3
"""Bocha's Grill pitch video v3 (2026-10-15), vertical 1080x1920 for WhatsApp.

rodrigo rejected the question-method videos and asked to go back to the videos he liked: same pitch
and editing as the Toreto's Grill vertical (toretos-grill/video/gen.py --vertical) and Coco Chicken v5.
Dark, slow, soft lights, full phrases on top with gold keywords, the visual below, "Still Buggin" with
every scene on a bar line, Clientia Tech outro. The question version is kept in gen-v2-preguntas.py.

Story, all from their own TikTok @bochasgrill: their own "primero empiezas, luego mejoras" photos ->
real comments asking the price and where they are -> their WhatsApp answers by itself and takes a pickup
order for the branch the customer picks -> stock per branch, supplier told by itself -> wait per branch,
live -> rating after every order -> the owner panel with the five branches -> his own goal, a franchise ->
Casa Digital -> outro. Conversations, stock, times, ratings and panel numbers are examples, labelled on screen.
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
SLUG = "bochas-grill-v3"
SCENES = [("intro", 0, 3), ("fame", 3, 7), ("asks", 7, 11), ("meet", 11, 13), ("bot", 13, 20), ("supply", 20, 24),
          ("wait", 24, 28), ("rate", 28, 32), ("owner", 32, 37), ("meta", 37, 42), ("us", 42, 46), ("end", 46, 50)]
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
/* their own before/after photos */
.hist{position:absolute;left:180px;top:820px;width:720px;height:900px;border-radius:40px;overflow:hidden;box-shadow:0 0 0 1px rgba(255,255,255,.1),0 50px 120px rgba(0,0,0,.6);}
.hist img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
.hist .cap2{position:absolute;left:24px;top:22px;font-size:20px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#fff;background:rgba(0,0,0,.55);padding:10px 16px;border-radius:12px;}
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
#fame .left{height:700px;}
#fame .stats{gap:56px;margin-top:40px;}
#asks .cms{top:860px;height:960px;}
#wait .riders{top:820px;padding:30px 40px 30px;}
#wait .rd{padding:20px 0;grid-template-columns:1fr 170px 250px;}
#wait .rd.hot{padding:20px;}
#rate .chat2{top:860px;}
#rate .alert2{top:1460px;}
#owner .shot{top:840px;}
#meta .goal{top:1240px;}
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
    for n in ("logo.png", "hist2.jpg", "hist4.jpg", "hist5.jpg", "hist1.jpg", "panel-m.jpg"):
        shutil.copy(os.path.join(SRC, n), A(n))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "bochas-grill-v3", "name": "Casa Digital x Bocha's Grill"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    # verbatim comments from redes/tiktok-comentarios.md
    cms = "".join(cm(t, i) for i, t in enumerate(["cuanto vale??", "donde estan ubicados en san pedro sula", "pero cual es el precio", "DIRECCIÓN SPS POR FAVOR... Y HORARIO"]))
    stats = [("139K", "vistas de su historia"), ("5", "sucursales"), ("21.8K", "seguidores")]
    stats_html = "".join(f'<div class="st" id="st{i}"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(stats))
    hist = "".join(f'<img id="hi{i}" src="assets/hist{n}.jpg">' for i, n in enumerate((2, 4, 5, 1)))
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
        scene("fame", f'''
          <div class="sp sp-red" style="left:900px;top:-300px;width:1500px;height:1500px"></div>
          <div class="hist" id="hist">{hist}<div class="cap2">Su historia · su propio TikTok</div></div>
          <div class="left">
            <div class="eb" id="f0">TikTok · @bochasgrill</div>
            <div class="h1" id="f1">{words("Primero empezó,")}</div>
            <div class="h1" id="f2">{words("luego mejoró.")}</div>
            <div class="h1" id="f3">{gold("Hoy son cinco.")}</div>
            <div class="stats">{stats_html}</div>
          </div>'''),
        scene("asks", f'''
          <div class="sp sp-gold" style="left:900px;top:-200px;width:1400px;height:1400px"></div>
          <div class="cms">{cms}</div>
          <div class="left">
            <div class="lgrp" id="ag1"><div class="eb" id="a0">Comentarios reales</div><div class="h1" id="a1">{words("Todos los días")}</div><div class="h1" id="a2">{words("le preguntan.")}</div></div>
            <div class="lgrp" id="ag2"><div class="h1" id="a3">{words("Y muchas preguntas")}</div><div class="h1" id="a4">{gold("se quedan sin respuesta.")}</div></div>
          </div>
          <div class="foot" id="afoot">Comentarios reales en su TikTok @bochasgrill</div>'''),
        scene("meet", f'''
          <div class="sp sp-green" style="left:260px;top:-300px;width:1400px;height:1400px"></div>
          <div class="center">
            <div class="wa-pill" id="mp"><i></i>WhatsApp · Bocha's Grill</div>
            <div class="h1" id="me1" style="font-size:124px">{words("Su WhatsApp,")}</div>
            <div class="h1" id="me2" style="font-size:124px">{gold("que contesta solo.")}</div>
          </div>'''),
        scene("bot", f'''
          <div class="sp sp-green" style="left:950px;top:-250px;width:1400px;height:1400px"></div>
          <div class="ph-stage">{gen3.phone(wa, "phw", dark=True)}</div>
          <div class="left">
            <div class="lgrp" id="bg1"><div class="eb g" id="b10">Al instante, a cualquier hora</div><div class="h1" id="b11">{words("Contesta el precio")}</div><div class="h1" id="b12">{gold("con la promo real.")}</div></div>
            <div class="lgrp" id="bg2"><div class="eb g" id="b20">En la sucursal que el cliente diga</div><div class="h1" id="b21">{words("Toma el pedido")}</div><div class="h1" id="b22">{gold("para recoger.")}</div></div>
            <div class="lgrp" id="bg3"><div class="eb g" id="b30">Sin que nadie lo copie a mano</div><div class="h1" id="b31">{words("Y lo manda")}</div><div class="h1" id="b32">{gold("a la cocina.")}</div></div>
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
            <div class="eb g" id="s0">Inventario por sucursal</div>
            <div class="h1 m" id="s1">{words("Se acaban los frijoles,")}</div>
            <div class="h1 m" id="s2">{gold("el proveedor ya sabe.")}</div>
            <div class="sub" id="s3">{words("Cada sucursal tiene su mínimo. Cuando algo baja, el panel le escribe solo al proveedor y le avisa a usted.")}</div>
          </div>
          <div class="demo" id="sdemo">Ejemplo</div>'''),
        scene("wait", f'''
          <div class="sp sp-red" style="left:900px;top:-300px;width:1400px;height:1400px"></div>
          <div class="riders" id="riders"><div class="k">Espera ahora · 7:30 pm</div>{wait_rows}</div>
          <div class="left">
            <div class="eb g" id="w0">Pedidos por sucursal</div>
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
            <div class="eb g" id="r0">Después de cada pedido</div>
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
        scene("owner", f'''
          <div class="sp sp-gold" style="left:700px;top:-300px;width:1500px;height:1500px"></div>
          <div class="shot" id="shot"><img src="assets/panel-m.jpg"></div>
          <div class="left">
            <div class="lgrp" id="cg1"><div class="eb g" id="c0">Panel Bocha's Grill</div><div class="h1 m" id="c1">{words("Sus cinco sucursales,")}</div><div class="h1 m" id="c2">{gold("en su celular.")}</div></div>
            <div class="lgrp" id="cg2"><div class="eb g" id="c3">Ventas, pedidos, inventario y quejas</div><div class="h1 m" id="c4">{words("Y le dice")}</div><div class="h1 m" id="c5">{gold("qué hacer hoy.")}</div></div>
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

// 2 · their own story: "primero empiezas, luego mejoras", five branches today
rise("#f0", K(3), { d: 1.2 }); rise("#f1 .w", K(3) + .2); rise("#f2 .w", K(3) + .55); rise("#f3 .w", K(3) + .9, { d: 1.8 });
tl.fromTo("#hist", { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(3) + .3);
tl.fromTo("#hist img", { scale: 1.05 }, { scale: 1, duration: K(7) - K(3), ease: "none" }, K(3));
[4.2, 5.2, 6.2].forEach((k, i) => tl.fromTo("#hi" + (i + 1), { opacity: 0 }, { opacity: 1, duration: 1.2, ease: "sine.inOut" }, K(k)));
tl.set("#hi1, #hi2, #hi3", { opacity: 0 }, 0);
[4.4, 4.9, 5.4].forEach((k, i) => rise("#st" + i, K(k), { y: 30, d: 1.4 }));

// 3 · real comments: the price and where they are
rise("#a0", K(7), { d: 1.2 }); rise("#a1 .w", K(7) + .3); rise("#a2 .w", K(7) + .6);
[7.3, 7.8, 8.3, 8.8].forEach((k, i) => rise("#cm" + i, K(k), { y: 40, d: 1.6 }));
rise("#afoot", K(7.8), { d: 1.2 });
out("#ag1", K(9.4) - .8);
rise("#a3 .w", K(9.4)); rise("#a4 .w", K(9.4) + .45, { d: 1.8 });

// 4 · meet their WhatsApp
rise("#mp", K(11), { d: 1.4 });
rise("#me1 .w", K(11) + .3, { d: 1.8, st: .12 });
rise("#me2 .w", K(11.7), { d: 2, st: .12 });

// 5 · the bot: the real L139 question, a pickup order, the kitchen (7 bars)
tl.fromTo("#phw", { y: 700, rotationY: -16, rotationX: 6 }, { y: 0, rotationY: -6, rotationX: 2, duration: 2.4, ease: SOFT }, K(13));
tl.to("#phw", { rotationY: 4, rotationX: 0, duration: K(20) - K(14), ease: "sine.inOut" }, K(14));
rise("#bdemo", K(13.5), { d: 1.2 });
rise("#b10", K(13), { d: 1.2 }); rise("#b11 .w", K(13) + .3); rise("#b12 .w", K(13) + .6);
show("m1", K(13.5)); show("t1", K(14)); dots("t1", K(14) + .3); hide("t1", K(14.6)); show("m2", K(14.6));
out("#bg1", K(15.7) - .8);
rise("#b20", K(15.7), { d: 1.2 }); rise("#b21 .w", K(15.7) + .3); rise("#b22 .w", K(15.7) + .6);
show("m3", K(15.8)); show("m4", K(16.6)); show("t2", K(17.2)); dots("t2", K(17.2) + .3); hide("t2", K(17.7)); show("m5", K(17.7));
out("#bg2", K(18.3) - .8);
rise("#b30", K(18.3), { d: 1.2 }); rise("#b31 .w", K(18.3) + .3); rise("#b32 .w", K(18.3) + .6);
show("m6", K(18.6));

// 6 · stock per branch, the supplier is told by itself
rise("#s0", K(20), { d: 1.2 }); rise("#s1 .w", K(20) + .3); rise("#s2 .w", K(20) + .6, { d: 1.8 });
rise("#s3 .w", K(21), { st: .03 });
tl.fromTo("#stk", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(20) + .3);
tl.fromTo("#plb", { scaleX: 1 }, { scaleX: .27, duration: 1.6, ease: FINE }, K(20.5));
tl.fromTo("#chat2", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.6, ease: SOFT }, K(21.2));
rise("#pm1", K(21.5), { y: 20, d: 1.2 });
rise("#pm2", K(22.6), { y: 20, d: 1.2 });
rise("#sdemo", K(20.6), { d: 1.2 });

// 7 · wait per branch, live
rise("#w0", K(24), { d: 1.2 }); rise("#w1 .w", K(24) + .3); rise("#w2 .w", K(24) + .6); rise("#w3 .w", K(24) + .9, { d: 1.8 });
rise("#w4 .w", K(25.2), { st: .03 });
tl.fromTo("#riders", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(24) + .3);
[24.6, 24.9, 25.2, 25.5, 25.8].forEach((k, i) => rise("#rd" + i, K(k), { y: 20, d: 1.2 }));
tl.fromTo("#rd4", { scale: 1 }, { scale: 1.025, duration: .5, yoyo: true, repeat: 1, ease: "sine.inOut" }, K(26.5));
rise("#wdemo", K(24.6), { d: 1.2 });

// 8 · every customer rates, the owner hears it the same day
rise("#r0", K(28), { d: 1.2 }); rise("#r1 .w", K(28) + .3); rise("#r2 .w", K(28) + .6, { d: 1.8 });
rise("#r3 .w", K(29), { st: .03 });
tl.fromTo("#rchat", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(28) + .3);
rise("#rm1", K(28.5), { y: 20, d: 1.2 });
rise("#rm2", K(29.3), { y: 20, d: 1.2 });
tl.fromTo("#ralert", { opacity: 0, y: 50, scale: .97 }, { opacity: 1, y: 0, scale: 1, duration: 1.4, ease: SOFT }, K(30.1));
rise("#rdemo", K(28.6), { d: 1.2 });

// 9 · the owner panel on his phone (5 bars)
tl.fromTo("#shot", { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(32) + .2);
tl.fromTo("#shot img", { objectPosition: "50% 0%" }, { objectPosition: "50% 100%", duration: K(37) - K(33.5), ease: "sine.inOut" }, K(33.5));
rise("#c0", K(32), { d: 1.2 }); rise("#c1 .w", K(32) + .3); rise("#c2 .w", K(32) + .6, { d: 1.8 });
out("#cg1", K(34.4) - .8);
rise("#c3", K(34.4), { d: 1.2 }); rise("#c4 .w", K(34.4) + .3); rise("#c5 .w", K(34.4) + .6, { d: 1.8 });
rise("#cdemo", K(32.5), { d: 1.2 });

// 10 · his own words: a franchise (5 bars)
rise("#g0", K(37), { d: 1.2 }); rise("#g1 .w", K(37) + .3); rise("#g2 .w", K(37) + .6); rise("#g3 .w", K(37) + .9, { d: 1.8 });
rise("#g4 .w", K(38.4), { st: .03 });
tl.fromTo("#quote", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(37) + .3);
tl.fromTo("#goal", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.8, ease: SOFT }, K(38));
tl.fromTo("#gb", { scaleX: 0 }, { scaleX: .4, duration: 2.4, ease: FINE }, K(38.5));
count("ng", 0, 2, K(38.5), n => String(n), 2.4);
rise("#gdemo", K(37.6), { d: 1.2 });

// 11 · Casa Digital, call to action
rise("#u0", K(42), { d: 1.2 }); rise("#u1 .w", K(42) + .3); rise("#u2 .w", K(42) + .7, { d: 1.8 });
[42.9, 43.4, 43.9].forEach((k, i) => rise("#wy" + i + " .w, #wy" + i + " i", K(k), { st: .04, d: 1.3 }));
tl.fromTo("#cta", { opacity: 0, y: 90, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 2.2, ease: SOFT }, K(42.5));
float("#cta", K(43.4), K(46) - K(43.4));

'''

if __name__ == "__main__":
    print(build())
