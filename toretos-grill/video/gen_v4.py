#!/usr/bin/env python3
"""Toreto's Grill pitch video v4 (2026-10-17), vertical 1080x1920 for WhatsApp.
rodrigo: "mejora un poco el video, se pierde un poco la idea; pon como de solución: por eso nosotros les
proponemos esto, creamos este sistema para automatizar...". Same scenes and look as the official vertical
video (gen.py --vertical), told in four labelled parts:
1 El problema (real comments, answered by hand) -> 2 La solución (new scene: "Por eso les proponemos esto",
the system and what it automates; then the bot and everything connected) -> 3 Su panel (four real screens of
the upgraded owner panel, zero unanswered, riders and cash, suppliers) -> his goal -> 4 Por qué nosotros.
Music: "Stylish" by FASSounds (110 BPM, /mnt/project-files/musica/stylish-fassounds.mp3 copied to
src/musica-stylish.mp3), every scene on a bar. gen.py and its video stay as the previous version."""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "coco-chicken", "video"))
import gen3, gen6  # noqa: E402
from gen2 import MARK, words, ribbons, DEPS  # noqa: E402
P0 = float(os.environ.get("MUSIC_P0", 0.035))  # "Stylish" (FASSounds), 110 BPM
BAR = float(os.environ.get("MUSIC_BAR", 4 * 60 / 110))
K = lambda k: round(P0 + BAR * k, 3)

SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "build")
VERTICAL = True
SLUG = "toretos-grill-v4"
SCENES = [("intro", 0, 3), ("fame", 3, 6), ("asks", 6, 10), ("sol", 10, 14), ("bot", 14, 21), ("link", 21, 25),
          ("owner", 25, 29), ("zero", 29, 33), ("moto", 33, 37), ("supply", 37, 40), ("meta", 40, 44), ("us", 44, 47), ("end", 47, 51)]
TOTAL = K(51)
# where each scene of gen.py's timeline lands now (old start, old end, new start, new end)
REMAP = {"intro": (0, 3, 0, 3), "fame": (3, 7, 3, 6), "asks": (7, 11, 6, 10), "bot": (13, 20, 14, 21), "link": (20, 25, 21, 25),
         "zero": (28, 32, 29, 33), "moto": (32, 36, 33, 37), "supply": (36, 39, 37, 40), "meta": (39, 43, 40, 44), "us": (43, 46, 44, 47)}
OUTRO_SHIFT = 47 - 37  # gen6's outro starts on bar 37
GOLD = "#F2B544"
ADDR = "colonia La Ideal, 6 y 7 calle, 15 avenida, atrás de Megamall"


def gold(t):
    return f'<span class="gold">{words(t)}</span>'


# the Coco Chicken v5 stylesheet, plus the Toretos scenes
CSS_BASE = re.search(r"CSS8 = r'''(.*?)'''", open(os.path.join(HERE, "..", "..", "coco-chicken", "video", "gen10.py"), encoding="utf-8").read(), re.S).group(1)
CSS_T = r'''
.ilogo img{object-position:50% 50%;}
.wa-av img{object-position:50% 50%;}
.iname{font-size:112px;}
#fame .left,#asks .left{width:860px;}
.cm p{font-size:34px;}
.kcol .tk b{font-size:14px;}
/* motoristas y efectivo */
#moto .left{width:780px;}
#moto .h1.m{font-size:72px;}
.riders{position:absolute;left:1000px;top:190px;width:780px;background:linear-gradient(180deg,#161618,#0F0F10);border-radius:40px;padding:36px 44px 38px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 60px 140px rgba(0,0,0,.7);}
.riders .k{font-size:19px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#8E8E93;}
.rd{display:grid;grid-template-columns:1fr 150px 170px;align-items:center;gap:18px;padding:26px 0;border-bottom:1px solid rgba(255,255,255,.08);}
.rd:last-of-type{border-bottom:0;}
.rd .n{font-size:32px;font-weight:600;color:#F5F5F7;}
.rd .n span{display:block;font-size:22px;font-weight:500;color:#8E8E93;margin-top:6px;}
.rd .c{font-size:34px;font-weight:600;color:#F5F5F7;font-variant-numeric:tabular-nums;text-align:right;}
.rd .st{justify-self:end;font-size:22px;font-weight:600;padding:10px 18px;border-radius:999px;}
.rd .st.ok{color:#5FD38A;background:rgba(95,211,138,.12);}
.rd .st.go{color:#F2B544;background:rgba(242,181,68,.12);}
.rtot{display:flex;align-items:baseline;justify-content:space-between;margin-top:8px;padding-top:24px;border-top:1px solid rgba(255,255,255,.12);font-size:28px;color:#F5F5F7;font-weight:500;}
.rtot b{font-size:52px;font-weight:600;font-variant-numeric:tabular-nums;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
/* meta */
#meta .left{width:820px;}
.quote{position:absolute;left:1020px;top:170px;width:760px;background:linear-gradient(180deg,#161618,#111113);border-radius:36px;padding:34px 40px;box-shadow:0 0 0 1px rgba(255,255,255,.07),0 40px 90px rgba(0,0,0,.5);}
.quote .h{display:flex;align-items:center;gap:14px;font-size:20px;color:#8E8E93;font-weight:500;}
.quote .h img{width:44px;height:44px;border-radius:50%;}
.quote p{margin-top:16px;font-size:38px;line-height:1.25;font-weight:500;letter-spacing:-.015em;color:#F5F5F7;}
.goal{position:absolute;left:1020px;top:560px;width:760px;background:linear-gradient(180deg,#161618,#0F0F10);border-radius:36px;padding:34px 40px 38px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 40px 110px rgba(0,0,0,.6);}
.goal .k{font-size:20px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#8E8E93;}
.goal .row{display:flex;align-items:baseline;justify-content:space-between;margin-top:12px;}
.goal .row b{font-size:96px;font-weight:600;letter-spacing:-.05em;line-height:1;font-variant-numeric:tabular-nums;}
.goal .row span{font-size:30px;color:#8E8E93;}
.goal .bar{height:14px;border-radius:7px;background:rgba(255,255,255,.08);margin-top:24px;overflow:hidden;}
.goal .bar i{display:block;height:100%;width:100%;border-radius:7px;background:linear-gradient(90deg,#D8261C,#F2B544);transform-origin:left;}
.goal .s{font-size:21px;color:#8E8E93;margin-top:14px;}
/* v4: the four labelled parts */
.chip{display:flex;width:max-content;align-items:center;gap:16px;margin-bottom:30px;padding:12px 26px 12px 12px;border-radius:999px;font-size:26px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;}
.chip b{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;letter-spacing:0;color:#0B0B0C;}
.chip.red{color:#FF8A80;background:rgba(255,69,58,.10);box-shadow:0 0 0 1px rgba(255,69,58,.4);}.chip.red b{background:#FF6B5E;}
.chip.green{color:#7BE3A2;background:rgba(37,211,102,.10);box-shadow:0 0 0 1px rgba(37,211,102,.4);}.chip.green b{background:#25D366;}
.chip.gold{color:#F2B544;background:rgba(242,181,68,.10);box-shadow:0 0 0 1px rgba(242,181,68,.4);}.chip.gold b{background:#F2B544;}
/* the system, what it automates */
.sys{position:absolute;left:90px;width:900px;top:760px;background:linear-gradient(180deg,#161618,#0F0F10);border-radius:40px;padding:34px 40px 30px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 60px 140px rgba(0,0,0,.7);}
.sys .k{display:flex;align-items:center;gap:16px;font-size:23px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#8E8E93;}
.sys .k img{width:52px;height:52px;border-radius:50%;}
.sy{display:grid;grid-template-columns:72px 1fr;gap:4px 24px;align-items:center;padding:24px 0;border-bottom:1px solid rgba(255,255,255,.08);}
.sy:last-child{border-bottom:0;padding-bottom:6px;}
.sy i{grid-row:span 2;width:72px;height:72px;border-radius:22px;background:rgba(242,181,68,.12);display:flex;align-items:center;justify-content:center;font-size:36px;font-style:normal;}
.sy b{font-size:36px;font-weight:600;color:#F5F5F7;letter-spacing:-.015em;line-height:1.2;}
.sy span{font-size:25px;color:#8E8E93;line-height:1.3;}
.sys-p{position:absolute;left:90px;right:90px;top:1560px;text-align:center;font-size:42px;font-weight:600;letter-spacing:-.02em;color:#F5F5F7;}
.sys-p em{font-style:normal;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
/* four real screens of the owner panel */
.shot img{position:absolute;left:14px;top:14px;}
.shot .sc{opacity:0;}
.shot .sc0{opacity:1;}
#owner .bl{font-size:38px;}
#owner .bl i{width:12px;height:12px;}
'''


