#!/usr/bin/env python3
"""Coco Chicken proposal video v7, vertical 1080x1920 (2026-10-15).
rodrigo liked the v6 pitch (the question method from his "sell me this pen" reference) but not its
editing: no 2-word captions, don't open with the owner's TikTok. So this is the v6 script told with
the v3-v5 look he liked: black luxury background with soft colored light, full headlines that rise
word by word with gold keywords, real UI cards, the iPhone WhatsApp conversation, and the Clientia
light-trail outro. Script: we won't pitch features -> 4 questions about their business with real
proof -> "if any answer was 'no sé', that's what we solve" -> 4 answers in the same order -> bottom
line -> call to action -> by Clientia Tech."""
import json, os, re, shutil
import gen3
from gen2 import MARK, words, ribbons, DEPS, HERE
from gen6 import K, P0, BAR, R

SRC = os.path.join(HERE, "coco-src")
OUT = os.path.join(HERE, "videos12")
SCENES = [("intro", 0, 3), ("nope", 3, 6), ("ask", 6, 8), ("q1", 8, 11), ("q2", 11, 14), ("q3", 14, 17), ("q4", 17, 20),
          ("bridge", 20, 23), ("a1", 23, 28), ("a2", 28, 31), ("a3", 31, 35), ("a4", 35, 38), ("line", 38, 41),
          ("us", 41, 44), ("end", 44, 48)]
TOTAL = K(48)


def gold(t):
    return f'<span class="gold">{words(t)}</span>'


def g8css(start, end):
    src = open(os.path.join(HERE, "gen8.py"), encoding="utf-8").read()
    return src[src.index(start):src.index(end)]


