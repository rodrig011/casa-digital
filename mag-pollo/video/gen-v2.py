#!/usr/bin/env python3
"""Mag Pollo pitch video v2 (2026-10-17), kept for the record; gen.py makes the current one.

rodrigo on v1 (gen-v1.py): "no quedó claro, no mostraste bien el panel, ni qué problema solucionamos,
ni por qué deberían contratarnos". v2 keeps the same look (dark, soft lights, full phrases with gold
keywords, Clientia Tech outro) and tells it in four labelled parts:
1 El problema: real comments, the four-branch block they paste by hand 16+ times, five phone numbers.
2 La solución: link in the bio + pinned comment -> one WhatsApp (the bot does NOT answer TikTok comments),
  the bot with the real L399 promo, nearest branch, order to that kitchen; delivery per branch.
3 Su panel: three big screens of the owner panel (Hoy, Pedidos en vivo, Qué hacer hoy).
4 Por qué nosotros: made for their four branches, nothing new to learn, we install and keep it up to date,
  a new branch the same day, and the result. Then Casa Digital and the outro.
Everything about them comes from their own TikTok @magpollohn; conversations and panel numbers are
examples, labelled on screen. No question method, no clips of the owner, nothing from Coco Chicken.

Music: src/musica.mp3. Cuts land on bars: MUSIC_P0 (first downbeat, s) and MUSIC_BAR (bar length, s)
set the grid; the defaults are "Stylish" by FASSounds (110 BPM), the song rodrigo picked on 2026-10-17.
Helpers come from coco-chicken/video and toretos-grill/video/gen.py, like bochas-grill/video/gen.py.
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
SLUG = "mag-pollo-v2-vertical"
SCENES = [("intro", 0, 3), ("fame", 3, 6), ("asks", 6, 10), ("paste", 10, 14), ("meet", 14, 18), ("bot", 18, 25),
          ("moto", 25, 28), ("p1", 28, 32), ("p2", 32, 36), ("p3", 36, 39), ("why", 39, 44), ("us", 44, 48), ("end", 48, 52)]
TOTAL = K(52)
OUTRO_SHIFT = 48 - 37  # gen6's outro starts on bar 37


def gold(t):
    return f'<span class="gold">{words(t)}</span>'


def cm(text, i, pre="cm"):
    return f'<div class="cm" id="{pre}{i}"><div class="cm-h"><i></i>Comentario en su TikTok</div><p>{text}</p></div>'


CSS_M = r'''
.ilogo{width:300px;height:300px;}
.wa-av{background:#F6A51C;}
/* their own menu photos */
.hist{position:absolute;left:180px;top:800px;width:720px;height:960px;border-radius:40px;overflow:hidden;box-shadow:0 0 0 1px rgba(255,255,255,.1),0 50px 120px rgba(0,0,0,.6);}
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
/* the owner panel card */
.pnl{position:absolute;left:90px;width:900px;top:820px;background:linear-gradient(180deg,#161618,#0F0F10);border-radius:40px;padding:34px 40px 36px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 60px 140px rgba(0,0,0,.7);}
.pnl .hd{display:flex;align-items:center;justify-content:space-between;}
.pnl .hd .t{display:flex;align-items:center;gap:16px;font-size:30px;font-weight:600;}
.pnl .hd img{width:56px;height:56px;border-radius:50%;}
.pnl .hd span{font-size:22px;color:#8E8E93;}
.pnl .kpi{display:flex;align-items:baseline;gap:20px;margin-top:26px;}
.pnl .kpi b{font-size:84px;font-weight:600;letter-spacing:-.04em;line-height:1;font-variant-numeric:tabular-nums;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;}
.pnl .kpi > span{font-size:26px;color:#8E8E93;}
.pnl .sec{font-size:20px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#8E8E93;margin-top:30px;}
.br{display:grid;grid-template-columns:260px 1fr 150px;align-items:center;gap:20px;margin-top:16px;}
.br .n{font-size:28px;font-weight:600;color:#F5F5F7;}
.br .bar{height:16px;border-radius:8px;background:rgba(255,255,255,.07);overflow:hidden;}
.br .bar i{display:block;height:100%;border-radius:8px;background:linear-gradient(90deg,#D8261C,#F2B544);transform-origin:left;}
.br .v{font-size:28px;font-weight:600;text-align:right;font-variant-numeric:tabular-nums;}
.pr{display:flex;align-items:center;justify-content:space-between;margin-top:14px;padding:18px 22px;border-radius:20px;background:rgba(255,255,255,.04);}
.pr b{font-size:28px;font-weight:600;}
.pr span{font-size:26px;color:#8E8E93;font-variant-numeric:tabular-nums;}
.pr.top{box-shadow:0 0 0 2px rgba(242,181,68,.45);background:rgba(242,181,68,.08);}
.pr.top span{color:#F2B544;}
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
.chip.gold{color:#F2B544;background:rgba(242,181,68,.10);box-shadow:0 0 0 1px rgba(242,181,68,.4);}.chip.gold b{background:#F2B544;}
.lgrp .chip{margin-bottom:26px;}
.tabs{display:flex;gap:10px;margin-top:22px;padding:6px;border-radius:16px;background:rgba(255,255,255,.05);}
.tabs span{flex:1;text-align:center;font-size:24px;font-weight:600;color:#8E8E93;padding:12px 0;border-radius:12px;}
.tabs span.on{background:rgba(242,181,68,.16);color:#F2B544;}
.chs{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:16px;}
.ch{padding:18px 16px;border-radius:18px;background:rgba(255,255,255,.05);text-align:center;}
.ch b{display:block;font-size:40px;font-weight:600;font-variant-numeric:tabular-nums;}
.ch span{display:block;font-size:19px;color:#8E8E93;margin-top:4px;}
.od{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:22px 0;border-bottom:1px solid rgba(255,255,255,.08);}
.od b{display:block;font-size:34px;font-weight:600;}
.od span{display:block;font-size:24px;color:#8E8E93;margin-top:4px;}
.od .st{font-size:24px;font-weight:600;padding:10px 18px;border-radius:999px;white-space:nowrap;margin:0;}
.od .st.ok{color:#5FD38A;background:rgba(95,211,138,.12);}.od .st.go{color:#F2B544;background:rgba(242,181,68,.12);}
.zero{display:flex;align-items:center;justify-content:space-between;margin-top:22px;padding:22px 28px;border-radius:22px;background:rgba(37,211,102,.08);box-shadow:0 0 0 2px rgba(37,211,102,.4);}
.zero span{font-size:28px;font-weight:600;color:#C7F5D6;}
.zero b{font-size:72px;font-weight:600;color:#25D366;line-height:1;}
.ac{display:grid;grid-template-columns:64px 1fr;gap:6px 20px;align-items:start;margin-top:22px;padding:24px;border-radius:24px;background:rgba(255,255,255,.04);}
.ac i{grid-row:span 2;width:64px;height:64px;border-radius:18px;background:rgba(242,181,68,.12);display:flex;align-items:center;justify-content:center;font-size:34px;font-style:normal;}
.ac b{display:block;font-size:30px;font-weight:600;line-height:1.25;}
.ac span{display:block;font-size:23px;color:#8E8E93;margin-top:6px;}
.ac em{grid-column:2;justify-self:start;margin-top:12px;font-style:normal;font-size:24px;font-weight:700;color:#0B0B0C;background:#F2B544;padding:12px 22px;border-radius:999px;}
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
#asks .cms{top:840px;height:980px;}
#moto .riders{top:820px;}
#moto .rd{grid-template-columns:1fr 150px 230px;}
#paste .left .sub{margin-top:22px;}
.pnl{top:800px;}
#p2 .pnl,#p3 .pnl{top:760px;}
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
    for n in ("logo.jpg", "food1.jpg", "food2.jpg", "food3.jpg", "food4.jpg"):
        shutil.copy(os.path.join(SRC, n), A(n))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "mag-pollo-v1", "name": "Casa Digital x Mag Pollo"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    # verbatim comments from redes/tiktok-comentarios.txt
    cms = "".join(cm(t, i) for i, t in enumerate(["donde están ubicados", "precio de las 24 alitas", "O sea que hacen envíos ??", "cuando para El Progreso?"]))
    stats = [("4", "sucursales en SPS"), ("63K", "vistas de su promo de alitas"), ("14.9K", "seguidores")]
    stats_html = "".join(f'<div class="st" id="st{i}"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(stats))
    hist = "".join(f'<img id="hi{i}" src="assets/food{n}.jpg">' for i, n in enumerate((1, 2, 3, 4)))
    # their own reply, as they paste it (shortened to the four lines)
    block = ('<div>📍 Plaza Calpules <span>· 9730-5423</span></div><div>📍 Plaza Prisma <span>· 3154-8175</span></div>'
             '<div>📍 Plaza La Guardia <span>· 3154-8195</span></div><div>📍 MAG POLLO Costas <span>· 3154-8697</span></div>')
    head = ('<div class="wa-h"><span class="bk">‹</span><div class="wa-av"><img src="assets/logo.jpg"></div>'
            '<div><b>Mag Pollo</b><span>en línea</span></div></div>')
    order = ('<div class="oc-in"><div class="oc-k">Pedido #4208</div><div class="oc-t">A domicilio</div>'
             '<div class="oc-s">Res. Santa Mónica · lo prepara Plaza Prisma</div>'
             '<div class="oc-r"><span>1 × Promo 24 alitas</span><b>L399</b></div>'
             '<div class="oc-s" style="margin-top:6px">papas familiar · refresco 1.1 L</div></div>')
    msgs = [("m1", '<div class="wb out">precio de las 24 alitas? y donde quedan<small>6:40 p. m.</small></div>'),
            ("t1", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m2", '<div class="wb in">¡Hola! 24 alitas + papas fritas familiar + refresco 1.1 L por L399, todo el mes. ¿Desde qué colonia nos escribe?<small>6:40 p. m.</small></div>'),
            ("m3", '<div class="wb out">res. santa monica, me la traen?<small>6:41 p. m.</small></div>'),
            ("t2", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m4", '<div class="wb in">Le queda cerca Plaza Prisma, blv. del norte. Sí se la llevamos 🛵<small>6:41 p. m.</small></div>'),
            ("m5", f'<div class="ocard">{order}</div>'),
            ("m6", '<div class="wb in">¡Listo! Ya está en la cocina de Plaza Prisma. Le aviso cuando salga.<small>6:42 p. m.</small></div>')]
    wa = (f'<div class="wa">{head}<div class="wa-msgs">' + "".join(f'<div class="slot" id="{i}">{h}</div>' for i, h in msgs)
          + '</div><div class="wa-in">Mensaje</div></div>')
    rides = [("Plaza Prisma", "Res. Santa Mónica", "6:58", "go", "En camino"), ("Plaza Calpules", "Col. Jardines del Valle", "7:05", "go", "En camino"),
             ("Plaza La Guardia", "Bo. Guamilito", "6:52", "ok", "✓ Entregado"), ("Costas", "Res. Costa Verde", "7:10", "go", "Saliendo")]
    ride_rows = "".join(f'<div class="rd" id="rd{i}"><div class="n">{n}<span>{s}</span></div><div class="c">{m}</div><div class="st {c}" id="rs{i}">{t}</div></div>'
                        for i, (n, s, m, c, t) in enumerate(rides))
    branches = [("Plaza Calpules", 1.0, "L18,420"), ("Plaza Prisma", .74, "L13,610"), ("Plaza La Guardia", .62, "L11,390"), ("Costas", .55, "L10,080")]
    br_html = "".join(f'<div class="br" id="br{i}"><div class="n">{n}</div><div class="bar"><i id="bb{i}" data-w="{w}"></i></div><div class="v">{v}</div></div>'
                      for i, (n, w, v) in enumerate(branches))
    promos = [("Pechuga con tajadas L99", "212 hoy", True), ("24 alitas L399", "64 hoy", False), ("4 en 1", "48 hoy", False)]
    pr_html = "".join(f'<div class="pr{" top" if t else ""}" id="pr{i}"><b>{n}</b><span>{v}</span></div>' for i, (n, v, t) in enumerate(promos))
    def tabs(i):
        t = "".join(f'<span class="{"on" if k == i else ""}">{n}</span>' for k, n in enumerate(["Hoy", "Pedidos", "Qué hacer"]))
        return f'<div class="hd"><div class="t"><img src="assets/logo.jpg">Panel Mag Pollo</div><span>Hoy · 7:00 pm</span></div><div class="tabs">{t}</div>'
    chans = [("Mostrador", "38%"), ("Autoservicio", "22%"), ("Delivery", "24%"), ("WhatsApp", "16%")]
    ch_html = "".join(f'<div class="ch" id="ch{i}"><b>{v}</b><span>{n}</span></div>' for i, (n, v) in enumerate(chans))
    orders = [("#4208", "Plaza Prisma · Delivery", "En cocina · 6 min", "go"), ("#4207", "Plaza Calpules · Autoservicio", "✓ Entregado", "ok"),
              ("#4206", "Plaza La Guardia · Para recoger", "Listo 7:15", "go"), ("#4205", "Costas · Delivery", "En camino", "go")]
    ord_html = "".join(f'<div class="od" id="od{i}"><div><b>{a}</b><span>{b}</span></div><div class="st {c}">{t}</div></div>' for i, (a, b, t, c) in enumerate(orders))
    acts = [("🔥", "Pechuga L99: 212 vendidas hoy", "La más vendida de la semana", "Repetir el sábado"),
            ("🛵", "Plaza Prisma: 3 deliveries de más de 40 min", "Hoy entre 6 y 7 pm", "Ver motoristas"),
            ("📉", "Costas vende menos los lunes", "Las últimas 4 semanas", "Crear promo lunes")]
    act_html = "".join(f'<div class="ac" id="ac{i}"><i>{e}</i><div><b>{t}</b><span>{d}</span></div><em>{c}</em></div>' for i, (e, t, d, c) in enumerate(acts))
    whyl = ["Su menú, sus promos y sus 4 sucursales, no una plantilla.", "Su equipo no aprende nada nuevo: todo pasa en WhatsApp.",
            "Nosotros lo instalamos y lo cambiamos con cada promo.", "Cuando abran El Progreso, se agrega el mismo día."]
    why_html = "".join(f'<div class="wl" id="wl{i}"><i>✓</i><span>{t}</span></div>' for i, t in enumerate(whyl))
    whys = ["Lo armamos con sus 4 sucursales.", "Funciona en su WhatsApp de siempre.", "Soporte por WhatsApp, en español."]
    whys_html = "".join(f'<div class="wy2" id="wy{i}"><i>✓</i><span>{words(t)}</span></div>' for i, t in enumerate(whys))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          <div class="sp sp-red"></div>
          <div class="sp sp-gold"></div>
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("una propuesta para")}</div>
            <div class="ilogo" id="ilogo"><img src="assets/logo.jpg"></div>
            <div class="iname" id="iname">Mag Pollo</div>
          </div>'''),
        scene("fame", f'''
          <div class="sp sp-red"></div>
          <div class="hist" id="hist">{hist}<div class="cap2">Sus platos · su propio TikTok</div></div>
          <div class="left">
            <div class="eb" id="f0">TikTok · @magpollohn</div>
            <div class="h1" id="f1">{words("Cuatro sucursales")}</div>
            <div class="h1" id="f2">{words("en San Pedro,")}</div>
            <div class="h1" id="f3">{gold("y mucha gente preguntando.")}</div>
            <div class="stats">{stats_html}</div>
          </div>'''),
        scene("asks", f'''
          <div class="sp sp-gold"></div>
          <div class="cms">{cms}</div>
          <div class="left">
            <div class="lgrp" id="ag1"><div class="chip red" id="a0"><b>1</b>El problema</div><div class="h1 m" id="a1">{words("Todos los días")}</div><div class="h1 m" id="a2">{words("les preguntan lo mismo.")}</div></div>
            <div class="lgrp" id="ag2"><div class="chip red" id="a0b"><b>1</b>El problema</div><div class="h1 m" id="a3">{words("Y cada respuesta")}</div><div class="h1 m" id="a4">{gold("la escribe una persona.")}</div></div>
          </div>
          <div class="foot" id="afoot">Comentarios reales en su TikTok @magpollohn</div>'''),
        scene("paste", f'''
          <div class="sp sp-red"></div>
          <div class="paste" id="paste"><div class="hd"><img src="assets/logo.jpg">Respuesta de Mag Pollo en su TikTok</div>
            <div class="q">“ubicación xf”</div>
            <div class="a">🏠 Visítanos:{block}</div></div>
          <div class="copies" id="copies"><b><span id="nc">1</span></b><span>veces, a mano</span></div>
          <div class="left">
            <div class="lgrp" id="pg1"><div class="chip red" id="p0"><b>1</b>El problema</div><div class="h1 m" id="p1">{words("La misma respuesta,")}</div><div class="h1 m" id="p2">{gold("pegada 16 veces.")}</div>
              <div class="sub" id="p3">{words("Y el cliente tiene cinco números distintos para escribir.")}</div></div>
            <div class="lgrp" id="pg2"><div class="chip red" id="p0b"><b>1</b>El problema</div><div class="h1 m" id="p4">{words("Mientras alguien pega direcciones,")}</div><div class="h1 m" id="p5">{gold("nadie toma pedidos.")}</div></div>
          </div>'''),
        scene("meet", f'''
          <div class="sp sp-green"></div>
          <div class="bio" id="bio"><div class="top"><img src="assets/logo.jpg"><div><b>MAG POLLO</b><span>@magpollohn</span></div></div>
            <div class="sig">📍 Plaza Calpules 📍 Plaza Prisma 📍 Plaza La Guardia 📍 Costas</div>
            <div class="lnk" id="lnk"><i></i>Pedí por WhatsApp</div></div>
          <div class="pin" id="pin"><div class="k">📌 Comentario fijado</div><p>Precios, sucursal más cercana y pedidos: <b>escríbanos al WhatsApp</b>, le contesta al instante.</p></div>
          <div class="nums" id="nums"><span>9730-5423</span><span>3154-8175</span><span>3154-8195</span><span>3154-8697</span><span>8842-5808</span></div>
          <div class="one" id="one"><span>Un solo WhatsApp</span></div>
          <div class="left">
            <div class="chip green" id="e0"><b>2</b>La solución</div>
            <div class="h1 m" id="e1">{words("Un solo WhatsApp")}</div>
            <div class="h1 m" id="e2">{gold("que contesta y toma")}</div>
            <div class="h1 m" id="e3">{gold("pedidos solo.")}</div>
          </div>
          <div class="demo" id="edemo">Ejemplo · los cinco números son los que ustedes publican</div>'''),
        scene("bot", f'''
          <div class="sp sp-green"></div>
          <div class="ph-stage">{gen3.phone(wa, "phw", dark=True)}</div>
          <div class="left">
            <div class="lgrp" id="bg1"><div class="chip green" id="b10"><b>2</b>Al instante, a cualquier hora</div><div class="h1" id="b11">{words("Contesta el precio")}</div><div class="h1" id="b12">{gold("con la promo real.")}</div></div>
            <div class="lgrp" id="bg2"><div class="chip green" id="b20"><b>2</b>Según la colonia del cliente</div><div class="h1" id="b21">{words("Busca la sucursal")}</div><div class="h1" id="b22">{gold("más cercana.")}</div></div>
            <div class="lgrp" id="bg3"><div class="chip green" id="b30"><b>2</b>Sin copiar nada a mano</div><div class="h1" id="b31">{words("Y manda el pedido")}</div><div class="h1" id="b32">{gold("a esa cocina.")}</div></div>
          </div>
          <div class="demo" id="bdemo">Conversación de ejemplo · la promo de L399 es la suya</div>'''),
        scene("moto", f'''
          <div class="sp sp-red"></div>
          <div class="riders" id="riders"><div class="k">Delivery ahora · 6:50 pm</div>{ride_rows}</div>
          <div class="left">
            <div class="chip green" id="w0"><b>2</b>Su delivery propio</div>
            <div class="h1 m" id="w1">{words("Cada pedido sale")}</div>
            <div class="h1 m" id="w2">{gold("de la sucursal correcta.")}</div>
            <div class="sub" id="w4">{words("Y cuando sale, el cliente recibe un mensaje solo. Nadie tiene que llamar a preguntar.")}</div>
          </div>
          <div class="demo" id="wdemo">Ejemplo</div>'''),
        scene("p1", f'''
          <div class="sp sp-gold"></div>
          <div class="pnl" id="pnl1">{tabs(0)}
            <div class="kpi"><b>L<span id="kv">0</span></b><span>vendido hoy · 4 sucursales</span></div>
            <div class="sec">Por sucursal</div>{br_html}
            <div class="sec">Por canal</div><div class="chs">{ch_html}</div></div>
          <div class="left">
            <div class="chip gold" id="q10"><b>3</b>Su panel</div>
            <div class="h1 m" id="q11">{words("Desde su celular,")}</div>
            <div class="h1 m" id="q12">{gold("cuánto vendió cada sucursal.")}</div>
            <div class="sub" id="q13">{words("Mostrador, autoservicio, delivery y WhatsApp, todo junto y al minuto.")}</div>
          </div>
          <div class="demo" id="q1demo">Panel demo · datos de ejemplo</div>'''),
        scene("p2", f'''
          <div class="sp sp-green"></div>
          <div class="pnl" id="pnl2">{tabs(1)}{ord_html}
            <div class="zero"><span>Clientes esperando respuesta</span><b>0</b></div></div>
          <div class="left">
            <div class="chip gold" id="q20"><b>3</b>Su panel</div>
            <div class="h1 m" id="q21">{words("Cada pedido,")}</div>
            <div class="h1 m" id="q22">{gold("en vivo.")}</div>
            <div class="sub" id="q23">{words("Qué sucursal lo hace, cuánto lleva y si ya salió. Y ningún cliente esperando respuesta.")}</div>
          </div>
          <div class="demo" id="q2demo">Panel demo · datos de ejemplo</div>'''),
        scene("p3", f'''
          <div class="sp sp-gold"></div>
          <div class="pnl" id="pnl3">{tabs(2)}{act_html}</div>
          <div class="left">
            <div class="chip gold" id="q30"><b>3</b>Su panel</div>
            <div class="h1 m" id="q31">{words("Y le dice")}</div>
            <div class="h1 m" id="q32">{gold("qué hacer hoy.")}</div>
          </div>
          <div class="demo" id="q3demo">Panel demo · datos de ejemplo</div>'''),
        scene("why", f'''
          <div class="sp sp-red"></div>
          <div class="whyl">{why_html}</div>
          <div class="result" id="result"><div class="k">Lo que gana Mag Pollo</div><p>Cero clientes sin respuesta.<br>Cero respuestas pegadas a mano.<br><b>Usted ve todo desde su celular.</b></p></div>
          <div class="left">
            <div class="chip gold" id="y0"><b>4</b>Por qué nosotros</div>
            <div class="h1 m" id="y1">{words("Hecho para")}</div>
            <div class="h1 m" id="y2">{gold("Mag Pollo.")}</div>
          </div>'''),
        scene("us", f'''
          <div class="sp sp-gold"></div>
          <div class="left">
            <div class="eb g" id="u0">Casa Digital</div>
            <div class="h1 m" id="u1">{words("Se lo mostramos")}</div>
            <div class="h1 m" id="u2">{gold("funcionando con su menú.")}</div>
            <div class="sub" id="u3">{words("Una llamada de 15 minutos, sin compromiso.")}</div>
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

    # their colors: red and yellow-orange
    css = (gen3.CSS.replace("$heroB", "#2a0806").replace("$hero", "#E3261B").replace("$acc", "#F6A51C").replace("$pri", "#F2B544")
           .replace("$washA", "rgba(0,0,0,0)").replace("$washB", "rgba(0,0,0,0)").replace("$sitebg", "#0B141A").replace("$siteink", "#fff")
           .replace("$dweight", "400").replace("$dcase", "uppercase").replace("$dtrack", "-0.01em")
           .replace("$italface", "").replace("$ital", '"Display"').replace("$introsizepx", "112px"))
    css += TG.CSS_BASE + TG.CSS_T + CSS_M + TG.CSS_V + CSS_MV
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    j6 = gen6.JS
    helpers = TG.JS_T[:TG.JS_T.index("// 1 · intro")]
    js = (j6[:j6.index("// 1 · intro")] + helpers + JS_M
          + re.sub(r"K\((\d+(?:\.\d+)?)\)", lambda m: f"K({float(m.group(1)) + OUTRO_SHIFT:g})", j6[j6.index("// 11 · outro"):])
          ).replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = (gen3.HTML.replace("$title", "Casa Digital x Mag Pollo").replace("$css", css).replace("$body", body)
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

// 2 · their own menu photos, four branches (3 bars)
rise("#f0", K(3), { d: 1.2 }); rise("#f1 .w", K(3) + .2); rise("#f2 .w", K(3) + .5); rise("#f3 .w", K(3) + .8, { d: 1.8 });
tl.fromTo("#hist", { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(3) + .3);
tl.fromTo("#hist img", { scale: 1.05 }, { scale: 1, duration: K(6) - K(3), ease: "none" }, K(3));
tl.set("#hi1, #hi2, #hi3", { opacity: 0 }, 0);
[3.9, 4.6, 5.3].forEach((k, i) => tl.fromTo("#hi" + (i + 1), { opacity: 0 }, { opacity: 1, duration: 1, ease: "sine.inOut" }, K(k)));
[3.8, 4.2, 4.6].forEach((k, i) => rise("#st" + i, K(k), { y: 30, d: 1.4 }));

// 3 · PROBLEM: real comments, every answer written by a person (4 bars)
rise("#a0", K(6), { d: 1.2 }); rise("#a1 .w", K(6) + .3); rise("#a2 .w", K(6) + .6);
[6.3, 6.8, 7.3, 7.8].forEach((k, i) => rise("#cm" + i, K(k), { y: 40, d: 1.6 }));
rise("#afoot", K(6.8), { d: 1.2 });
out("#ag1", K(8.2) - .8);
rise("#a0b", K(8.2), { d: 1 }); rise("#a3 .w", K(8.2)); rise("#a4 .w", K(8.2) + .45, { d: 1.8 });

// 4 · PROBLEM: the same block pasted by hand, nobody takes orders meanwhile (4 bars)
rise("#p0", K(10), { d: 1.2 }); rise("#p1 .w", K(10) + .3); rise("#p2 .w", K(10) + .6, { d: 1.8 });
rise("#p3 .w", K(10.8), { st: .03 });
tl.fromTo("#paste", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(10) + .3);
rise("#copies", K(10.8), { y: 30, d: 1.4 });
count("nc", 1, 16, K(10.8) + .3, n => String(n), 2.4);
out("#pg1", K(12.3) - .8);
rise("#p0b", K(12.3), { d: 1 }); rise("#p4 .w", K(12.3)); rise("#p5 .w", K(12.3) + .45, { d: 1.8 });

// 5 · SOLUTION: bio link, pinned comment, five numbers become one WhatsApp (4 bars)
rise("#e0", K(14), { d: 1.2 }); rise("#e1 .w", K(14) + .3); rise("#e2 .w", K(14) + .6); rise("#e3 .w", K(14) + .9, { d: 1.8 });
tl.fromTo("#bio", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(14) + .3);
tl.fromTo("#lnk", { scale: 1 }, { scale: 1.06, duration: .5, yoyo: true, repeat: 1, ease: "sine.inOut" }, K(15));
tl.fromTo("#pin", { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 1.6, ease: SOFT }, K(15.3));
rise("#nums span", K(15.8), { y: 20, d: 1.2, st: .12 });
tl.to("#nums span", { opacity: 0, scale: .8, filter: "blur(8px)", duration: .9, stagger: .06, ease: "power2.in" }, K(16.9));
tl.fromTo("#one", { opacity: 0, scale: .85 }, { opacity: 1, scale: 1, duration: 1.4, ease: SOFT }, K(17.2));
rise("#edemo", K(14.6), { d: 1.2 });

// 6 · SOLUTION: the bot, the real L399 promo, nearest branch, that kitchen (7 bars)
tl.fromTo("#phw", { y: 700, rotationY: -16, rotationX: 6 }, { y: 0, rotationY: -6, rotationX: 2, duration: 2.4, ease: SOFT }, K(18));
tl.to("#phw", { rotationY: 4, rotationX: 0, duration: K(25) - K(19), ease: "sine.inOut" }, K(19));
rise("#bdemo", K(18.5), { d: 1.2 });
rise("#b10", K(18), { d: 1.2 }); rise("#b11 .w", K(18) + .3); rise("#b12 .w", K(18) + .6);
show("m1", K(18.5)); show("t1", K(19)); dots("t1", K(19) + .3); hide("t1", K(19.6)); show("m2", K(19.6));
out("#bg1", K(20.7) - .8);
rise("#b20", K(20.7), { d: 1.2 }); rise("#b21 .w", K(20.7) + .3); rise("#b22 .w", K(20.7) + .6);
show("m3", K(20.8)); show("t2", K(21.5)); dots("t2", K(21.5) + .3); hide("t2", K(22)); show("m4", K(22));
out("#bg2", K(23.1) - .8);
rise("#b30", K(23.1), { d: 1.2 }); rise("#b31 .w", K(23.1) + .3); rise("#b32 .w", K(23.1) + .6);
show("m5", K(22.9)); show("m6", K(23.7));

// 7 · SOLUTION: own delivery from the right branch (3 bars)
rise("#w0", K(25), { d: 1.2 }); rise("#w1 .w", K(25) + .3); rise("#w2 .w", K(25) + .6, { d: 1.8 });
rise("#w4 .w", K(25.9), { st: .03 });
tl.fromTo("#riders", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(25) + .3);
[25.5, 25.8, 26.1, 26.4].forEach((k, i) => rise("#rd" + i, K(k), { y: 20, d: 1.2 }));
rise("#wdemo", K(25.5), { d: 1.2 });

// 8 · PANEL 1: sales per branch and channel (4 bars)
rise("#q10", K(28), { d: 1.2 }); rise("#q11 .w", K(28) + .3); rise("#q12 .w", K(28) + .6, { d: 1.8 });
rise("#q13 .w", K(29), { st: .03 });
tl.fromTo("#pnl1", { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(28) + .2);
count("kv", 0, 53500, K(28.5), n => n.toLocaleString("en-US"), 2.4);
rise("#pnl1 .br", K(28.7), { y: 20, d: 1.2, st: .15 });
document.querySelectorAll("#pnl1 .br .bar i").forEach((el, i) => tl.fromTo(el, { scaleX: 0 }, { scaleX: +el.dataset.w, duration: 1.8, ease: FINE }, K(28.9) + i * .2));
rise("#pnl1 .ch", K(30.2), { y: 20, d: 1.2, st: .15 });
rise("#q1demo", K(28.5), { d: 1.2 });

// 9 · PANEL 2: every order live, nobody waiting (4 bars)
rise("#q20", K(32), { d: 1.2 }); rise("#q21 .w", K(32) + .3); rise("#q22 .w", K(32) + .6, { d: 1.8 });
rise("#q23 .w", K(33), { st: .03 });
tl.fromTo("#pnl2", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(32) + .2);
rise("#pnl2 .od", K(32.6), { y: 20, d: 1.2, st: .3 });
tl.fromTo("#pnl2 .zero", { opacity: 0, scale: .96 }, { opacity: 1, scale: 1, duration: 1.4, ease: SOFT }, K(34));
rise("#q2demo", K(32.5), { d: 1.2 });

// 10 · PANEL 3: what to do today (3 bars)
rise("#q30", K(36), { d: 1.2 }); rise("#q31 .w", K(36) + .3); rise("#q32 .w", K(36) + .6, { d: 1.8 });
tl.fromTo("#pnl3", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(36) + .2);
rise("#pnl3 .ac", K(36.5), { y: 24, d: 1.3, st: .45 });
rise("#q3demo", K(36.5), { d: 1.2 });

// 11 · WHY US (5 bars)
rise("#y0", K(39), { d: 1.2 }); rise("#y1 .w", K(39) + .3); rise("#y2 .w", K(39) + .6, { d: 1.8 });
[39.6, 40.3, 41, 41.7].forEach((k, i) => rise("#wl" + i, K(k), { y: 24, d: 1.4 }));
tl.fromTo("#result", { opacity: 0, y: 60, scale: .97 }, { opacity: 1, y: 0, scale: 1, duration: 1.8, ease: SOFT }, K(42.4));

// 12 · Casa Digital, call to action (4 bars)
rise("#u0", K(44), { d: 1.2 }); rise("#u1 .w", K(44) + .3); rise("#u2 .w", K(44) + .7, { d: 1.8 });
rise("#u3 .w", K(44.9), { st: .03 });
tl.fromTo("#cta", { opacity: 0, y: 90, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 2.2, ease: SOFT }, K(44.5));
float("#cta", K(45.4), K(48) - K(45.4));

'''

if __name__ == "__main__":
    print(build())
