#!/usr/bin/env python3
"""Generate one HyperFrames project per restaurant from restaurants.json."""
import json, os, random, shutil, sys
from string import Template

HERE = os.path.dirname(os.path.abspath(__file__))
DEPS = os.path.join(HERE, "deps", "node_modules")
OUT = os.path.join(HERE, "videos")
MUSIC = os.path.join(HERE, "musica.mp3")
LOGO = os.path.join(HERE, "logo-clientia.jpeg")
WHATSAPP = "+1 (765) 543-4251"

B = 0.017  # offset of the beat grid in the track (120 BPM, bar = 2 s)


def t(sec):
    """Absolute time of a beat that lands at `sec` on the grid."""
    return round(sec + B, 3)


# (id, start_beat, end_beat) - every cut lands on a downbeat
SCENES = [
    ("intro1", 0, 4), ("intro2", 4, 8), ("hero", 8, 12), ("stat", 12, 14),
    ("search", 14, 16), ("phonescene", 16, 20), ("qr", 20, 22), ("pay", 22, 24),
    ("modes", 24, 26), ("res", 26, 28), ("zero", 28, 30), ("ready", 30, 32),
    ("cta", 32, 36), ("end", 36, 40),
]
TOTAL = 40.0


def qr_svg(seed, size=21, cell=24, fg="#000"):
    rnd = random.Random(seed)
    rects = []
    def finder(x0, y0):
        for y in range(7):
            for x in range(7):
                on = x in (0, 6) or y in (0, 6) or (2 <= x <= 4 and 2 <= y <= 4)
                if on:
                    rects.append((x0 + x, y0 + y))
    finder(0, 0); finder(size - 7, 0); finder(0, size - 7)
    reserved = lambda x, y: (x < 8 and y < 8) or (x >= size - 8 and y < 8) or (x < 8 and y >= size - 8)
    for y in range(size):
        for x in range(size):
            if not reserved(x, y) and rnd.random() < 0.48:
                rects.append((x, y))
    px = size * cell
    body = "".join(f'<rect x="{x*cell}" y="{y*cell}" width="{cell}" height="{cell}"/>' for x, y in rects)
    return f'<svg viewBox="0 0 {px} {px}" width="{px}" height="{px}" fill="{fg}">{body}</svg>'


def house_svg(color):
    return (f'<svg viewBox="0 0 64 64" width="64" height="64" fill="none" stroke="{color}" stroke-width="6" '
            f'stroke-linejoin="round"><path d="M8 30 L32 9 L56 30 V56 H8 Z"/><path d="M26 56 V40 H38 V56"/></svg>')


