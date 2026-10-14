#!/usr/bin/env python3
"""Coco Chicken pitch video (2026-10-14). Same look as gen3/gen5 (light 1920x1080, big headline
left with yellow highlighter, live UI right, Clientia Tech outro) on "Still Buggin" (194 BPM,
bar = 2.474 s; every scene starts on a bar line).
Story: they already have the attention (real TikTok + numbers) -> 3 branches, every day ->
today the order path ends in PedidosYa -> proposal: own ordering page, WhatsApp bot, their promo
in their own channel, owner panel -> why us -> outro.
Everything about Coco Chicken comes from their own TikTok, Facebook and PedidosYa (screenshots
from rodrigo in coco/src). Example conversations and panel numbers are labelled as examples."""
import json, os, shutil, sys
import gen3
from gen2 import MARK, words, rgba, lum, lift, hexrgb, ribbons, DEPS, HERE

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "coco-src")
OUT = os.path.join(HERE, "videos6")
P0, BAR = 0.0012, 8 * 0.3092783
K = lambda k: round(P0 + BAR * k, 3)
SCENES = [("intro", 0, 3), ("fame", 3, 8), ("local", 8, 11), ("path", 11, 16), ("calm", 16, 18),
          ("site", 18, 23), ("bot", 23, 28), ("promo", 28, 31), ("panel", 31, 34), ("why", 34, 37), ("end", 37, 41)]
TOTAL = K(41)
hl = gen3.hl

R = {"slug": "coco-chicken", "name": "Coco Chicken",
     "fonts": {"display": "Archivo Black", "displayFile": "archivo-black-latin-400-normal.woff2", "displayWeight": 400,
               "displayCase": "uppercase", "displayTracking": "-0.01em"},
     "colors": {"bg": "#FFF8E6", "ink": "#1A1210", "primary": "#D8261C", "accent": "#FFD21F"}}
RED, YEL, ORG = "#D8261C", "#FFD21F", "#F28C1B"

# real menu, exactly as on their PedidosYa (name, price)
MENU = [("Pierna y tajadas", "L75"), ("Cadera y tajadas", "L85"), ("Ala y tajadas", "L95"), ("Pierna, cadera y tajadas", "L140")]
BRANCHES = ["Barrio Cabañas", "Colonia Satélite", "Barrio Medina"]

