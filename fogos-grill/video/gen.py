#!/usr/bin/env python3
"""Fogos Grill Beer Garden pitch video (2026-10-17), vertical 1080x1920 for WhatsApp.

Same pitch and editing as the official videos (Toreto's vertical, Coco Chicken v5, Bocha's v3): dark, slow,
soft lights, full phrases on top with gold keywords, the visual below, every scene on a bar line, Clientia
Tech outro. No question method.

Story, all from their own TikTok @fogosbeergarden: their own clips (storefront, plate, beer garden, grill)
and their numbers -> real comments asking where they are, the menu with prices, delivery, a phone number
-> step 1: every video sends people to their WhatsApp (bio link, pinned comment, the number in each video;
a WhatsApp bot can't answer TikTok comments, rodrigo 2026-10-17) -> their WhatsApp answers by itself:
address, map, menu with the real L130 price, a beer-garden table booked -> a simple page with menu, map and
reservations for the bio link -> the owner sees orders, bookings and which video sold -> Casa Digital ->
outro. Conversations, page and panel numbers are examples, labelled on screen.

Music: `--music path.mp3 --bpm N --p0 S` (first downbeat in seconds; a bar is 4 beats). Without them it
uses src/musica.mp3 on the "Still Buggin" grid of the other videos (8 x 0.3092783 s per bar).
Helpers come from coco-chicken/video (gen2, gen3, gen6, gen10) and toretos-grill/video/gen.py.
"""
import importlib.util, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.path.join(HERE, "..", "..", "coco-chicken", "video")
sys.path.insert(0, CC)
import gen3, gen6  # noqa: E402
from gen2 import MARK, words, ribbons, DEPS  # noqa: E402

_spec = importlib.util.spec_from_file_location("toretos_gen", os.path.join(HERE, "..", "..", "toretos-grill", "video", "gen.py"))
TG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TG)


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "build")
SLUG = "fogos-grill-vertical"
MUSIC = arg("--music", os.path.join(SRC, "musica.mp3"))
P0 = float(arg("--p0", gen6.P0))
BAR = 4 * 60 / float(arg("--bpm", 0)) if "--bpm" in sys.argv else gen6.BAR
K = lambda k: round(P0 + BAR * k, 3)
SCENES = [("intro", 0, 3), ("fame", 3, 7), ("asks", 7, 11), ("path", 11, 16), ("meet", 16, 18), ("bot", 18, 25),
          ("web", 25, 29), ("owner", 29, 33), ("us", 33, 37), ("end", 37, 41)]
TOTAL = K(41)
WA = "9844-8314"
ADDR = "Col. Trejo, esquina de la 11 calle y 23 avenida, cerca del City Mall"
BIO = ["🔥 Asados y parrilla en San Pedro Sula", "🍖 Ordená comida 👇", f"📲 WhatsApp {WA}"]


def gold(t):
    return f'<span class="gold">{words(t)}</span>'


def cm(text, i):
    return f'<div class="cm" id="cm{i}"><div class="cm-h"><i></i>Comentario en su TikTok</div><p>{text}</p></div>'