def build(r):
    c = r["colors"]; f = r["fonts"]
    dark = r.get("dark", False)
    proj = os.path.join(OUT, r["slug"])
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    shutil.copy(MUSIC, os.path.join(proj, "assets", "musica.mp3"))
    shutil.copy(LOGO, os.path.join(proj, "assets", "logo-clientia.jpeg"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), os.path.join(proj, "assets", "gsap.min.js"))
    fam_dir = f["display"].lower().replace(" ", "-")
    shutil.copy(os.path.join(DEPS, "@fontsource", fam_dir, "files", f["displayFile"]), os.path.join(proj, "assets", "fonts", "display.woff2"))
    italic = f.get("italicFile")
    if italic:
        shutil.copy(os.path.join(DEPS, "@fontsource", fam_dir, "files", italic), os.path.join(proj, "assets", "fonts", "display-italic.woff2"))
    for w in (400, 600, 800):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter", "files", f"inter-latin-{w}-normal.woff2"), os.path.join(proj, "assets", "fonts", f"inter-{w}.woff2"))
    with open(os.path.join(proj, "hyperframes.json"), "w") as fh:
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                   "media": {"autoProxy": True}}, fh, indent=2)
    with open(os.path.join(proj, "meta.json"), "w") as fh:
        json.dump({"id": r["slug"], "name": f"Casa Digital x {r['name']}"}, fh)

    # scene wrappers
    def scene(sid, inner):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        start = 0 if s == 0 else t(s)
        end = TOTAL if e == 40 else t(e)
        return (f'<section id="{sid}" class="clip scene" data-start="{start}" data-duration="{round(end-start,3)}" '
                f'data-track-index="0">{inner}</section>')

    name_lines = "".join(f'<div class="mask"><div class="hl">{ln}</div></div>' for ln in r["nameLines"])
    intro_letters = "".join(f'<span class="il">{ch if ch != " " else "&nbsp;"}</span>' for ch in r["name"])
    found_rows = "".join(
        f'<div class="res"><div class="res-url">{u}</div><div class="res-title">{r["name"]} · {r["city"]}</div></div>'
        for u in r["found"])
    dishes_rows = "".join(f'<div class="dish"><span>{d}</span><i></i><b>Ver</b></div>' for d in r["dishes"])
    qr = qr_svg(r["slug"], fg=c["ink"] if not dark else "#111")

    body = "\n".join([
        scene("intro1", f'''
          <div class="center col">
            <div class="cd-mark" id="i1mark">{house_svg(c["ink"])}<span>CASA DIGITAL</span></div>
            <div class="small-cap" id="i1pres">presenta</div>
          </div>'''),
        scene("intro2", f'''
          <div class="center col">
            <div class="small-cap" id="i2for">una propuesta para</div>
            <div class="intro-name">{intro_letters}</div>
            <div class="buildbar"><div id="i2bar"></div></div>
          </div>'''),
        scene("hero", f'''
          <div class="hero-bg"></div>
          <div class="hero-in">
            <div class="kicker" id="hkick">{r["kind"]}</div>
            <div class="hero-name">{name_lines}</div>
            <div class="rule" id="hrule"></div>
            <div class="tagline" id="htag">{r["tagline"]}</div>
            <div class="where" id="hwhere">{r["city"]} · {r["zone"]}</div>
          </div>'''),
        scene("stat", f'''
          <div class="center col">
            <div class="stars" id="sstars">★★★★★</div>
            <div class="big-num" id="snum">{r["rating"]}</div>
            <div class="stat-sub" id="ssub">{r["reviews"]} reseñas en Google</div>
            <div class="stat-line" id="sline">La gente ya te ama.</div>
          </div>'''),
        scene("search", f'''
          <div class="pad col">
            <div class="q-label" id="qlab">Alguien te busca en Google…</div>
            <div class="searchbar" id="qbar"><span class="glass">⌕</span><span class="q-text" id="qtext">{r["name"]} {r["city"]}</span></div>
            <div class="results" id="qres">{found_rows}</div>
            <div class="stamp" id="qstamp">¿Y tu página?</div>
          </div>'''),
        scene("phonescene", f'''
          <div class="ph-caption"><div id="pc1">Tu propia casa digital.</div><div id="pc2">Un menú que cambias desde el celular.</div></div>
          <div class="phone" id="phone">
            <div class="ph-screen">
              <div class="ph-url">{r["domain"]}</div>
              <div class="ph-scroll" id="phscroll">
                <div class="site-hero">
                  <div class="site-nav"><b>{r["name"]}</b><span>Menú · Reservas</span></div>
                  <div class="site-name">{"<br>".join(r["nameLines"])}</div>
                  <div class="site-tag">{r["tagline"]}</div>
                  <div class="site-btns"><span class="b1">Pedir ahora</span><span class="b2">Reservar</span></div>
                </div>
                <div class="site-menu">
                  <div class="menu-h">Menú</div>
                  {dishes_rows}
                  <div class="menu-foot">Hoy: especial del día</div>
                </div>
              </div>
            </div>
          </div>'''),
        scene("qr", f'''
          <div class="center col">
            <div class="qr-card" id="qrcard">{qr}</div>
            <div class="h2" id="qrh">Menú vivo con QR</div>
            <div class="sub" id="qrs">Sin PDF viejos. Sin reimprimir.</div>
          </div>'''),
        scene("pay", f'''
          <div class="center col">
            <div class="h2" id="payh">Piden y pagan en tu web.</div>
            <div class="paycard" id="paycard">
              <div class="pc-row"><span>{r["dishes"][0]}</span><span>×2</span></div>
              <div class="pc-row"><span>{r["dishes"][1]}</span><span>×1</span></div>
              <div class="pc-card">VISA •••• 4821</div>
              <div class="pc-btn" id="paybtn"><span id="paybtn1">Pagar con tarjeta</span><span id="paybtn2">✓ Pago confirmado</span></div>
            </div>
            <div class="sub" id="pays">El dinero va directo a tu cuenta.</div>
          </div>'''),
        scene("modes", '''
          <div class="pad col modes">
            <div class="mode" id="m1">En la mesa.</div>
            <div class="mode" id="m2">Para recoger.</div>
            <div class="mode" id="m3">A domicilio.</div>
          </div>'''),
        scene("res", f'''
          <div class="center col">
            <div class="h2" id="resh">Reservas sin llamadas perdidas.</div>
            <div class="rescard" id="rescard">
              <div class="rc-top">Reserva · {r["name"]}</div>
              <div class="rc-big">Sábado · 8:00 pm</div>
              <div class="rc-mid">Mesa para 4</div>
              <div class="rc-ok" id="resok">✓ Confirmada por WhatsApp</div>
            </div>
          </div>'''),
        scene("zero", '''
          <div class="center col zero">
            <div class="zero-num" id="znum">0%</div>
            <div class="zero-sub" id="zsub">de comisión nuestra por pedido</div>
            <div class="zero-line" id="zline">Tus clientes y tus datos son tuyos.</div>
          </div>'''),
        scene("ready", f'''
          <div class="center col">
            <div class="ready-k" id="rk">Lista en</div>
            <div class="ready-n" id="rn">14 días</div>
            <div class="pill" id="rpill">{r["domain"]}</div>
          </div>'''),
        scene("cta", f'''
          <div class="center col">
            <div class="cd-mark big" id="cmark">{house_svg(c["bg"] if not dark else c["ink"])}<span>CASA DIGITAL</span></div>
            <div class="cta-for" id="cfor">Hecha a mano para {r["name"]}</div>
            <div class="cta-wa" id="cwa"><div class="wa-k">Escríbenos por WhatsApp</div><div class="wa-n">{WHATSAPP}</div></div>
            <div class="cta-small" id="csmall">Precio de fundador para los primeros 5 restaurantes</div>
          </div>'''),
        scene("end", '''
          <div class="center col endc">
            <img id="elogo" src="assets/logo-clientia.jpeg" alt="Clientia Tech">
            <div class="by" id="eby">by <b>Clientia Tech</b></div>
          </div>'''),
    ])

    disp_case = f.get("displayCase", "none")
    italic_face = ('@font-face{font-family:"DisplayI";src:url("assets/fonts/display-italic.woff2") format("woff2");font-style:italic;}'
                   if italic else "")
    cta_bg = c["ink"] if not dark else c["deep"]
    cta_fg = c["bg"] if not dark else c["ink"]
    css = Template(CSS).substitute(
        bg=c["bg"], ink=c["ink"], primary=c["primary"], accent=c["accent"], deep=c["deep"],
        dweight=f["displayWeight"], dcase=disp_case, dtrack=f["displayTracking"], italic_face=italic_face,
        ital_family='"DisplayI"' if italic else '"Display"', cta_bg=cta_bg, cta_fg=cta_fg,
        on_primary="#FFFFFF" if not dark else "#111111", herosize=r.get("heroSize",250),
    )
    js = Template(JS).substitute({k: t(v) for k, v in BEATS.items()} | {"nletters": len(r["name"])})
    html = Template(HTML).substitute(css=css, body=body, js=js, total=TOTAL, title=f"Casa Digital x {r['name']}")
    with open(os.path.join(proj, "index.html"), "w") as fh:
        fh.write(html)
    return proj


