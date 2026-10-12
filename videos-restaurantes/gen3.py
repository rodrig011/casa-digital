#!/usr/bin/env python3
"""Casa Digital pitch videos v3: landscape product-launch look (light UI, big headline left,
live interface right), keeping the v2 Clientia Tech outro. Cuts land on downbeats of the track
(120 BPM, bar = 2 s, offset 0.017 s)."""
import json, os, shutil, sys
from gen2 import MARK, words, rgba, lum, lift, hexrgb, ribbons, DEPS, HERE

OUT = os.path.join(HERE, "videos3")
WHATSAPP = "+1 (765) 543-4251"
B = 0.017
TOTAL = 64.0
W, H = 1920, 1080
SCENES = [("intro", 0, 8), ("reviews", 8, 16), ("search", 16, 22), ("site", 22, 30), ("chat", 30, 36),
          ("calm", 36, 40), ("pay", 40, 48), ("offer", 48, 56), ("end", 56, 64)]
HOUSE = ('<svg class="house" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="5" stroke-linejoin="round" '
         'stroke-linecap="round"><path d="M9 29 L32 10 L55 29 V54 H9 Z"/><path d="M26 54 V40 H38 V54"/></svg>')


def hl(text):
    """A word or phrase with a yellow highlighter swipe behind it."""
    return f'<span class="hl"><span class="hlbg"></span>{words(text)}</span>'


def review_wall():
    cols = []
    for ci in range(3):
        cards = []
        for k in range(7):
            n = (ci * 7 + k)
            letter = "ABCDEFGHJKLMNPRSTVWY"[n % 20]
            hue = ["#FF9F0A", "#30D158", "#0A84FF", "#BF5AF2", "#FF375F", "#64D2FF"][n % 6]
            l1 = 70 + (n * 37) % 25
            l2 = 45 + (n * 53) % 40
            cards.append(f'<div class="rv"><div class="rv-top"><div class="av" style="background:{hue}">{letter}</div>'
                         f'<div class="rv-stars">★★★★★</div></div><div class="sk" style="width:{l1}%"></div>'
                         f'<div class="sk" style="width:{l2}%"></div><div class="rv-g">Reseña de Google</div></div>')
        cols.append(f'<div class="rcol" id="rcol{ci}">{"".join(cards)}</div>')
    return f'<div class="wall"><div class="wall-in">{"".join(cols)}</div></div>'


def phone(inner, pid, dark=False):
    return (f'<div class="iph{" dark" if dark else ""}" id="{pid}"><div class="iph-scr"><div class="island"></div>{inner}</div></div>')