CSS_F = r'''
/* their logo is a sticker on dark brown: a dark round card, shown at its own size */
.ilogo{width:300px;height:300px;background:#1A0F0C;}
.ilogo img{object-fit:contain;object-position:50% 50%;}
.wa-av{background:#1A0F0C;}
.wa-av img{object-fit:cover;}
.iname{font-size:84px !important;line-height:1.05;}
.iname small{display:block;font-size:40px;letter-spacing:.32em;color:#E3A94A;margin-top:18px;}
#fame .stats{gap:48px;margin-top:40px;}
#asks .cms{top:840px;height:980px;}
/* step 1: from TikTok to WhatsApp */
.tk{position:absolute;left:90px;width:900px;background:linear-gradient(180deg,#161618,#111113);border-radius:36px;padding:30px 36px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 40px 100px rgba(0,0,0,.55);}
.tk .k{display:flex;align-items:center;gap:14px;font-size:22px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#8E8E93;}
.tk .k b{font-size:20px;color:#0B0B0C;background:#F2B544;padding:6px 14px;border-radius:999px;letter-spacing:.1em;}
.prof{display:flex;gap:26px;align-items:center;margin-top:22px;}
.prof img{width:120px;height:120px;border-radius:50%;object-fit:cover;flex:none;box-shadow:0 0 0 3px rgba(255,255,255,.1);}
.prof .n{font-size:34px;font-weight:600;color:#F5F5F7;}
.prof .n span{display:block;font-size:22px;color:#8E8E93;font-weight:500;margin-top:4px;}
.bio{margin-top:18px;font-size:26px;line-height:1.4;color:#C7C7CC;}
.wabtn{position:relative;margin-top:22px;display:flex;align-items:center;justify-content:center;gap:14px;height:78px;border-radius:20px;background:#25D366;color:#fff;font-size:32px;font-weight:600;}
.wabtn i{position:absolute;inset:-6px;border-radius:26px;box-shadow:0 0 0 4px rgba(242,181,68,.9);opacity:0;}
.pin .row{display:flex;gap:20px;margin-top:20px;}
.pin .row img{width:72px;height:72px;border-radius:50%;object-fit:cover;flex:none;}
.pin .row b{font-size:26px;color:#F5F5F7;font-weight:600;}
.pin .row b em{font-style:normal;font-size:20px;color:#FF3B5C;margin-left:10px;background:rgba(255,59,92,.12);padding:4px 10px;border-radius:8px;}
.pin .row p{margin-top:8px;font-size:32px;line-height:1.3;color:#F5F5F7;font-weight:500;}
.every{display:flex;gap:26px;align-items:center;margin-top:20px;}
.every img{width:150px;height:150px;border-radius:22px;object-fit:cover;flex:none;}
.every p{font-size:32px;line-height:1.3;color:#F5F5F7;font-weight:500;}
.every p .num{display:block;margin-top:8px;font-size:40px;color:#25D366;font-weight:600;letter-spacing:-.01em;}
/* bot cards inside WhatsApp */
.mapc{align-self:flex-start;width:290px;background:#202C33;border-radius:14px;border-top-left-radius:4px;margin-top:8px;overflow:hidden;}
.mapc img{display:block;width:100%;height:170px;object-fit:cover;object-position:50% 38%;}
.mapc div{padding:9px 12px 10px;font-size:15px;color:#E9EDEF;font-weight:600;}
.mapc div span{display:block;font-size:12px;color:#8696A0;font-weight:500;margin-top:2px;}
.menuc .mr{display:flex;align-items:center;gap:10px;margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08);}
.menuc .mr img{width:52px;height:52px;border-radius:10px;object-fit:cover;}
.menuc .mr div{flex:1;font-size:16px;line-height:1.25;}
.menuc .mr div span{display:block;font-size:12px;color:#8696A0;}
.menuc .mr b{font-size:17px;}
/* the page for the bio link */
#web .ph-stage{top:740px;}
.pg{position:absolute;inset:0;background:#0F0B0A;color:#F5F5F7;font-family:"IT",sans-serif;overflow:hidden;}
.pg-in{position:absolute;left:0;right:0;top:0;}
.pg-hero{position:relative;height:330px;}
.pg-hero img{width:100%;height:100%;object-fit:cover;object-position:50% 40%;}
.pg-hero:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,11,10,0) 45%,#0F0B0A 100%);}
.pg-t{padding:0 22px;margin-top:-30px;position:relative;}
.pg-t h3{font-size:27px;font-weight:600;letter-spacing:-.02em;line-height:1.1;}
.pg-t p{font-size:14px;color:#A1A1A6;margin-top:6px;}
.pg-b{display:flex;flex-direction:column;gap:9px;padding:16px 22px 0;}
.pg-b div{height:46px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:600;background:#1F1A18;box-shadow:0 0 0 1px rgba(255,255,255,.08);}
.pg-b .g{background:#25D366;color:#fff;box-shadow:none;}
.pg-m{padding:20px 22px 0;}
.pg-m h4{font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:#E3A94A;font-weight:600;}
.pg-dish{display:flex;gap:12px;align-items:center;margin-top:12px;}
.pg-dish img{width:84px;height:84px;border-radius:14px;object-fit:cover;}
.pg-dish div{flex:1;font-size:17px;font-weight:600;}
.pg-dish div span{display:block;font-size:12px;color:#A1A1A6;font-weight:500;margin-top:3px;line-height:1.3;}
.pg-dish b{font-size:18px;color:#F2B544;}
.pg-map{margin:18px 22px 0;border-radius:14px;overflow:hidden;height:220px;}
.pg-map img{width:100%;height:100%;object-fit:cover;object-position:50% 40%;}
.pg-f{padding:12px 22px 30px;font-size:13px;color:#A1A1A6;line-height:1.4;}
/* the owner panel card */
.pn{position:absolute;left:90px;top:830px;width:900px;background:linear-gradient(180deg,#161618,#0F0F10);border-radius:40px;padding:36px 40px 40px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 60px 140px rgba(0,0,0,.7);}
.pn .k{font-size:23px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#8E8E93;}
.pn .kp{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:22px;}
.pn .kp div{background:rgba(255,255,255,.04);border-radius:24px;padding:22px 22px 20px;box-shadow:0 0 0 1px rgba(255,255,255,.06);}
.pn .kp span{display:block;font-size:22px;color:#8E8E93;font-weight:500;line-height:1.2;}
.pn .kp b{display:block;font-size:64px;font-weight:600;letter-spacing:-.04em;margin-top:10px;color:#F5F5F7;font-variant-numeric:tabular-nums;}
.pn .kp .ok b{color:#5FD38A;}
.pn h5{margin-top:34px;font-size:23px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#E3A94A;}
.vb{display:grid;grid-template-columns:96px 1fr;gap:22px;align-items:center;margin-top:22px;}
.vb img{width:96px;height:96px;border-radius:18px;object-fit:cover;}
.vb .t{display:flex;justify-content:space-between;font-size:30px;font-weight:600;color:#F5F5F7;}
.vb .t span{color:#8E8E93;font-weight:500;font-size:26px;}
.vb .bar{height:14px;border-radius:7px;background:rgba(255,255,255,.08);margin-top:14px;overflow:hidden;}
.vb .bar i{display:block;height:100%;border-radius:7px;background:linear-gradient(90deg,#D8261C,#F2B544);transform-origin:left;}
'''