# beat seconds used by the animation script (all on the 0.5 s grid)
BEATS = dict(b0=0, b2=2, b4=4, b5=5, b6=6, b65=6.5, b75=7.5, b8=8, b825=8.25, b875=8.75, b95=9.5, b10=10, b11=11,
             b12=12, b125=12.5, b13=13, b14=14, b145=14.5, b15=15, b155=15.5, b16=16, b165=16.5, b17=17, b18=18, b19=19,
             b20=20, b205=20.5, b21=21, b22=22, b225=22.5, b23=23, b235=23.5, b24=24, b2475=24.75, b2525=25.5,
             b26=26, b265=26.5, b27=27, b28=28, b285=28.5, b295=29.5, b30=30, b305=30.5, b31=31, b32=32, b3275=32.75,
             b34=34, b35=35, b36=36, b365=36.5, b37=37)

HTML = r'''<!doctype html>
<html lang="es" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>$title</title>
<script src="assets/gsap.min.js"></script>
<style>$css</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="$total" data-width="1080" data-height="1920">
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="$total" data-fade-out="2" data-track-index="1"></audio>
$body
</div>
<script>$js</script>
</body>
</html>
'''

CSS = r'''
@font-face{font-family:"Display";src:url("assets/fonts/display.woff2") format("woff2");}
$italic_face
@font-face{font-family:"InterL";src:url("assets/fonts/inter-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"InterL";src:url("assets/fonts/inter-600.woff2") format("woff2");font-weight:600;}
@font-face{font-family:"InterL";src:url("assets/fonts/inter-800.woff2") format("woff2");font-weight:800;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:$bg;}
#root{position:relative;width:1080px;height:1920px;font-family:"InterL",sans-serif;color:$ink;background:$bg;}
.scene{position:absolute;inset:0;overflow:hidden;background:$bg;}
.center{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;padding:0 90px;}
.pad{position:absolute;inset:0;padding:220px 90px;}
.col{flex-direction:column;display:flex;}
.disp{font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;}
.cd-mark{display:flex;align-items:center;gap:22px;font-weight:800;letter-spacing:0.28em;font-size:40px;}
.cd-mark svg{width:56px;height:56px;}
.cd-mark.big{font-size:64px;gap:30px;}
.cd-mark.big svg{width:96px;height:96px;}
.small-cap{margin-top:36px;font-size:34px;letter-spacing:0.3em;text-transform:uppercase;opacity:.7;}
#intro2 .small-cap{margin:0 0 50px;}
.intro-name{font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;font-size:150px;line-height:1;color:$primary;}
.il{display:inline-block;}
.buildbar{margin-top:70px;width:600px;height:8px;background:rgba(127,127,127,.25);border-radius:4px;overflow:hidden;}
#i2bar{width:100%;height:100%;background:$accent;transform-origin:0 50%;transform:scaleX(0);}
#hero{background:$primary;}
.hero-in{position:absolute;left:90px;right:90px;top:380px;color:$on_primary;}
.kicker{font-size:34px;letter-spacing:.22em;text-transform:uppercase;font-weight:600;opacity:.85;}
.hero-name{margin-top:40px;font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;font-size:${herosize}px;line-height:.92;}
.mask{overflow:hidden;padding-bottom:12px;}
.hl{display:block;}
.rule{margin-top:50px;width:260px;height:14px;background:$accent;transform-origin:0 50%;}
.tagline{margin-top:50px;font-family:$ital_family;font-style:italic;font-size:64px;line-height:1.15;max-width:880px;}
.where{margin-top:40px;font-size:34px;letter-spacing:.12em;text-transform:uppercase;opacity:.8;}
#stat{background:$ink;color:$bg;}
.stars{font-size:90px;color:$accent;letter-spacing:.1em;}
.big-num{font-family:"Display";font-weight:$dweight;font-size:440px;line-height:1;margin-top:10px;}
.stat-sub{font-size:52px;font-weight:600;margin-top:20px;}
.stat-line{margin-top:90px;font-family:$ital_family;font-style:italic;font-size:80px;color:$accent;}
.q-label{font-size:58px;font-weight:600;margin-top:60px;}
.searchbar{margin-top:60px;background:#fff;color:#202124;border-radius:70px;height:140px;display:flex;align-items:center;padding:0 50px;font-size:50px;box-shadow:0 10px 40px rgba(0,0,0,.18);border:2px solid rgba(0,0,0,.08);}
.glass{font-size:64px;margin-right:24px;color:#5f6368;}
.q-text{white-space:nowrap;overflow:hidden;display:inline-block;}
.results{margin-top:60px;display:flex;flex-direction:column;gap:30px;}
.res{background:#fff;color:#202124;border-radius:28px;padding:36px 44px;text-align:left;box-shadow:0 6px 24px rgba(0,0,0,.12);}
.res-url{font-size:34px;color:#188038;}
.res-title{font-size:44px;color:#1a0dab;margin-top:8px;}
.stamp{margin-top:90px;align-self:center;font-family:"Display";font-weight:$dweight;text-transform:$dcase;font-size:120px;color:$primary;border:12px solid $primary;padding:20px 50px;border-radius:24px;transform:rotate(-6deg);}
#phone-scene,#phone{}
#phone{position:absolute;left:190px;top:470px;width:700px;height:1400px;border-radius:90px;background:#0b0b0b;padding:22px;box-shadow:0 40px 90px rgba(0,0,0,.35);}
#phone .ph-screen{position:relative;width:100%;height:100%;border-radius:70px;overflow:hidden;background:$bg;color:$ink;}
.ph-url{position:absolute;top:0;left:0;right:0;height:120px;z-index:2;display:flex;align-items:flex-end;justify-content:center;padding-bottom:18px;font-size:28px;background:rgba(127,127,127,.12);backdrop-filter:blur(4px);}
.ph-scroll{position:absolute;left:0;right:0;top:120px;}
.site-hero{height:1240px;background:$primary;color:$on_primary;padding:50px 50px;position:relative;}
.site-nav{display:flex;justify-content:space-between;font-size:26px;align-items:center;}
.site-nav b{font-family:"Display";font-weight:$dweight;text-transform:$dcase;font-size:34px;}
.site-name{margin-top:200px;font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;font-size:130px;line-height:.95;}
.site-tag{margin-top:40px;font-family:$ital_family;font-style:italic;font-size:42px;line-height:1.2;}
.site-btns{position:absolute;left:50px;right:50px;bottom:80px;display:flex;gap:20px;}
.site-btns span{flex:1;text-align:center;padding:30px 0;border-radius:60px;font-weight:800;font-size:32px;}
.b1{background:$accent;color:#111;}
.b2{border:3px solid currentColor;}
.site-menu{padding:60px 50px;background:$bg;color:$ink;}
.menu-h{font-family:"Display";font-weight:$dweight;text-transform:$dcase;font-size:90px;color:$primary;margin-bottom:30px;}
.dish{display:flex;align-items:baseline;font-size:38px;padding:30px 0;border-bottom:2px solid rgba(127,127,127,.25);}
.dish i{flex:1;}
.dish b{font-size:26px;letter-spacing:.15em;text-transform:uppercase;color:$primary;}
.menu-foot{margin-top:40px;background:$accent;color:#111;display:inline-block;padding:16px 30px;border-radius:40px;font-weight:800;font-size:28px;}
.ph-caption{position:absolute;left:90px;right:90px;top:200px;height:200px;text-align:center;font-size:62px;font-weight:800;line-height:1.1;}
.ph-caption div{position:absolute;left:0;right:0;}
#qr{background:$accent;}
#qr .center{color:#111;}
.qr-card{background:#fff;padding:50px;border-radius:50px;box-shadow:0 30px 70px rgba(0,0,0,.25);}
.qr-card svg{display:block;width:520px;height:520px;}
.h2{font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;font-size:110px;line-height:1;margin-top:80px;}
.sub{font-size:48px;margin-top:40px;font-weight:600;opacity:.85;}
#pay .h2{margin:0 0 70px;}
.paycard{width:860px;background:#fff;color:#111;border-radius:50px;padding:60px;text-align:left;box-shadow:0 30px 80px rgba(0,0,0,.2);}
.pc-row{display:flex;justify-content:space-between;font-size:42px;padding:22px 0;border-bottom:2px solid #eee;}
.pc-card{margin-top:40px;font-size:38px;letter-spacing:.08em;color:#555;}
.pc-btn{position:relative;margin-top:50px;height:130px;border-radius:70px;background:$primary;color:$on_primary;font-weight:800;font-size:44px;overflow:hidden;}
.pc-btn span{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;}
#paybtn2{background:#1e8e3e;color:#fff;opacity:0;}
#modes{background:$ink;color:$bg;}
.modes{justify-content:center;gap:40px;}
.mode{font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;font-size:150px;line-height:1;}
#m2{color:$accent;}
#res .h2{margin:0 0 80px;font-size:96px;}
.rescard{width:860px;background:$primary;color:$on_primary;border-radius:50px;padding:70px;text-align:left;}
.rc-top{font-size:34px;letter-spacing:.15em;text-transform:uppercase;opacity:.85;}
.rc-big{font-family:"Display";font-weight:$dweight;text-transform:$dcase;font-size:100px;margin-top:30px;line-height:1;}
.rc-mid{font-size:50px;margin-top:20px;}
.rc-ok{margin-top:50px;background:#25D366;color:#073b1c;font-weight:800;font-size:40px;padding:26px 36px;border-radius:60px;display:inline-block;}
#zero{background:$primary;color:$on_primary;}
.zero-num{font-family:"Display";font-weight:$dweight;font-size:520px;line-height:.9;}
.zero-sub{font-size:58px;font-weight:800;margin-top:30px;}
.zero-line{margin-top:80px;font-family:$ital_family;font-style:italic;font-size:62px;}
.ready-k{font-size:70px;font-weight:600;}
.ready-n{font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;font-size:250px;line-height:1;color:$primary;margin-top:20px;}
.pill{margin-top:80px;font-size:54px;font-weight:800;padding:30px 60px;border-radius:80px;background:$ink;color:$bg;}
#cta{background:$cta_bg;color:$cta_fg;}
.cta-for{margin-top:70px;font-family:$ital_family;font-style:italic;font-size:64px;}
.cta-wa{margin-top:120px;background:#25D366;color:#073b1c;border-radius:50px;padding:50px 70px;}
.wa-k{font-size:40px;font-weight:600;}
.wa-n{font-size:80px;font-weight:800;margin-top:10px;letter-spacing:.01em;}
.cta-small{margin-top:80px;font-size:36px;opacity:.75;max-width:760px;line-height:1.3;}
#end{background:#0C1C33;color:#fff;}
#elogo{width:520px;height:auto;display:block;}
.by{margin-top:40px;font-size:60px;font-weight:400;letter-spacing:.04em;}
.by b{font-weight:800;}
'''

