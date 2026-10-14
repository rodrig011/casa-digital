#!/usr/bin/env python3
"""Casa Digital pitch videos v2: slow, readable, Apple-keynote look.

Every scene cut lands on a downbeat of the track (120 BPM, bar = 2 s, grid offset 0.017 s).
Sections follow the song: drop at 8, break at 36, second break at 56 (logo draws on in the
silence) and the drop at 58 locks the Clientia Tech lockup.
"""
import json, os, shutil, sys
from string import Template

HERE = os.path.dirname(os.path.abspath(__file__))
DEPS = os.path.join(HERE, "deps", "node_modules")
OUT = os.path.join(HERE, "videos2")
WHATSAPP = "+1 (765) 543-4251"
B = 0.017
TOTAL = 64.0
MARK = json.load(open(os.path.join(HERE, "clientia-mark.json")))

SCENES = [  # id, start, end (seconds on the bar grid)
    ("intro", 0, 8), ("hero", 8, 16), ("stat", 16, 22), ("problem", 22, 28), ("phone", 28, 36),
    ("calm", 36, 40), ("bento", 40, 48), ("offer", 48, 52), ("cta", 52, 56), ("end", 56, 64),
]


def words(text, cls="w"):
    return " ".join(f'<span class="{cls}">{w}</span>' for w in text.split())


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgba(h, a):
    r, g, b = hexrgb(h)
    return f"rgba({r},{g},{b},{a})"


def lum(h):
    r, g, b = [v / 255 for v in hexrgb(h)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def lift(h, target=0.5):
    """Mix a color with white until it reads on black."""
    r, g, b = hexrgb(h)
    t = 0.0
    while t < 1:
        m = tuple(int(v + (255 - v) * t) for v in (r, g, b))
        if lum("#%02x%02x%02x" % m) >= target:
            return "#%02x%02x%02x" % m
        t += 0.05
    return "#ffffff"


RIBBONS = [  # long sweeping curves through the center of a 1080x1920 frame, with stroke widths
    ("M -220,1750 C 300,1500 200,720 700,600 S 1300,200 1420,-120", 70),
    ("M -300,1180 C 200,1300 500,1100 560,900 S 900,300 1320,180", 46),
    ("M 1320,1820 C 820,1700 400,1300 520,960 S 300,300 -220,90", 90),
    ("M -220,560 C 300,480 820,900 600,1220 S 700,1900 1120,2120", 38),
    ("M 1420,1080 C 900,1220 720,820 540,960 S 200,1500 -220,1520", 60),
    ("M 180,2140 C 300,1500 920,1320 800,800 S 400,100 620,-220", 52),
]


def ribbons(rid, palette):
    """Apple TV style light trails: blurred bloom + gradient body + hot white core per curve."""
    grads, glow, body, core = [], [], [], []
    n = len(palette)
    for i, (d, w) in enumerate(RIBBONS):
        a, b, c3 = palette[i % n], palette[(i + 1) % n], palette[(i + 2) % n]
        gid = f"{rid}g{i}"
        grads.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="1920" x2="1080" y2="0">'
                     f'<stop offset="0" stop-color="{a}"/><stop offset=".5" stop-color="{b}"/><stop offset="1" stop-color="{c3}"/></linearGradient>')
        common = f'd="{d}" pathLength="1000" fill="none" stroke-linecap="round" class="{rid}-p{i}"'
        glow.append(f'<path {common} stroke="url(#{gid})" stroke-width="{w * 2.6}"/>')
        body.append(f'<path {common} stroke="url(#{gid})" stroke-width="{w}"/>')
        core.append(f'<path {common} stroke="#fff" stroke-opacity=".85" stroke-width="{max(3, w * .12):.0f}"/>')
    return (f'<div class="rib" id="{rid}">'
            f'<svg class="rl glowl" viewBox="0 0 1080 1920"><defs>{"".join(grads)}</defs>{"".join(glow)}</svg>'
            f'<svg class="rl" viewBox="0 0 1080 1920"><defs>{"".join(g.replace(f"id=\"{rid}g", f"id=\"{rid}h") for g in grads)}</defs>'
            f'{"".join(p.replace(f"url(#{rid}g", f"url(#{rid}h") for p in body)}</svg>'
            f'<svg class="rl corel" viewBox="0 0 1080 1920">{"".join(core)}</svg></div>')