def build(r):
    c = r["colors"]; f = r["fonts"]
    hero = c["primary"] if lum(c["primary"]) < 0.45 else c["accent"]
    acc = lift(c["accent"], 0.5)
    pri = lift(c["primary"], 0.38)
    reviews_n = int(r["reviews"].replace(",", ""))
    proj = os.path.join(OUT, r["slug"])
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    shutil.copy(os.path.join(HERE, "musica.mp3"), os.path.join(proj, "assets", "musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), os.path.join(proj, "assets", "gsap.min.js"))
    fam = f["display"].lower().replace(" ", "-")
    shutil.copy(os.path.join(DEPS, "@fontsource", fam, "files", f["displayFile"]), os.path.join(proj, "assets", "fonts", "display.woff2"))
    if f.get("italicFile"):
        shutil.copy(os.path.join(DEPS, "@fontsource", fam, "files", f["italicFile"]), os.path.join(proj, "assets", "fonts", "display-italic.woff2"))
    for w in (300, 400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"),
                    os.path.join(proj, "assets", "fonts", f"it-{w}.woff2"))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": r["slug"], "name": f"Casa Digital x {r['name']}"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        start = 0 if s == 0 else round(s + B, 3)
        end = TOTAL if e == 64 else round(e + B, 3)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{start}" data-duration="{round(end - start, 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    site_html = (f'<div class="ph-scroll" id="phs"><div class="site"><div class="site-nav"><b>{r["name"]}</b><span>Menú&nbsp;&nbsp;Reservas</span></div>'
                 f'<div class="site-name">{"<br>".join(r["nameLines"])}</div><div class="site-tag">{r["tagline"]}</div>'
                 f'<div class="site-btns"><span class="b1">Pedir ahora</span><span class="b2">Reservar</span></div></div>'
                 f'<div class="menu"><div class="menu-h">Menú</div>'
                 + "".join(f'<div class="dish"><span>{d}</span><em>Ver</em></div>' for d in r["dishes"]) +
                 '<div class="today">Hoy · especial del día</div></div></div>'
                 '<div class="notif" id="notif"><div class="n-ic">' + HOUSE + '</div><div><b>Casa Digital</b>'
                 '<span>Nuevo pedido pagado con tarjeta ✓</span></div><i>ahora</i></div>')
    orders = [("Mesa 4", "En la mesa"), ("Para recoger", "Listo 7:30 pm"), ("A domicilio", "En camino")]
    orders_html = ('<div class="ord"><div class="ord-h">Pedidos de hoy</div>' +
                   "".join(f'<div class="orow" id="or{i}"><div><b>{a}</b><span>{b}</span></div><em>Pagado</em></div>' for i, (a, b) in enumerate(orders)) +
                   '</div>')
    found = "".join(f'<div class="res" id="res{i}"><div class="res-u">{u}</div><div class="res-t">{r["name"]} · {r["city"]}</div><div class="sk2"></div></div>'
                    for i, u in enumerate(r["found"]))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          <div class="wash w1"></div><div class="wash w2"></div>
          <div class="center">
            <div class="cd" id="icd">{HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("presenta una idea para")}</div>
            <div class="disp intro-name" id="iname">{r["name"]}</div>
          </div>'''),
        scene("reviews", f'''
          <div class="wash w3"></div>
          {review_wall()}
          <div class="left">
            <div class="grp" id="rg1">
              <div class="h1" id="r1">{words("Más de")}</div>
              <div class="h1 num" id="rnum">0</div>
              <div class="h1" id="r2">{words("reseñas en Google.")}</div>
            </div>
            <div class="grp" id="rg2">
              <div class="h1" id="r3">{words("La gente")}</div>
              <div class="h1" id="r4">{words("ya te")} {hl("ama.")}</div>
            </div>
          </div>'''),
        scene("search", f'''
          <div class="browser" id="brw">
            <div class="br-bar"><i></i><i></i><i></i><div class="br-url">google.com</div></div>
            <div class="br-body">
              <div class="gsearch"><span class="g-ic">⌕</span><span class="g-q" id="gq">{r["name"]} {r["city"]}</span></div>
              {found}
              <div class="nochip" id="nochip">Sin sitio oficial</div>
            </div>
          </div>
          <div class="left">
            <div class="h1" id="s1">{words("Te buscan en Google")}</div>
            <div class="h1" id="s2">{words("y encuentran")}</div>
            <div class="h1" id="s3">{hl("directorios.")}</div>
            <div class="h2 gray" id="s4">{words("No tu página.")}</div>
          </div>'''),
        scene("site", f'''
          <div class="wash w4"></div>
          <div class="ph-stage">{phone(site_html, "ph1")}</div>
          <div class="left">
            <div class="grp" id="sg1">
              <div class="eyebrow" id="t0">Presentamos</div>
              <div class="h1" id="t1">{words("tu")} {hl("casa digital.")}</div>
            </div>
            <div class="grp" id="sg2">
              <div class="h1" id="t2">{words("Un menú que")}</div>
              <div class="h1" id="t3">{words("cambias desde")}</div>
              <div class="h1" id="t4">{words("tu celular.")}</div>
            </div>
          </div>'''),
        scene("chat", f'''
          <div class="wash w5"></div>
          <div class="chat" id="chat">
            <div class="ch-head"><div class="ch-av" style="background:{hero}">{r["name"][0]}</div><div><b>{r["name"]}</b><span>en línea</span></div></div>
            <div class="ch-body">
              <div class="bub in" id="b1">Hola, ¿tienen mesa para 4 el sábado a las 8?</div>
              <div class="slot"><div class="typing" id="b2"><i></i><i></i><i></i></div><div class="bub out" id="b3">¡Claro! Su mesa quedó reservada ✓</div></div>
              <div class="rcard" id="b4"><div class="rc-k">Reserva confirmada</div><div class="rc-b">Sábado · 8:00 pm</div><div class="rc-s">Mesa para 4 · {r["name"]}</div></div>
            </div>
          </div>
          <div class="left">
            <div class="h1" id="c1">{words("Reservas por")}</div>
            <div class="h1" id="c2">{hl("WhatsApp.")}</div>
            <div class="h2 gray" id="c3">{words("Sin llamadas perdidas.")}</div>
          </div>'''),
        scene("calm", f'''
          <div class="wash w6"></div>
          <div class="center">
            <div class="h1" id="k1">{words("Hecha a mano.")}</div>
            <div class="h1" id="k2">{words("Solo para")} <span class="disp kname">{r["name"]}.</span></div>
          </div>'''),
        scene("pay", f'''
          <div class="navy"></div><div class="wash w7"></div>
          <div class="ph-stage two">{phone(orders_html, "ph2", True)}{phone('<div class="paysheet"><div class="ps-h">Pagar pedido</div><div class="ps-card">VISA •••• 4821</div><div class="ps-btn" id="psb"><span id="psb1">Pagar con tarjeta</span><span id="psb2">✓ Pago confirmado</span></div></div>', "ph3", True)}</div>
          <div class="left">
            <div class="h1 white" id="p1">{hl("0% de comisión.")}</div>
            <div class="h2 soft" id="p2">{words("Cobras con tarjeta,")}</div>
            <div class="h2 soft" id="p3">{words("directo a tu cuenta.")}</div>
          </div>''', "darkscene"),
        scene("offer", f'''
          <div class="wash w8"></div>
          <div class="left">
            <div class="h1" id="o1">{words("Lista en")}</div>
            <div class="h1 big" id="o2">{hl("14 días.")}</div>
            <div class="h2 gray" id="o3">{words("Precio de fundador para los primeros 5 restaurantes.")}</div>
          </div>
          <div class="ctacard" id="cta">
            <div class="cta-ic">{HOUSE}</div>
            <div class="cta-t">Casa Digital</div>
            <div class="cta-s">Hablemos.</div>
            <div class="cta-wa"><span>WhatsApp</span>{WHATSAPP}</div>
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

    css = (CSS.replace("$heroB", "rgb(%d,%d,%d)" % tuple(int(v * .22) for v in hexrgb(hero))).replace("$hero", hero).replace("$acc", acc).replace("$pri", pri)
           .replace("$washA", rgba(hero, .16)).replace("$washB", rgba(acc, .22)).replace("$sitebg", c["bg"]).replace("$siteink", c["ink"])
           .replace("$dweight", str(f["displayWeight"])).replace("$dcase", f.get("displayCase", "none")).replace("$dtrack", f["displayTracking"])
           .replace("$ital", '"DisplayI"' if f.get("italicFile") else '"Display"')
           .replace("$italface", '@font-face{font-family:"DisplayI";src:url("assets/fonts/display-italic.woff2") format("woff2");font-style:italic;}' if f.get("italicFile") else "")
           .replace("$introsizepx", str(r.get("introSize3", 150)) + "px"))
    js = JS.replace("$reviews", str(reviews_n))
    html = (HTML.replace("$title", f"Casa Digital x {r['name']}").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)))
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


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
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="$total" data-fade-out="2.5" data-track-index="1"></audio>
$body
</div>
<script>$js</script>
</body>
</html>
'''

CSS = r'''
@font-face{font-family:"Display";src:url("assets/fonts/display.woff2") format("woff2");}
$italface
@font-face{font-family:"IT";src:url("assets/fonts/it-300.woff2") format("woff2");font-weight:300;}
@font-face{font-family:"IT";src:url("assets/fonts/it-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"IT";src:url("assets/fonts/it-500.woff2") format("woff2");font-weight:500;}
@font-face{font-family:"IT";src:url("assets/fonts/it-600.woff2") format("woff2");font-weight:600;}
@font-face{font-family:"IT";src:url("assets/fonts/it-700.woff2") format("woff2");font-weight:700;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1920px;height:1080px;overflow:hidden;background:#FBFAF7;}
#root{position:relative;width:1920px;height:1080px;background:#FBFAF7;color:#111113;font-family:"IT",sans-serif;-webkit-font-smoothing:antialiased;}
.scene{position:absolute;inset:0;overflow:hidden;background:#FBFAF7;}
.cam{position:absolute;inset:0;transform-origin:30% 50%;}
.w{display:inline-block;}
.wash{position:absolute;border-radius:50%;}
.w1{width:1500px;height:1500px;left:-300px;top:-700px;background:radial-gradient(closest-side,$washA,rgba(251,250,247,0));}
.w2{width:1300px;height:1300px;left:900px;top:200px;background:radial-gradient(closest-side,$washB,rgba(251,250,247,0));}
.w3{width:1600px;height:1600px;left:900px;top:-500px;background:radial-gradient(closest-side,$washA,rgba(251,250,247,0));}
.w4{width:1500px;height:1500px;left:950px;top:-300px;background:radial-gradient(closest-side,$washB,rgba(251,250,247,0));}
.w5{width:1700px;height:1700px;left:800px;top:-400px;background:radial-gradient(closest-side,rgba(48,209,88,.16),rgba(251,250,247,0));}
.w6{width:1900px;height:1900px;left:10px;top:-420px;background:radial-gradient(closest-side,$washA,rgba(251,250,247,0));}
.w7{width:1500px;height:1500px;left:900px;top:-200px;background:radial-gradient(closest-side,rgba(90,130,255,.28),rgba(0,0,0,0));}
.w8{width:1600px;height:1600px;left:900px;top:-300px;background:radial-gradient(closest-side,rgba(255,214,10,.20),rgba(251,250,247,0));}
.center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.left{position:absolute;left:150px;top:0;bottom:0;width:860px;display:flex;flex-direction:column;justify-content:center;}
.grp{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);}
.disp{font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;}
.cd{display:flex;align-items:center;gap:18px;font-weight:600;font-size:40px;letter-spacing:-.015em;color:#111113;}
.cd .house{width:50px;height:50px;}
.sub-g{margin-top:70px;font-size:34px;font-weight:500;color:#86868B;}
.intro-name{margin-top:24px;font-size:$introsizepx;line-height:1;color:$hero;}
.h1{font-weight:600;font-size:116px;line-height:1.02;letter-spacing:-.045em;}
.h1.big{font-size:170px;}
.h2{font-weight:500;font-size:52px;line-height:1.2;letter-spacing:-.02em;margin-top:40px;}
.gray{color:#86868B;}
.white{color:#fff;}
.soft{color:rgba(235,235,245,.7);margin-top:14px;}
#p1{margin-bottom:36px;}
.eyebrow{font-size:40px;font-weight:500;color:#86868B;margin-bottom:12px;}
.num{font-variant-numeric:tabular-nums;color:$hero;}
.hl{position:relative;display:inline-block;white-space:nowrap;isolation:isolate;}
.hlbg{position:absolute;left:-10px;right:-14px;top:14%;bottom:6%;background:#FFD60A;border-radius:12px;transform-origin:0 50%;transform:scaleX(0);z-index:-1;}
.hl .w{position:relative;}

.wall{position:absolute;left:1000px;top:-200px;width:1100px;height:1500px;perspective:2200px;}
.wall-in{position:absolute;inset:0;display:flex;gap:28px;transform:rotateX(14deg) rotateY(-22deg) rotateZ(6deg);transform-style:preserve-3d;}
.rcol{width:300px;display:flex;flex-direction:column;gap:28px;}
.rv{background:#fff;border-radius:30px;padding:30px;box-shadow:0 20px 50px rgba(0,0,0,.08),0 0 0 1px rgba(0,0,0,.04);}
.rv-top{display:flex;align-items:center;gap:14px;margin-bottom:22px;}
.av{width:52px;height:52px;border-radius:50%;color:#fff;font-weight:600;font-size:24px;display:flex;align-items:center;justify-content:center;}
.rv-stars{color:#FFB800;font-size:28px;letter-spacing:.06em;}
.sk{height:14px;border-radius:8px;background:#ECECEF;margin-top:12px;}
.rv-g{margin-top:22px;font-size:20px;color:#A1A1A6;font-weight:500;}
.browser{position:absolute;left:1010px;top:150px;width:820px;height:780px;background:#fff;border-radius:34px;box-shadow:0 40px 100px rgba(0,0,0,.14),0 0 0 1px rgba(0,0,0,.05);overflow:hidden;}
.br-bar{height:76px;background:#F2F2F4;display:flex;align-items:center;padding:0 28px;gap:12px;}
.br-bar i{width:16px;height:16px;border-radius:50%;background:#D1D1D6;}
.br-bar i:nth-child(1){background:#FF5F57;}.br-bar i:nth-child(2){background:#FEBC2E;}.br-bar i:nth-child(3){background:#28C840;}
.br-url{margin-left:40px;flex:1;height:44px;border-radius:12px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:22px;color:#6E6E73;}
.br-body{padding:44px 48px;position:relative;}
.gsearch{height:84px;border-radius:44px;box-shadow:0 0 0 1.5px #DADCE0;display:flex;align-items:center;padding:0 34px;font-size:32px;color:#202124;}
.g-ic{font-size:40px;color:#9AA0A6;margin-right:18px;}
.g-q{white-space:nowrap;overflow:hidden;display:inline-block;}
.res{margin-top:34px;}
.res-u{font-size:22px;color:#188038;}
.res-t{font-size:32px;color:#1A0DAB;margin-top:4px;}
.sk2{height:12px;width:80%;border-radius:6px;background:#EEE;margin-top:12px;}
.nochip{position:absolute;right:48px;top:150px;background:#FF3B30;color:#fff;font-weight:600;font-size:28px;padding:16px 30px;border-radius:40px;box-shadow:0 14px 34px rgba(255,59,48,.35);}
.ph-stage{position:absolute;left:1080px;top:0;width:760px;height:1080px;perspective:2400px;}
.iph{position:absolute;left:170px;top:90px;width:430px;height:900px;border-radius:78px;padding:14px;background:linear-gradient(145deg,#E8E8ED,#B9B9C0 40%,#F5F5F7 70%,#C7C7CC);box-shadow:0 60px 120px rgba(0,0,0,.22),inset 0 0 0 2px rgba(255,255,255,.7);transform-style:preserve-3d;}
.iph.dark{background:linear-gradient(145deg,#3A3A3C,#0C0C0D 40%,#1C1C1E 70%,#48484A);box-shadow:0 60px 140px rgba(0,0,0,.6),inset 0 0 0 2px rgba(255,255,255,.12);}
.iph-scr{position:relative;width:100%;height:100%;border-radius:66px;overflow:hidden;background:$sitebg;color:$siteink;}
.iph.dark .iph-scr{background:#0B0B0F;color:#fff;}
.island{position:absolute;top:16px;left:50%;width:130px;height:38px;margin-left:-65px;border-radius:22px;background:#000;z-index:5;}
.ph-scroll{position:absolute;left:0;right:0;top:0;}
.site{height:872px;padding:90px 36px 40px;background:radial-gradient(120% 70% at 30% 10%,$hero,$heroB);color:#fff;position:relative;}
.site-nav{display:flex;justify-content:space-between;font-size:17px;opacity:.9;}
.site-nav b{font-family:"Display";font-weight:$dweight;text-transform:$dcase;font-size:21px;}
.site-name{margin-top:190px;font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;font-size:76px;line-height:.98;}
.site-tag{margin-top:24px;font-family:$ital;font-style:italic;font-size:27px;line-height:1.2;}
.site-btns{position:absolute;left:36px;right:36px;bottom:60px;display:flex;gap:12px;}
.site-btns span{flex:1;text-align:center;padding:20px 0;border-radius:40px;font-weight:600;font-size:21px;}
.b1{background:#fff;color:#000;}.b2{background:rgba(255,255,255,.16);border:1.5px solid rgba(255,255,255,.4);}
.menu{padding:90px 36px 40px;}
.menu-h{font-family:"Display";font-weight:$dweight;text-transform:$dcase;font-size:58px;margin-bottom:16px;}
.dish{display:flex;justify-content:space-between;align-items:baseline;font-size:25px;font-weight:500;padding:20px 0;border-bottom:1.5px solid rgba(127,127,127,.22);}
.dish em{font-style:normal;font-size:16px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:$hero;}
.today{margin-top:30px;display:inline-block;padding:12px 22px;border-radius:30px;background:$hero;color:#fff;font-weight:600;font-size:18px;}
.notif{position:absolute;left:14px;right:14px;top:66px;z-index:6;background:rgba(245,245,247,.92);color:#111;border-radius:30px;padding:18px 20px;display:flex;gap:14px;align-items:center;box-shadow:0 16px 40px rgba(0,0,0,.25);}
.n-ic{width:52px;height:52px;border-radius:14px;background:#111;color:#fff;display:flex;align-items:center;justify-content:center;}
.n-ic .house{width:30px;height:30px;}
.notif b{display:block;font-size:19px;}
.notif span{font-size:18px;color:#3A3A3C;}
.notif i{margin-left:auto;font-style:normal;font-size:15px;color:#8E8E93;align-self:flex-start;}
.chat{position:absolute;left:1040px;top:120px;width:760px;height:840px;border-radius:40px;background:#EFEAE2;box-shadow:0 40px 100px rgba(0,0,0,.14);overflow:hidden;}
.ch-head{height:110px;background:#fff;display:flex;align-items:center;gap:20px;padding:0 34px;border-bottom:1px solid #eee;}
.ch-av{width:64px;height:64px;border-radius:50%;color:#fff;font-weight:600;font-size:30px;display:flex;align-items:center;justify-content:center;}
.ch-head b{display:block;font-size:30px;}
.ch-head span{font-size:22px;color:#25D366;}
.ch-body{padding:40px 34px;display:flex;flex-direction:column;gap:22px;}
.bub{max-width:76%;font-size:30px;line-height:1.3;padding:20px 26px;border-radius:26px;box-shadow:0 2px 2px rgba(0,0,0,.06);}
.bub.in{background:#fff;align-self:flex-start;border-top-left-radius:6px;}
.bub.out{background:#D9FDD3;align-self:flex-end;border-top-right-radius:6px;}
.slot{display:grid;justify-items:end;}.slot>*{grid-area:1/1;}.slot .bub{max-width:76%;}
.typing{align-self:start;background:#D9FDD3;border-radius:26px;padding:24px 28px;display:flex;gap:10px;}
.typing i{width:14px;height:14px;border-radius:50%;background:#7C8C7A;}
.rcard{align-self:flex-end;width:440px;background:#fff;border-radius:26px;padding:28px 30px;box-shadow:0 10px 30px rgba(0,0,0,.08);border-left:8px solid #25D366;}
.rc-k{font-size:22px;font-weight:600;color:#25D366;text-transform:uppercase;letter-spacing:.08em;}
.rc-b{font-size:42px;font-weight:600;margin-top:8px;letter-spacing:-.02em;}
.rc-s{font-size:24px;color:#6E6E73;margin-top:6px;}
.kname{color:$hero;}
.navy{position:absolute;inset:0;background:linear-gradient(160deg,#0B1530,#050814 70%);}
.darkscene{background:#050814;}
.ph-stage.two .iph{top:120px;}
#ph2{left:60px;}
#ph3{left:380px;top:200px;}
.ord{padding:90px 30px;}
.ord-h{font-size:38px;font-weight:600;letter-spacing:-.02em;margin-bottom:24px;}
.orow{display:flex;justify-content:space-between;align-items:center;background:#1C1C22;border-radius:22px;padding:22px;margin-top:16px;}
.orow b{display:block;font-size:24px;}
.orow span{font-size:19px;color:#8E8E93;}
.orow em{font-style:normal;font-size:18px;font-weight:600;color:#30D158;background:rgba(48,209,88,.14);padding:8px 14px;border-radius:20px;}
.paysheet{position:absolute;left:0;right:0;bottom:0;background:#1C1C22;border-radius:40px 40px 0 0;padding:40px 30px 60px;}
.ps-h{font-size:32px;font-weight:600;}
.ps-card{margin-top:24px;font-size:22px;color:#8E8E93;letter-spacing:.08em;}
.ps-btn{position:relative;margin-top:30px;height:90px;border-radius:50px;background:#fff;color:#000;font-weight:600;font-size:26px;overflow:hidden;}
.ps-btn span{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;}
#psb2{background:#30D158;color:#fff;opacity:0;}
.ctacard{position:absolute;left:1180px;top:230px;width:600px;height:620px;border-radius:60px;background:#fff;box-shadow:0 50px 120px rgba(0,0,0,.14),0 0 0 1px rgba(0,0,0,.04);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.cta-ic{width:150px;height:150px;border-radius:40px;background:#111113;color:#fff;display:flex;align-items:center;justify-content:center;}
.cta-ic .house{width:90px;height:90px;}
.cta-t{margin-top:34px;font-size:52px;font-weight:600;letter-spacing:-.03em;}
.cta-s{margin-top:6px;font-size:34px;color:#86868B;}
.cta-wa{margin-top:44px;background:#25D366;color:#fff;font-weight:600;font-size:40px;padding:24px 44px;border-radius:50px;letter-spacing:-.01em;}
.cta-wa span{display:block;font-size:20px;font-weight:500;opacity:.85;}
.endscene{background:#000;color:#F5F5F7;}
.endglow{position:absolute;width:1300px;height:1300px;left:310px;top:-110px;border-radius:50%;background:radial-gradient(closest-side,rgba(90,130,255,.30),rgba(0,0,0,0));}
.ribwrap{position:absolute;left:420px;top:-420px;width:1080px;height:1920px;transform:rotate(90deg);}
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

JS = r'''
const tl = gsap.timeline({ paused: true });
const B = 0.017, at = s => s + B;
const SOFT = "expo.out", INOUT = "power2.inOut";
function rise(sel, t, o) {
  o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y || 50, filter: "blur(" + (o.blur || 14) + "px)" },
    { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d || 1.2, ease: SOFT, stagger: o.st || 0.08 }, t);
}
function out(sel, t, d) { tl.to(sel, { opacity: 0, y: -40, filter: "blur(12px)", duration: d || .7, ease: "power2.in" }, t); }
function swipe(sel, t) { tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: .7, ease: "power3.inOut" }, t); }
function float(sel, t, d) { tl.fromTo(sel, { y: 0 }, { y: -26, duration: d, ease: "sine.inOut" }, t); }
[["intro",0,8],["reviews",8,16],["search",16,22],["site",22,30],["chat",30,36],["calm",36,40],["pay",40,48],["offer",48,56],["end",56,64]]
  .forEach(([id, s, e]) => tl.fromTo("#cam-" + id, { scale: 1.0 }, { scale: 1.035, duration: e - s, ease: "none" }, s === 0 ? 0 : at(s)));

// 1 · intro, quiet
tl.fromTo(".w1", { x: -200, opacity: 0 }, { x: 100, opacity: 1, duration: 8, ease: "sine.inOut" }, 0);
tl.fromTo(".w2", { x: 200, opacity: 0 }, { x: -100, opacity: 1, duration: 8, ease: "sine.inOut" }, 0);
rise("#icd", 0.6, { d: 1.8 });
rise("#ipres .w", at(2.5), { d: 1.4, st: .12 });
tl.fromTo("#iname", { opacity: 0, scale: 1.08, filter: "blur(24px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, at(4.5));

// 2 · reviews: count-up + flowing wall of review cards
rise("#r1 .w", at(8));
const ctr = { v: 0 }, numEl = document.getElementById("rnum");
tl.fromTo("#rnum", { opacity: 0, filter: "blur(16px)" }, { opacity: 1, filter: "blur(0px)", duration: 1, ease: SOFT }, at(8.25));
tl.fromTo(ctr, { v: 0 }, { v: $reviews, duration: 2.4, ease: "power3.out", onUpdate: () => { numEl.textContent = Math.round(ctr.v).toLocaleString("en-US"); } }, at(8.25));
rise("#r2 .w", at(9));
tl.fromTo(".wall", { opacity: 0, x: 200 }, { opacity: 1, x: 0, duration: 1.6, ease: SOFT }, at(8));
tl.fromTo("#rcol0", { y: 0 }, { y: -700, duration: 8, ease: "none" }, at(8));
tl.fromTo("#rcol1", { y: -350 }, { y: -900, duration: 8, ease: "none" }, at(8));
tl.fromTo("#rcol2", { y: -120 }, { y: -760, duration: 8, ease: "none" }, at(8));
out("#rg1", at(12) - .7);
rise("#r3 .w", at(12));
rise("#r4 .w", at(12.5));
swipe("#r4 .hlbg", at(13.5));

// 3 · search
rise("#s1 .w", at(16));
tl.fromTo("#brw", { opacity: 0, x: 120, rotationY: -10 }, { opacity: 1, x: 0, rotationY: 0, duration: 1.4, ease: SOFT }, at(16));
tl.fromTo("#gq", { width: 0 }, { width: "auto", duration: .9, ease: "steps(18)" }, at(16.5));
rise("#res0, #res1, #res2", at(17.2), { st: .25, y: 30, blur: 6 });
rise("#s2 .w", at(17));
rise("#s3 .w", at(18));
swipe("#s3 .hlbg", at(18.6));
tl.to("#res0, #res1, #res2", { opacity: .35, duration: .8 }, at(20));
tl.fromTo("#nochip", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: .6, ease: "back.out(2)" }, at(20));
rise("#s4 .w", at(20));

// 4 · the site on an iPhone
rise("#t0", at(22));
rise("#t1 .w", at(22.4));
swipe("#t1 .hlbg", at(23.4));
tl.fromTo("#ph1", { y: 700, rotationY: -24, rotationX: 10 }, { y: 0, rotationY: -12, rotationX: 4, duration: 2, ease: SOFT }, at(22));
tl.to("#ph1", { rotationY: 6, rotationX: 0, duration: 6, ease: "sine.inOut" }, at(24));
tl.fromTo("#notif", { y: -160, opacity: 0 }, { y: 0, opacity: 1, duration: .8, ease: "back.out(1.4)" }, at(24));
tl.to("#notif", { y: -160, opacity: 0, duration: .6, ease: "power2.in" }, at(25.4));
out("#sg1", at(26) - .7);
rise("#t2 .w", at(26));
rise("#t3 .w", at(26.4));
rise("#t4 .w", at(26.8));
tl.fromTo("#phs", { y: 0 }, { y: -872, duration: 1.4, ease: "power3.inOut" }, at(26));
rise(".dish", at(26.8), { st: .12, y: 24, blur: 6, d: .9 });

// 5 · WhatsApp reservations
rise("#c1 .w", at(30));
rise("#c2 .w", at(30.4));
swipe("#c2 .hlbg", at(31.2));
tl.fromTo("#chat", { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 1.2, ease: SOFT }, at(30));
float("#chat", at(31), 5);
rise("#b1", at(30.8), { y: 20, blur: 4, d: .6 });
tl.fromTo("#b2", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: .3, ease: "back.out(2)" }, at(31.4));
tl.fromTo("#b2 i", { y: 0 }, { y: -8, duration: .25, yoyo: true, repeat: 3, stagger: .1, ease: "sine.inOut" }, at(31.5));
tl.to("#b2", { opacity: 0, duration: .15 }, at(32) - .15);
rise("#b3", at(32), { y: 20, blur: 4, d: .6 });
tl.fromTo("#b4", { opacity: 0, scale: .85, y: 30 }, { opacity: 1, scale: 1, y: 0, duration: .8, ease: "back.out(1.6)" }, at(33));
rise("#c3 .w", at(34));

// 6 · break: calm statement
rise("#k1 .w", at(36), { d: 1.6, st: .14 });
rise("#k2 .w, #k2 .kname", at(37), { d: 1.6, st: .14 });

// 7 · dark: payments
rise("#p1 .w", at(40));
swipe("#p1 .hlbg", at(40.6));
tl.fromTo("#p1 .w", { color: "#ffffff" }, { color: "#111113", duration: .4 }, at(40.6) + .25);
tl.fromTo("#ph2", { y: 700, rotationY: 18, rotationZ: -6 }, { y: 0, rotationY: 10, rotationZ: -4, duration: 1.8, ease: SOFT }, at(40));
tl.fromTo("#ph3", { y: 800, rotationY: -16, rotationZ: 5 }, { y: 0, rotationY: -10, rotationZ: 4, duration: 1.8, ease: SOFT }, at(40) + .2);
float("#ph2", at(42), 6); float("#ph3", at(42), 6);
rise("#p2 .w", at(42));
rise("#p3 .w", at(42.5));
[42, 44, 46].forEach((s, i) => rise("#or" + i, at(s), { y: 24, blur: 6, d: .8 }));
tl.fromTo("#psb2", { opacity: 0 }, { opacity: 1, duration: .2 }, at(44));
tl.fromTo("#psb", { scale: 1 }, { scale: 1.05, duration: .15, yoyo: true, repeat: 1 }, at(44));

// 8 · offer + CTA
rise("#o1 .w", at(48));
rise("#o2 .w", at(48.5));
swipe("#o2 .hlbg", at(49.4));
rise("#o3 .w", at(50), { st: .05 });
tl.fromTo("#cta", { opacity: 0, y: 120, scale: .92 }, { opacity: 1, y: 0, scale: 1, duration: 1.4, ease: SOFT }, at(52));
float("#cta", at(53), 3);

// 9 · outro (kept from v2): light trails, outline draws in the break, fills on the drop
function trails(rid, t0, dur, spin) {
  for (let i = 0; i < 6; i++) {
    const st = t0 + i * 0.22, len = 480 + (i % 3) * 170;
    tl.fromTo("." + rid + "-p" + i, { strokeDasharray: len + " 2000", strokeDashoffset: len }, { strokeDashoffset: -1000, duration: dur - i * 0.15, ease: "power2.inOut" }, st);
  }
  tl.fromTo("#" + rid, { rotation: spin[0], scale: spin[2], opacity: 0 }, { rotation: spin[1], scale: spin[3], opacity: 1, duration: dur, ease: "power1.inOut" }, t0);
}
const strokes = document.querySelectorAll("#mstroke path");
strokes.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
trails("re", at(56) - 0.4, 2.6, [20, -8, 1.6, 0.9]);
tl.to("#re", { scale: 3.2, opacity: 0, duration: 1.1, ease: "expo.out" }, at(58));
tl.to("#mstroke path", { strokeDashoffset: 0, duration: 1.9, ease: "power2.inOut" }, at(56) + .05);
tl.fromTo("#mfill", { opacity: 0 }, { opacity: 1, duration: .5, ease: "power2.out" }, at(58));
tl.to("#mstroke", { opacity: 0, duration: .5 }, at(58));
tl.fromTo("#mwrap", { scale: .92 }, { scale: 1, duration: 2.2, ease: SOFT }, at(56));
tl.fromTo("#mwrap", { filter: "drop-shadow(0 0 0px rgba(140,170,255,0))" }, { filter: "drop-shadow(0 0 60px rgba(140,170,255,.65))", duration: .35, ease: "power2.out", yoyo: true, repeat: 1 }, at(58));
tl.fromTo("#eglow", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: 1.6, ease: SOFT }, at(58));
tl.fromTo("#msweep", { x: -200 }, { x: 900, duration: 1.4, ease: "power2.inOut" }, at(58.5));
rise("#lby", at(58.5), { d: 1.2 });
rise(".lt", at(58.5) + .2, { d: 1.2, st: .035, y: 40, blur: 12 });
tl.to("#end .center, #eglow", { opacity: 0, duration: 1.4, ease: "power2.in" }, 62.4);

window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
tl.seek(0);
'''

if __name__ == "__main__":
    data = json.load(open(os.path.join(HERE, "restaurants.json")))
    only = sys.argv[1:]
    for r in data:
        if not only or r["slug"] in only:
            print(build(r))