JS = r'''
const tl = gsap.timeline({ paused: true });
const E = "power3.out", P = "back.out(1.8)";
// intro 1: soft build
tl.fromTo("#i1mark", {opacity:0, y:30}, {opacity:1, y:0, duration:1.4, ease:E}, $b0);
tl.fromTo("#i1pres", {opacity:0}, {opacity:.7, duration:1.2, ease:E}, $b2);
// intro 2: name letters land on the eighth notes leading into the drop
tl.fromTo("#i2for", {opacity:0, y:20}, {opacity:.7, y:0, duration:.8, ease:E}, $b4);
tl.fromTo(".il", {opacity:0, y:80, scale:.6}, {opacity:1, y:0, scale:1, duration:.35, ease:P, stagger:(1.4/$nletters)}, $b65);
tl.fromTo("#i2bar", {scaleX:0}, {scaleX:1, duration:1.5, ease:"none"}, $b65);
tl.to(".intro-name", {scale:1.12, duration:.5, ease:"power2.in"}, $b75);
// hero (drop)
tl.fromTo("#hero .hl", {yPercent:110}, {yPercent:0, duration:.5, ease:"power4.out", stagger:.25}, $b8);
tl.fromTo("#hkick", {opacity:0, x:-40}, {opacity:.85, x:0, duration:.4, ease:E}, $b8);
tl.fromTo("#hrule", {scaleX:0}, {scaleX:1, duration:.35, ease:E}, $b95);
tl.fromTo("#htag", {opacity:0, y:40}, {opacity:1, y:0, duration:.5, ease:E}, $b10);
tl.fromTo("#hwhere", {opacity:0}, {opacity:.8, duration:.4}, $b11);
tl.fromTo(".hero-name", {scale:1}, {scale:1.03, duration:.25, yoyo:true, repeat:1, ease:"power1.out"}, $b10);
// stat
tl.fromTo("#sstars", {opacity:0, scale:.4}, {opacity:1, scale:1, duration:.4, ease:P}, $b12);
tl.fromTo("#snum", {opacity:0, scale:1.6}, {opacity:1, scale:1, duration:.45, ease:E}, $b12);
tl.fromTo("#ssub", {opacity:0, y:30}, {opacity:1, y:0, duration:.4, ease:E}, $b125);
tl.fromTo("#sline", {opacity:0, scale:.8}, {opacity:1, scale:1, duration:.4, ease:P}, $b13);
// search
tl.fromTo("#qlab", {opacity:0, y:30}, {opacity:1, y:0, duration:.35, ease:E}, $b14);
tl.fromTo("#qbar", {opacity:0, y:60}, {opacity:1, y:0, duration:.4, ease:E}, $b14);
tl.fromTo("#qtext", {width:0}, {width:"auto", duration:.45, ease:"steps(14)"}, $b14);
tl.fromTo("#qres .res", {opacity:0, y:40}, {opacity:1, y:0, duration:.3, stagger:.12, ease:E}, $b145);
tl.fromTo("#qstamp", {opacity:0, scale:2.2}, {opacity:1, scale:1, duration:.3, ease:"power4.in"}, $b15 - .15);
tl.to("#qres", {opacity:.35, duration:.3}, $b155);
// phone
tl.fromTo("#phone", {y:900}, {y:0, duration:.6, ease:"power4.out"}, $b16);
tl.fromTo("#pc1", {opacity:0, y:40}, {opacity:1, y:0, duration:.4, ease:E}, $b16);
tl.fromTo(".site-btns span", {opacity:0, y:30}, {opacity:1, y:0, duration:.3, stagger:.25, ease:E}, $b17);
tl.to("#pc1", {opacity:0, y:-40, duration:.25}, $b18);
tl.fromTo("#pc2", {opacity:0, y:40}, {opacity:1, y:0, duration:.35, ease:E}, $b18);
tl.fromTo("#phscroll", {y:0}, {y:-1240, duration:.7, ease:"power3.inOut"}, $b18);
tl.fromTo(".dish", {opacity:0, x:40}, {opacity:1, x:0, duration:.3, stagger:.12, ease:E}, $b18 + .4);
tl.fromTo(".menu-foot", {scale:0}, {scale:1, duration:.35, ease:P}, $b19);
// qr
tl.fromTo("#qrcard", {scale:0, rotation:-12}, {scale:1, rotation:0, duration:.5, ease:P}, $b20);
tl.fromTo("#qrh", {opacity:0, y:40}, {opacity:1, y:0, duration:.35, ease:E}, $b205);
tl.fromTo("#qrs", {opacity:0}, {opacity:.85, duration:.3}, $b21);
// pay
tl.fromTo("#payh", {opacity:0, y:40}, {opacity:1, y:0, duration:.35, ease:E}, $b22);
tl.fromTo("#paycard", {opacity:0, y:120}, {opacity:1, y:0, duration:.45, ease:E}, $b22);
tl.fromTo("#paybtn2", {opacity:0}, {opacity:1, duration:.15}, $b23);
tl.fromTo("#paybtn", {scale:1}, {scale:1.06, duration:.15, yoyo:true, repeat:1}, $b23);
tl.fromTo("#pays", {opacity:0}, {opacity:.85, duration:.3}, $b235);
// modes - one per accent hit
tl.fromTo("#m1", {opacity:0, x:-120}, {opacity:1, x:0, duration:.3, ease:E}, $b24);
tl.fromTo("#m2", {opacity:0, x:-120}, {opacity:1, x:0, duration:.3, ease:E}, $b2475);
tl.fromTo("#m3", {opacity:0, x:-120}, {opacity:1, x:0, duration:.3, ease:E}, $b2525);
// reservations
tl.fromTo("#resh", {opacity:0, y:40}, {opacity:1, y:0, duration:.35, ease:E}, $b26);
tl.fromTo("#rescard", {opacity:0, scale:.85}, {opacity:1, scale:1, duration:.4, ease:P}, $b265);
tl.fromTo("#resok", {opacity:0, scale:.5}, {opacity:1, scale:1, duration:.3, ease:P}, $b27);
// zero
tl.fromTo("#znum", {scale:2.4, opacity:0}, {scale:1, opacity:1, duration:.4, ease:"power4.out"}, $b28);
tl.fromTo("#zsub", {opacity:0, y:30}, {opacity:1, y:0, duration:.35, ease:E}, $b285);
tl.fromTo("#zline", {opacity:0}, {opacity:1, duration:.35}, $b295);
// ready
tl.fromTo("#rk", {opacity:0, y:30}, {opacity:1, y:0, duration:.3, ease:E}, $b30);
tl.fromTo("#rn", {opacity:0, scale:.6}, {opacity:1, scale:1, duration:.4, ease:P}, $b305);
tl.fromTo("#rpill", {opacity:0, y:40}, {opacity:1, y:0, duration:.35, ease:E}, $b31);
// cta
tl.fromTo("#cmark", {opacity:0, scale:.8}, {opacity:1, scale:1, duration:.45, ease:P}, $b32);
tl.fromTo("#cfor", {opacity:0, y:30}, {opacity:1, y:0, duration:.4, ease:E}, $b3275);
tl.fromTo("#cwa", {opacity:0, y:80}, {opacity:1, y:0, duration:.45, ease:P}, $b34);
tl.fromTo("#csmall", {opacity:0}, {opacity:.75, duration:.4}, $b35);
// end card: by Clientia Tech
tl.fromTo("#elogo", {opacity:0, scale:.85}, {opacity:1, scale:1, duration:.6, ease:E}, $b36);
tl.fromTo("#eby", {opacity:0, y:30}, {opacity:1, y:0, duration:.5, ease:E}, $b365);
tl.to(".endc", {opacity:0, duration:.8}, 39.15);
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