CSS6 = r'''
.left.narrow{width:760px;}
.left.narrow .h1{font-size:96px;}
.stats{margin-top:56px;display:grid;grid-template-columns:repeat(2,330px);gap:34px 40px;}
.st b{display:block;font-size:84px;font-weight:600;letter-spacing:-.04em;line-height:1;font-variant-numeric:tabular-nums;color:$hero;}
.st span{display:block;margin-top:10px;font-size:26px;line-height:1.25;color:#6E6E73;font-weight:500;}
.vid{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
.tagv{position:absolute;left:1180px;top:1000px;font-size:22px;color:#86868B;font-weight:500;}
.photo{position:absolute;left:335px;top:300px;width:1250px;height:462px;border-radius:36px;overflow:hidden;box-shadow:0 50px 110px rgba(0,0,0,.18),0 0 0 1px rgba(0,0,0,.05);}
.photo img{display:block;width:1250px;height:462px;}
.top{position:absolute;left:0;right:0;top:110px;text-align:center;}
.top .h1{font-size:92px;}
.chips{position:absolute;left:0;right:0;top:812px;display:flex;justify-content:center;gap:22px;}
.chip{display:flex;align-items:center;gap:14px;background:#fff;border-radius:40px;padding:20px 32px;font-size:32px;font-weight:600;letter-spacing:-.01em;box-shadow:0 14px 40px rgba(0,0,0,.08),0 0 0 1px rgba(0,0,0,.04);}
.chip i{width:18px;height:18px;border-radius:50%;background:$hero;box-shadow:0 0 0 6px rgba(216,38,28,.16);}
.chip.hrs{background:#111113;color:#fff;}.chip.hrs i{background:#FFD60A;box-shadow:0 0 0 6px rgba(255,214,10,.2);}
.shotc{position:absolute;background:#fff;border-radius:30px;overflow:hidden;box-shadow:0 40px 100px rgba(0,0,0,.16),0 0 0 1px rgba(0,0,0,.05);}
.shotc img{display:block;}
.shotc .lbl{position:absolute;left:0;right:0;top:0;height:58px;background:#F2F2F4;display:flex;align-items:center;padding:0 24px;gap:10px;font-size:20px;font-weight:600;color:#6E6E73;}
.shotc .lbl i{width:13px;height:13px;border-radius:50%;background:#D1D1D6;}
.shotc .body{position:absolute;left:0;top:58px;}
.mk2{position:absolute;border:4px solid #FF3B30;border-radius:14px;box-shadow:0 0 0 8px rgba(255,59,48,.16),0 0 40px rgba(255,59,48,.3);}
.stepn{font-size:30px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:$hero;margin-bottom:18px;}
.cap2{position:absolute;left:150px;bottom:96px;width:1620px;display:flex;align-items:center;gap:26px;background:rgba(17,17,19,.92);color:#fff;font-weight:600;font-size:48px;line-height:1.15;letter-spacing:-.025em;padding:30px 44px;border-radius:34px;box-shadow:0 40px 90px rgba(0,0,0,.3);}
.cap2 i{flex:none;width:24px;height:24px;border-radius:50%;background:#FFD60A;box-shadow:0 0 0 10px rgba(255,214,10,.22);}
.pgrp{position:absolute;left:150px;top:96px;width:1620px;}
.pgrp .h1{font-size:84px;}
.kname{color:$hero;}
/* ordering site inside the phone */
.cs{position:absolute;inset:0;background:#FFF8E6;color:#1A1210;}
.cs-top{height:300px;background:radial-gradient(120% 90% at 30% 0%,#E8352A,#A8160E);padding:70px 28px 0;color:#fff;position:relative;}
.cs-logo{position:absolute;right:20px;top:58px;width:128px;height:128px;border-radius:50%;overflow:hidden;background:#000;box-shadow:0 0 0 4px #FFD21F;}
.cs-logo img{width:100%;height:100%;object-fit:cover;object-position:50% 30%;}
.cs-name{font-family:"Display";text-transform:uppercase;font-size:44px;line-height:.95;margin-top:18px;}
.cs-tag{margin-top:10px;font-size:20px;font-weight:600;color:#FFD21F;}
.cs-hrs{margin-top:12px;font-size:16px;opacity:.85;}
.cs-br{display:flex;gap:8px;padding:20px 18px 6px;flex-wrap:wrap;}
.cs-br span{font-size:15px;font-weight:600;padding:10px 14px;border-radius:20px;background:#fff;box-shadow:0 0 0 1.5px rgba(0,0,0,.08);}
.cs-br span.on{background:#1A1210;color:#fff;box-shadow:none;}
.cs-k{padding:14px 22px 2px;font-size:14px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#A8160E;}
.cs-it{margin:10px 18px 0;background:#fff;border-radius:20px;padding:16px 18px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 4px 14px rgba(0,0,0,.05);}
.cs-it b{display:block;font-size:19px;letter-spacing:-.01em;}
.cs-it span{display:block;font-size:13px;color:#8E8E93;margin-top:3px;}
.cs-it em{font-style:normal;font-size:20px;font-weight:700;}
.cs-add{width:36px;height:36px;border-radius:50%;background:#D8261C;color:#fff;font-size:26px;font-weight:600;display:flex;align-items:center;justify-content:center;margin-left:12px;}
.cs-cart{position:absolute;left:18px;right:18px;bottom:30px;height:74px;border-radius:40px;background:#D8261C;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 28px;font-size:20px;font-weight:700;box-shadow:0 14px 30px rgba(216,38,28,.35);}
.cs-cart small{font-size:14px;font-weight:600;opacity:.85;}
.props2{margin-top:44px;display:flex;flex-direction:column;gap:26px;}
.demo{position:absolute;right:120px;bottom:44px;font-size:20px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#A1A1A6;}
#chat3{left:1060px;top:110px;width:720px;height:860px;}
.rcard .rc-row{display:flex;justify-content:space-between;font-size:24px;color:#3A3A3C;margin-top:8px;}
/* stamp card */
.stamp{position:absolute;left:1060px;top:230px;width:720px;height:440px;border-radius:44px;background:radial-gradient(120% 120% at 20% 0%,#E8352A,#A8160E);color:#fff;padding:48px 52px;box-shadow:0 50px 110px rgba(168,22,14,.32);}
.stamp-k{font-size:22px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#FFD21F;}
.stamp-t{font-family:"Display";text-transform:uppercase;font-size:58px;line-height:1;margin-top:14px;}
.stamp-row{display:flex;gap:30px;margin-top:52px;}
.sp{position:relative;width:118px;height:118px;border-radius:50%;border:4px dashed rgba(255,255,255,.55);}
.sp b{position:absolute;inset:-4px;border-radius:50%;background:#FFD21F;color:#A8160E;display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:700;}
.sp.free b{background:#fff;font-size:26px;letter-spacing:.04em;}
.stamp-s{position:absolute;left:52px;bottom:40px;font-size:24px;opacity:.85;}
.list{position:absolute;left:1060px;top:720px;width:720px;background:#fff;border-radius:30px;padding:26px 34px;display:flex;align-items:center;gap:22px;box-shadow:0 30px 80px rgba(0,0,0,.12);}
.list i{flex:none;width:58px;height:58px;border-radius:18px;background:#25D366;color:#fff;font-style:normal;font-size:30px;font-weight:700;display:flex;align-items:center;justify-content:center;}
.list b{display:block;font-size:28px;letter-spacing:-.01em;}.list span{display:block;font-size:22px;color:#6E6E73;margin-top:4px;}
/* owner panel */
.panel{position:absolute;left:1000px;top:150px;width:820px;height:780px;background:#fff;border-radius:40px;box-shadow:0 40px 100px rgba(0,0,0,.14),0 0 0 1px rgba(0,0,0,.05);padding:44px 48px;}
.pn-k{font-size:22px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#86868B;}
.pn-t{font-size:46px;font-weight:600;letter-spacing:-.03em;margin-top:6px;}
.bars{margin-top:40px;display:flex;flex-direction:column;gap:30px;}
.bar b{display:flex;justify-content:space-between;font-size:28px;font-weight:600;margin-bottom:12px;}
.bar b em{font-style:normal;color:#6E6E73;font-weight:500;}
.trk{height:26px;border-radius:14px;background:#F2F2F4;overflow:hidden;}
.fill{height:100%;border-radius:14px;background:linear-gradient(90deg,#F28C1B,#D8261C);transform-origin:0 50%;}
.pn-row{margin-top:40px;display:flex;gap:20px;}
.pn-box{flex:1;background:#F7F7F9;border-radius:24px;padding:22px 26px;}
.pn-box span{display:block;font-size:20px;color:#86868B;font-weight:600;}
.pn-box b{display:block;font-size:30px;font-weight:600;margin-top:6px;letter-spacing:-.02em;}
.pn-alert{margin-top:24px;display:flex;align-items:center;gap:16px;background:#111113;color:#fff;border-radius:22px;padding:20px 26px;font-size:24px;font-weight:500;}
.pn-alert i{width:14px;height:14px;border-radius:50%;background:#30D158;box-shadow:0 0 0 6px rgba(48,209,88,.22);}
#why .ctacard{left:1180px;}
.quote{position:absolute;left:1130px;top:600px;width:620px;}
.quote span{display:block;font-size:24px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#86868B;}
.quote b{display:block;margin-top:12px;font-size:54px;font-weight:600;letter-spacing:-.03em;line-height:1.1;}
'''