def build():
    proj = os.path.join(OUT, SLUG)
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    A = lambda *p: os.path.join(proj, "assets", *p)
    shutil.copy(MUSIC, A("musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), A("gsap.min.js"))
    shutil.copy(os.path.join(DEPS, "@fontsource", "archivo-black", "files", "archivo-black-latin-400-normal.woff2"), A("fonts", "display.woff2"))
    for w in (300, 400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"), A("fonts", f"it-{w}.woff2"))
    for n in ("fogos.mp4", "logo.png", "local.jpg", "mapa.jpg", "plato.jpg", "parrillada.jpg", "entrana.jpg"):
        shutil.copy(os.path.join(SRC, n), A(n))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "fogos-grill-v1", "name": "Casa Digital x Fogos Grill"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    # their own clips: storefront, pollo chuco, the beer garden, the grill (src/README)
    vid = (f'<video id="tkvid" class="vid" src="assets/fogos.mp4" data-start="{K(3)}" data-duration="{round(K(7) - K(3), 3)}" '
           f'data-media-start="0" data-track-index="2" muted playsinline></video>')
    stats = [("70K", "vistas en 3 semanas"), ("L130", "su pollo chuco"), ("11:30", "abren todos los días")]
    stats_html = "".join(f'<div class="st" id="st{i}"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(stats))
    # verbatim from redes/tiktok-comentarios.txt
    cms = "".join(cm(t, i) for i, t in enumerate(["cuál es la dirección para ir a comer por ahi", "menú con precios",
                                                    "hacen envíos", "necesito un número de teléfono"]))
    bio = "<br>".join(BIO)
    path = f'''
          <div class="tk" id="pk0" style="top:800px"><div class="k">Link en su perfil <b>Nuevo</b></div>
            <div class="prof"><img src="assets/local.jpg"><div class="n">Fogos Grill Beer Garden<span>@fogosbeergarden</span></div></div>
            <div class="bio">{bio}</div>
            <div class="wabtn" id="wabtn"><i id="wabtng"></i>Pedí por WhatsApp</div></div>
          <div class="tk pin" id="pk1" style="top:1290px"><div class="k">📌 Comentario fijado <b>Nuevo</b></div>
            <div class="row"><img src="assets/local.jpg"><div><b>Fogos Grill Beer Garden<em>Creador</em></b>
              <p>Menú, precios y ubicación 👉 escribinos al WhatsApp {WA}</p></div></div></div>
          <div class="tk" id="pk2" style="top:1570px"><div class="every"><img src="assets/plato.jpg">
            <p>Y en cada video, el mismo número<span class="num">WhatsApp {WA}</span></p></div></div>'''

    head = ('<div class="wa-h"><span class="bk">‹</span><div class="wa-av"><img src="assets/logo.png"></div>'
            '<div><b>Fogos Grill</b><span>en línea</span></div></div>')
    menu = ('<div class="oc-in menuc"><div class="oc-k">Menú · Fogos Grill</div><div class="oc-t">Asados y parrilla</div>'
            '<div class="mr"><img src="assets/plato.jpg"><div>Pollo chuco<span>pechuga y ala, tajadas, repollo y aderezo</span></div><b>L130</b></div></div>'
            '<div class="oc-b">Ver menú completo</div>')
    resv = ('<div class="oc-in"><div class="oc-k">Reserva #118</div><div class="oc-t">Beer garden</div>'
            '<div class="oc-s">Sábado · 7:00 pm</div>'
            '<div class="oc-r"><span>Mesa para 6</span><b>✓</b></div></div>')
    msgs = [("m1", '<div class="wb out">cuál es la dirección para ir a comer por ahi<small>12:05 p. m.</small></div>'),
            ("t1", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m2", f'<div class="wb in">¡Hola! Estamos en la {ADDR}. Abrimos todos los días desde las 11:30 am.<small>12:05 p. m.</small></div>'),
            ("m3", '<div class="mapc"><img src="assets/mapa.jpg"><div>Fogos Grill Beer Garden<span>Cómo llegar · Col. Trejo</span></div></div>'),
            ("m4", '<div class="wb out">y el menú con precios?<small>12:06 p. m.</small></div>'),
            ("t2", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m5", f'<div class="ocard">{menu}</div>'),
            ("m6", '<div class="wb out">quiero reservar para 6 el sábado a las 7<small>12:07 p. m.</small></div>'),
            ("t3", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m7", f'<div class="ocard">{resv}</div>'),
            ("m8", '<div class="wb in">¡Listo! Su mesa queda apartada. El sábado le recordamos.<small>12:07 p. m.</small></div>')]
    wa = (f'<div class="wa">{head}<div class="wa-msgs">' + "".join(f'<div class="slot" id="{i}">{h}</div>' for i, h in msgs)
          + '</div><div class="wa-in">Mensaje</div></div>')
    page = (f'<div class="pg"><div class="pg-in" id="pgin">'
            '<div class="pg-hero"><img src="assets/local.jpg"></div>'
            '<div class="pg-t"><h3>Fogos Grill Beer Garden</h3><p>Asados y parrilla en San Pedro Sula</p></div>'
            '<div class="pg-b"><div class="g">Pedir por WhatsApp</div><div>Reservar mesa</div><div>Cómo llegar</div></div>'
            '<div class="pg-m"><h4>Menú</h4><div class="pg-dish"><img src="assets/plato.jpg"><div>Pollo chuco'
            '<span>pechuga y ala bien doraditas, tajadas de guineo verde, repollo y aderezo</span></div><b>L130</b></div></div>'
            '<div class="pg-map"><img src="assets/mapa.jpg"></div>'
            f'<div class="pg-f">{ADDR}<br>Todos los días desde las 11:30 am · WhatsApp {WA}</div>'
            '</div></div>')
    vbars = [("Pollo chuco", "plato", 11, 1.0), ("Parrillada para dos", "parrillada", 5, .45), ("Entraña al carbón", "entrana", 3, .27)]
    vb_html = "".join(f'<div class="vb" id="vb{i}"><img src="assets/{f}.jpg"><div><div class="t">{n}<span>{c} pedidos</span></div>'
                      f'<div class="bar"><i id="vbb{i}" style="width:{w * 100:g}%"></i></div></div></div>' for i, (n, f, c, w) in enumerate(vbars))
    whys = ["Lo armamos con su menú y su dirección.", "Funciona en su WhatsApp de siempre.", "Soporte por WhatsApp, en español."]
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
            <div class="iname" id="iname">Fogos Grill<small>BEER GARDEN</small></div>
          </div>'''),
        scene("fame", f'''
          <div class="sp sp-red" style="left:900px;top:-300px;width:1500px;height:1500px"></div>
          <div class="left">
            <div class="eb" id="f0">TikTok · @fogosbeergarden</div>
            <div class="h1" id="f1">{words("Sus videos")}</div>
            <div class="h1" id="f2">{words("ya los ve")}</div>
            <div class="h1" id="f3">{gold("mucha gente.")}</div>
            <div class="stats">{stats_html}</div>
          </div>'''),
        scene("asks", f'''
          <div class="sp sp-gold" style="left:900px;top:-200px;width:1400px;height:1400px"></div>
          <div class="cms">{cms}</div>
          <div class="left">
            <div class="lgrp" id="ag1"><div class="eb" id="a0">Comentarios reales</div><div class="h1" id="a1">{words("Y la gente")}</div><div class="h1" id="a2">{words("pregunta.")}</div></div>
            <div class="lgrp" id="ag2"><div class="h1" id="a3">{words("Cada pregunta")}</div><div class="h1" id="a4">{gold("es un pedido.")}</div></div>
          </div>
          <div class="foot" id="afoot">Comentarios reales en su TikTok @fogosbeergarden</div>'''),
        scene("path", f'''
          <div class="sp sp-green" style="left:900px;top:-300px;width:1400px;height:1400px"></div>
          {path}
          <div class="left">
            <div class="eb g" id="pp0">Paso 1 · De TikTok a WhatsApp</div>
            <div class="h1 m" id="pp1">{words("Cada video")}</div>
            <div class="h1 m" id="pp2">{words("lleva directo")}</div>
            <div class="h1 m" id="pp3">{gold("a su WhatsApp.")}</div>
          </div>
          <div class="demo" id="pdemo">Ejemplo · su perfil y su número son reales</div>'''),
        scene("meet", f'''
          <div class="sp sp-green" style="left:260px;top:-300px;width:1400px;height:1400px"></div>
          <div class="center">
            <div class="wa-pill" id="mp"><i></i>WhatsApp · {WA}</div>
            <div class="h1" id="me1" style="font-size:124px">{words("Y ahí, su WhatsApp")}</div>
            <div class="h1" id="me2" style="font-size:124px">{gold("contesta solo.")}</div>
          </div>'''),
        scene("bot", f'''
          <div class="sp sp-green" style="left:950px;top:-250px;width:1400px;height:1400px"></div>
          <div class="ph-stage">{gen3.phone(wa, "phw", dark=True)}</div>
          <div class="left">
            <div class="lgrp" id="bg1"><div class="eb g" id="b10">Al instante, a cualquier hora</div><div class="h1" id="b11">{words("Dice dónde están,")}</div><div class="h1" id="b12">{gold("con el mapa.")}</div></div>
            <div class="lgrp" id="bg2"><div class="eb g" id="b20">Con sus precios</div><div class="h1" id="b21">{words("Manda el menú")}</div><div class="h1" id="b22">{gold("y toma el pedido.")}</div></div>
            <div class="lgrp" id="bg3"><div class="eb g" id="b30">Para el beer garden</div><div class="h1" id="b31">{words("Y aparta")}</div><div class="h1" id="b32">{gold("la mesa.")}</div></div>
          </div>
          <div class="demo" id="bdemo">Conversación de ejemplo · dirección, horario y precio reales</div>'''),
        scene("web", f'''
          <div class="sp sp-gold" style="left:900px;top:-300px;width:1400px;height:1400px"></div>
          <div class="ph-stage" id="wstage">{gen3.phone(page, "phs", dark=True)}</div>
          <div class="left">
            <div class="eb g" id="w0">El link de su perfil</div>
            <div class="h1 m" id="w1">{words("Una página")}</div>
            <div class="h1 m" id="w2">{gold("con su menú.")}</div>
            <div class="sub" id="w3">{words("Precios, mapa, reservas y el botón de WhatsApp, todo en un solo lugar.")}</div>
          </div>
          <div class="demo" id="wdemo">Página de ejemplo · fotos, dirección y precio reales</div>'''),
        scene("owner", f'''
          <div class="sp sp-red" style="left:900px;top:-300px;width:1400px;height:1400px"></div>
          <div class="pn" id="pn"><div class="k">Panel Fogos Grill · esta semana</div>
            <div class="kp"><div id="kp0"><span>Pedidos por WhatsApp</span><b id="nk0">0</b></div>
              <div id="kp1"><span>Mesas reservadas</span><b id="nk1">0</b></div>
              <div class="ok" id="kp2"><span>Sin contestar</span><b>0</b></div></div>
            <h5 id="pnh">Qué video trajo clientes</h5>{vb_html}</div>
          <div class="left">
            <div class="eb g" id="o0">Panel del dueño</div>
            <div class="h1 m" id="o1">{words("Y usted ve")}</div>
            <div class="h1 m" id="o2">{gold("qué video vende.")}</div>
            <div class="sub" id="o3">{words("Cada pedido y cada reserva queda anotado, con el video que lo trajo.")}</div>
          </div>
          <div class="demo" id="odemo">Datos de ejemplo</div>'''),
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
        f'<div class="ph-stage" id="fstage" style="opacity:0;left:1080px">{gen3.phone(vid, "phv", dark=True)}</div>',
    ])

    css = (gen3.CSS.replace("$heroB", "#2a0806").replace("$hero", "#D8261C").replace("$acc", "#F2B544").replace("$pri", "#F2B544")
           .replace("$washA", "rgba(0,0,0,0)").replace("$washB", "rgba(0,0,0,0)").replace("$sitebg", "#0B141A").replace("$siteink", "#fff")
           .replace("$dweight", "400").replace("$dcase", "uppercase").replace("$dtrack", "-0.01em")
           .replace("$italface", "").replace("$ital", '"Display"').replace("$introsizepx", "112px"))
    css += TG.CSS_BASE + TG.CSS_T
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    j6 = gen6.JS
    helpers = TG.JS_T[:TG.JS_T.index("// 1 · intro")]
    js = (j6[:j6.index("// 1 · intro")] + helpers + JS_F + j6[j6.index("// 11 · outro"):]
          ).replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = (gen3.HTML.replace("$title", "Casa Digital x Fogos Grill").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)).replace('data-fade-out="2.5"', 'data-fade-out="4"'))
    html = TG.vertical(html).replace("</style>", CSS_F + "</style>", 1)
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


JS_F = r'''
// 1 · intro
rise("#icd", 0.4, { d: 2 });
rise("#ipres .w", K(.9), { d: 1.6, st: .12 });
tl.fromTo("#ilogo", { opacity: 0, scale: .9, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(1.3));
tl.fromTo("#iname", { opacity: 0, y: 30, filter: "blur(20px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.4, ease: SOFT }, K(1.7));

// 2 · their own clips play in the phone, with their numbers
rise("#f0", K(3), { d: 1.2 }); rise("#f1 .w", K(3) + .2); rise("#f2 .w", K(3) + .55); rise("#f3 .w", K(3) + .9);
tl.set("#fstage", { opacity: 1 }, K(3)); tl.set("#fstage", { opacity: 0 }, K(7));
tl.fromTo("#phv", { y: 700, rotationY: -18, rotationX: 8 }, { y: 0, rotationY: -8, rotationX: 2, duration: 2.6, ease: SOFT }, K(3));
tl.to("#phv", { rotationY: 6, rotationX: 0, duration: K(7) - K(4), ease: "sine.inOut" }, K(4));
[4.4, 4.9, 5.4].forEach((k, i) => rise("#st" + i, K(k), { y: 30, d: 1.4 }));

// 3 · real comments: where, the menu with prices, delivery, a phone number
rise("#a0", K(7), { d: 1.2 }); rise("#a1 .w", K(7) + .3); rise("#a2 .w", K(7) + .6);
[7.3, 7.8, 8.3, 8.8].forEach((k, i) => rise("#cm" + i, K(k), { y: 40, d: 1.6 }));
rise("#afoot", K(7.8), { d: 1.2 });
out("#ag1", K(9.4) - .8);
rise("#a3 .w", K(9.4)); rise("#a4 .w", K(9.4) + .45, { d: 1.8 });

// 4 · step 1: every video sends people to their WhatsApp (5 bars)
rise("#pp0", K(11), { d: 1.2 }); rise("#pp1 .w", K(11) + .3); rise("#pp2 .w", K(11) + .6); rise("#pp3 .w", K(11) + .9, { d: 1.8 });
tl.fromTo("#pk0", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(11.5));
tl.fromTo("#wabtng", { opacity: 0 }, { opacity: 1, duration: .6, yoyo: true, repeat: 3, ease: "sine.inOut" }, K(12.4));
tl.fromTo("#pk1", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(13.3));
tl.fromTo("#pk2", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(14.6));
rise("#pdemo", K(12), { d: 1.2 });

// 5 · their WhatsApp
rise("#mp", K(16), { d: 1.4 });
rise("#me1 .w", K(16) + .3, { d: 1.8, st: .12 });
rise("#me2 .w", K(16.7), { d: 2, st: .12 });

// 6 · the bot: address and map, menu with the real price, a table booked (7 bars)
tl.fromTo("#phw", { y: 700, rotationY: -16, rotationX: 6 }, { y: 0, rotationY: -6, rotationX: 2, duration: 2.4, ease: SOFT }, K(18));
tl.to("#phw", { rotationY: 4, rotationX: 0, duration: K(25) - K(19), ease: "sine.inOut" }, K(19));
rise("#bdemo", K(18.5), { d: 1.2 });
rise("#b10", K(18), { d: 1.2 }); rise("#b11 .w", K(18) + .3); rise("#b12 .w", K(18) + .6);
show("m1", K(18.5)); show("t1", K(19)); dots("t1", K(19) + .3); hide("t1", K(19.5)); show("m2", K(19.5)); show("m3", K(20.1));
out("#bg1", K(20.7) - .8);
rise("#b20", K(20.7), { d: 1.2 }); rise("#b21 .w", K(20.7) + .3); rise("#b22 .w", K(20.7) + .6);
show("m4", K(20.9)); show("t2", K(21.4)); dots("t2", K(21.4) + .3); hide("t2", K(21.9)); show("m5", K(21.9));
out("#bg2", K(23.1) - .8);
rise("#b30", K(23.1), { d: 1.2 }); rise("#b31 .w", K(23.1) + .3); rise("#b32 .w", K(23.1) + .6);
show("m6", K(23)); show("t3", K(23.5)); dots("t3", K(23.5) + .3); hide("t3", K(24)); show("m7", K(24)); show("m8", K(24.5));

// 7 · the page for the bio link, scrolled slowly
tl.fromTo("#phs", { y: 700, rotationY: -16, rotationX: 6 }, { y: 0, rotationY: -6, rotationX: 2, duration: 2.4, ease: SOFT }, K(25));
tl.to("#phs", { rotationY: 4, rotationX: 0, duration: K(29) - K(26), ease: "sine.inOut" }, K(26));
tl.fromTo("#pgin", { y: 0 }, { y: -150, duration: K(28.6) - K(26.4), ease: "sine.inOut" }, K(26.4));
rise("#w0", K(25), { d: 1.2 }); rise("#w1 .w", K(25) + .3); rise("#w2 .w", K(25) + .6, { d: 1.8 });
rise("#w3 .w", K(26), { st: .03 });
rise("#wdemo", K(25.5), { d: 1.2 });

// 8 · the owner sees orders, bookings and which video sold
rise("#o0", K(29), { d: 1.2 }); rise("#o1 .w", K(29) + .3); rise("#o2 .w", K(29) + .6, { d: 1.8 });
rise("#o3 .w", K(30), { st: .03 });
tl.fromTo("#pn", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(29) + .3);
count("nk0", 0, 19, K(29.6), n => String(n), 1.6); count("nk1", 0, 7, K(29.6), n => String(n), 1.6);
[30.2, 30.6, 31].forEach((k, i) => { rise("#vb" + i, K(k), { y: 20, d: 1.2 }); tl.fromTo("#vbb" + i, { scaleX: 0 }, { scaleX: 1, duration: 1.4, ease: FINE }, K(k) + .2); });
rise("#odemo", K(29.5), { d: 1.2 });

// 9 · Casa Digital
rise("#u0", K(33), { d: 1.2 }); rise("#u1 .w", K(33) + .3); rise("#u2 .w", K(33) + .7, { d: 1.8 });
[33.9, 34.4, 34.9].forEach((k, i) => rise("#wy" + i + " .w, #wy" + i + " i", K(k), { st: .04, d: 1.3 }));
tl.fromTo("#cta", { opacity: 0, y: 90, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 2.2, ease: SOFT }, K(33.5));
float("#cta", K(34.4), K(37) - K(34.4));

'''

if __name__ == "__main__":
    print(build())