CSS = r'''
@font-face{font-family:"Display";src:url("assets/fonts/display.woff2") format("woff2");}
@font-face{font-family:"IT";src:url("assets/fonts/it-300.woff2") format("woff2");font-weight:300;}
@font-face{font-family:"IT";src:url("assets/fonts/it-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"IT";src:url("assets/fonts/it-500.woff2") format("woff2");font-weight:500;}
@font-face{font-family:"IT";src:url("assets/fonts/it-600.woff2") format("woff2");font-weight:600;}
@font-face{font-family:"IT";src:url("assets/fonts/it-700.woff2") format("woff2");font-weight:700;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:#070708;}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:#070708;color:#F5F5F7;font-family:"IT",sans-serif;-webkit-font-smoothing:antialiased;}
.scene{position:absolute;inset:0;overflow:hidden;background:#070708;}
.cam{position:absolute;inset:0;transform-origin:50% 40%;}
.w{display:inline-block;}
.sp{position:absolute;border-radius:50%;pointer-events:none;}
.sp-red{background:radial-gradient(closest-side,rgba(216,38,28,.26),rgba(7,7,8,0));}
.sp-gold{background:radial-gradient(closest-side,rgba(242,181,68,.16),rgba(7,7,8,0));}
.sp-green{background:radial-gradient(closest-side,rgba(37,211,102,.16),rgba(7,7,8,0));}
.top{position:absolute;left:90px;right:90px;top:210px;}
.center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 80px;}
.h1{font-weight:600;font-size:96px;line-height:1.04;letter-spacing:-.045em;color:#F5F5F7;}
.h1.m{font-size:80px;}
.h1.l{font-size:112px;}
.gold .w{background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;padding-bottom:.08em;}
.eb{font-size:26px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:#8E8E93;margin-bottom:26px;}
.eb.g{color:#E3A94A;}
.sub{font-size:36px;font-weight:500;line-height:1.3;letter-spacing:-.015em;color:#8E8E93;margin-top:30px;}
.demo{position:absolute;left:0;right:0;bottom:70px;text-align:center;font-size:20px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#4E4E53;}
.vis{position:absolute;left:90px;right:90px;top:820px;}
.card{background:linear-gradient(180deg,#18181A,#0F0F10);border-radius:44px;box-shadow:0 0 0 1px rgba(255,255,255,.09),0 60px 140px rgba(0,0,0,.7);padding:44px 50px;}
.k{font-size:24px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#8E8E93;}
/* intro */
.cd{display:flex;align-items:center;gap:16px;font-size:34px;font-weight:600;letter-spacing:-.01em;color:#F5F5F7;}
.cd .house{width:40px;height:40px;}
.sub-g{margin-top:60px;font-size:34px;color:#8E8E93;font-weight:500;}
.ilogo{margin-top:40px;width:420px;}
.ilogo img{width:100%;display:block;}
.iname{margin-top:30px;font-family:"Display";font-size:96px;text-transform:uppercase;letter-spacing:-.01em;}
/* nope: the easy pitch, struck through */
.pitch{position:relative;display:inline-block;margin-top:10px;}
.pitch .h1{color:#6E6E73;}
#npitch .h1{white-space:nowrap;font-size:62px;}
.strike{position:absolute;left:-10px;right:-10px;top:52%;height:10px;border-radius:5px;background:#FF453A;transform-origin:left;}
/* comments */
.cm{background:linear-gradient(180deg,#1A1A1C,#121214);border-radius:30px;padding:28px 34px;margin-top:22px;box-shadow:0 0 0 1px rgba(255,255,255,.07),0 30px 70px rgba(0,0,0,.45);}
.cm:first-child{margin-top:0;}
.cm-h{display:flex;align-items:center;gap:12px;font-size:20px;font-weight:600;letter-spacing:.06em;color:#8E8E93;}
.cm-h i{width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#3A3A3C,#1C1C1E);}
.cm p{font-size:40px;font-weight:600;letter-spacing:-.02em;margin-top:12px;line-height:1.2;}
.cm-l{margin-top:10px;font-size:22px;color:#8E8E93;font-weight:500;}
.cm-l b{color:#FF375F;font-weight:600;}
/* tiles */
.tile{display:flex;align-items:center;gap:34px;background:linear-gradient(180deg,#161618,#111113);border-radius:32px;padding:32px 40px;margin-top:22px;box-shadow:0 0 0 1px rgba(255,255,255,.07),0 30px 80px rgba(0,0,0,.5);}
.tile:first-child{margin-top:0;}
.tile b{flex:none;width:180px;font-size:110px;font-weight:600;letter-spacing:-.05em;line-height:1;font-variant-numeric:tabular-nums;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
.tile>span{font-size:34px;line-height:1.25;font-weight:500;color:#E5E5EA;letter-spacing:-.01em;}
.tile>span em{display:block;font-style:normal;font-size:26px;color:#8E8E93;margin-top:6px;}
/* stock */
.row{display:flex;justify-content:space-between;align-items:baseline;margin-top:22px;}
.row b{font-size:58px;font-weight:600;letter-spacing:-.03em;}
.row span{font-size:58px;font-weight:600;color:#FF6B5E;font-variant-numeric:tabular-nums;}
.row span small{font-size:28px;color:#8E8E93;font-weight:500;}
.bar{height:14px;border-radius:7px;background:rgba(255,255,255,.08);margin-top:24px;overflow:hidden;}
.bar i{display:block;height:100%;width:63%;background:#FF6B5E;border-radius:7px;transform-origin:left;}
.min{font-size:28px;color:#8E8E93;margin-top:16px;}
.who{margin-top:38px;padding-top:32px;border-top:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:20px;font-size:34px;font-weight:600;}
.who i{flex:none;width:58px;height:58px;border-radius:50%;background:#2A2A2D;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:30px;color:#8E8E93;}
/* branches */
.br{display:flex;justify-content:space-between;align-items:center;padding:32px 0;border-top:1px solid rgba(255,255,255,.08);font-size:44px;font-weight:600;letter-spacing:-.02em;}
.br:first-of-type{border-top:0;}
.br .dot{display:inline-block;width:20px;height:20px;border-radius:50%;margin-right:22px;}
.br span.q{font-size:66px;font-weight:600;color:#5A5A5F;}
/* phone */
.ph{position:absolute;left:50%;top:640px;width:430px;height:900px;margin-left:-215px;transform:scale(1.22);transform-origin:50% 0;perspective:2400px;}
.ph .iph{left:0;top:0;}
/* inbox (answer 2) */
.iq{display:flex;align-items:center;gap:22px;padding:24px 0;border-top:1px solid rgba(255,255,255,.07);}
.iq .q{flex:1;min-width:0;}
.iq .q b{display:block;font-size:38px;font-weight:600;letter-spacing:-.02em;}
.iq .q span{display:block;font-size:24px;color:#8E8E93;margin-top:4px;}
.iq .ok{flex:none;padding:12px 20px;border-radius:30px;background:rgba(37,211,102,.12);box-shadow:0 0 0 1px rgba(37,211,102,.35);color:#25D366;font-size:23px;font-weight:600;}
.zres{display:flex;align-items:flex-end;justify-content:space-between;margin-top:14px;padding-top:24px;border-top:1px solid rgba(255,255,255,.1);}
.zres .k{padding-bottom:26px;}
.zres .big{font-size:170px;font-weight:600;letter-spacing:-.05em;line-height:.9;background:linear-gradient(100deg,#FFE7B3,#F2B544 55%,#D98E1C);-webkit-background-clip:text;background-clip:text;color:transparent;font-variant-numeric:tabular-nums;}
/* supplier chat (answer 3) */
.chat2{margin-top:26px;background:#0B141A;border-radius:40px;padding:0 0 28px;overflow:hidden;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 40px 110px rgba(0,0,0,.6);}
.chat2 .hd{display:flex;align-items:center;gap:16px;padding:22px 30px;background:#1F2C34;font-size:28px;font-weight:600;}
.chat2 .hd i{width:52px;height:52px;border-radius:50%;background:#2A3942;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:28px;}
.chat2 .hd span{display:block;font-size:19px;color:#8696A0;font-weight:500;}
.chat2 .b{margin:20px 28px 0;padding:16px 22px 12px;border-radius:22px;font-size:28px;line-height:1.35;max-width:740px;width:fit-content;}
.chat2 .out{margin-left:auto;background:#005C4B;border-top-right-radius:5px;}
.chat2 .in{background:#1F2C34;border-top-left-radius:5px;}
.chat2 .b small{display:block;text-align:right;font-size:17px;color:rgba(255,255,255,.6);margin-top:4px;}
.chat2 .b small em{font-style:normal;color:#53BDEB;}
.chat2 .tag{display:block;font-size:17px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#25D366;margin-bottom:4px;}
/* panel shot */
.shot{border-radius:30px;overflow:hidden;box-shadow:0 0 0 1px rgba(255,255,255,.12),0 60px 140px rgba(0,0,0,.7);background:#fff;height:930px;}
.shot img{display:block;width:100%;}
/* cta */
.cta2{position:absolute;left:150px;right:150px;top:840px;border-radius:56px;background:linear-gradient(180deg,#18181A,#0F0F10);box-shadow:0 0 0 1px rgba(255,255,255,.09),0 60px 140px rgba(0,0,0,.7);display:flex;flex-direction:column;align-items:center;text-align:center;padding:70px 40px 60px;}
.cta2 .ic{width:150px;height:150px;border-radius:40px;background:#F5F5F7;color:#0B0B0C;display:flex;align-items:center;justify-content:center;}
.cta2 .ic .house{width:90px;height:90px;}
.cta2 .t{margin-top:34px;font-size:56px;font-weight:600;letter-spacing:-.03em;}
.cta2 .s{margin-top:8px;font-size:30px;color:#8E8E93;}
.cta2 .wa2{margin-top:46px;background:#25D366;color:#fff;font-weight:600;font-size:44px;padding:22px 46px;border-radius:60px;letter-spacing:-.01em;}
.cta2 .wa2 span{display:block;font-size:20px;font-weight:500;opacity:.85;}
.cta2 .who2{margin-top:28px;font-size:24px;color:#6E6E73;}
/* outro */
.endscene{background:#000;}
.endglow{position:absolute;width:1100px;height:1100px;left:-10px;top:410px;border-radius:50%;background:radial-gradient(closest-side,rgba(90,130,255,.30),rgba(0,0,0,0));}
.ribwrap{position:absolute;left:0;top:0;width:1080px;height:1920px;}
.rib{position:absolute;inset:0;mix-blend-mode:screen;transform-origin:50% 50%;}
.rl{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible;}
.glowl{filter:blur(42px);opacity:.9;}
.corel{filter:blur(1.5px);}
.mark-wrap{width:330px;height:390px;}
.mark{width:100%;height:100%;overflow:visible;}
.lockup{margin-top:60px;font-size:64px;letter-spacing:-.025em;white-space:nowrap;}
.by{font-weight:300;color:#86868B;display:inline-block;}
.ct{font-weight:600;color:#F5F5F7;}
.lt{display:inline-block;}
'''