def build():
    c = R["colors"]; f = R["fonts"]
    hero = RED
    acc = lift(c["accent"], 0.5); pri = lift(c["primary"], 0.38)
    proj = os.path.join(OUT, R["slug"])
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    A = lambda *p: os.path.join(proj, "assets", *p)
    shutil.copy(os.path.join(HERE, "musica2.mp3"), A("musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), A("gsap.min.js"))
    shutil.copy(os.path.join(DEPS, "@fontsource", "archivo-black", "files", f["displayFile"]), A("fonts", "display.woff2"))
    for w in (300, 400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"), A("fonts", f"it-{w}.woff2"))
    for n in ("tiktok.mp4", "local.jpg", "logo.png", "tk-perfil.png", "py-menu.png", "tk-videos.png"):
        shutil.copy(os.path.join(SRC, n), A(n))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "coco-chicken", "name": "Casa Digital x Coco Chicken"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    vid = (f'<video id="tkvid" class="vid" src="assets/tiktok.mp4" data-start="{K(3)}" data-duration="{round(K(8) - K(3), 3)}" '
           f'data-media-start="0" data-track-index="2" muted playsinline></video>')
    stats = [("204.9K", "seguidores en TikTok"), ("3.1M", "me gusta en TikTok"), ("127K", "seguidores en Facebook"),
             ("871.5K", "vistas: «¿Pollos a 15 lempiras?»")]
    stats_html = "".join(f'<div class="st" id="st{i}"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(stats))
    chips = "".join(f'<div class="chip" id="cp{i}"><i></i>{b}</div>' for i, b in enumerate(BRANCHES))
    chips += '<div class="chip hrs" id="cp3"><i></i>Lunes a domingo · 9 am a 10 pm</div>'

    def shotc(sid, img, w, h, lbl, x, y, marks):
        mk = "".join(f'<div class="mk2" id="{sid}-mk{i}" style="left:{a}px;top:{b}px;width:{cw}px;height:{ch}px"></div>'
                     for i, (a, b, cw, ch) in enumerate(marks))
        return (f'<div class="shotc" id="{sid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h + 58}px">'
                f'<div class="lbl"><i></i><i></i><i></i>&nbsp;&nbsp;{lbl}</div>'
                f'<div class="body"><img src="assets/{img}" style="width:{w}px;height:{h}px">{mk}</div></div>')

    # tk-perfil.png is 620x230 (crop of their TikTok profile); bio "Pagas 3 El 4 Es Gratis / En Pedidos Ya"
    tk = shotc("shtk", "tk-perfil.png", 620, 230, "tiktok.com/@cocochiken1", 1130, 230, [(200, 140, 196, 50)])
    # py-menu.png is 1410x840 shown at 0.62 (874x521): header and the best-sellers
    s = 0.62
    py = shotc("shpy", "py-menu.png", round(1410 * s), round(840 * s), "PedidosYa · Coco Chicken", 940, 170,
               [(round(130 * s), round(10 * s), round(170 * s), round(80 * s)), (round(4 * s), round(325 * s), round(1395 * s), round(300 * s))])

    site = (f'<div class="cs"><div class="cs-top"><div class="cs-logo"><img src="assets/logo.png"></div>'
            f'<div style="font-size:15px;font-weight:600;opacity:.85">cocochicken.hn</div>'
            f'<div class="cs-name">Coco<br>Chicken</div><div class="cs-tag">¡Qué sabroso!</div>'
            f'<div class="cs-hrs">Lunes a domingo · 9:00 am a 10:00 pm</div></div>'
            f'<div class="cs-br">' + "".join(f'<span class="{"on" if i == 1 else ""}" id="csb{i}">{b}</span>' for i, b in enumerate(BRANCHES)) + '</div>'
            f'<div class="cs-k">Pollo con tajadas</div>'
            + "".join(f'<div class="cs-it" id="csi{i}"><div><b>{n}</b><span>Repollo, chimol, aderezos y caldo</span></div>'
                      f'<div style="display:flex;align-items:center"><em>{p}</em><div class="cs-add">+</div></div></div>' for i, (n, p) in enumerate(MENU[:3]))
            + '<div class="cs-cart" id="cscart"><span>Ver pedido · 2<br><small>Sucursal Colonia Satélite</small></span><span>L170</span></div></div>'
            '<div class="notif" id="notif"><div class="n-ic">' + gen3.HOUSE + '</div><div><b>Coco Chicken · Satélite</b>'
            '<span>Nuevo pedido pagado ✓ L170</span></div><i>ahora</i></div>')
    props = [("El link en la bio de TikTok", "Del video al pedido en tres toques."),
             ("Eligen sucursal, pagan y listo", "Con tarjeta o al recibir. Sin comisión por pedido."),
             ("Su menú, sus precios", "Lo cambian ustedes desde el celular.")]
    props_html = "".join(f'<div class="pr" id="pr{i}"><i>{i + 1}</i><div><b>{a}</b><span>{b}</span></div></div>' for i, (a, b) in enumerate(props))
    whys = ["Hecho a la medida de Coco Chicken.", "PedidosYa sigue, como un canal más.", "Las 3 sucursales en Google Maps.", "Listo en 14 días."]
    whys_html = "".join(f'<div class="wy" id="wy{i}"><i>✓</i><span>{words(t)}</span></div>' for i, t in enumerate(whys))
    bars = [("Colonia Satélite", 46), ("Barrio Cabañas", 38), ("Barrio Medina", 31)]
    bars_html = "".join(f'<div class="bar" id="bar{i}"><b>{n}<em><span class="cnt" data-n="{v}">0</span> pedidos</em></b>'
                        f'<div class="trk"><div class="fill" style="width:{round(v / 50 * 100)}%"></div></div></div>' for i, (n, v) in enumerate(bars))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          <div class="wash w1"></div><div class="wash w2"></div>
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("una propuesta para")}</div>
            <div class="disp intro-name" id="iname">Coco Chicken</div>
          </div>'''),
        scene("fame", f'''
          <div class="wash w3"></div>
          <div class="tagv" id="tagv">Su video fijado en TikTok</div>
          <div class="left narrow">
            <div class="h1" id="f1">{words("Ya tienen")}</div>
            <div class="h1" id="f2">{words("lo más difícil:")}</div>
            <div class="h1" id="f3">{hl("la atención.")}</div>
            <div class="stats">{stats_html}</div>
          </div>'''),
        scene("local", f'''
          <div class="wash w6"></div>
          <div class="top"><div class="h1" id="l1">{words("Tres sucursales.")} {hl("Todos los días.")}</div></div>
          <div class="photo" id="photo"><img src="assets/local.jpg"></div>
          <div class="chips">{chips}</div>'''),
        scene("path", f'''
          <div class="wash w4"></div>
          {tk}{py}
          <div class="quote" id="qtk"><span>Su bio en TikTok</span><b>“Pagas 3 El 4 Es Gratis<br>En Pedidos Ya”</b></div>
          <div class="quote" id="qpy" style="top:800px;left:940px;width:874px"><span>En PedidosYa</span><b>★ 4.4 · 1,097 opiniones</b></div>
          <div class="left narrow">
            <div class="grp" id="pg1"><div class="stepn" id="pa0">Hoy, para pedir</div><div class="h1" id="pa1">{words("El video")}</div><div class="h1" id="pa2">{words("lleva a")}</div><div class="h1" id="pa3">{hl("PedidosYa.")}</div></div>
            <div class="grp" id="pg2"><div class="h1" id="pa4">{words("Su menú,")}</div><div class="h1" id="pa5">{words("su promo,")}</div><div class="h1" id="pa6">{words("en la app")}</div><div class="h1" id="pa7">{hl("de otro.")}</div></div>
          </div>'''),
        scene("calm", f'''
          <div class="wash w6"></div>
          <div class="center">
            <div class="h1" id="k1">{words("Ustedes ponen el pollo y la fama.")}</div>
            <div class="h1" id="k2">{words("La app cobra")} <span class="kname">{words("cada pedido.")}</span></div>
          </div>'''),
        scene("site", f'''
          <div class="wash w8"></div>
          <div class="ph-stage">{gen3.phone(site, "ph1")}</div>
          <div class="left">
            <div class="eyebrow2" id="y0">La propuesta · 1</div>
            <div class="h1" id="y1">{words("Su propia")}</div>
            <div class="h1" id="y2">{hl("página de pedidos.")}</div>
            <div class="props2">{props_html}</div>
          </div>
          <div class="demo" id="sdemo">Diseño de muestra</div>'''),
        scene("bot", f'''
          <div class="wash w5"></div>
          <div class="chat" id="chat3">
            <div class="ch-head"><div class="ch-av" style="background:{RED}">C</div><div><b>Coco Chicken</b><span>WhatsApp · responde al instante</span></div></div>
            <div class="ch-body">
              <div class="bub out" id="b1">Buenas, quiero 2 cadera y tajadas</div>
              <div class="bub in" id="b2">¡Con gusto! ¿Para recoger o a domicilio?</div>
              <div class="bub out" id="b3">A domicilio, en la Satélite</div>
              <div class="rcard" id="b4"><div class="rc-k">Pedido listo · Sucursal Satélite</div>
                <div class="rc-row"><span>2 × Cadera y tajadas</span><span>L170</span></div>
                <div class="rc-s">Pagar con tarjeta o al recibir</div></div>
            </div>
          </div>
          <div class="left narrow">
            <div class="eyebrow2" id="t0">La propuesta · 2</div>
            <div class="h1" id="t1">{words("Un WhatsApp")}</div>
            <div class="h1" id="t2">{words("que toma")}</div>
            <div class="h1" id="t3">{hl("el pedido.")}</div>
            <div class="h2 gray" id="t4">{words("A cualquier hora, y lo manda a la cocina de la sucursal.")}</div>
          </div>
          <div class="demo" id="bdemo">Conversación de ejemplo</div>'''),
        scene("promo", f'''
          <div class="wash w8"></div>
          <div class="stamp" id="stamp"><div class="stamp-k">Tarjeta Coco Chicken</div><div class="stamp-t">Pagas 3,<br>el 4 es gratis</div>
            <div class="stamp-row">{"".join(f'<div class="sp{" free" if i == 3 else ""}"><b id="sb{i}">{"GRATIS" if i == 3 else "✓"}</b></div>' for i in range(4))}</div></div>
          <div class="list" id="list"><i>✓</i><div><b>Cada cliente queda en su lista</b><span>Para avisarle de la próxima promo por WhatsApp.</span></div></div>
          <div class="left narrow">
            <div class="eyebrow2" id="m0">La propuesta · 3</div>
            <div class="h1" id="m1">{words("Su promo,")}</div>
            <div class="h1" id="m2">{words("en su")}</div>
            <div class="h1" id="m3">{hl("propio canal.")}</div>
          </div>'''),
        scene("panel", f'''
          <div class="wash w4"></div>
          <div class="panel" id="pnl">
            <div class="pn-k">Panel del dueño · hoy</div><div class="pn-t">Pedidos por sucursal</div>
            <div class="bars">{bars_html}</div>
            <div class="pn-row"><div class="pn-box"><span>Más vendido</span><b>Cadera y tajadas</b></div><div class="pn-box"><span>Clientes nuevos</span><b>+24</b></div></div>
            <div class="pn-alert" id="pnal"><i></i>Pedido nuevo en Barrio Medina · L140</div>
          </div>
          <div class="left narrow">
            <div class="eyebrow2" id="n0">La propuesta · 4</div>
            <div class="h1" id="n1">{words("Las tres")}</div>
            <div class="h1" id="n2">{words("sucursales,")}</div>
            <div class="h1" id="n3">{hl("en un panel.")}</div>
          </div>
          <div class="demo" id="ndemo">Datos de ejemplo</div>'''),
        scene("why", f'''
          <div class="wash w8"></div>
          <div class="left">
            <div class="h1" id="w1">{words("Por qué")} {hl("nosotros.")}</div>
            <div class="whys">{whys_html}</div>
          </div>
          <div class="ctacard" id="cta">
            <div class="cta-ic">{gen3.HOUSE}</div>
            <div class="cta-t">Casa Digital</div>
            <div class="cta-s">Se lo mostramos en 15 minutos.</div>
            <div class="cta-wa"><span>WhatsApp</span>{gen3.WHATSAPP}</div>
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
        f'<div class="ph-stage" id="fstage" style="opacity:0">{gen3.phone(vid, "phv", dark=True)}</div>',
    ])

    css = (gen3.CSS.replace("$heroB", "rgb(%d,%d,%d)" % tuple(int(v * .22) for v in hexrgb(hero))).replace("$hero", hero).replace("$acc", acc).replace("$pri", pri)
           .replace("$washA", rgba(hero, .12)).replace("$washB", rgba(ORG, .18)).replace("$sitebg", c["bg"]).replace("$siteink", c["ink"])
           .replace("$dweight", str(f["displayWeight"])).replace("$dcase", f["displayCase"]).replace("$dtrack", f["displayTracking"])
           .replace("$italface", "").replace("$ital", '"Display"').replace("$introsizepx", "150px"))
    css += GEN5_CSS + CSS6.replace("$hero", hero)
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    js = JS.replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = (gen3.HTML.replace("$title", "Casa Digital x Coco Chicken").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)).replace('data-fade-out="2.5"', 'data-fade-out="4"'))
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