def build():
    proj = os.path.join(OUT, SLUG)
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    A = lambda *p: os.path.join(proj, "assets", *p)
    shutil.copy(os.path.join(SRC, "musica-stylish.mp3"), A("musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), A("gsap.min.js"))
    shutil.copy(os.path.join(DEPS, "@fontsource", "archivo-black", "files", "archivo-black-latin-400-normal.woff2"), A("fonts", "display.woff2"))
    for w in (300, 400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"), A("fonts", f"it-{w}.woff2"))
    for n in ("tiktok.mp4", "logo.jpg", "pv4-hoy.jpg", "pv4-pedidos.jpg", "pv4-caja.jpg", "pv4-clientes.jpg"):
        shutil.copy(os.path.join(SRC, n), A(n))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "toretos-grill-v4", "name": "Casa Digital x Toreto's Grill"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    vid = (f'<video id="tkvid" class="vid" src="assets/tiktok.mp4" data-start="{K(3)}" data-duration="{round(K(6) - K(3), 3)}" '
           f'data-media-start="0" data-track-index="2" muted playsinline></video>')
    stats = [("176.8K", "vistas de su video fijado"), ("L80", "almuerzo, lunes a domingo"), ("55K", "me gusta en TikTok")]
    stats_html = "".join(f'<div class="st" id="st{i}"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(stats))
    # verbatim from redes/tiktok-respuestas.md
    comments = [("donde estan ubicados?", None), ("y pa domicilio", None), ("Dan factura con rtn ?", None), ("No contestan whats", None)]
    cms = "".join(f'<div class="cm" id="cm{i}"><div class="cm-h"><i></i>Comentario en su TikTok</div><p>{t}</p></div>' for i, (t, _) in enumerate(comments))

    head = ('<div class="wa-h"><span class="bk">‹</span><div class="wa-av"><img src="assets/logo.jpg"></div>'
            '<div><b>Toreto\'s Grill</b><span>en línea</span></div></div>')
    order = ('<div class="oc-in"><div class="oc-k">Pedido #2311</div><div class="oc-t">A domicilio</div>'
             '<div class="oc-s">Col. Trejo · lo lleva su motorista</div>'
             '<div class="oc-r"><span>3 × Almuerzo</span><b>L240</b></div>'
             '<div class="oc-s" style="margin-top:6px">2 con carne, 1 con pollo · más el envío</div></div>')
    msgs = [("m1", '<div class="wb out">donde estan ubicados?<small>1:40 p. m.</small></div>'),
            ("t1", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m2", f'<div class="wb in">¡Hola! Estamos en San Pedro Sula, {ADDR}. Abrimos de lunes a domingo, de 11 am a 10:30 pm.<small>1:40 p. m.</small></div>'),
            ("m3", '<div class="wb in">Hoy hay almuerzo de L80 hasta las 3. ¿Se lo llevamos?<small>1:40 p. m.</small></div>'),
            ("m4", '<div class="wb out">si, 3 almuerzos a la colonia Trejo. 2 carne 1 pollo<small>1:41 p. m.</small></div>'),
            ("t2", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m5", f'<div class="ocard">{order}<div class="oc-b"><i id="okbtn"></i>Confirmar pedido</div></div>'),
            ("m6", '<div class="wb out">Confirmar pedido<small>1:41 p. m.</small></div>'),
            ("t3", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m7", '<div class="wb in">¡Listo! Ya está en la cocina. Le aviso cuando salga el motorista.<small>1:41 p. m.</small></div>')]
    wa = (f'<div class="wa">{head}<div class="wa-msgs">' + "".join(f'<div class="slot" id="{i}">{h}</div>' for i, h in msgs)
          + '</div><div class="wa-in">Mensaje</div></div>')

    tickets_old = {0: [("#2310", "2 × Asado")], 1: [("#2308", "1 × Pollo con tajadas"), ("#2309", "4 × Almuerzo")], 2: []}
    kcols = "".join(f'<div class="kcol"><h4>{t}</h4>' + "".join(f'<div class="tk"><b>{a}<em>hace {4 + j * 6 + c * 3} min</em></b><p>{b}</p></div>' for j, (a, b) in enumerate(tickets_old[c])) + '</div>'
                    for c, t in enumerate(["Nuevos", "En cocina", "En camino"]))
    tab = ('<div class="tab"><div class="tab-s"><div class="tab-h">Cocina · Toreto\'s Grill<span>1:41 pm</span></div>'
           f'<div class="kcols">{kcols}</div>'
           '<div class="tk new" id="tnew"><b>#2311<em>Domicilio</em></b><p>3 × Almuerzo</p><span class="ok" id="tok">Salió el motorista</span></div></div></div>')
    bars = [("En el local", 58), ("Para llevar", 34), ("Domicilio", 46)]
    lap = ('<div class="lap"><div class="lap-s"><div class="lap-in"><div class="lp-h"><i></i>Panel Toreto\'s Grill · Inicio</div>'
           '<div class="kp"><div class="kpi2 hot" id="kv"><span>Ventas de hoy</span><b><span id="nv">L17,340</span></b></div>'
           '<div class="kpi2" id="kr"><span>Pedidos a domicilio</span><b><span id="nr">9</span></b></div>'
           '<div class="kpi2"><span>WhatsApp sin contestar</span><b>0</b></div>'
           '<div class="kpi2"><span>Almuerzos vendidos</span><b><span id="na">98</span></b></div></div>'
           '<div class="lbars">' + "".join(f'<div class="lb"><span>{n}</span><div><i id="lb{i}" style="width:{v}%"></i></div></div>' for i, (n, v) in enumerate(bars))
           + '</div></div></div><div class="lap-b"></div></div>')
    mini = (f'<div class="mini"><div class="mini-s">{head}'
            '<div class="wb out">Confirmar pedido</div>'
            f'<div class="ocard">{order}</div>'
            '<div class="mnot" id="mnot"><div class="ic"></div><div><b>Toreto\'s Grill</b><span>Su pedido #2311 va en camino con el motorista. ¡Buen provecho!</span></div></div></div></div>')
    wires = ('<svg class="wires" viewBox="0 0 1920 1080">'
             '<path class="base" d="M 374 560 C 440 560 480 580 556 580"/><path class="run" id="wa" d="M 374 560 C 440 560 480 580 556 580"/>'
             '<path class="base" d="M 1228 580 C 1255 580 1270 560 1298 560"/><path class="run" id="wb" d="M 1228 580 C 1255 580 1270 560 1298 560"/>'
             '<path class="base" d="M 890 352 C 820 230 450 220 270 300"/><path class="run" id="wc" d="M 890 352 C 820 230 450 220 270 300"/>'
             '</svg>')
    sysrows = [("💬", "Su WhatsApp contesta y toma pedidos", "a cualquier hora, con su menú y su dirección"),
               ("🛵", "La cocina y el motorista reciben cada pedido", "sin copiar nada a mano"),
               ("💵", "La caja y el efectivo se cuadran solos", "lo del mostrador y lo que traen los motoristas"),
               ("🔥", "El proveedor sabe antes de que se acabe", "carbón, carne y tortillas")]
    sys_html = "".join(f'<div class="sy" id="sy{i}"><i>{e}</i><b>{t}</b><span>{d}</span></div>' for i, (e, t, d) in enumerate(sysrows))
    whys = ["Ya lo armamos con su menú y su dirección.", "Se instala en 14 días.", "Soporte por WhatsApp, en español."]
    whys_html = "".join(f'<div class="wy2" id="wy{i}"><i>✓</i><span>{words(t)}</span></div>' for i, t in enumerate(whys))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          <div class="sp sp-red" style="left:260px;top:-520px;width:1400px;height:1400px"></div>
          <div class="sp sp-gold" style="left:560px;top:520px;width:800px;height:800px"></div>
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("una propuesta para")}</div>
            <div class="ilogo" id="ilogo"><img src="assets/logo.jpg"></div>
            <div class="iname" id="iname">Toreto's Grill</div>
          </div>'''),
        scene("fame", f'''
          <div class="sp sp-red" style="left:900px;top:-300px;width:1500px;height:1500px"></div>
          <div class="tagv" id="tagv">Su video fijado · 176.8K vistas</div>
          <div class="left">
            <div class="eb" id="f0">TikTok · @toretosgrills</div>
            <div class="h1" id="f1">{words("El Colocho")}</div>
            <div class="h1" id="f2">{words("ya tiene")}</div>
            <div class="h1" id="f3">{gold("a la gente.")}</div>
            <div class="stats">{stats_html}</div>
          </div>'''),
        scene("asks", f'''
          <div class="sp sp-gold" style="left:900px;top:-200px;width:1400px;height:1400px"></div>
          <div class="cms">{cms}</div>
          <div class="left">
            <div class="lgrp" id="ag1"><div class="chip red" id="a0"><b>1</b>El problema</div><div class="h1" id="a1">{words("Todos los días")}</div><div class="h1" id="a2">{words("le preguntan.")}</div></div>
            <div class="lgrp" id="ag2"><div class="chip red" id="a0b"><b>1</b>El problema</div><div class="h1" id="a3">{words("Y él contesta")}</div><div class="h1" id="a4">{gold("uno por uno.")}</div></div>
          </div>
          <div class="foot" id="afoot">Comentarios reales en su TikTok @toretosgrills</div>'''),
        scene("sol", f'''
          <div class="sp sp-green" style="left:0;top:0;width:1400px;height:1400px"></div>
          <div class="sys" id="sys"><div class="k"><img src="assets/logo.jpg">El sistema de Toreto's</div>{sys_html}</div>
          <div class="sys-p" id="sysp">Y usted lo ve todo en <em>un solo panel.</em></div>
          <div class="left">
            <div class="lgrp" id="vg1"><div class="chip green" id="v0"><b>2</b>La solución</div><div class="h1 m" id="v1">{words("Por eso les")}</div><div class="h1 m" id="v2">{gold("proponemos esto.")}</div></div>
            <div class="lgrp" id="vg2"><div class="chip green" id="v0b"><b>2</b>La solución</div><div class="h1 m" id="v3">{words("Creamos un sistema")}</div><div class="h1 m" id="v4">{gold("que automatiza Toreto's.")}</div></div>
          </div>'''),
        scene("bot", f'''
          <div class="sp sp-green" style="left:950px;top:-250px;width:1400px;height:1400px"></div>
          <div class="ph-stage">{gen3.phone(wa, "phw", dark=True)}</div>
          <div class="left">
            <div class="lgrp" id="bg1"><div class="chip green" id="b10"><b>2</b>Al instante, a cualquier hora</div><div class="h1" id="b11">{words("Contesta")}</div><div class="h1" id="b12">{gold("dónde están.")}</div></div>
            <div class="lgrp" id="bg2"><div class="chip green" id="b20"><b>2</b>Con su menú y sus precios</div><div class="h1" id="b21">{words("Toma el pedido")}</div><div class="h1" id="b22">{gold("a domicilio.")}</div></div>
            <div class="lgrp" id="bg3"><div class="chip green" id="b30"><b>2</b>Sin que nadie lo copie a mano</div><div class="h1" id="b31">{words("Y lo manda")}</div><div class="h1" id="b32">{gold("a la cocina.")}</div></div>
          </div>
          <div class="demo" id="bdemo">Conversación de ejemplo · dirección, horario y precio reales</div>'''),
        scene("link", f'''
          <div class="sp sp-gold" style="left:360px;top:-200px;width:1200px;height:1200px"></div>
          <div class="ttl"><div class="h1 m" id="lk1">{words("Y todo")} {gold("queda conectado.")}</div></div>
          {wires}
          <div class="dev" id="dv0" style="left:120px;top:300px">{mini}<div class="dcap" style="top:546px">El cliente pide<span>por WhatsApp</span></div></div>
          <div class="dev" id="dv1" style="left:560px;top:360px">{tab}<div class="dcap" style="top:486px">La cocina lo ve<span>y el motorista sabe a dónde va</span></div></div>
          <div class="dev" id="dv2" style="left:1300px;top:390px">{lap}<div class="dcap" style="top:400px">Usted lo ve todo<span>en su panel</span></div></div>
          <div class="demo" id="ldemo">Datos de ejemplo</div>'''),
        scene("owner", f'''
          <div class="sp sp-red" style="left:700px;top:-300px;width:1500px;height:1500px"></div>
          <div class="shot" id="shot"><img class="sc sc0" id="sc0" src="assets/pv4-hoy.jpg"><img class="sc sc1" id="sc1" src="assets/pv4-pedidos.jpg"><img class="sc sc2" id="sc2" src="assets/pv4-caja.jpg"><img class="sc sc3" id="sc3" src="assets/pv4-clientes.jpg"></div>
          <div class="left">
            <div class="chip gold" id="o0"><b>3</b>Su panel</div>
            <div class="h1 m" id="o1">{words("Todo Toreto's,")}</div>
            <div class="h1 m" id="o2">{gold("en un solo lugar.")}</div>
            <div class="blt">
              <div class="bl" id="ob0"><i></i><span>{words("Pedidos y motoristas")}</span></div>
              <div class="bl" id="ob1"><i></i><span>{words("La caja, cuadrada cada noche")}</span></div>
              <div class="bl" id="ob2"><i></i><span>{words("Clientes, promos y facturas con RTN")}</span></div>
            </div>
          </div>
          <div class="demo" id="odemo">Datos de ejemplo</div>'''),
        scene("zero", f'''
          <div class="sp sp-green" style="left:900px;top:-300px;width:1500px;height:1500px"></div>
          <div class="inbox" id="inbox">
            <div class="ibh"><i></i>Su WhatsApp, hoy</div>
            <div class="iq" id="iq0"><div class="q"><b>“donde estan ubicados?”</b><span>Le escribieron la dirección a mano 10 veces</span></div><div class="ok" id="ok0">✓ Contestado</div></div>
            <div class="iq" id="iq1"><div class="q"><b>“y pa domicilio”</b><span>Pedido tomado y mandado a la cocina</span></div><div class="ok" id="ok1">✓ Contestado</div></div>
            <div class="iq" id="iq2"><div class="q"><b>“Dan factura con rtn ?”</b><span>Pide el RTN y la factura sale con el pedido</span></div><div class="ok" id="ok2">✓ Contestado</div></div>
            <div class="zres" id="zres"><div class="k">Sin contestar</div><div class="big"><span id="nz">3</span></div></div>
          </div>
          <div class="left">
            <div class="chip gold" id="z0"><b>3</b>Cero sin respuesta</div>
            <div class="h1 m" id="z1">{words("Cero clientes")}</div>
            <div class="h1 m" id="z2">{gold("sin respuesta.")}</div>
            <div class="sub" id="z3">{words("Un “No contestan whats” es un almuerzo que se vende en otro lado. El bot contesta todos, y el Colocho sigue en la parrilla.")}</div>
          </div>
          <div class="foot" id="zfoot">Preguntas tal como las escribieron en su TikTok, octubre 2026.</div>'''),
        scene("moto", f'''
          <div class="sp sp-gold" style="left:900px;top:-300px;width:1400px;height:1400px"></div>
          <div class="riders" id="riders"><div class="k">Motoristas · hoy</div>
            <div class="rd" id="rd0"><div class="n">Motorista 1<span>9 entregas</span></div><div class="c">L1,240</div><div class="st ok" id="rs0">✓ Cuadrado</div></div>
            <div class="rd" id="rd1"><div class="n">Motorista 2<span>7 entregas</span></div><div class="c">L980</div><div class="st ok" id="rs1">✓ Cuadrado</div></div>
            <div class="rd" id="rd2"><div class="n">Motorista 3<span>2 en camino</span></div><div class="c">L360</div><div class="st go" id="rs2">Trae L360</div></div>
            <div class="rtot" id="rtot"><span>Efectivo cobrado hoy</span><b>L<span id="ncash">0</span></b></div></div>
          <div class="left">
            <div class="chip gold" id="l0"><b>3</b>Domicilio propio</div>
            <div class="h1 m" id="l1">{words("Sus motoristas,")}</div>
            <div class="h1 m" id="l2">{gold("con las cuentas")}</div>
            <div class="h1 m" id="l3">{gold("claras.")}</div>
            <div class="sub" id="l4">{words("Cada entrega queda anotada con lo que cobró. Al volver, el efectivo se cuadra con un clic.")}</div>
          </div>
          <div class="demo" id="ldemo2">Ejemplo</div>'''),
        scene("supply", f'''
          <div class="sp sp-gold" style="left:900px;top:-300px;width:1400px;height:1400px"></div>
          <div class="stk" id="stk"><div class="k">Inventario · Toreto's Grill</div>
            <div class="row"><b>Carbón</b><span id="pl">3 <small>sacos</small></span></div>
            <div class="bar"><i id="plb"></i></div><div class="min">Mínimo: 6 sacos</div></div>
          <div class="chat2" id="chat2"><div class="hd"><i>🔥</i><div>Carbón<span>proveedor</span></div></div>
            <div class="b out" id="pm1"><div class="tag">Aviso automático</div>Buenas, le escribe Toreto's Grill. Se nos acaba el carbón: quedan 3 sacos, necesitamos 9. ¿A qué hora nos los trae?<small>11:42 am <em>✓✓</em></small></div>
            <div class="b in" id="pm2">Claro, se los llevo a las 4.<small>11:50 am</small></div></div>
          <div class="left">
            <div class="chip gold" id="s0"><b>3</b>Proveedores</div>
            <div class="h1 m" id="s1">{words("Se acaba el carbón,")}</div>
            <div class="h1 m" id="s2">{gold("el proveedor ya sabe.")}</div>
            <div class="sub" id="s3">{words("El panel ve el inventario y le escribe solo al proveedor. La parrilla nunca se queda sin fuego.")}</div>
          </div>
          <div class="demo" id="sdemo">Ejemplo</div>'''),
        scene("meta", f'''
          <div class="sp sp-red" style="left:900px;top:-200px;width:1300px;height:1300px"></div>
          <div class="quote" id="quote"><div class="h"><img src="assets/logo.jpg">Toretos Grills, respondiendo en TikTok</div><p>“Pronto 🔜 cuando vendamos 1000 almuerzos diarios en sps nos vamos a tegus”</p></div>
          <div class="goal" id="goal"><div class="k">Almuerzos al día · promedio de la semana</div>
            <div class="row"><b><span id="ng">0</span></b><span>de 1,000</span></div>
            <div class="bar"><i id="gb"></i></div><div class="s">El panel lleva la cuenta todos los días.</div></div>
          <div class="left">
            <div class="eb g" id="g0">Su meta</div>
            <div class="h1 m" id="g1">{words("Mil almuerzos")}</div>
            <div class="h1 m" id="g2">{words("al día, y")}</div>
            <div class="h1 m" id="g3">{gold("rumbo a Tegus.")}</div>
            <div class="sub" id="g4">{words("Para llegar ahí, cada pedido tiene que entrar, salir y cobrarse sin depender de que alguien lo vea a tiempo.")}</div>
          </div>
          <div class="demo" id="gdemo">Cita real · conteo de ejemplo</div>'''),
        scene("us", f'''
          <div class="sp sp-gold" style="left:900px;top:-200px;width:1400px;height:1400px"></div>
          <div class="left">
            <div class="chip gold" id="u0"><b>4</b>Por qué nosotros</div>
            <div class="h1 m" id="u1">{words("Hecho por hondureños,")}</div>
            <div class="h1 m" id="u2">{gold("para negocios hondureños.")}</div>
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

    css = (gen3.CSS.replace("$heroB", "#2a0806").replace("$hero", "#D8261C").replace("$acc", GOLD).replace("$pri", GOLD)
           .replace("$washA", "rgba(0,0,0,0)").replace("$washB", "rgba(0,0,0,0)").replace("$sitebg", "#0B141A").replace("$siteink", "#fff")
           .replace("$dweight", "400").replace("$dcase", "uppercase").replace("$dtrack", "-0.01em")
           .replace("$italface", "").replace("$ital", '"Display"').replace("$introsizepx", "112px"))
    css += CSS_BASE + CSS_T
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    j6 = gen6.JS
    js = (j6[:j6.index("// 1 · intro")] + remap_js() + re.sub(r"K\((\d+(?:\.\d+)?)\)", lambda m: f"K({float(m.group(1)) + OUTRO_SHIFT:g})", j6[j6.index("// 11 · outro"):])).replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = (gen3.HTML.replace("$title", "Casa Digital x Toreto's Grill").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)).replace('data-fade-out="2.5"', 'data-fade-out="4"'))
    html = vertical(html).replace('src="assets/pv-hoy-m.jpg"', 'src="assets/pv4-hoy.jpg"')
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


# vertical: same scenes and timing, re-laid out for a phone screen
CSS_V = r'''
html,body,#root{width:1080px !important;height:1920px !important;}
.left{left:80px;right:80px;width:auto !important;top:110px;bottom:auto;height:660px;}
.h1{font-size:100px;}
.h1.m,#owner .h1.m,#moto .h1.m{font-size:82px;}
.sub{font-size:34px;margin-top:28px;}
.foot{left:80px;bottom:60px;}
.iname{font-size:92px;}
.ilogo{width:240px;height:240px;}
#me1,#me2{font-size:96px !important;}
.ttl{top:150px;}
.ttl .h1.m{font-size:76px;}
/* phone under the text, a bit bigger */
.ph-stage{left:160px !important;top:720px;height:1100px;transform:scale(1.15);transform-origin:50% 0;}
.tagv{display:none;}
.demo{left:80px;right:80px;bottom:22px;text-align:center;font-size:16px;}
.stats{gap:44px;margin-top:50px;}
.st b{font-size:64px;}
.st span{font-size:22px;}
/* cards under the text, with bigger type */
.cms{left:90px;right:90px;width:auto;top:820px;bottom:auto;height:1000px;gap:26px;}
.cm-h{font-size:24px;}.cm-h i{width:36px;height:36px;}
.cm p{font-size:46px;}
.inbox{left:90px;top:860px;width:900px;}
.iq .q b{font-size:40px;}.iq .q span{font-size:27px;}.iq .ok{font-size:25px;}.ibh{font-size:25px;}
.riders{left:90px;top:880px;width:900px;}
.riders .k{font-size:23px;}
.rd{grid-template-columns:1fr 170px 200px;}
.rd .n{font-size:40px;}.rd .n span{font-size:27px;}.rd .c{font-size:42px;}.rd .st{font-size:26px;}
.rtot{font-size:32px;}.rtot b{font-size:60px;}
.stk{left:90px;top:840px;width:900px;}
.stk .k{font-size:23px;}.stk .row b,.stk .row span{font-size:46px;}.stk .min{font-size:24px;}
.chat2{left:90px;top:1150px;width:900px;}
.chat2 .hd{font-size:28px;}.chat2 .b{font-size:31px;max-width:700px;}.chat2 .b small{font-size:18px;}.chat2 .tag{font-size:18px;}
.quote{left:90px;top:860px;width:900px;}
.quote p{font-size:46px;}.quote .h{font-size:24px;}
.goal{left:90px;top:1240px;width:900px;}
.goal .k{font-size:23px;}.goal .s{font-size:25px;}
#us .left{top:110px;height:900px;}
.cta2{left:260px;top:1110px;}
/* the owner panel, as it looks on the owner's phone */
.shot{left:300px;top:800px;width:480px;height:1010px;border-radius:64px;padding:14px;background:linear-gradient(145deg,#3A3A3C,#0C0C0D 40%,#1C1C1E 70%,#48484A);}
.shot img{width:452px;height:982px;border-radius:52px;object-fit:cover;object-position:50% 0;}
#owner .blt{margin-top:36px;gap:16px;}
/* connected devices, stacked and larger */
.wires{width:1080px;height:1920px;}
.mini,.tab,.lap{transform:scale(1.2);transform-origin:0 0;}
#dv0{width:300px;}#dv1{width:792px;}#dv2{width:648px;}
.dcap{font-size:28px;}.dcap span{font-size:22px;}
/* outro */
.ribwrap{left:0;top:0;transform:none;}
.endglow{left:-110px;top:310px;}
'''


def vertical(html):
    html = (html.replace('content="width=1920, height=1080"', 'content="width=1080, height=1920"')
            .replace('data-width="1920" data-height="1080"', 'data-width="1080" data-height="1920"'))
    # the soft lights: keep them on the narrow frame, alternating high and low
    n = iter(range(100))
    html = re.sub(r'(<div class="sp sp-\w+") style="[^"]*"', lambda m: m.group(1) + (' style="left:-260px;top:%dpx;width:1600px;height:1600px"' % (-500 if next(n) % 2 == 0 else 700)), html)
    # devices: phone top left, panel top right, kitchen below
    html = (html.replace('id="dv0" style="left:120px;top:300px"', 'id="dv0" style="left:44px;top:290px"')
            .replace('id="dv2" style="left:1300px;top:390px"', 'id="dv2" style="left:366px;top:410px"')
            .replace('id="dv1" style="left:560px;top:360px"', 'id="dv1" style="left:144px;top:1110px"')
            .replace('<div class="dcap" style="top:546px">', '<div class="dcap" style="top:648px">')
            .replace('<div class="dcap" style="top:486px">', '<div class="dcap" style="top:556px">')
            .replace('<div class="dcap" style="top:400px">', '<div class="dcap" style="top:460px">')
            .replace('viewBox="0 0 1920 1080"', 'viewBox="0 0 1080 1920"'))
    paths = {"M 374 560 C 440 560 480 580 556 580": "M 194 1030 C 194 1180 60 1330 140 1390",
             "M 1228 580 C 1255 580 1270 560 1298 560": "M 940 1330 C 1050 1270 1060 820 1025 720",
             "M 890 352 C 820 230 450 220 270 300": "M 690 405 C 630 290 360 240 230 290"}
    for a, b in paths.items():
        html = html.replace(a, b)
    return html.replace("</style>", CSS_V + "</style>", 1)


JS_T = r'''
function show(id, t) { // grow a chat slot open, then fade its bubble in
  tl.fromTo("#" + id, { height: 0 }, { height: "auto", duration: .55, ease: "power2.out" }, t);
  tl.fromTo("#" + id + " > *", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .6, ease: SOFT }, t + .15);
}
function hide(id, t) { tl.to("#" + id, { height: 0, duration: .35, ease: "power2.in" }, t); }
function dots(id, t) { tl.fromTo("#" + id + " i", { opacity: .25 }, { opacity: 1, duration: .3, stagger: .12, repeat: 3, yoyo: true, ease: "sine.inOut" }, t); }
function wire(id, t, d) {
  const p = document.getElementById(id), L = p.getTotalLength(), seg = 90;
  p.style.strokeDasharray = seg + " " + (L + seg); p.style.strokeDashoffset = seg;
  tl.set(p, { opacity: 1 }, t);
  tl.fromTo(p, { strokeDashoffset: seg }, { strokeDashoffset: -L, duration: d || 1.1, ease: "power1.inOut" }, t);
  tl.set(p, { opacity: 0 }, t + (d || 1.1));
}
function count(id, from, to, t, fmt, d) {
  const el = document.getElementById(id), o = { v: from };
  tl.fromTo(o, { v: from }, { v: to, duration: d || 1.2, ease: FINE, onUpdate: () => { el.textContent = fmt(Math.round(o.v)); } }, t);
}
const Lf = n => "L" + n.toLocaleString("en-US");

// 1 · intro
rise("#icd", 0.4, { d: 2 });
rise("#ipres .w", K(.9), { d: 1.6, st: .12 });
tl.fromTo("#ilogo", { opacity: 0, scale: .86, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(1.3));
tl.fromTo("#iname", { opacity: 0, y: 30, filter: "blur(20px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.4, ease: SOFT }, K(1.7));

// 2 · the Colocho already has people watching (his pinned TikTok plays in the phone)
rise("#f0", K(3), { d: 1.2 }); rise("#f1 .w", K(3) + .2); rise("#f2 .w", K(3) + .55); rise("#f3 .w", K(3) + .9);
tl.set("#fstage", { opacity: 1 }, K(3)); tl.set("#fstage", { opacity: 0 }, K(7));
tl.fromTo("#phv", { y: 700, rotationY: -18, rotationX: 8 }, { y: 0, rotationY: -8, rotationX: 2, duration: 2.6, ease: SOFT }, K(3));
tl.to("#phv", { rotationY: 6, rotationX: 0, duration: K(7) - K(4), ease: "sine.inOut" }, K(4));
rise("#tagv", K(4), { d: 1.4 });
[4.4, 4.9, 5.4].forEach((k, i) => rise("#st" + i, K(k), { y: 30, d: 1.4 }));

// 3 · real comments, answered by hand
rise("#a0", K(7), { d: 1.2 }); rise("#a1 .w", K(7) + .3); rise("#a2 .w", K(7) + .6);
[7.3, 7.8, 8.3, 8.8].forEach((k, i) => rise("#cm" + i, K(k), { y: 40, d: 1.6 }));
out("#ag1", K(9.4) - .8);
rise("#a3 .w", K(9.4)); rise("#a4 .w", K(9.4) + .45, { d: 1.8 });

// 4 · meet their WhatsApp
rise("#mp", K(11), { d: 1.4 });
rise("#me1 .w", K(11) + .3, { d: 1.8, st: .12 });
rise("#me2 .w", K(11.7), { d: 2, st: .12 });

// 5 · the bot, step by step (7 bars)
tl.fromTo("#phw", { y: 700, rotationY: -16, rotationX: 6 }, { y: 0, rotationY: -6, rotationX: 2, duration: 2.4, ease: SOFT }, K(13));
tl.to("#phw", { rotationY: 4, rotationX: 0, duration: K(20) - K(14), ease: "sine.inOut" }, K(14));
rise("#bdemo", K(13.5), { d: 1.2 });
rise("#b10", K(13), { d: 1.2 }); rise("#b11 .w", K(13) + .3); rise("#b12 .w", K(13) + .6);
show("m1", K(13.5)); show("t1", K(14)); dots("t1", K(14) + .3); hide("t1", K(14.5)); show("m2", K(14.5)); show("m3", K(15.1));
out("#bg1", K(15.7) - .8);
rise("#b20", K(15.7), { d: 1.2 }); rise("#b21 .w", K(15.7) + .3); rise("#b22 .w", K(15.7) + .6);
show("m4", K(16)); show("t2", K(16.5)); dots("t2", K(16.5) + .3); hide("t2", K(17)); show("m5", K(17));
tl.fromTo("#okbtn", { opacity: 0 }, { opacity: 1, duration: .25, yoyo: true, repeat: 1 }, K(17.9));
out("#bg2", K(18.1) - .8);
rise("#b30", K(18.1), { d: 1.2 }); rise("#b31 .w", K(18.1) + .3); rise("#b32 .w", K(18.1) + .6);
show("m6", K(18.1)); show("t3", K(18.5)); dots("t3", K(18.5) + .3); hide("t3", K(19)); show("m7", K(19));

// 6 · everything connected: phone -> kitchen -> panel -> back to the customer
rise("#lk1 .w", K(20), { d: 1.6 });
[20.2, 20.5, 20.8].forEach((k, i) => tl.fromTo("#dv" + i, { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(k)));
rise("#ldemo", K(21), { d: 1.2 });
wire("wa", K(21.3), 1.2);
tl.fromTo("#tnew", { opacity: 0, x: -40, scale: .96 }, { opacity: 1, x: 0, scale: 1, duration: 1, ease: SOFT }, K(21.3) + 1.1);
wire("wb", K(22.1), 1);
count("nv", 17340, 17580, K(22.1) + .9, Lf); count("nr", 9, 10, K(22.1) + .9, n => String(n)); count("na", 98, 101, K(22.1) + .9, n => String(n));
tl.fromTo("#lb2", { scaleX: 1 }, { scaleX: 1.06, duration: 1.2, ease: FINE }, K(22.1) + .9);
tl.fromTo("#tok", { opacity: 0 }, { opacity: 1, duration: .3 }, K(23.1));
tl.to("#tnew", { x: 414, duration: 1.4, ease: "power3.inOut" }, K(23.1) + .3);
tl.fromTo("#tok", { scale: .6 }, { scale: 1, duration: .5, ease: "back.out(2)" }, K(23.1));
wire("wc", K(23.7), 1.4);
tl.fromTo("#mnot", { y: -120, opacity: 0 }, { y: 0, opacity: 1, duration: .9, ease: "back.out(1.3)" }, K(23.7) + 1.3);

// 7 · the real owner panel
tl.fromTo("#shot", { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(25) + .2);
tl.fromTo("#shot img", { scale: 1 }, { scale: 1.035, duration: K(28) - K(25), ease: "none", transformOrigin: "30% 30%" }, K(25));
rise("#o0", K(25), { d: 1.2 }); rise("#o1 .w", K(25) + .3); rise("#o2 .w", K(25) + .6);
[25.9, 26.3, 26.7].forEach((k, i) => rise("#ob" + i + " .w, #ob" + i + " i", K(k), { st: .04, d: 1.3 }));
rise("#odemo", K(25.5), { d: 1.2 });

// 8 · zero customers left without an answer
rise("#z0", K(28), { d: 1.2 }); rise("#z1 .w", K(28) + .3); rise("#z2 .w", K(28) + .6, { d: 1.8 });
rise("#z3 .w", K(29.1), { st: .03 });
tl.fromTo("#inbox", { opacity: 0, y: 70, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(28) + .3);
[28.5, 28.9, 29.3].forEach((k, i) => rise("#iq" + i, K(k), { y: 24, d: 1.3 }));
rise("#zres", K(29.5), { y: 20, d: 1.3 });
[30.1, 30.6, 31.1].forEach((k, i) => {
  tl.fromTo("#ok" + i, { opacity: 0, scale: .7 }, { opacity: 1, scale: 1, duration: .6, ease: "back.out(2)" }, K(k));
  tl.fromTo("#nz", { scale: 1.12 }, { scale: 1, duration: .5, ease: "power2.out" }, K(k) + .2);
});
// one tween drives the counter so any seek lands on the right number: 3, then 2, 1, 0 as each badge lands
const zo = { p: 0 }, zn = document.getElementById("nz");
tl.fromTo(zo, { p: 0 }, { p: 1, duration: K(31.1) - K(30.1), ease: "none", onUpdate: () => { zn.textContent = String(zo.p <= 0 ? 3 : Math.max(0, 2 - Math.floor(zo.p * 2 + 1e-6))); } }, K(30.1) + .2);
rise("#zfoot", K(29), { d: 1.2 });

// 9 · their own riders: every delivery logged with the cash, squared on return
rise("#l0", K(32), { d: 1.2 }); rise("#l1 .w", K(32) + .3); rise("#l2 .w", K(32) + 1); rise("#l3 .w", K(32) + 1.3, { d: 1.8 });
rise("#l4 .w", K(33.4), { st: .03 });
tl.fromTo("#riders", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(32) + .3);
[32.8, 33.2, 33.6].forEach((k, i) => rise("#rd" + i, K(k), { y: 20, d: 1.2 }));
[0, 1, 2].forEach(i => tl.fromTo("#rs" + i, { opacity: 0, scale: .85 }, { opacity: 1, scale: 1, duration: .9, ease: SOFT }, K(34) + i * .35));
rise("#rtot", K(34.2), { y: 20, d: 1.2 });
count("ncash", 0, 2580, K(34.2) + .3, n => n.toLocaleString("en-US"), 1.6);
rise("#ldemo2", K(32.6), { d: 1.2 });

// 10 · the panel warns the supplier by itself
rise("#s0", K(36), { d: 1.2 }); rise("#s1 .w", K(36) + .3); rise("#s2 .w", K(36) + .6, { d: 1.8 });
rise("#s3 .w", K(37), { st: .03 });
tl.fromTo("#stk", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(36) + .3);
tl.fromTo("#plb", { scaleX: 1 }, { scaleX: .5, duration: 1.6, ease: FINE }, K(36.5));
tl.fromTo("#chat2", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.6, ease: SOFT }, K(37));
rise("#pm1", K(37.3), { y: 20, d: 1.2 });
rise("#pm2", K(38.1), { y: 20, d: 1.2 });
rise("#sdemo", K(36.6), { d: 1.2 });

// 11 · his own goal: 1,000 lunches a day, then Tegucigalpa
rise("#g0", K(39), { d: 1.2 }); rise("#g1 .w", K(39) + .3); rise("#g2 .w", K(39) + .6); rise("#g3 .w", K(39) + .9, { d: 1.8 });
rise("#g4 .w", K(40.4), { st: .03 });
tl.fromTo("#quote", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(39) + .3);
tl.fromTo("#goal", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.8, ease: SOFT }, K(39.8));
tl.fromTo("#gb", { scaleX: 0 }, { scaleX: .187, duration: 2.4, ease: FINE }, K(40.3));
count("ng", 0, 187, K(40.3), n => String(n), 2.4);
rise("#gdemo", K(39.6), { d: 1.2 });

// 12 · Casa Digital
rise("#u0", K(43), { d: 1.2 }); rise("#u1 .w", K(43) + .3); rise("#u2 .w", K(43) + .7, { d: 1.8 });
[43.9, 44.4, 44.9].forEach((k, i) => rise("#wy" + i + " .w, #wy" + i + " i", K(k), { st: .04, d: 1.3 }));
tl.fromTo("#cta", { opacity: 0, y: 90, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 2.2, ease: SOFT }, K(43.5));
float("#cta", K(44.4), K(46) - K(44.4));

'''

# gen.py's sections, in order, and the scene each one animates
SECTIONS = [("1 · intro", "intro"), ("2 · the Colocho", "fame"), ("3 · real comments", "asks"), ("4 · meet", None), ("5 · the bot", "bot"),
            ("6 · everything connected", "link"), ("7 · the real owner panel", None), ("8 · zero", "zero"), ("9 · their own riders", "moto"),
            ("10 · the panel warns", "supply"), ("11 · his own goal", "meta"), ("12 · Casa Digital", "us")]

JS_SOL = r"""
// 4 · SOLUTION: "por eso les proponemos esto", the system and what it automates (4 bars)
rise("#v0", K(10), { d: 1.2 }); rise("#v1 .w", K(10) + .3); rise("#v2 .w", K(10) + .7, { d: 1.8 });
tl.fromTo("#sys", { opacity: 0, y: 70, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(10.5));
[10.9, 11.5, 12.1, 12.7].forEach((k, i) => rise("#sy" + i, K(k), { y: 24, d: 1.3 }));
out("#vg1", K(11.6) - .8);
rise("#v0b", K(11.6), { d: 1 }); rise("#v3 .w", K(11.6) + .1); rise("#v4 .w", K(11.6) + .5, { d: 1.8 });
rise("#sysp", K(13.2), { y: 24, d: 1.3 });
"""

JS_OWNER = r"""
// 7 · PANEL: four real screens of the owner panel (4 bars)
tl.fromTo("#shot", { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(25) + .2);
rise("#o0", K(25), { d: 1.2 }); rise("#o1 .w", K(25) + .3); rise("#o2 .w", K(25) + .6);
[26, 27, 28].forEach((k, i) => { tl.fromTo("#sc" + (i + 1), { opacity: 0 }, { opacity: 1, duration: .7, ease: "sine.inOut" }, K(k));
  rise("#ob" + i + " .w, #ob" + i + " i", K(k) - .1, { st: .04, d: 1.3 }); });
rise("#odemo", K(25.5), { d: 1.2 });
"""


def remap_js():
    out = [JS_T[:JS_T.index("// 1 · intro")]]
    marks = [JS_T.index("// " + m) for m, _ in SECTIONS] + [len(JS_T)]
    for (m, sc), a, b in zip(SECTIONS, marks, marks[1:]):
        part = JS_T[a:b]
        if sc is None:
            out.append(JS_SOL if m.startswith("4") else JS_OWNER)
            continue
        o0, o1, n0, n1 = REMAP[sc]
        part = re.sub(r"K\((\d+(?:\.\d+)?)\)", lambda q: f"K({n0 + (float(q.group(1)) - o0) * (n1 - n0) / (o1 - o0):.3f})", part)
        if sc == "asks":
            part += 'rise("#a0b", K(8.400), { d: 1 }); rise("#afoot", K(7), { d: 1.2 });\n'
        out.append(part)
    return "".join(out)


if __name__ == "__main__":
    print(build())