def build():
    proj = os.path.join(OUT, "coco-chicken")
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    A = lambda *p: os.path.join(proj, "assets", *p)
    shutil.copy(os.path.join(HERE, "musica2.mp3"), A("musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), A("gsap.min.js"))
    shutil.copy(os.path.join(DEPS, "@fontsource", "archivo-black", "files", R["fonts"]["displayFile"]), A("fonts", "display.woff2"))
    for w in (300, 400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"), A("fonts", f"it-{w}.woff2"))
    shutil.copy(os.path.join(SRC, "logo.png"), A("logo.png"))
    shutil.copy(os.path.join(SRC, "panel", "pv-hoy-v.png"), A("pv-hoy.png"))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "coco-chicken-v7", "name": "Casa Digital x Coco Chicken (vertical)"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    comments = [("Incluye refresco ese combo ?", "3,071"), ("Y al fin bro dnd Estan ubicados", "50"),
                ("Hacen envíos??", None), ("Yo quierooooooo pero nunca me responden 😞😞", None)]
    cms = "".join(f'<div class="cm" id="cm{i}"><div class="cm-h"><i></i>Comentario en su TikTok</div><p>{t}</p>'
                  + (f'<div class="cm-l"><b>♥</b> {l} me gusta</div>' if l else "") + '</div>' for i, (t, l) in enumerate(comments))
    tiles = "".join(f'<div class="tile" id="ti{i}"><b><span class="cnt" data-n="{n}">0</span></b><span>{a}<em>{b}</em></span></div>'
                    for i, (n, a, b) in enumerate([(87, "piden una sucursal en su ciudad", "“cuando para Tegucigalpa”"),
                                                   (56, "preguntan el precio o el combo", "“precio?”"),
                                                   (25, "preguntan dónde están", "“Donde están ubicados”")]))
    branches = "".join(f'<div class="br" id="br{i}"><span><i class="dot" style="background:{c}"></i>{n}</span><span class="q">L ?</span></div>'
                       for i, (n, c) in enumerate([("Barrio Cabañas", "#2E844A"), ("Colonia Satélite", "#0176D3"), ("Barrio Medina", "#FE9339")]))
    head = ('<div class="wa-h"><span class="bk">‹</span><div class="wa-av"><img src="assets/logo.png"></div>'
            '<div><b>Coco Chicken</b><span>en línea</span></div></div>')
    order = ('<div class="oc-in"><div class="oc-k">Pedido #4132</div><div class="oc-t">Colonia Satélite</div>'
             '<div class="oc-s">Para recoger · listo en unos 15 min</div>'
             '<div class="oc-r"><span>1 × Ala y tajadas</span><b>L95</b></div>'
             '<div class="oc-s" style="margin-top:6px">Paga al recoger, en efectivo o tarjeta</div></div>')
    msgs = [("m1", '<div class="wb out">Buenas, ¿dónde están ubicados?<small>5:02 p. m.</small></div>'),
            ("t1", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m2", '<div class="wb in">¡Hola! Tenemos 3 sucursales: Barrio Cabañas, Colonia Satélite y Barrio Medina. '
                   'Abrimos de lunes a domingo, de 9 am a 10 pm.<small>5:02 p. m.</small></div>'),
            ("m3", '<div class="wb in">¿Le preparo algo para recoger? Así no hace fila.<small>5:02 p. m.</small></div>'),
            ("m4", '<div class="wb out">Sí, un ala y tajadas en la Satélite<small>5:03 p. m.</small></div>'),
            ("t2", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m5", f'<div class="ocard">{order}<div class="oc-b"><i id="okbtn"></i>Confirmar pedido</div></div>'),
            ("m7", '<div class="wb in">¡Listo! Ya está en la cocina de la Satélite. Le escribo cuando esté listo.<small>5:03 p. m.</small></div>')]
    wa = (f'<div class="wa">{head}<div class="wa-msgs">' + "".join(f'<div class="slot" id="{i}">{h}</div>' for i, h in msgs)
          + '</div><div class="wa-in">Mensaje</div></div>')
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          <div class="sp sp-red" style="left:-300px;top:-200px;width:1600px;height:1600px"></div>
          <div class="sp sp-gold" style="left:200px;top:1100px;width:900px;height:900px"></div>
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("una propuesta para")}</div>
            <div class="ilogo" id="ilogo"><img src="assets/logo.png"></div>
            <div class="iname" id="iname">Coco Chicken</div>
          </div>'''),
        scene("nope", f'''
          <div class="sp sp-red" style="left:-200px;top:300px;width:1500px;height:1500px"></div>
          <div class="center">
            <div class="eb" id="n0">Lo fácil sería decirle</div>
            <div class="pitch" id="npitch"><div class="h1 m">{words("«Tenemos el mejor bot del mundo.»")}</div><div class="strike" id="nstrike"></div></div>
            <div class="h1 l" id="n2" style="margin-top:90px">{gold("No lo vamos a hacer.")}</div>
          </div>'''),
        scene("ask", f'''
          <div class="sp sp-gold" style="left:-200px;top:200px;width:1500px;height:1500px"></div>
          <div class="center">
            <div class="h1 l" id="k1">{words("Primero,")}</div>
            <div class="h1 l" id="k2">{gold("le hacemos")}</div>
            <div class="h1 l" id="k3">{gold("preguntas.")}</div>
          </div>'''),
        scene("q1", f'''
          <div class="sp sp-gold" style="left:-100px;top:500px;width:1400px;height:1400px"></div>
          <div class="top"><div class="eb g" id="q1a">Pregunta 1</div><div class="h1" id="q1b">{words("¿Cuántos clientes le escriben")} {gold("cada día?")}</div></div>
          <div class="vis" style="top:760px">{cms}</div>
          <div class="demo" id="q1d">Comentarios reales de su TikTok</div>'''),
        scene("q2", f'''
          <div class="sp sp-red" style="left:-100px;top:500px;width:1400px;height:1400px"></div>
          <div class="top"><div class="eb g" id="q2a">Pregunta 2</div><div class="h1" id="q2b">{words("¿Cuántos se quedan")} {gold("sin respuesta?")}</div></div>
          <div class="vis">{tiles}</div>
          <div class="demo" id="q2d">De 506 comentarios reales de su TikTok, octubre 2026</div>'''),
        scene("q3", f'''
          <div class="sp sp-gold" style="left:-100px;top:500px;width:1400px;height:1400px"></div>
          <div class="top"><div class="eb g" id="q3a">Pregunta 3</div><div class="h1" id="q3b">{words("¿Quién le avisa al proveedor cuando se acaba")} {gold("el plátano?")}</div></div>
          <div class="vis" style="top:960px"><div class="card" id="q3c"><div class="k">Inventario · Colonia Satélite</div><div class="row"><b>Plátano verde</b><span>95 <small>unid.</small></span></div>
            <div class="bar"><i id="plb"></i></div><div class="min">Mínimo: 150 unid.</div><div class="who"><i>?</i>¿Quién le escribe al proveedor?</div></div></div>
          <div class="demo" id="q3d">Ejemplo</div>'''),
        scene("q4", f'''
          <div class="sp sp-red" style="left:-100px;top:500px;width:1400px;height:1400px"></div>
          <div class="top"><div class="eb g" id="q4a">Pregunta 4</div><div class="h1" id="q4b">{words("¿Sabe cuánto vendió hoy")} {gold("cada sucursal?")}</div></div>
          <div class="vis" style="top:900px"><div class="card" id="q4c"><div class="k">Ventas de hoy</div>{branches}</div></div>'''),
        scene("bridge", f'''
          <div class="sp sp-gold" style="left:-200px;top:200px;width:1500px;height:1500px"></div>
          <div class="center">
            <div class="h1 m" id="g1">{words("Si alguna respuesta")}</div>
            <div class="h1 m" id="g2">{words("fue «no sé»,")}</div>
            <div class="h1 l" id="g3" style="margin-top:60px">{gold("eso es lo que")}</div>
            <div class="h1 l" id="g4">{gold("resolvemos.")}</div>
          </div>'''),
        scene("a1", f'''
          <div class="sp sp-green" style="left:-200px;top:400px;width:1500px;height:1500px"></div>
          <div class="top" style="top:150px"><div class="eb g" id="a1a">Respuesta 1</div><div class="h1 m" id="a1b">{words("Su WhatsApp")} {gold("contesta solo,")}</div><div class="h1 m" id="a1c">{words("a cualquier hora.")}</div></div>
          <div class="ph" id="ph">{gen3.phone(wa, "phw", dark=True)}</div>
          <div class="demo" id="a1d" style="bottom:40px">Conversación de ejemplo · menú, precios y sucursales reales</div>'''),
        scene("a2", f'''
          <div class="sp sp-green" style="left:-100px;top:500px;width:1400px;height:1400px"></div>
          <div class="top"><div class="eb g" id="a2a">Respuesta 2</div><div class="h1" id="a2b">{gold("Cero clientes")}</div><div class="h1" id="a2c">{gold("sin respuesta.")}</div></div>
          <div class="vis" style="top:760px"><div class="card" id="a2v"><div class="k">Su WhatsApp, hoy</div>
            <div class="iq" id="iq0"><div class="q"><b>“Donde están ubicados”</b><span>25 lo preguntaron</span></div><div class="ok" id="ok0">✓ Contestado</div></div>
            <div class="iq" id="iq1"><div class="q"><b>“precio?”</b><span>56 lo preguntaron</span></div><div class="ok" id="ok1">✓ Contestado</div></div>
            <div class="iq" id="iq2"><div class="q"><b>“cuando para Tegucigalpa”</b><span>87 lo pidieron</span></div><div class="ok" id="ok2">✓ Anotado</div></div>
            <div class="zres"><div class="k">Sin contestar</div><div class="big"><span id="nz">3</span></div></div></div></div>
          <div class="demo" id="a2d">Preguntas reales de su TikTok</div>'''),
        scene("a3", f'''
          <div class="sp sp-gold" style="left:-100px;top:500px;width:1400px;height:1400px"></div>
          <div class="top"><div class="eb g" id="a3a">Respuesta 3</div><div class="h1 m" id="a3b">{words("Se acaba el plátano,")}</div><div class="h1 m" id="a3c">{gold("el proveedor ya sabe.")}</div></div>
          <div class="vis" style="top:660px">
            <div class="card" id="a3s" style="padding:34px 44px"><div class="k">Inventario · Colonia Satélite</div><div class="row"><b>Plátano verde</b><span>95 <small>unid.</small></span></div><div class="bar"><i id="plb2"></i></div></div>
            <div class="chat2" id="a3ch"><div class="hd"><i>🥬</i><div>Verdulería<span>proveedor</span></div></div>
              <div class="b out" id="pm1"><span class="tag">Aviso automático del panel</span>Buenas, le escribe Coco Chicken. Se nos acaba el plátano verde en Satélite: necesitamos 205 unid. ¿A qué hora nos lo trae?<small>4:52 pm <em>✓✓</em></small></div>
              <div class="b in" id="pm2">Claro, se lo llevo a las 6.<small>4:58 pm</small></div></div></div>
          <div class="demo" id="a3d">Ejemplo</div>'''),
        scene("a4", f'''
          <div class="sp sp-red" style="left:-100px;top:500px;width:1400px;height:1400px"></div>
          <div class="top"><div class="eb g" id="a4a">Respuesta 4</div><div class="h1" id="a4b">{words("Sus 3 sucursales,")}</div><div class="h1" id="a4c">{gold("en un solo lugar.")}</div></div>
          <div class="vis" style="top:720px"><div class="shot" id="shot"><img src="assets/pv-hoy.png"></div></div>
          <div class="demo" id="a4d">Su panel · datos de ejemplo</div>'''),
        scene("line", f'''
          <div class="sp sp-gold" style="left:-200px;top:200px;width:1500px;height:1500px"></div>
          <div class="center">
            <div class="h1 m" id="l1">{words("No le vendemos")}</div>
            <div class="h1 m" id="l2">{words("un sistema.")}</div>
            <div class="h1 l" id="l3" style="margin-top:70px">{gold("Resolvemos lo que")}</div>
            <div class="h1 l" id="l4">{gold("Coco Chicken necesita.")}</div>
          </div>'''),
        scene("us", f'''
          <div class="sp sp-gold" style="left:-100px;top:400px;width:1400px;height:1400px"></div>
          <div class="top"><div class="eb g" id="u0">Casa Digital</div><div class="h1 m" id="u1">{words("Escríbanos y se lo")}</div><div class="h1 m" id="u2">{gold("mostramos en 15 minutos.")}</div></div>
          <div class="cta2" id="cta">
            <div class="ic">{gen3.HOUSE}</div>
            <div class="t">Casa Digital</div>
            <div class="s">Hecho por hondureños, para negocios hondureños.</div>
            <div class="wa2"><span>WhatsApp</span>{gen3.WHATSAPP}</div>
            <div class="who2">Rodrigo Herrera</div>
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

    phone_css = "\n".join(l for l in gen3.CSS.split("\n") if l.startswith((".iph", ".island"))).replace("$sitebg", "#0B141A").replace("$siteink", "#fff")
    css = CSS + phone_css + "\n" + g8css("/* WhatsApp inside the phone */", ".ph-stage{left:1100px;}")
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    js = JS.replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = f'''<!doctype html>
<html lang="es" data-resolution="portrait">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" /><title>Casa Digital x Coco Chicken</title>
<script src="assets/gsap.min.js"></script><style>{css}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="{TOTAL}" data-fade-out="4" data-track-index="1"></audio>
{body}
</div>
<script>{js}</script>
</body></html>'''
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


JS = r'''
const tl = gsap.timeline({ paused: true });
const K = k => $P0 + $BAR * k;
const SOFT = "expo.out", FINE = "power2.inOut";
function rise(sel, t, o) {
  o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y || 40, filter: "blur(" + (o.blur || 12) + "px)" },
    { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d || 1.6, ease: SOFT, stagger: o.st || 0.1 }, t);
}
function out(sel, t, d) { tl.to(sel, { opacity: 0, y: -30, filter: "blur(10px)", duration: d || .9, ease: "power2.in" }, t); }
function show(id, t) {
  tl.fromTo("#" + id, { height: 0 }, { height: "auto", duration: .55, ease: "power2.out" }, t);
  tl.fromTo("#" + id + " > *", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .6, ease: SOFT }, t + .15);
}
function hide(id, t) { tl.to("#" + id, { height: 0, duration: .35, ease: "power2.in" }, t); }
function dots(id, t) { tl.fromTo("#" + id + " i", { opacity: .25 }, { opacity: 1, duration: .3, stagger: .12, repeat: 3, yoyo: true, ease: "sine.inOut" }, t); }
const SC = $scenes;
// slow camera drift on every scene, and a soft fade out of each scene's content so nothing is chopped
SC.forEach(([id, s, e]) => {
  tl.fromTo("#cam-" + id, { scale: 1.0 }, { scale: 1.025, duration: e - s, ease: "none" }, s);
  if (id !== "end") tl.to("#cam-" + id, { opacity: 0, filter: "blur(8px)", duration: .55, ease: "power2.in" }, e - .55);
});
function head(p, t) { // eyebrow + headline lines of a scene
  rise("#" + p + "a", t, { d: 1.2 });
  rise("#" + p + "b .w", t + .3, { st: .07 });
  rise("#" + p + "c .w", t + .8, { st: .07 });
  rise("#" + p + "d", t + 1, { d: 1.2 });
}

// intro
rise("#icd", 0.4, { d: 2 });
rise("#ipres .w", K(.9), { d: 1.6, st: .12 });
tl.fromTo("#ilogo", { opacity: 0, scale: .86, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(1.3));
tl.fromTo("#iname", { opacity: 0, y: 30, filter: "blur(20px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.4, ease: SOFT }, K(1.7));

// the easy pitch, struck through
rise("#n0", K(3), { d: 1.2 });
rise("#npitch .w", K(3) + .3, { st: .08 });
tl.fromTo("#nstrike", { scaleX: 0 }, { scaleX: 1, duration: .7, ease: "power3.inOut" }, K(4.2));
rise("#n2 .w", K(4.6), { st: .1, d: 1.8 });

// first, questions
rise("#k1 .w", K(6) + .1); rise("#k2 .w", K(6.5)); rise("#k3 .w", K(6.8), { d: 1.8 });

// q1: real comments
head("q1", K(8));
[8.5, 8.9, 9.3, 9.7].forEach((k, i) => rise("#cm" + i, K(k), { y: 40, d: 1.4 }));
// q2: real counts
head("q2", K(11));
[11.4, 11.8, 12.2].forEach((k, i) => rise("#ti" + i, K(k), { y: 40, d: 1.4 }));
document.querySelectorAll("#q2 .cnt").forEach((el, i) => { const o = { v: 0 }, n = +el.dataset.n;
  tl.fromTo(o, { v: 0 }, { v: n, duration: 1.3, ease: FINE, onUpdate: () => { el.textContent = Math.round(o.v); } }, K(11.5 + i * .4)); });
// q3: stock drains below the minimum
head("q3", K(14));
rise("#q3c", K(14.5), { y: 50, d: 1.6 });
tl.fromTo("#plb", { scaleX: 1.58 }, { scaleX: 1, duration: 1.8, ease: FINE }, K(14.9));
// q4
head("q4", K(17));
rise("#q4c", K(17.4), { y: 50, d: 1.6 });
[17.6, 17.9, 18.2].forEach((k, i) => rise("#br" + i, K(k), { y: 20, d: 1.2 }));

// bridge
rise("#g1 .w", K(20) + .1); rise("#g2 .w", K(20.4)); rise("#g3 .w", K(21)); rise("#g4 .w", K(21.3), { d: 1.8 });

// a1: the bot, in their WhatsApp
head("a1", K(23));
tl.fromTo("#ph", { opacity: 0, y: 260 }, { opacity: 1, y: 0, duration: 2.2, ease: SOFT }, K(23) + .2);
show("m1", K(23.6)); show("t1", K(24)); dots("t1", K(24) + .3); hide("t1", K(24.5)); show("m2", K(24.5)); show("m3", K(25.1));
show("m4", K(25.8)); show("t2", K(26.2)); dots("t2", K(26.2) + .3); hide("t2", K(26.6)); show("m5", K(26.6));
tl.fromTo("#okbtn", { opacity: 0 }, { opacity: 1, duration: .25, yoyo: true, repeat: 1 }, K(27.1));
show("m7", K(27.2));

// a2: zero unanswered
head("a2", K(28));
rise("#a2v", K(28.3), { y: 50, d: 1.6 });
[29, 29.4, 29.8].forEach((k, i) => tl.fromTo("#ok" + i, { opacity: 0, scale: .7 }, { opacity: 1, scale: 1, duration: .6, ease: "back.out(2)" }, K(k)));
const zo = { p: 0 }, zn = document.getElementById("nz"); // one tween drives the counter so any seek lands right
tl.fromTo(zo, { p: 0 }, { p: 1, duration: K(29.8) - K(29), ease: "none", onUpdate: () => { zn.textContent = String(zo.p <= 0 ? 3 : Math.max(0, 2 - Math.floor(zo.p * 2 + 1e-6))); } }, K(29) + .2);

// a3: the panel warns the supplier
head("a3", K(31));
rise("#a3s", K(31.3), { y: 40, d: 1.4 });
tl.fromTo("#plb2", { scaleX: 1.58 }, { scaleX: 1, duration: 1.6, ease: FINE }, K(31.6));
rise("#a3ch", K(32), { y: 50, d: 1.6 });
rise("#pm1", K(32.5), { y: 20, d: 1.2 });
rise("#pm2", K(33.6), { y: 20, d: 1.2 });

// a4: the real panel
head("a4", K(35));
rise("#shot", K(35.3), { y: 60, d: 2 });
tl.fromTo("#shot img", { y: 0 }, { y: -230, duration: K(38) - K(36), ease: "sine.inOut" }, K(36));

// bottom line
rise("#l1 .w", K(38) + .1); rise("#l2 .w", K(38.4)); rise("#l3 .w", K(39)); rise("#l4 .w", K(39.3), { d: 1.8 });

// call to action
rise("#u0", K(41), { d: 1.2 }); rise("#u1 .w", K(41) + .3); rise("#u2 .w", K(41) + .7, { d: 1.8 });
tl.fromTo("#cta", { opacity: 0, y: 90, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 2.2, ease: SOFT }, K(41.5));
tl.fromTo("#cta", { y: 0 }, { y: -18, duration: K(44) - K(42.5), ease: "sine.inOut", immediateRender: false }, K(42.5));

// outro: trails converge, mark draws, fills on the bar
function trails(rid, t0, dur, spin) {
  for (let i = 0; i < 6; i++) {
    const st = t0 + i * 0.22, len = 480 + (i % 3) * 170;
    tl.fromTo("." + rid + "-p" + i, { strokeDasharray: len + " 2000", strokeDashoffset: len }, { strokeDashoffset: -1000, duration: dur - i * 0.15, ease: "power2.inOut" }, st);
  }
  tl.fromTo("#" + rid, { rotation: spin[0], scale: spin[2], opacity: 0 }, { rotation: spin[1], scale: spin[3], opacity: 1, duration: dur, ease: "power1.inOut" }, t0);
}
const strokes = document.querySelectorAll("#mstroke path");
strokes.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
trails("re", K(44) - 0.3, 3, [20, -8, 1.6, 0.9]);
tl.to("#re", { scale: 3.2, opacity: 0, duration: 1.3, ease: "expo.out" }, K(45));
tl.to("#mstroke path", { strokeDashoffset: 0, duration: 2.3, ease: FINE }, K(44) + .1);
tl.fromTo("#mfill", { opacity: 0 }, { opacity: 1, duration: .6, ease: "power2.out" }, K(45));
tl.to("#mstroke", { opacity: 0, duration: .6 }, K(45));
tl.fromTo("#mwrap", { scale: .92 }, { scale: 1, duration: 2.6, ease: SOFT }, K(44));
tl.fromTo("#mwrap", { filter: "drop-shadow(0 0 0px rgba(140,170,255,0))" }, { filter: "drop-shadow(0 0 60px rgba(140,170,255,.65))", duration: .4, ease: "power2.out", yoyo: true, repeat: 1 }, K(45));
tl.fromTo("#eglow", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: 2, ease: SOFT }, K(45));
tl.fromTo("#msweep", { x: -200 }, { x: 900, duration: 1.8, ease: FINE }, K(45.5));
rise("#lby", K(45.5), { d: 1.6 });
rise(".lt", K(45.5) + .3, { d: 1.6, st: .04, y: 36, blur: 12 });
tl.to("#end .center, #eglow", { opacity: 0, duration: 2, ease: "power2.in" }, K(47.1));

window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
tl.seek(0);
'''

if __name__ == "__main__":
    print(build())