# the bits of gen4/gen5 CSS this video uses (props, whys, eyebrow, narrow column)
GEN5_CSS = r'''
.props{margin-top:46px;display:flex;flex-direction:column;gap:30px;}
.pr{display:flex;gap:26px;align-items:flex-start;}
.pr i{flex:none;width:64px;height:64px;border-radius:20px;background:#111113;color:#FFD60A;font-style:normal;font-size:30px;font-weight:700;display:flex;align-items:center;justify-content:center;}
.pr b{display:block;font-size:44px;font-weight:600;letter-spacing:-.025em;line-height:1.1;}
.pr span{display:block;font-size:30px;color:#6E6E73;margin-top:6px;}
#site .left{width:900px;}
#site .h1{font-size:100px;}
.eyebrow2{font-size:34px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#86868B;margin-bottom:16px;}
.whys{margin-top:40px;display:flex;flex-direction:column;gap:22px;}
.wy{display:flex;gap:22px;align-items:center;font-size:40px;font-weight:500;letter-spacing:-.02em;}
.wy i{flex:none;width:52px;height:52px;border-radius:50%;background:#111113;color:#FFD60A;font-style:normal;font-size:28px;font-weight:700;display:flex;align-items:center;justify-content:center;}
.tk{font-style:normal;font-size:22px;color:#8696A0;margin-left:10px;}
'''

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
function swipe(sel, t) { tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: 1, ease: "power3.inOut" }, t); }
function float(sel, t, d) { tl.fromTo(sel, { y: 0 }, { y: -20, duration: d, ease: "sine.inOut" }, t); }
function box(sel, t) { tl.fromTo(sel, { opacity: 0, scale: 1.08 }, { opacity: 1, scale: 1, duration: .8, ease: "power3.out" }, t); }
$scenes.forEach(([id, s, e]) => tl.fromTo("#cam-" + id, { scale: 1.0 }, { scale: 1.02, duration: e - s, ease: "none" }, s));

