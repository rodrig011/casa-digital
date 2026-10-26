#!/usr/bin/env python3
"""Libby's Cajun pitch video (2026-10-26), vertical 1080x1920 for WhatsApp.

Same look and structure as fusion-food/video/gen.py (dark, soft lights, full phrases with gold keywords,
four labelled parts, Clientia Tech outro):
1 El problema: real questions from their TikTok comments (price, location, "para 5 personas", birthdays), and
  that the account answered 57 of the 94 comments we could read on its 1.1M-view video by hand. They already use
  Meta's free assistant on WhatsApp, so the problem is what comes after the chat: the order stays in the chat.
2 La solución: "Por eso les proponemos esto", the four jobs the system automates after the chat, their same
  WhatsApp 9309-9296 sending the complete order to the kitchen, and the assistant taking a delivery order
  (example prices, labelled on screen).
3 Su panel: the real demo panel (libbys-cajun/panel), screenshots at phone width scrolling slowly: Inicio,
  Pedidos de WhatsApp, Reservaciones. Retake them if the panel changes.
4 Por qué nosotros, the 30 free days, Casa Digital and the outro.
Everything about them comes from their own TikTok @libbyscajun (photos are their video covers at their native
540 px width, never upscaled; the logo is their profile photo, the sign on the restaurant); conversations, prices
and panel numbers are examples, labelled on screen. Nothing from other restaurants.

Music: src/musica.mp3. Cuts land on bars: MUSIC_P0 (first downbeat, s) and MUSIC_BAR (bar length, s)
set the grid; the defaults are "Stylish" by FASSounds (110 BPM), the song rodrigo picked on 2026-10-17.
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

P0 = float(os.environ.get("MUSIC_P0", 0.035))  # "Stylish" (FASSounds), 110 BPM
BAR = float(os.environ.get("MUSIC_BAR", 4 * 60 / 110))
K = lambda k: round(P0 + BAR * k, 3)

SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "build")
SLUG = "libbys-cajun-vertical"
SCENES = [("intro", 0, 3), ("fame", 3, 6), ("asks", 6, 10), ("paste", 10, 14), ("prop", 14, 19), ("meet", 19, 22), ("bot", 22, 29),
          ("pa", 29, 33), ("pb", 33, 37), ("pc", 37, 40), ("why", 40, 44), ("us", 44, 48), ("end", 48, 52)]
# panel screenshots: (scene, file, css height of the page, stops = css y at the top of the screen)
SHOTS = [("pa", "panel-hoy.jpg", 2444, [330, 600, 1480]), ("pb", "panel-whatsapp.jpg", 2966, [365, 620, 900]),
         ("pc", "panel-reservas.jpg", 1631, [365, 585, 1195])]
SCR_W = 872  # inner screen width in the frame; the shots are 390 css px wide
TOTAL = K(52)
OUTRO_SHIFT = 48 - 37  # gen6's outro starts on bar 37


def gold(t):
    return f'<span class="gold">{words(t)}</span>'


def cm(text, i, label, pre="cm"):
    return f'<div class="cm" id="{pre}{i}"><div class="cm-h"><i></i>{label}</div><p>{text}</p></div>'


CSS_M = r'''
.ilogo{width:300px;height:300px;}
.ilogo{width:420px;height:420px;}
.ilogo img{object-fit:cover;background:#fff;border-radius:50%;}
.wa-av{background:#000;}
/* covers of their own TikTok videos, at their native 540 px width (never upscaled) */
.hist{position:absolute;left:290px;top:930px;width:500px;height:536px;border-radius:40px;overflow:hidden;box-shadow:0 0 0 1px rgba(255,255,255,.1),0 50px 120px rgba(0,0,0,.6);}
.hist img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
.cap2{position:absolute;left:24px;top:22px;font-size:20px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#fff;background:rgba(0,0,0,.55);padding:10px 16px;border-radius:12px;}
/* the block they paste by hand */
.paste{position:absolute;left:90px;width:900px;top:820px;background:linear-gradient(180deg,#161618,#0F0F10);border-radius:36px;padding:34px 40px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 50px 120px rgba(0,0,0,.6);}
.paste .hd{display:flex;align-items:center;gap:16px;font-size:24px;color:#8E8E93;font-weight:500;}
.paste .hd img{width:52px;height:52px;border-radius:50%;}
.paste .q{font-size:30px;color:#C7C7CC;margin-top:18px;}
.paste .a{margin-top:18px;padding:24px 28px;border-radius:24px;background:rgba(255,255,255,.05);font-size:28px;line-height:1.45;color:#F5F5F7;}
.paste .a div{margin-top:6px;}
.paste .a span{color:#8E8E93;}
.copies{position:absolute;left:90px;right:90px;top:1600px;display:flex;align-items:baseline;justify-content:center;gap:24px;}
.copies b{font-size:200px;font-weight:600;letter-spacing:-.06em;line-height:1;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;font-variant-numeric:tabular-nums;}
.copies > span{font-size:40px;color:#8E8E93;font-weight:500;}
/* bio link and pinned comment -> one WhatsApp */
.bio{position:absolute;left:90px;width:900px;top:820px;background:linear-gradient(180deg,#161618,#0F0F10);border-radius:36px;padding:32px 40px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 50px 120px rgba(0,0,0,.6);}
.bio .top{display:flex;align-items:center;gap:22px;}
.bio .top img{width:110px;height:110px;border-radius:50%;}
.bio .top b{display:block;font-size:40px;font-weight:600;}
.bio .top span{display:block;font-size:24px;color:#8E8E93;margin-top:4px;}
.bio .sig{font-size:26px;color:#C7C7CC;margin-top:22px;line-height:1.4;}
.bio .lnk{display:inline-flex;align-items:center;gap:14px;margin-top:22px;padding:16px 26px;border-radius:999px;background:#25D366;color:#04210f;font-size:30px;font-weight:700;}
.bio .lnk i{width:16px;height:16px;border-radius:50%;background:#04210f;}
.pin{position:absolute;left:90px;width:900px;top:1290px;background:linear-gradient(180deg,#161618,#111113);border-radius:32px;padding:28px 36px;box-shadow:0 0 0 1px rgba(242,181,68,.35),0 40px 100px rgba(0,0,0,.55);}
.pin .k{font-size:22px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#F2B544;}
.pin p{font-size:32px;line-height:1.35;margin-top:10px;color:#F5F5F7;}
.pin p b{color:#5FD38A;font-weight:600;}
.nums{position:absolute;left:90px;right:90px;top:1600px;display:flex;flex-wrap:wrap;justify-content:center;gap:14px 18px;}
.nums span{font-size:28px;font-weight:600;color:#8E8E93;padding:12px 20px;border-radius:999px;background:rgba(255,255,255,.06);font-variant-numeric:tabular-nums;}
.one{position:absolute;left:90px;right:90px;top:1600px;display:flex;justify-content:center;}
.one span{display:inline-flex;align-items:center;gap:16px;font-size:40px;font-weight:700;color:#04210f;background:#25D366;padding:22px 40px;border-radius:999px;box-shadow:0 20px 60px rgba(37,211,102,.35);}
/* their own reply */
.rep{position:absolute;left:90px;width:900px;top:820px;}
.rep .cm{position:relative;}
.rep .ans{margin:18px 0 0 90px;background:linear-gradient(180deg,#1b1b1e,#121214);border-radius:28px;padding:24px 30px;box-shadow:0 0 0 1px rgba(242,181,68,.35);}
.rep .ans .h{display:flex;align-items:center;gap:12px;font-size:22px;color:#F2B544;font-weight:600;}
.rep .ans .h img{width:40px;height:40px;border-radius:50%;}
.rep .ans p{font-size:44px;font-weight:600;margin-top:10px;}
.map{position:absolute;left:90px;width:900px;top:1290px;background:linear-gradient(180deg,#161618,#0F0F10);border-radius:36px;padding:30px 40px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 50px 120px rgba(0,0,0,.6);}
.map .k{font-size:22px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#8E8E93;}
.map .row{display:flex;align-items:center;gap:16px;margin-top:16px;font-size:30px;font-weight:500;color:#F5F5F7;}
.map .row i{width:14px;height:14px;border-radius:50%;background:#5FD38A;flex:none;}
.map .row.nw{color:#F2B544;font-weight:600;}
.map .row.nw i{background:#F2B544;box-shadow:0 0 18px rgba(242,181,68,.8);}
.map .row em{font-style:normal;font-size:22px;color:#8E8E93;margin-left:auto;}

/* v2: the four labelled parts */
.chip{display:flex;width:max-content;align-self:flex-start;align-items:center;gap:16px;margin-bottom:30px;padding:12px 26px 12px 12px;border-radius:999px;font-size:26px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;}
.chip b{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;letter-spacing:0;color:#0B0B0C;}
.chip.red{color:#FF8A80;background:rgba(255,69,58,.10);box-shadow:0 0 0 1px rgba(255,69,58,.4);}.chip.red b{background:#FF6B5E;}
.chip.green{color:#7BE3A2;background:rgba(37,211,102,.10);box-shadow:0 0 0 1px rgba(37,211,102,.4);}.chip.green b{background:#25D366;}
.auto{position:absolute;left:90px;right:90px;top:800px;}
.auto .k{font-size:24px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#8E8E93;margin-bottom:6px;}
.ar{display:grid;grid-template-columns:72px 1fr;gap:4px 26px;align-items:center;padding:26px 0;border-bottom:1px solid rgba(255,255,255,.08);}
.ar i{grid-row:span 2;width:72px;height:72px;border-radius:20px;background:rgba(37,211,102,.12);color:#5FD38A;display:flex;align-items:center;justify-content:center;font-size:34px;font-style:normal;font-weight:700;}
.ar b{font-size:40px;font-weight:600;line-height:1.2;color:#F5F5F7;letter-spacing:-.015em;}
.ar span{font-size:26px;color:#8E8E93;}
.allp{position:absolute;left:90px;right:90px;top:1650px;display:flex;justify-content:center;}
.allp span{font-size:38px;font-weight:700;color:#0B0B0C;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);padding:22px 42px;border-radius:999px;box-shadow:0 20px 60px rgba(242,181,68,.3);}
.scr{position:absolute;left:90px;top:800px;width:900px;height:1010px;border-radius:52px;padding:14px;background:linear-gradient(145deg,#3A3A3C,#0C0C0D 40%,#1C1C1E 70%,#48484A);box-shadow:0 60px 140px rgba(0,0,0,.7),inset 0 0 0 2px rgba(255,255,255,.12);}
.scr .in{position:relative;width:872px;height:982px;border-radius:40px;overflow:hidden;background:#F3F3F3;}
.scr img{position:absolute;left:0;top:0;width:872px;will-change:transform;}
.chip.gold{color:#F2B544;background:rgba(242,181,68,.10);box-shadow:0 0 0 1px rgba(242,181,68,.4);}.chip.gold b{background:#F2B544;}
.lgrp .chip{margin-bottom:26px;}
.whyl{position:absolute;left:90px;right:90px;top:640px;}
.wl{display:flex;align-items:flex-start;gap:24px;padding:24px 0;border-bottom:1px solid rgba(255,255,255,.08);}
.wl i{flex:none;width:52px;height:52px;border-radius:50%;background:rgba(242,181,68,.14);color:#F2B544;display:flex;align-items:center;justify-content:center;font-size:28px;font-style:normal;font-weight:700;}
.wl span{font-size:40px;line-height:1.25;font-weight:500;color:#F5F5F7;letter-spacing:-.015em;}
.result{position:absolute;left:90px;right:90px;top:1400px;padding:36px 40px;border-radius:36px;background:linear-gradient(180deg,#1b1710,#110f0b);box-shadow:0 0 0 2px rgba(242,181,68,.45),0 50px 120px rgba(0,0,0,.6);}
.result .k{font-size:22px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#F2B544;}
.result p{font-size:44px;line-height:1.35;font-weight:500;margin-top:14px;color:#F5F5F7;}
.result p b{font-weight:600;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
'''

# vertical positions (after the Toreto's vertical rules)
CSS_MV = r'''
#fame .left{height:660px;}
#asks .cms{top:820px;height:1000px;}
#asks .cm p{font-size:36px;line-height:1.3;}
.nums span{font-size:32px;color:#C7C7CC;}
#paste .copies,.copies{flex-direction:column;align-items:center;gap:8px;top:1560px;}
.copies b{font-size:150px!important;}
#paste .left .sub{margin-top:22px;}
.ilogo{width:420px!important;height:420px!important;}
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
    for n in ("logo.jpg", "food1.jpg", "food2.jpg", "food3.jpg", "food4.jpg") + tuple(f for _, f, _, _ in SHOTS):
        shutil.copy(os.path.join(SRC, n), A(n))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "libbys-cajun-v1", "name": "Casa Digital x Libby's Cajun"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    # word for word from comments on their own TikTok videos (redes/tiktok-datos.json)
    cms = "".join(cm(t, i, l) for i, (t, l) in enumerate([
        ("cuanto vale y donde estan ubicados", "Comentario en su TikTok"),
        ("A ver que cuesta ese plato ?", "Comentario en su TikTok"),
        ("Cuál es el costo para 5 personas", "Comentario en su TikTok"),
        ("Que promociones tienen para los cumpleañeros", "Comentario en su TikTok")]))
    stats = [("39.9K", "seguidores en TikTok"), ("1.1M", "vistas a su mariscada"), ("667.7K", "me gusta")]
    stats_html = "".join(f'<div class="st" id="st{i}"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(stats))
    hist = "".join(f'<img id="hi{i}" src="assets/food{n}.jpg">' for i, n in enumerate((1, 2, 3, 4)))
    head = ('<div class="wa-h"><span class="bk">‹</span><div class="wa-av"><img src="assets/logo.jpg"></div>'
            '<div><b>Libby’s Cajun</b><span>en línea</span></div></div>')
    order = ('<div class="oc-in"><div class="oc-k">Pedido #2421</div><div class="oc-t">A domicilio · llega 8:00 pm</div>'
             '<div class="oc-s">Jardines del Valle · paga al recibir</div>'
             '<div class="oc-r"><span>Mariscada Catracha + 2 bebidas</span><b>L1,570</b></div>'
             '<div class="oc-s" style="margin-top:6px">Ya está en la pantalla de cocina</div></div>')
    msgs = [("m1", '<div class="wb out">Buenas, la mariscada catracha a domicilio cuánto sale?<small>6:58 p. m.</small></div>'),
            ("t1", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m2", '<div class="wb in">¡Hola! 🦞 La Mariscada Catracha Louisiana está en L1,450. ¿A qué colonia sería?<small>6:58 p. m.</small></div>'),
            ("m3", '<div class="wb out">Jardines del Valle. Una mariscada y 2 bebidas, pago en efectivo<small>6:59 p. m.</small></div>'),
            ("t2", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m4", '<div class="wb in">¡Listo! Se la llevamos 🛵<small>6:59 p. m.</small></div>'),
            ("m5", f'<div class="ocard">{order}</div>'),
            ("m6", '<div class="wb in">Ya está en cocina. Le aviso cuando salga 🛵<small>6:59 p. m.</small></div>')]
    wa = (f'<div class="wa">{head}<div class="wa-msgs">' + "".join(f'<div class="slot" id="{i}">{h}</div>' for i, h in msgs)
          + '</div><div class="wa-in">Mensaje</div></div>')
    whyl = ["Su menú y sus precios, no una plantilla.", "Su mismo número de WhatsApp.",
            "Su equipo no aprende nada nuevo.", "Nosotros lo instalamos y lo cambiamos cuando cambie el menú."]
    why_html = "".join(f'<div class="wl" id="wl{i}"><i>✓</i><span>{t}</span></div>' for i, t in enumerate(whyl))
    autos = [("Tomar el pedido completo, con total", "qué quiere, para cuándo y cómo paga"),
             ("Mandarlo solo a la cocina", "a una pantalla, sin copiarlo a mano"),
             ("Anotar las reservaciones", "cumpleaños y cenas, con recordatorio"),
             ("Avisarle al proveedor", "cuando el camarón baja del mínimo")]
    auto_html = "".join(f'<div class="ar" id="ar{i}"><i>{i + 1}</i><b>{t}</b><span>{d}</span></div>' for i, (t, d) in enumerate(autos))
    scr = {sid: f'<div class="scr" id="scr-{sid}"><div class="in"><img id="img-{sid}" src="assets/{f}"></div></div>' for sid, f, _, _ in SHOTS}
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f"""
          <div class="sp sp-red"></div>
          <div class="sp sp-gold"></div>
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("una propuesta para")}</div>
            <div class="ilogo" id="ilogo"><img src="assets/logo.jpg"></div>
            <div class="iname" id="iname">Libby's Cajun</div>
          </div>"""),
        scene("fame", f"""
          <div class="sp sp-red"></div>
          <div class="hist" id="hist">{hist}<div class="cap2">Sus videos · su TikTok</div></div>
          <div class="left">
            <div class="eb" id="f0">TikTok · @libbyscajun</div>
            <div class="h1" id="f1">{words("Mariscos al estilo")}</div>
            <div class="h1" id="f2">{words("Louisiana en San Pedro Sula,")}</div>
            <div class="h1" id="f3">{gold("que llenan TikTok.")}</div>
            <div class="stats">{stats_html}</div>
          </div>"""),
        scene("asks", f"""
          <div class="sp sp-gold"></div>
          <div class="cms">{cms}</div>
          <div class="left">
            <div class="lgrp" id="ag1"><div class="chip red" id="a0"><b>1</b>El problema</div><div class="h1 m" id="a1">{words("Cada video trae")}</div><div class="h1 m" id="a2">{words("las mismas preguntas.")}</div></div>
            <div class="lgrp" id="ag2"><div class="chip red" id="a0b"><b>1</b>El problema</div><div class="h1 m" id="a3">{words("Precio, ubicación")}</div><div class="h1 m" id="a4">{gold("y para cuántos alcanza.")}</div></div>
          </div>
          <div class="foot" id="afoot">Comentarios reales de sus videos</div>"""),
        scene("paste", f"""
          <div class="sp sp-red"></div>
          <div class="paste" id="paste"><div class="hd"><img src="assets/logo.jpg">Su video más visto · 1.1M de vistas</div>
            <div class="q">“Nueva mariscada Catracha Louisiana”</div>
            <div class="a"><span>Su perfil:</span><div>“Restaurante al estilo Louisiana en SPS 🇭🇳 Pedidos al 9309-9296 🦞🦀”</div></div></div>
          <div class="copies" id="copies"><b><span id="nc">1</span> de 94</b><span>comentarios contestados por ustedes</span></div>
          <div class="left">
            <div class="lgrp" id="pg1"><div class="chip red" id="p0"><b>1</b>El problema</div><div class="h1 m" id="p1">{words("Ustedes contestan,")}</div><div class="h1 m" id="p2">{gold("y mucho.")}</div>
              <div class="sub" id="p3">{words("Y en WhatsApp ya tienen el asistente de Meta, que contesta y pasa a una persona.")}</div></div>
            <div class="lgrp" id="pg2"><div class="chip red" id="p0b"><b>1</b>El problema</div><div class="h1 m" id="p4">{words("Pero el pedido")}</div><div class="h1 m" id="p5">{gold("se queda en el chat.")}</div></div>
          </div>"""),
        scene("prop", f"""
          <div class="sp sp-green"></div>
          <div class="auto" id="auto"><div class="k" id="autok">Lo que el sistema hace solo</div>{auto_html}</div>
          <div class="allp" id="allp"><span>Y usted lo ve todo en un panel</span></div>
          <div class="left">
            <div class="chip green" id="o0"><b>2</b>La solución</div>
            <div class="h1 m" id="o1">{words("Por eso les")}</div>
            <div class="h1 m" id="o2">{gold("proponemos esto.")}</div>
            <div class="sub" id="o3">{words("Creamos un sistema para lo que pasa después del chat: pedidos, cocina, reservaciones y ventas.")}</div>
          </div>"""),
        scene("meet", f"""
          <div class="sp sp-green"></div>
          <div class="bio" id="bio"><div class="top"><img src="assets/logo.jpg" style="object-fit:cover;background:#fff"><div><b>Libby’s Cajun San Pedro Sula</b><span>@libbyscajun</span></div></div>
            <div class="sig">Restaurante al estilo Louisiana en SPS 🇭🇳 Pedidos al 9309-9296 🦞🦀</div>
            <div class="lnk" id="lnk"><i></i>WhatsApp 9309-9296</div></div>
          <div class="pin" id="pin"><div class="k">💬 El mismo WhatsApp de siempre</div><p>El asistente que ya tienen se queda. <b>Lo nuevo es lo que pasa después</b>: el pedido llega solo a cocina.</p></div>
          <div class="nums" id="nums"><span>Pedido completo</span><span>Con total</span><span>Cómo paga</span></div>
          <div class="one" id="one"><span>Directo a la cocina</span></div>
          <div class="left">
            <div class="chip green" id="e0"><b>2</b>La solución</div>
            <div class="h1 m" id="e1">{words("Su mismo WhatsApp,")}</div>
            <div class="h1 m" id="e2">{gold("con el pedido")}</div>
            <div class="h1 m" id="e3">{gold("directo a cocina.")}</div>
          </div>
          <div class="demo" id="edemo">No cambia su número ni lo que ve el cliente</div>"""),
        scene("bot", f"""
          <div class="sp sp-green"></div>
          <div class="ph-stage">{gen3.phone(wa, "phw", dark=True)}</div>
          <div class="left">
            <div class="lgrp" id="bg1"><div class="chip green" id="b10"><b>2</b>Al instante, a cualquier hora</div><div class="h1" id="b11">{words("Contesta el")}</div><div class="h1" id="b12">{gold("precio al instante.")}</div></div>
            <div class="lgrp" id="bg2"><div class="chip green" id="b20"><b>2</b>Como lo quiere el cliente</div><div class="h1" id="b21">{words("Toma el pedido")}</div><div class="h1" id="b22">{gold("completo.")}</div></div>
            <div class="lgrp" id="bg3"><div class="chip green" id="b30"><b>2</b>Sin copiar nada</div><div class="h1" id="b31">{words("Y lo manda solo")}</div><div class="h1" id="b32">{gold("a la cocina.")}</div></div>
          </div>
          <div class="demo" id="bdemo">Conversación y precios de ejemplo · el asistente usa su menú y sus precios</div>"""),
        scene("pa", f"""
          <div class="sp sp-gold"></div>
          {scr["pa"]}
          <div class="left">
            <div class="chip gold" id="qa0"><b>3</b>Su panel</div>
            <div class="h1 m" id="qa1">{words("Todo el negocio")}</div>
            <div class="h1 m" id="qa2">{gold("en su celular.")}</div>
            <div class="sub" id="qa3">{words("Lo que se vendió hoy, lo más pedido, la cocina y las reservaciones.")}</div>
          </div>
          <div class="demo" id="qademo">Panel demo · nombres de platos y número reales, ventas de ejemplo</div>"""),
        scene("pb", f"""
          <div class="sp sp-green"></div>
          {scr["pb"]}
          <div class="left">
            <div class="chip gold" id="qb0"><b>3</b>Su panel</div>
            <div class="h1 m" id="qb1">{words("Del chat")}</div>
            <div class="h1 m" id="qb2">{gold("a la cocina.")}</div>
            <div class="sub" id="qb3">{words("Cada pedido de WhatsApp llega completo y con el total a la pantalla de cocina.")}</div>
          </div>
          <div class="demo" id="qbdemo">Panel demo · conversaciones de ejemplo</div>"""),
        scene("pc", f"""
          <div class="sp sp-gold"></div>
          {scr["pc"]}
          <div class="left">
            <div class="chip gold" id="qc0"><b>3</b>Su panel</div>
            <div class="h1 m" id="qc1">{words("Cumpleaños y cenas,")}</div>
            <div class="h1 m" id="qc2">{gold("bien anotados.")}</div>
            <div class="sub" id="qc3">{words("Con hora y personas, y un recordatorio al cliente el mismo día.")}</div>
          </div>
          <div class="demo" id="qcdemo">Panel demo · reservaciones de ejemplo</div>"""),
        scene("why", f"""
          <div class="sp sp-red"></div>
          <div class="whyl">{why_html}</div>
          <div class="result" id="result"><div class="k">Lo que gana Libby's Cajun</div><p>Pedidos completos, directo a cocina.<br>Reservaciones que no se pierden.<br><b>Y las ventas del día en su celular.</b></p></div>
          <div class="left">
            <div class="chip gold" id="y0"><b>4</b>Por qué nosotros</div>
            <div class="h1 m" id="y1">{words("Hecho para")}</div>
            <div class="h1 m" id="y2">{gold("Libby's Cajun.")}</div>
          </div>"""),
        scene("us", f"""
          <div class="sp sp-gold"></div>
          <div class="left">
            <div class="eb g" id="u0">Casa Digital</div>
            <div class="h1 m" id="u1">{words("Se lo mostramos")}</div>
            <div class="h1 m" id="u2">{gold("funcionando con su menú.")}</div>
            <div class="sub" id="u3">{words("Los primeros 30 días son gratis, sin compromiso.")}</div>
          </div>
          <div class="cta2" id="cta">
            <div class="ic">{gen3.HOUSE}</div>
            <div class="t">Casa Digital</div>
            <div class="s">Se lo mostramos en 10 minutos.</div>
            <div class="wa2"><span>WhatsApp</span>{gen3.WHATSAPP}</div>
            <div class="who">Rodrigo Herrera</div>
          </div>"""),
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

    # their colors: the orange-red of their sign, with the gold accents of the series
    css = (gen3.CSS.replace("$heroB", "#170c08").replace("$hero", "#E8553A").replace("$acc", "#F06A45").replace("$pri", "#F2B544")
           .replace("$washA", "rgba(0,0,0,0)").replace("$washB", "rgba(0,0,0,0)").replace("$sitebg", "#0B141A").replace("$siteink", "#fff")
           .replace("$dweight", "400").replace("$dcase", "uppercase").replace("$dtrack", "-0.01em")
           .replace("$italface", "").replace("$ital", '"Display"').replace("$introsizepx", "112px"))
    css += TG.CSS_BASE + TG.CSS_T + CSS_M + TG.CSS_V + CSS_MV
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    bars = {i: (a, b) for i, a, b in SCENES}
    shots_js = json.dumps([[sid, *bars[sid], stops] for sid, _, _, stops in SHOTS])
    j6 = gen6.JS
    helpers = TG.JS_T[:TG.JS_T.index("// 1 · intro")]
    js = (j6[:j6.index("// 1 · intro")] + helpers + JS_M
          + re.sub(r"K\((\d+(?:\.\d+)?)\)", lambda m: f"K({float(m.group(1)) + OUTRO_SHIFT:g})", j6[j6.index("// 11 · outro"):])
          ).replace("$scenes", scenes_js).replace("$shots", shots_js).replace("$scale", str(SCR_W / 390)).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = (gen3.HTML.replace("$title", "Casa Digital x Libby's Cajun").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)).replace('data-fade-out="2.5"', 'data-fade-out="4"'))
    html = (html.replace('content="width=1920, height=1080"', 'content="width=1080, height=1920"')
            .replace('data-width="1920" data-height="1080"', 'data-width="1080" data-height="1920"'))
    n = iter(range(100))  # soft lights kept on the narrow frame, alternating high and low
    html = re.sub(r'(<div class="sp sp-\w+")(?: style="[^"]*")?', lambda m: m.group(1) + (' style="left:-260px;top:%dpx;width:1600px;height:1600px"' % (-500 if next(n) % 2 == 0 else 700)), html)
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


JS_M = r'''
// 1 · intro
rise("#icd", 0.4, { d: 2 });
rise("#ipres .w", K(.9), { d: 1.6, st: .12 });
tl.fromTo("#ilogo", { opacity: 0, scale: .9, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(1.3));
tl.fromTo("#iname", { opacity: 0, y: 30, filter: "blur(20px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.4, ease: SOFT }, K(1.7));

// 2 · their restaurant and frames of their own videos (3 bars)
rise("#f0", K(3), { d: 1.2 }); rise("#f1 .w", K(3) + .2); rise("#f2 .w", K(3) + .5); rise("#f3 .w", K(3) + .8, { d: 1.8 });
tl.fromTo("#hist", { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(3) + .3);
tl.fromTo("#hist img", { scale: 1.05 }, { scale: 1, duration: K(6) - K(3), ease: "none" }, K(3));
tl.set("#hi1, #hi2, #hi3", { opacity: 0 }, 0);
[3.9, 4.6, 5.3].forEach((k, i) => tl.fromTo("#hi" + (i + 1), { opacity: 0 }, { opacity: 1, duration: 1, ease: "sine.inOut" }, K(k)));
[3.8, 4.2, 4.6].forEach((k, i) => rise("#st" + i, K(k), { y: 30, d: 1.4 }));

// 3 · PROBLEM: real questions from their TikTok comments (4 bars)
rise("#a0", K(6), { d: 1.2 }); rise("#a1 .w", K(6) + .3); rise("#a2 .w", K(6) + .6);
[6.3, 6.8, 7.3, 7.8].forEach((k, i) => rise("#cm" + i, K(k), { y: 40, d: 1.6 }));
rise("#afoot", K(6.8), { d: 1.2 });
out("#ag1", K(8.2) - .8);
rise("#a0b", K(8.2), { d: 1 }); rise("#a3 .w", K(8.2)); rise("#a4 .w", K(8.2) + .45, { d: 1.8 });

// 4 · PROBLEM: they answer a lot by hand, and the order stays in the chat (4 bars)
rise("#p0", K(10), { d: 1.2 }); rise("#p1 .w", K(10) + .3); rise("#p2 .w", K(10) + .6, { d: 1.8 });
rise("#p3 .w", K(10.8), { st: .03 });
tl.fromTo("#paste", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(10) + .3);
rise("#copies", K(10.8), { y: 30, d: 1.4 });
count("nc", 1, 57, K(10.8) + .3, n => String(n), 1.6);
out("#pg1", K(12.3) - .8);
rise("#p0b", K(12.3), { d: 1 }); rise("#p4 .w", K(12.3)); rise("#p5 .w", K(12.3) + .45, { d: 1.8 });

// 5 · SOLUTION: "por eso les proponemos esto", what the system automates (5 bars)
rise("#o0", K(14), { d: 1.2 }); rise("#o1 .w", K(14) + .3); rise("#o2 .w", K(14) + .6, { d: 1.8 });
rise("#o3 .w", K(14.8), { st: .03 });
rise("#autok", K(15), { d: 1.2 });
[15.3, 15.9, 16.5, 17.1].forEach((k, i) => rise("#ar" + i, K(k), { y: 30, d: 1.5 }));
tl.fromTo("#allp", { opacity: 0, scale: .9 }, { opacity: 1, scale: 1, duration: 1.4, ease: SOFT }, K(17.9));

// 6 · SOLUTION: their same WhatsApp, with the order going straight to the kitchen (3 bars)
rise("#e0", K(19), { d: 1.2 }); rise("#e1 .w", K(19) + .3); rise("#e2 .w", K(19) + .6); rise("#e3 .w", K(19) + .9, { d: 1.8 });
tl.fromTo("#bio", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(19) + .3);
tl.fromTo("#lnk", { scale: 1 }, { scale: 1.06, duration: .5, yoyo: true, repeat: 1, ease: "sine.inOut" }, K(19.8));
tl.fromTo("#pin", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 1.6, ease: SOFT }, K(20));
rise("#nums span", K(20.4), { y: 20, d: 1.2, st: .1 });
tl.to("#nums span", { opacity: 0, scale: .8, filter: "blur(8px)", duration: .8, stagger: .05, ease: "power2.in" }, K(21.05));
tl.fromTo("#one", { opacity: 0, scale: .85 }, { opacity: 1, scale: 1, duration: 1.3, ease: SOFT }, K(21.3));
rise("#edemo", K(19.5), { d: 1.2 });

// 7 · SOLUTION: the assistant answers the price and takes a delivery order (7 bars)
tl.fromTo("#phw", { y: 700, rotationY: -16, rotationX: 6 }, { y: 0, rotationY: -6, rotationX: 2, duration: 2.4, ease: SOFT }, K(22));
tl.to("#phw", { rotationY: 4, rotationX: 0, duration: K(29) - K(23), ease: "sine.inOut" }, K(23));
rise("#bdemo", K(22.5), { d: 1.2 });
rise("#b10", K(22), { d: 1.2 }); rise("#b11 .w", K(22) + .3); rise("#b12 .w", K(22) + .6);
show("m1", K(22.5)); show("t1", K(23)); dots("t1", K(23) + .3); hide("t1", K(23.6)); show("m2", K(23.6));
out("#bg1", K(24.7) - .8);
rise("#b20", K(24.7), { d: 1.2 }); rise("#b21 .w", K(24.7) + .3); rise("#b22 .w", K(24.7) + .6);
show("m3", K(24.8)); show("t2", K(25.5)); dots("t2", K(25.5) + .3); hide("t2", K(26)); show("m4", K(26));
out("#bg2", K(27.1) - .8);
rise("#b30", K(27.1), { d: 1.2 }); rise("#b31 .w", K(27.1) + .3); rise("#b32 .w", K(27.1) + .6);
show("m5", K(26.9)); show("m6", K(27.7));

// 8-10 · PANEL: the real demo panel scrolling slowly, holding on each part (4, 4, 3 bars)
const SHOTS = $shots;
SHOTS.forEach(([sid, s0, e0, stops]) => {
  rise(`#q${sid[1]}0`, K(s0), { d: 1.2 }); rise(`#q${sid[1]}1 .w`, K(s0) + .3); rise(`#q${sid[1]}2 .w`, K(s0) + .6, { d: 1.8 });
  rise(`#q${sid[1]}3 .w`, K(s0 + .8), { st: .03 }); rise(`#q${sid[1]}demo`, K(s0 + .5), { d: 1.2 });
  tl.fromTo(`#scr-${sid}`, { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(s0) + .2);
  const sc = $scale, img = `#img-${sid}`; tl.set(img, { y: -stops[0] * sc }, 0);
  const seg = (e0 - s0) / stops.length;
  stops.slice(1).forEach((y, i) => tl.to(img, { y: -y * sc, duration: 1.6, ease: FINE }, K(s0 + seg * (i + 1)) - .4));
});

// 11 · WHY US (4 bars)
rise("#y0", K(40), { d: 1.2 }); rise("#y1 .w", K(40) + .3); rise("#y2 .w", K(40) + .6, { d: 1.8 });
[40.5, 41, 41.5, 42].forEach((k, i) => rise("#wl" + i, K(k), { y: 24, d: 1.3 }));
tl.fromTo("#result", { opacity: 0, y: 60, scale: .97 }, { opacity: 1, y: 0, scale: 1, duration: 1.7, ease: SOFT }, K(42.6));
// 12 · Casa Digital, call to action (4 bars)
rise("#u0", K(44), { d: 1.2 }); rise("#u1 .w", K(44) + .3); rise("#u2 .w", K(44) + .7, { d: 1.8 });
rise("#u3 .w", K(44.9), { st: .03 });
tl.fromTo("#cta", { opacity: 0, y: 90, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 2.2, ease: SOFT }, K(44.5));
float("#cta", K(45.4), K(48) - K(45.4));

// every scene fades out softly just before its bar line, so nothing is chopped and nothing overlaps
$scenes.forEach(([id, s, e]) => { if (id !== "end") tl.to("#cam-" + id, { opacity: 0, y: -24, filter: "blur(10px)", duration: .7, ease: "power2.in" }, e - .75); });

'''

if __name__ == "__main__":
    print(build())