ICONS = {
    "qr": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="14" height="14" rx="3"/><rect x="28" y="6" width="14" height="14" rx="3"/><rect x="6" y="28" width="14" height="14" rx="3"/><path d="M28 28h6v6M42 28v14H34M28 40v2"/></svg>',
    "card": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="38" height="26" rx="5"/><path d="M5 19h38M12 30h8"/></svg>',
    "cal": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="9" width="34" height="32" rx="5"/><path d="M7 18h34M16 5v8M32 5v8M17 29l5 5 9-10"/></svg>',
    "zero": '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><circle cx="24" cy="24" r="17"/><path d="M14 34L34 14"/></svg>',
}


def build(r):
    c = r["colors"]; f = r["fonts"]
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

    hero = c["primary"] if lum(c["primary"]) < 0.45 else c["accent"]
    acc = lift(c["accent"], 0.5)
    pri = lift(c["primary"], 0.38)

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        start = 0 if s == 0 else round(s + B, 3)
        end = TOTAL if e == 64 else round(e + B, 3)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{start}" data-duration="{round(end - start, 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    name_lines = "".join(f'<div class="mask"><div class="nl">{ln}</div></div>' for ln in r["nameLines"])
    found = "".join(f'<div class="found">{u}</div>' for u in r["found"])
    dishes = "".join(f'<div class="dish"><span>{d}</span><em>Ver</em></div>' for d in r["dishes"])
    house = ('<svg class="house" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="5" stroke-linejoin="round" '
             'stroke-linecap="round"><path d="M9 29 L32 10 L55 29 V54 H9 Z"/><path d="M26 54 V40 H38 V54"/></svg>')
    cards = [("qr", "Menú vivo con QR", "Cambias precios y platos desde el celular."),
             ("card", "Pedidos pagados en línea", "Con tarjeta, directo a tu cuenta."),
             ("cal", "Reservas por WhatsApp", "Confirmadas al instante."),
             ("zero", "0% de comisión", "Nuestra, por cada pedido.")]
    bento = "".join(f'<div class="card" id="card{i}"><div class="ic">{ICONS[k]}</div><div class="ct">{t}</div><div class="cs">{s}</div></div>'
                    for i, (k, t, s) in enumerate(cards))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          <div class="glow g1"></div><div class="glow g2"></div>
          {ribbons("ri", [acc, "#5AC8FA", "#BF5AF2", pri, "#FF375F", "#FF9F0A"])}<div class="flash" id="iflash"></div>
          <div class="stack center">
            <div class="cd" id="icd">{house}<span>Casa Digital</span></div>
            <div class="eyebrow" id="ipres">{words("presenta una idea para")}</div>
            <div class="disp intro-name" id="iname">{r["name"]}</div>
          </div>'''),
        scene("hero", f'''
          <div class="hero-bg"></div><div class="glow g3"></div><div class="flash" id="hflash"></div>
          <div class="hero">
            <div class="eyebrow light" id="hkick">{r["kind"]}</div>
            <div class="disp hero-name">{name_lines}</div>
            <div class="serif-i tag" id="htag">{words(r["tagline"])}</div>
            <div class="where" id="hwhere">{r["city"]} · {r["zone"]}</div>
          </div>'''),
        scene("stat", f'''
          <div class="glow g4"></div>
          <div class="stack center">
            <div class="stars" id="sstars">{''.join('<span>★</span>' for _ in range(5))}</div>
            <div class="num grad" id="snum">0.0</div>
            <div class="h3" id="ssub">{words(r["reviews"] + " reseñas en Google.")}</div>
            <div class="serif-i love" id="slove">{words("La gente ya te ama.")}</div>
          </div>'''),
        scene("problem", f'''
          <div class="stack center">
            <div class="h2 dark" id="p1">{words("Pero cuando te buscan,")}</div>
            <div class="h2 dark mute" id="p2">{words("encuentran directorios.")}</div>
            <div class="founds" id="pf">{found}</div>
            <div class="disp-x" id="p3">No tu casa.</div>
          </div>''', "light"),
        scene("phone", f'''
          <div class="glow g5"></div>
          <div class="cap"><div class="eyebrow" id="pc0">Presentamos</div>
            <div class="capswap"><div class="h2" id="pc1">tu casa digital.</div><div class="h2" id="pc2">Un menú que cambias desde tu celular.</div></div></div>
          <div class="stage"><div class="phone" id="ph">
            <div class="ph-glass"><div class="ph-screen">
              <div class="ph-island"></div>
              <div class="ph-scroll" id="phs">
                <div class="site">
                  <div class="site-nav"><b>{r["name"]}</b><span>Menú&nbsp;&nbsp;Reservas</span></div>
                  <div class="site-name">{"<br>".join(r["nameLines"])}</div>
                  <div class="site-tag">{r["tagline"]}</div>
                  <div class="site-btns"><span class="b1">Pedir ahora</span><span class="b2">Reservar</span></div>
                </div>
                <div class="menu"><div class="menu-h">Menú</div>{dishes}<div class="today">Hoy · especial del día</div></div>
              </div>
              <div class="sheen" id="sheen"></div>
            </div></div>
          </div></div>'''),
        scene("calm", f'''
          <div class="stack center">
            <div class="h1" id="c1">{words("Hecha a mano.")}</div>
            <div class="h1 grad2" id="c2">{words("Solo para " + r["name"] + ".")}</div>
          </div>'''),
        scene("bento", f'''
          <div class="glow g6"></div>
          <div class="bento-wrap">
            <div class="h2" id="bt">{words("Todo en un solo lugar.")}</div>
            <div class="bento">{bento}</div>
          </div>'''),
        scene("offer", f'''
          <div class="stack center">
            <div class="h3 mute" id="o1">Lista en</div>
            <div class="num2 grad" id="o2">14 días.</div>
            <div class="h3" id="o3">{words("Precio de fundador para los primeros 5 restaurantes.")}</div>
          </div>'''),
        scene("cta", f'''
          <div class="glow g7"></div>
          <div class="stack center">
            <div class="cd big" id="ccd">{house}<span>Casa Digital</span></div>
            <div class="h1" id="ch">{words("Hablemos.")}</div>
            <div class="wa" id="cwa"><div class="wa-k">WhatsApp</div><div class="wa-n">{WHATSAPP}</div></div>
          </div>'''),
        scene("end", f'''
          <div class="endglow" id="eglow"></div>
          {ribbons("re", ["#3E7BFA", "#8E7CFF", "#5AC8FA", "#FFFFFF", "#BF5AF2", "#64D2FF"])}
          <div class="stack center">
            <div class="mark-wrap" id="mwrap">
              <svg class="mark" viewBox="{MARK["viewBox"]}">
                <defs>
                  <linearGradient id="sweepg" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
                  </linearGradient>
                  <clipPath id="mclip">{mark_paths}</clipPath>
                </defs>
                <g id="mstroke" fill="none" stroke="#fff" stroke-width="1.6" stroke-linejoin="round">{mark_paths}</g>
                <g id="mfill" fill="url(#markfill)">{mark_paths}</g>
                <g clip-path="url(#mclip)"><rect id="msweep" x="-200" y="0" width="160" height="600" fill="url(#sweepg)" transform="rotate(20)"/></g>
                <linearGradient id="markfill" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#C9D6FF"/><stop offset=".55" stop-color="#FFFFFF"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
              </svg>
            </div>
            <div class="lockup" id="lock"><span class="by" id="lby">by</span> <span class="ct" id="lct">{"".join(f'<span class="lt">{ch if ch != " " else "&nbsp;"}</span>' for ch in "Clientia Tech")}</span></div>
          </div>'''),
    ])

    css = Template(CSS).substitute(
        primary=pri, accent=acc, hero=hero, deep=c["deep"], bgc=c["bg"],
        glowA=rgba(hero, .55), glowB=rgba(acc, .30), glowC=rgba(hero, .35),
        heroA=hero, heroB="rgb(%d,%d,%d)" % tuple(int(v*.22) for v in hexrgb(hero)),
        dweight=f["displayWeight"], dcase=f.get("displayCase", "none"), dtrack=f["displayTracking"],
        ital='"DisplayI"' if f.get("italicFile") else '"Display"',
        italface=('@font-face{font-family:"DisplayI";src:url("assets/fonts/display-italic.woff2") format("woff2");font-style:italic;}'
                  if f.get("italicFile") else ""),
        herosize=r.get("heroSize2", 210), introsize=r.get("introSize2", 120),
        sitebg=c["bg"], siteink=c["ink"],
    )
    js = Template(JS).substitute(rating=r["rating"], nchars=len(r["name"]))
    html = HTML.replace("$title", f"Casa Digital x {r['name']}").replace("$css", css).replace("$body", body) \
        .replace("$js", js).replace("$total", str(TOTAL))
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


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
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="$total" data-fade-out="2.5" data-track-index="1"></audio>
$body
<div class="vig clip" data-start="0" data-duration="$total" data-track-index="2"></div>
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
html,body{width:1080px;height:1920px;overflow:hidden;background:#000;}
#root{position:relative;width:1080px;height:1920px;background:#000;color:#F5F5F7;font-family:"IT",sans-serif;-webkit-font-smoothing:antialiased;}
.scene{position:absolute;inset:0;overflow:hidden;background:#000;}
.scene.light{background:#F5F5F7;color:#1D1D1F;}
.cam{position:absolute;inset:0;transform-origin:50% 50%;}
.stack{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 100px;}
.w{display:inline-block;}
.glow{position:absolute;border-radius:50%;pointer-events:none;}
.g1{width:1400px;height:1400px;left:-160px;top:260px;background:radial-gradient(closest-side,$glowA,rgba(0,0,0,0));}
.g2{width:1100px;height:1100px;left:300px;top:900px;background:radial-gradient(closest-side,$glowB,rgba(0,0,0,0));}
.g3{width:1500px;height:1500px;left:-500px;top:-300px;background:radial-gradient(closest-side,rgba(255,255,255,.12),rgba(0,0,0,0));}
.g4{width:1600px;height:1600px;left:-260px;top:160px;background:radial-gradient(closest-side,$glowC,rgba(0,0,0,0));}
.g5{width:1700px;height:1700px;left:-310px;top:520px;background:radial-gradient(closest-side,$glowA,rgba(0,0,0,0));}
.g6{width:1500px;height:1500px;left:-210px;top:700px;background:radial-gradient(closest-side,$glowC,rgba(0,0,0,0));}
.g7{width:1500px;height:1500px;left:-210px;top:300px;background:radial-gradient(closest-side,$glowB,rgba(0,0,0,0));}
.disp{font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;}
.serif-i{font-family:$ital;font-style:italic;}
.cd{display:flex;align-items:center;gap:20px;font-weight:600;font-size:44px;letter-spacing:-.01em;}
.cd .house{width:54px;height:54px;}
.cd.big{font-size:56px;gap:24px;margin-bottom:90px;}
.cd.big .house{width:72px;height:72px;}
.eyebrow{font-size:38px;font-weight:500;color:#86868B;letter-spacing:.01em;}
.eyebrow.light{color:rgba(255,255,255,.75);}
#ipres{margin-top:90px;}
.intro-name{margin-top:36px;font-size:${introsize}px;line-height:1.02;color:#F5F5F7;}
.hero-bg{position:absolute;inset:0;background:radial-gradient(120% 80% at 30% 20%,$heroA 0%,$heroB 55%,#000 100%);}
.hero{position:absolute;left:100px;right:90px;top:420px;color:#fff;}
.hero-name{margin-top:44px;font-size:${herosize}px;line-height:.95;}
.mask{overflow:hidden;padding:0 0 .08em;}
.nl{display:block;}
.tag{margin-top:70px;font-size:66px;line-height:1.18;max-width:860px;}
.where{margin-top:56px;font-size:34px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.7);}
.stars{font-size:64px;letter-spacing:.18em;color:$accent;}
.stars span{display:inline-block;}
.num{font-weight:600;font-size:400px;line-height:1;letter-spacing:-.05em;margin-top:20px;font-variant-numeric:tabular-nums;}
.grad{background:linear-gradient(180deg,#FFFFFF 10%,$accent 140%);-webkit-background-clip:text;background-clip:text;color:transparent;}
.grad2 .w{background:linear-gradient(90deg,$primary,$accent);-webkit-background-clip:text;background-clip:text;color:transparent;padding-bottom:.1em;}
.h1{font-weight:600;font-size:120px;line-height:1.04;letter-spacing:-.035em;}
.h2{font-weight:600;font-size:84px;line-height:1.08;letter-spacing:-.03em;}
.h3{font-weight:500;font-size:52px;line-height:1.25;letter-spacing:-.015em;margin-top:40px;color:#F5F5F7;}
.mute{color:#86868B !important;}
.dark{color:#1D1D1F;}
.love{margin-top:110px;font-size:84px;color:$accent;}
#p2{margin-top:10px;}
.founds{margin-top:90px;display:flex;flex-direction:column;gap:22px;align-items:center;}
.found{font-size:40px;font-weight:500;color:#6E6E73;background:#fff;border-radius:999px;padding:24px 50px;box-shadow:0 20px 50px rgba(0,0,0,.08);}
.disp-x{margin-top:120px;font-weight:700;font-size:150px;letter-spacing:-.045em;color:#1D1D1F;}
.cap{position:absolute;left:0;right:0;top:170px;text-align:center;padding:0 90px;}
.capswap{position:relative;height:200px;margin-top:20px;}
.capswap .h2{position:absolute;left:0;right:0;top:0;}
.stage{position:absolute;left:0;right:0;top:470px;height:1500px;perspective:2600px;}
.phone{position:absolute;left:220px;top:40px;width:640px;height:1300px;transform-style:preserve-3d;}
.ph-glass{position:absolute;inset:0;border-radius:110px;padding:20px;background:linear-gradient(145deg,#3A3A3C,#0C0C0D 40%,#1C1C1E 70%,#48484A);box-shadow:0 80px 160px rgba(0,0,0,.6),inset 0 0 0 2px rgba(255,255,255,.12);}
.ph-screen{position:relative;width:100%;height:100%;border-radius:92px;overflow:hidden;background:$sitebg;color:$siteink;}
.ph-island{position:absolute;top:24px;left:50%;width:190px;height:54px;margin-left:-95px;border-radius:30px;background:#000;z-index:3;}
.ph-scroll{position:absolute;left:0;right:0;top:0;}
.site{height:1260px;padding:120px 52px 60px;background:radial-gradient(120% 70% at 30% 10%,$heroA,$heroB);color:#fff;position:relative;}
.site-nav{display:flex;justify-content:space-between;align-items:center;font-size:24px;opacity:.9;}
.site-nav b{font-family:"Display";font-weight:$dweight;text-transform:$dcase;font-size:30px;}
.site-name{margin-top:260px;font-family:"Display";font-weight:$dweight;text-transform:$dcase;letter-spacing:$dtrack;font-size:110px;line-height:.98;}
.site-tag{margin-top:36px;font-family:$ital;font-style:italic;font-size:38px;line-height:1.2;opacity:.92;}
.site-btns{position:absolute;left:52px;right:52px;bottom:90px;display:flex;gap:18px;}
.site-btns span{flex:1;text-align:center;padding:28px 0;border-radius:60px;font-weight:600;font-size:30px;}
.b1{background:#fff;color:#000;}
.b2{background:rgba(255,255,255,.16);border:1.5px solid rgba(255,255,255,.4);}
.menu{padding:120px 52px 60px;background:$sitebg;color:$siteink;}
.menu-h{font-family:"Display";font-weight:$dweight;text-transform:$dcase;font-size:84px;margin-bottom:24px;}
.dish{display:flex;justify-content:space-between;align-items:baseline;font-size:36px;font-weight:500;padding:30px 0;border-bottom:1.5px solid rgba(127,127,127,.25);}
.dish em{font-style:normal;font-size:24px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:$hero;}
.today{margin-top:44px;display:inline-block;padding:16px 30px;border-radius:40px;background:$hero;color:#fff;font-weight:600;font-size:26px;}
.sheen{position:absolute;top:-20%;left:-60%;width:40%;height:140%;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.28),rgba(255,255,255,0));transform:rotate(18deg);z-index:4;}
.bento-wrap{position:absolute;left:80px;right:80px;top:300px;}
.bento-wrap .h2{text-align:center;margin-bottom:80px;}
.bento{display:grid;grid-template-columns:1fr 1fr;gap:32px;}
.card{height:520px;border-radius:56px;padding:56px 48px;background:linear-gradient(160deg,rgba(255,255,255,.12),rgba(255,255,255,.04));box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.14);display:flex;flex-direction:column;}
.ic{width:96px;height:96px;color:$accent;}
.ic svg{width:100%;height:100%;}
.ct{margin-top:auto;font-size:54px;font-weight:600;line-height:1.08;letter-spacing:-.025em;}
.cs{margin-top:20px;font-size:32px;line-height:1.3;color:#A1A1A6;}
.num2{font-weight:600;font-size:250px;line-height:1;letter-spacing:-.05em;margin-top:10px;}
#o1{margin:0;}
#o3{margin-top:90px;max-width:820px;}
.wa{margin-top:80px;padding:44px 80px;border-radius:999px;background:linear-gradient(160deg,rgba(255,255,255,.16),rgba(255,255,255,.05));box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.18);}
.wa-k{font-size:34px;font-weight:500;color:#30D158;}
.wa-n{margin-top:8px;font-size:76px;font-weight:600;letter-spacing:-.02em;}
#end{background:#000;}
.endglow{position:absolute;width:1300px;height:1300px;left:-110px;top:180px;border-radius:50%;background:radial-gradient(closest-side,rgba(90,130,255,.30),rgba(0,0,0,0));}
.mark-wrap{width:430px;height:500px;}
.mark{width:100%;height:100%;overflow:visible;}
.lockup{margin-top:90px;font-size:76px;letter-spacing:-.025em;white-space:nowrap;}
.by{font-weight:300;color:#86868B;display:inline-block;}
.ct{font-weight:600;color:#F5F5F7;}
.lt{display:inline-block;}
.rib{position:absolute;inset:0;mix-blend-mode:screen;transform-origin:50% 50%;}
.rl{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible;}
.glowl{filter:blur(42px);opacity:.9;}
.corel{filter:blur(1.5px);}
.flash{position:absolute;inset:-200px;background:radial-gradient(closest-side,rgba(255,255,255,.85),rgba(255,255,255,0));opacity:0;pointer-events:none;}
.vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(130% 90% at 50% 50%,rgba(0,0,0,0) 55%,rgba(0,0,0,.55) 100%);z-index:50;}
'''

JS = r'''
const tl = gsap.timeline({ paused: true });
const B = 0.017, at = s => s + B;
const SOFT = "expo.out", INOUT = "power2.inOut";
// Apple-keynote text reveal: rise, blur to sharp, fade in. Slow and readable.
function rise(sel, t, o) {
  o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y || 60, filter: "blur(" + (o.blur || 18) + "px)" },
    { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d || 1.4, ease: SOFT, stagger: o.st || 0.09 }, t);
}
function fadeOut(sel, t, d) { tl.to(sel, { opacity: 0, filter: "blur(14px)", duration: d || .8, ease: "power2.in" }, t); }
// slow camera push in every scene, the AE "never static" feel
[["intro",0,8],["hero",8,16],["stat",16,22],["problem",22,28],["phone",28,36],["calm",36,40],["bento",40,48],["offer",48,52],["cta",52,56],["end",56,64]]
  .forEach(([id, s, e]) => tl.fromTo("#cam-" + id, { scale: 1.0 }, { scale: 1.045, duration: e - s, ease: "none" }, s === 0 ? 0 : at(s)));
// drifting light
tl.fromTo(".g1", { x: -120, y: 80, opacity: 0 }, { x: 80, y: -60, opacity: 1, duration: 8, ease: "sine.inOut" }, 0);
tl.fromTo(".g2", { x: 120, y: 0, opacity: 0 }, { x: -60, y: -120, opacity: 1, duration: 8, ease: "sine.inOut" }, 0);
tl.fromTo(".g3", { x: 0, y: 0 }, { x: 240, y: 200, duration: 8, ease: "sine.inOut" }, at(8));
tl.fromTo(".g4", { x: -100, scale: .9 }, { x: 100, scale: 1.05, duration: 6, ease: "sine.inOut" }, at(16));
tl.fromTo(".g5", { y: 200, opacity: 0 }, { y: -80, opacity: 1, duration: 8, ease: "sine.out" }, at(28));
tl.fromTo(".g6", { x: -150 }, { x: 150, duration: 8, ease: "sine.inOut" }, at(40));
tl.fromTo(".g7", { scale: .8, opacity: 0 }, { scale: 1.05, opacity: 1, duration: 4, ease: "sine.out" }, at(52));

// 1 · intro (quiet build)
rise("#icd", 1.4, { d: 2.2, blur: 24 });
rise("#ipres .w", at(4), { d: 1.6, st: .14 });
tl.fromTo("#iname", { opacity: 0, scale: 1.12, filter: "blur(30px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.6, ease: SOFT }, 5.5);
tl.to("#icd, #ipres", { opacity: .35, duration: 1.5, ease: INOUT }, at(5.5));

// 2 · hero (drop)
tl.fromTo(".hero-bg", { opacity: 0, scale: 1.25 }, { opacity: 1, scale: 1, duration: 2.4, ease: SOFT }, at(8));
rise("#hkick", at(8), { d: 1.2 });
tl.fromTo(".nl", { yPercent: 105 }, { yPercent: 0, duration: 1.3, ease: "expo.out", stagger: .2 }, at(8));
rise("#htag .w", at(10), { st: .08 });
rise("#hwhere", at(12), { d: 1.2 });

// 3 · rating
rise("#sstars span", at(16), { st: .1, d: 1 });
const ctr = { v: 0 }, numEl = document.getElementById("snum");
tl.fromTo("#snum", { opacity: 0, filter: "blur(24px)", scale: .92 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: 1.4, ease: SOFT }, at(16));
tl.fromTo(ctr, { v: 0 }, { v: $rating, duration: 1.8, ease: "power3.out", onUpdate: () => { numEl.textContent = ctr.v.toFixed(1); } }, at(16));
rise("#ssub .w", at(18), { st: .07 });
rise("#slove .w", at(20), { st: .12, d: 1.6 });

// 4 · problem (light section)
rise("#p1 .w", at(22), { st: .08 });
rise("#p2 .w", at(23), { st: .08 });
rise("#pf .found", at(24), { st: .2, d: 1.1 });
tl.to("#pf .found", { opacity: .35, duration: 1, ease: INOUT }, at(25.5));
tl.fromTo("#p3", { opacity: 0, scale: .9, filter: "blur(20px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 1.4, ease: SOFT }, at(26));

// 5 · phone reveal, 3D, with slow turn
rise("#pc0", at(28), { d: 1.2 });
rise("#pc1", at(28.5), { d: 1.3 });
tl.fromTo("#ph", { y: 900, rotationX: 28, rotationY: -22, rotationZ: 4 }, { y: 0, rotationX: 6, rotationY: -12, rotationZ: 0, duration: 2.6, ease: "expo.out" }, at(28));
tl.to("#ph", { rotationX: 2, rotationY: 12, duration: 5.4, ease: "sine.inOut" }, at(30.6));
tl.fromTo("#sheen", { x: 0 }, { x: 1300, duration: 1.8, ease: "power2.inOut" }, at(30));
fadeOut("#pc1", at(32) - .6, .6);
rise("#pc2", at(32), { d: 1.3 });
tl.fromTo("#phs", { y: 0 }, { y: -1260, duration: 1.6, ease: "power3.inOut" }, at(32));
rise(".dish", at(32) + .9, { st: .12, d: 1, y: 30, blur: 8 });
tl.fromTo("#sheen", { x: 0 }, { x: 1300, duration: 1.8, ease: "power2.inOut" }, at(34));

// 6 · calm (music break)
rise("#c1 .w", at(36), { d: 1.8, st: .15 });
rise("#c2 .w", at(37), { d: 1.8, st: .15 });

// 7 · bento, one card per bar
rise("#bt .w", at(40), { st: .08 });
[40, 42, 44, 46].forEach((s, i) => {
  tl.fromTo("#card" + i, { opacity: 0, y: 80, scale: .94, filter: "blur(16px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 1.3, ease: SOFT }, at(s) + (i === 0 ? .4 : 0));
});

// 8 · offer
rise("#o1", at(48), { d: 1.2 });
tl.fromTo("#o2", { opacity: 0, scale: 1.15, filter: "blur(26px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 1.6, ease: SOFT }, at(48.5));
rise("#o3 .w", at(50) - .9, { st: .05 });

// 9 · CTA
rise("#ccd", at(52), { d: 1.4 });
rise("#ch .w", at(52.5), { d: 1.4 });
tl.fromTo("#cwa", { opacity: 0, y: 80, scale: .95, filter: "blur(14px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 1.4, ease: SOFT }, at(54));

// 10 · Clientia Tech: outline draws on in the silence, locks on the drop
const strokes = document.querySelectorAll("#mstroke path");
strokes.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
tl.to("#mstroke path", { strokeDashoffset: 0, duration: 1.9, ease: "power2.inOut" }, at(56) + .05);
tl.fromTo("#mfill", { opacity: 0 }, { opacity: 1, duration: .5, ease: "power2.out" }, at(58));
tl.to("#mstroke", { opacity: 0, duration: .5 }, at(58));
tl.fromTo("#mwrap", { scale: .92 }, { scale: 1, duration: 2.2, ease: SOFT }, at(56));
tl.fromTo("#mwrap", { filter: "drop-shadow(0 0 0px rgba(140,170,255,0))" }, { filter: "drop-shadow(0 0 60px rgba(140,170,255,.65))", duration: .35, ease: "power2.out", yoyo: true, repeat: 1 }, at(58));
tl.fromTo("#eglow", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: 1.6, ease: SOFT }, at(58));
tl.fromTo("#msweep", { x: -200 }, { x: 900, duration: 1.4, ease: "power2.inOut" }, at(58.5));
rise("#lby", at(58.5), { d: 1.2 });
rise(".lt", at(58.5) + .2, { d: 1.2, st: .035, y: 40, blur: 12 });
tl.to("#end .stack, #eglow", { opacity: 0, duration: 1.4, ease: "power2.in" }, 62.4);

// light trails (Apple TV style): comets travel each curve, the rig swirls like a camera orbit
function trails(rid, t0, dur, spin) {
  for (let i = 0; i < 6; i++) {
    const st = t0 + i * 0.22, len = 480 + (i % 3) * 170;
    tl.fromTo("." + rid + "-p" + i, { strokeDasharray: len + " 2000", strokeDashoffset: len }, { strokeDashoffset: -1000, duration: dur - i * 0.15, ease: "power2.inOut" }, st);
  }
  tl.fromTo("#" + rid, { rotation: spin[0], scale: spin[2], opacity: 0 }, { rotation: spin[1], scale: spin[3], opacity: 1, duration: dur, ease: "power1.inOut" }, t0);
}
trails("ri", 0.1, 3.7, [-24, 6, 1.5, 1.0]);
trails("ri", 3.6, 2.1, [6, 70, 1.4, 0.22]);
tl.fromTo("#iflash", { opacity: 0, scale: 0.2 }, { opacity: 0.7, scale: 0.9, duration: 0.35, ease: "power2.out" }, 5.45);
tl.to("#iflash", { opacity: 0, scale: 1.5, duration: 1.4, ease: "expo.out" }, 5.8);
tl.to("#ri", { opacity: 0, duration: 0.3 }, 5.55);
tl.fromTo("#hflash", { opacity: 0.55, scale: 0.4 }, { opacity: 0, scale: 1.6, duration: 0.7, ease: "expo.out" }, at(8));
trails("re", at(56) - 0.4, 2.6, [20, -8, 1.6, 0.9]);
tl.to("#re", { scale: 3.2, opacity: 0, duration: 1.1, ease: "expo.out" }, at(58));

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