// 1 · intro
tl.fromTo(".w1", { x: -200, opacity: 0 }, { x: 100, opacity: 1, duration: K(3), ease: "sine.inOut" }, 0);
tl.fromTo(".w2", { x: 200, opacity: 0 }, { x: -100, opacity: 1, duration: K(3), ease: "sine.inOut" }, 0);
rise("#icd", 0.4, { d: 2 });
rise("#ipres .w", K(1), { d: 1.6, st: .14 });
tl.fromTo("#iname", { opacity: 0, scale: 1.06, filter: "blur(24px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.6, ease: SOFT }, K(1.5));

// 2 · they already have the attention: their real TikTok + numbers
rise("#f1 .w", K(3)); rise("#f2 .w", K(3) + .4); rise("#f3 .w", K(3) + .8);
swipe("#f3 .hlbg", K(4) - .3);
tl.set("#fstage", { opacity: 1 }, K(3)); tl.set("#fstage", { opacity: 0 }, K(8));
tl.fromTo("#phv", { y: 700, rotationY: -18, rotationX: 8 }, { y: 0, rotationY: -8, rotationX: 2, duration: 2.6, ease: SOFT }, K(3));
tl.to("#phv", { rotationY: 6, rotationX: 0, duration: K(8) - K(4), ease: "sine.inOut" }, K(4));
rise("#tagv", K(4), { d: 1.4 });
[4.5, 5.2, 5.9, 6.6].forEach((k, i) => rise("#st" + i, K(k), { y: 30, d: 1.4 }));

// 3 · three branches, every day (their storefront photo)
rise("#l1 .w", K(8));
swipe("#l1 .hlbg", K(8.6));
tl.fromTo("#photo", { opacity: 0, y: 80, scale: .96, filter: "blur(14px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(8) + .3);
tl.fromTo("#photo img", { scale: 1.06 }, { scale: 1, duration: K(11) - K(8), ease: "none" }, K(8));
[9, 9.35, 9.7, 10.1].forEach((k, i) => rise("#cp" + i, K(k), { y: 24, d: 1.2 }));

// 4 · today the order path ends in PedidosYa
rise("#pa0", K(11), { d: 1.2 }); rise("#pa1 .w", K(11) + .2); rise("#pa2 .w", K(11) + .5); rise("#pa3 .w", K(11) + .8);
swipe("#pa3 .hlbg", K(11.6));
tl.fromTo("#shtk", { opacity: 0, y: 70, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(11.3));
box("#shtk-mk0", K(12.3));
rise("#qtk", K(12.6), { d: 1.4 });
out("#qtk", K(13.4) - 1);
tl.to("#shtk", { opacity: 0, y: -40, filter: "blur(14px)", duration: .9, ease: "power2.in" }, K(13.4) - 1);
tl.fromTo("#shpy", { opacity: 0, y: 70, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(13.4) - .2);
box("#shpy-mk0", K(14)); box("#shpy-mk1", K(14.5));
rise("#qpy", K(14.2), { d: 1.4 });
out("#pg1", K(14) - .9);
rise("#pa4 .w", K(14)); rise("#pa5 .w", K(14) + .4); rise("#pa6 .w", K(14) + .8); rise("#pa7 .w", K(14) + 1.2);
swipe("#pa7 .hlbg", K(14.8));

// 5 · break
rise("#k1 .w", K(16), { d: 2, st: .12 });
rise("#k2 .w", K(16.8), { d: 2, st: .14 });

// 6 · proposal 1: their own ordering page
rise("#y0", K(18), { d: 1.2 }); rise("#y1 .w", K(18) + .3); rise("#y2 .w", K(18) + .7);
swipe("#y2 .hlbg", K(18.6));
[19.3, 20.3, 21.3].forEach((k, i) => rise("#pr" + i, K(k), { y: 30, d: 1.4 }));
tl.fromTo("#ph1", { y: 700, rotationY: -20, rotationX: 8 }, { y: 0, rotationY: -10, rotationX: 3, duration: 2.4, ease: SOFT }, K(18));
tl.to("#ph1", { rotationY: 4, rotationX: 0, duration: K(23) - K(19), ease: "sine.inOut" }, K(19));
[19.2, 19.5, 19.8].forEach((k, i) => rise("#csi" + i, K(k), { y: 20, blur: 4, d: 1 }));
tl.fromTo("#cscart", { y: 140 }, { y: 0, duration: 1, ease: "back.out(1.2)" }, K(20.6));
tl.fromTo("#notif", { y: -160, opacity: 0 }, { y: 0, opacity: 1, duration: 1, ease: "back.out(1.3)" }, K(21.6));
tl.to("#notif", { y: -160, opacity: 0, duration: .8, ease: "power2.in" }, K(22.6));
rise("#sdemo", K(19), { d: 1.2 });

// 7 · proposal 2: WhatsApp bot takes the order
rise("#t0", K(23), { d: 1.2 }); rise("#t1 .w", K(23) + .3); rise("#t2 .w", K(23) + .6); rise("#t3 .w", K(23) + .9);
swipe("#t3 .hlbg", K(23.7));
rise("#t4 .w", K(24.5), { st: .04 });
tl.fromTo("#chat3", { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 1.8, ease: SOFT }, K(23));
[23.8, 24.8, 25.8, 26.6].forEach((k, i) => rise("#b" + (i + 1), K(k), { y: 24, blur: 4, d: 1.1 }));
rise("#bdemo", K(24), { d: 1.2 });

// 8 · proposal 3: their promo in their own channel
rise("#m0", K(28), { d: 1.2 }); rise("#m1 .w", K(28) + .3); rise("#m2 .w", K(28) + .6); rise("#m3 .w", K(28) + .9);
swipe("#m3 .hlbg", K(28.7));
tl.fromTo("#stamp", { opacity: 0, y: 90, rotation: -3 }, { opacity: 1, y: 0, rotation: 0, duration: 2, ease: SOFT }, K(28));
[29, 29.25, 29.5, 29.85].forEach((k, i) => tl.fromTo("#sb" + i, { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: .6, ease: "back.out(2)" }, K(k)));
rise("#list", K(30.1), { y: 30, d: 1.4 });

// 9 · proposal 4: owner panel for the three branches
rise("#n0", K(31), { d: 1.2 }); rise("#n1 .w", K(31) + .3); rise("#n2 .w", K(31) + .6); rise("#n3 .w", K(31) + .9);
swipe("#n3 .hlbg", K(31.7));
tl.fromTo("#pnl", { opacity: 0, x: 100 }, { opacity: 1, x: 0, duration: 1.8, ease: SOFT }, K(31));
document.querySelectorAll("#pnl .fill").forEach((el, i) => tl.fromTo(el, { scaleX: 0 }, { scaleX: 1, duration: 1.6, ease: FINE }, K(31.6) + i * .3));
document.querySelectorAll("#pnl .cnt").forEach((el, i) => {
  const o = { v: 0 }, n = +el.dataset.n;
  tl.fromTo(o, { v: 0 }, { v: n, duration: 1.6, ease: FINE, onUpdate: () => { el.textContent = Math.round(o.v); } }, K(31.6) + i * .3);
});
rise("#pnal", K(32.8), { y: 20, d: 1.2 });
rise("#ndemo", K(31.5), { d: 1.2 });

// 10 · why us + call to action
rise("#w1 .w", K(34));
swipe("#w1 .hlbg", K(34.4));
[34.6, 35.1, 35.6, 36.1].forEach((k, i) => rise("#wy" + i + " .w, #wy" + i + " i", K(k), { st: .04, d: 1.2 }));
tl.fromTo("#cta", { opacity: 0, y: 100, scale: .94 }, { opacity: 1, y: 0, scale: 1, duration: 2, ease: SOFT }, K(34.5));
float("#cta", K(35.3), K(37) - K(35.3));

// 11 · outro: trails converge, mark draws, fills on the bar
function trails(rid, t0, dur, spin) {
  for (let i = 0; i < 6; i++) {
    const st = t0 + i * 0.22, len = 480 + (i % 3) * 170;
    tl.fromTo("." + rid + "-p" + i, { strokeDasharray: len + " 2000", strokeDashoffset: len }, { strokeDashoffset: -1000, duration: dur - i * 0.15, ease: "power2.inOut" }, st);
  }
  tl.fromTo("#" + rid, { rotation: spin[0], scale: spin[2], opacity: 0 }, { rotation: spin[1], scale: spin[3], opacity: 1, duration: dur, ease: "power1.inOut" }, t0);
}
const strokes = document.querySelectorAll("#mstroke path");
strokes.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
trails("re", K(37) - 0.3, 3, [20, -8, 1.6, 0.9]);
tl.to("#re", { scale: 3.2, opacity: 0, duration: 1.3, ease: "expo.out" }, K(38));
tl.to("#mstroke path", { strokeDashoffset: 0, duration: 2.3, ease: FINE }, K(37) + .1);
tl.fromTo("#mfill", { opacity: 0 }, { opacity: 1, duration: .6, ease: "power2.out" }, K(38));
tl.to("#mstroke", { opacity: 0, duration: .6 }, K(38));
tl.fromTo("#mwrap", { scale: .92 }, { scale: 1, duration: 2.6, ease: SOFT }, K(37));
tl.fromTo("#mwrap", { filter: "drop-shadow(0 0 0px rgba(140,170,255,0))" }, { filter: "drop-shadow(0 0 60px rgba(140,170,255,.65))", duration: .4, ease: "power2.out", yoyo: true, repeat: 1 }, K(38));
tl.fromTo("#eglow", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: 2, ease: SOFT }, K(38));
tl.fromTo("#msweep", { x: -200 }, { x: 900, duration: 1.8, ease: FINE }, K(38.5));
rise("#lby", K(38.5), { d: 1.6 });
rise(".lt", K(38.5) + .3, { d: 1.6, st: .04, y: 36, blur: 12 });
tl.to("#end .center, #eglow", { opacity: 0, duration: 2, ease: "power2.in" }, K(40.1));

window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
tl.seek(0);
'''

if __name__ == "__main__":
    print(build())
