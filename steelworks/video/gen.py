#!/usr/bin/env python3
"""Steel Works · video de propuesta (HyperFrames, 1920x1080).

Cuenta la página nueva con su mismo lenguaje: el lema de la empresa, «Todo… en hierro», con
fotos de sus trabajos reales pasando entre las dos palabras; luego cómo cotiza el cliente por
WhatsApp, un verbo por paso (Mide, Elige, Cotiza, Agenda, Forja); la tabla de precios que
cambia con la medida; las piezas por su nombre, sin códigos. Fondo de taller, texto que sale
al rojo vivo y se enfría a acero, chispas en cada golpe. Cierra con el outro de Clientia Tech.

Música: "Still Buggin" (194 BPM). Un compás de 8 tiempos = 2.474 s; toda escena empieza en
una línea de compás K(n). Requisitos junto al script: musica.mp3, capturas/*.jpg, ../fotos y
deps/node_modules con gsap@3.14.2 y @fontsource/{big-shoulders-display,archivo,inter-tight}.

    python3 gen.py && cd build && hyperframes render . -o ../steelworks-propuesta.mp4 -q high
"""
import json, math, os, random, shutil
from outro import ribbons

HERE = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(HERE, "..", "fotos")
DEPS = os.environ.get("DEPS", os.path.join(HERE, "deps", "node_modules"))
OUT = os.path.join(HERE, "build")
WHATSAPP = "+1 (765) 543-4251"
MARK = json.load(open(os.path.join(HERE, "clientia-mark.json")))
P0, BAR = 0.0012, 8 * 0.3092783
K = lambda k: round(P0 + BAR * k, 3)
SCENES = [("intro", 0, 3), ("hook", 3, 6), ("lema", 6, 10), ("verbs", 10, 20), ("price", 20, 24),
          ("pieces", 24, 27), ("site", 27, 30), ("offer", 30, 32), ("cta", 32, 34), ("end", 34, 37)]
TOTAL = K(37)

# the same rates the bot and the page use (bot/engine.js TARIFAS, portón, por m²)
TARIFAS = [("Moderno", 3200, 4200), ("Forjado clásico", 4200, 5800), ("Calado CNC", 5200, 7200)]
REEL = [("obra-puerta-cnc", "50% 38%"), ("obra-cerco", "50% 62%"), ("obra-ventana", "50% 50%"), ("obra-puerta-arco", "50% 55%")]
VERBS = [  # verb, photo, what it means, chat (side, html)
    ("Mide.", "obra-ventana", "El cliente escribe con sus palabras.",
     [("out", "cuánto me sale un portón de 4 por 2.5"), ("in", "Perfecto: portón, 4 × 2.5 m.<br>¿Lo quieres con motor eléctrico?")]),
    ("Elige.", "obra-puerta-cnc", "Escoge el estilo viendo trabajos reales.",
     [("in", "¿Qué estilo te gusta? Estos son trabajos nuestros:"
             '<div class="gal"><figure><img src="assets/obra-puerta-arco.jpg"><b>Moderno</b></figure>'
             '<figure><img src="assets/obra-cerco.jpg"><b>Forjado</b></figure>'
             '<figure><img src="assets/obra-puerta-cnc.jpg"><b>Calado CNC</b></figure></div>'), ("out", "Forjado clásico")]),
    ("Cotiza.", "obra-puerta-arco", "Recibe un precio inicial al momento.",
     [("in", "Precio estimado: <b>L 42,000 a L 58,000</b><br>Incluye fabricación, pintura e instalación.<br>El precio final lo confirma el taller al medir.")]),
    ("Agenda.", "obra-cerco", "Deja la visita para medir agendada.",
     [("out", "Agendar visita para medir"), ("in", "Listo, Carlos. Visita para medir: jueves, de 8 a 10 a. m.<br>Tu ficha ya la tiene la sucursal.")]),
    ("Forja.", None, "Y el taller recibe la ficha completa.", []),
]
PIECES = [("Remates de poste", "p-110-702"), ("esferas", "p-110-721"), ("adornos de barra", "p-120-1016"),
          ("barras con volutas", "cat-barras-forjadas"), ("bases de poste", "cat-adorno-barra"), ("cruces caladas", "cat-cnc-cruz"),
          ("volutas y flores", "panel-volutas"), ("llamadores", "cat-llamadores"), ("jaladores", "p-222-2650")]
OFFER = [("Asistente de WhatsApp", "Cotiza a cualquier hora: medidas, estilo con fotos, precio inicial y cita."),
         ("Página nueva", "Su lema, sus trabajos y una tabla de precios que cambia con la medida."),
         ("Ficha a la sucursal", "Cada cliente llega con lo que pidió, su medida y su cita."),
         ("Reporte semanal", "Cuántos cotizaron, cuántas visitas y cuántas ventas.")]


def words(text, cls="w"):
    return " ".join(f'<span class="{cls}">{w}</span>' for w in text.split())


def L0(n):
    return "L " + f"{round(n / 100) * 100:,}"


def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    A = os.path.join(OUT, "assets")
    os.makedirs(os.path.join(A, "fonts"))
    shutil.copy(os.path.join(HERE, "musica.mp3"), os.path.join(A, "musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), os.path.join(A, "gsap.min.js"))
    fs = os.path.join(DEPS, "@fontsource")
    for src, dst in [("big-shoulders-display/files/big-shoulders-display-latin-800-normal.woff2", "bsd-800"),
                     ("big-shoulders-display/files/big-shoulders-display-latin-600-normal.woff2", "bsd-600")] + \
            [(f"archivo/files/archivo-latin-{w}-normal.woff2", f"ar-{w}") for w in (400, 500, 700)] + \
            [(f"inter-tight/files/inter-tight-latin-{w}-normal.woff2", f"it-{w}") for w in (300, 600)]:
        shutil.copy(os.path.join(fs, src), os.path.join(A, "fonts", dst + ".woff2"))
    for f in os.listdir(os.path.join(HERE, "capturas")):
        shutil.copy(os.path.join(HERE, "capturas", f), os.path.join(A, f))
    for f in os.listdir(FOTOS):  # Steel Works' own photos, and their pieces cut out
        if f.endswith(".jpg"):
            shutil.copy(os.path.join(FOTOS, f), os.path.join(A, f))
    for f in os.listdir(os.path.join(FOTOS, "recortes")):
        shutil.copy(os.path.join(FOTOS, "recortes", f), os.path.join(A, "r-" + f))
    shutil.copy(os.path.join(HERE, "..", "logo", "simbolo", "steelworks-logo-simbolo-naranja.svg"), os.path.join(A, "simbolo.svg"))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(OUT, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "steelworks-propuesta", "name": "Casa Digital x Steel Works"}, open(os.path.join(OUT, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    # hand-forged C-scroll for the intro (same geometry as the logo)
    def spiral(cx, cy, r, turns, end, s):
        return [(cx + r * (0.1 + 0.9 * t) * math.cos(end + s * (1 - t) * turns * 2 * math.pi),
                 cy + r * (0.1 + 0.9 * t) * math.sin(end + s * (1 - t) * turns * 2 * math.pi)) for t in [i / 80 for i in range(81)]]
    def cscroll(x, y, h, side, turns=1.2):
        r = h * .27; cx = x + side * r
        top = spiral(cx, y + r, r, turns, math.pi if side > 0 else 0, 1 if side > 0 else -1)
        bot = list(reversed(spiral(cx, y + h - r, r, turns, math.pi if side > 0 else 0, -1 if side > 0 else 1)))
        return "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in top + bot)
    scroll_paths = "".join(f'<path class="fp" d="{cscroll(300 + sd * 8, 40, 520, sd)}"/>' for sd in (-1, 1)) + '<path class="fp" d="M300 600 L300 0"/>'

    reel = "".join(f'<div class="frame"><img src="assets/{f}.jpg" style="object-position:{pos}"></div>' for f, pos in REEL)

    verbs = []
    for i, (v, foto, say, chat) in enumerate(VERBS):
        pic = (f'<div class="vpic" id="vp{i}"><img src="assets/{foto}.jpg"></div>' if foto else
               '<div class="vtrio" id="vp4">' + "".join(f'<img src="assets/r-{p}.png">' for p in ("p-110-702", "p-120-1016", "p-110-721")) + '</div>')
        bubs = "".join(f'<div class="bub {side}" id="vb{i}{j}">{html}<time>9:41</time></div>' for j, (side, html) in enumerate(chat))
        verbs.append(f'''<div class="vgroup{' light' if not foto else ''}" id="vg{i}">
            <div class="vword" id="vw{i}">{v}</div>
            <div class="vsay" id="vs{i}">{say}</div>
            {pic}<div class="vchat">{bubs}</div></div>''')

    rows = "".join(f'<div class="prow" id="pr{i}"><span class="pk">Portón</span><span class="ps">{n}</span>'
                   f'<span class="pv" id="pv{i}">{L0(lo * 6.6)} a {L0(hi * 6.6)}</span></div>' for i, (n, lo, hi) in enumerate(TARIFAS))

    pieces = "".join(f'<span class="pn" id="pn{i}">{n}<i class="fr"><img src="assets/r-{f}.png"></i>{"," if i < len(PIECES) - 1 else "…"}</span> '
                     for i, (n, f) in enumerate(PIECES))

    offer_html = "".join(f'<div class="of" id="of{i}"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(OFFER))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    # sparks: deterministic bursts (seeded) + ambient embers
    rnd = random.Random(7)
    BURSTS = [("b0", K(2) + .05, 960, 700, 34), ("b1", K(3), 960, 560, 26), ("b2", K(6), 960, 540, 26),
              ("b3", K(10), 420, 560, 22), ("b4", K(18), 420, 560, 26), ("b5", K(20), 960, 900, 22),
              ("b6", K(24), 960, 980, 22), ("b7", K(32), 960, 640, 30)]
    sparks, spark_js = [], []
    for bid, t, x, y, n in BURSTS:
        for j in range(n):
            ang = rnd.uniform(-math.pi * .95, -math.pi * .05)
            v = rnd.uniform(220, 640)
            dx, dy = math.cos(ang) * v, math.sin(ang) * v
            sz = rnd.choice([3, 3, 4, 5, 6])
            dur = rnd.uniform(.8, 1.6)
            sid = f"{bid}s{j}"
            sparks.append(f'<i class="spk" id="{sid}" style="left:{x}px;top:{y}px;width:{sz}px;height:{sz}px"></i>')
            spark_js.append(f'spark("#{sid}",{t:.3f},{dx:.0f},{dy:.0f},{dur:.2f});')
    embers = []
    for j in range(36):
        x, y = rnd.uniform(0, 1920), rnd.uniform(500, 1180)
        t0 = rnd.uniform(0, TOTAL - 12)
        embers.append((f"em{j}", x, y, t0, rnd.uniform(7, 12), rnd.uniform(-120, 120), rnd.uniform(2, 4)))
    ember_html = "".join(f'<i class="ember" id="{e}" style="left:{x:.0f}px;top:{y:.0f}px;width:{s:.1f}px;height:{s:.1f}px"></i>' for e, x, y, _, _, _, s in embers)
    ember_js = "".join(f'ember("#{e}",{t:.2f},{d:.2f},{dx:.0f});' for e, x, y, t, d, dx, s in embers)

    body = "\n".join([
        scene("intro", f'''
          <div class="heatglow" id="ig"></div>
          <svg class="forge" id="forge" viewBox="0 0 600 600" fill="none" stroke-linecap="round" stroke-linejoin="round">{scroll_paths}</svg>
          <div class="center intro">
            <div class="pre" id="ik">{words("Casa Digital presenta una propuesta para")}</div>
            <div class="mega hot" id="iname">Steel Works</div>
          </div>'''),
        scene("hook", '''
          <div class="center">
            <div class="mega2 hot" id="h1">«¿Cuánto me sale un portón?»</div>
            <div class="line" id="h2">Esa pregunta les llega a cualquier hora.</div>
            <div class="line dim" id="h3">Cada una es un cliente que ya quiere comprar.</div>
          </div>'''),
        scene("lema", f'''
          <div class="half ha" id="la">Todo,</div>
          <div class="reel" id="lreel"><div class="track" id="ltrack">{reel}</div></div>
          <div class="half hb" id="lb">en hierro.</div>
          <div class="lsub" id="lsub">Su propio lema, con sus trabajos reales.</div>'''),
        scene("verbs", "".join(verbs)),
        scene("price", f'''
          <div class="ph2" id="ph">Tu medida, tu precio inicial.</div>
          <div class="size" id="psize"><span class="pl">Ancho</span><b id="pw">3.0</b><span class="px">×</span><span class="pl">Alto</span><b id="phh">2.2</b><span class="pl">metros</span></div>
          <div class="prows">{rows}</div>
          <div class="pnote" id="pnote">Las mismas tarifas en la página y en WhatsApp. El precio final se confirma al medir.</div>'''),
        scene("pieces", f'''
          <div class="pieces" id="pcs"><span class="pn lead" id="pnl">Piezas sueltas:</span> {pieces}</div>
          <div class="pnote2" id="pn2">Sin códigos. El herrero pide por el nombre o con una foto.</div>''', "light"),
        scene("site", '''
          <div class="browser" id="br"><div class="bbar"><i></i><i></i><i></i><span>steelworkshn.com</span></div>
            <div class="bview"><img id="sh0" src="assets/web-hero.jpg"><img id="sh1" src="assets/web-verbos.jpg"><img id="sh2" src="assets/web-precios.jpg"><img id="sh3" src="assets/web-piezas.jpg"></div></div>
          <div class="iph" id="sph"><div class="iph-scr"><img src="assets/movil-chat.jpg"></div></div>
          <div class="scap" id="scap">La página nueva, con el asistente adentro.</div>'''),
        scene("offer", f'''
          <div class="offh" id="offh">Lo que construimos para Steel Works</div>
          <div class="offers">{offer_html}</div>'''),
        scene("cta", f'''
          <div class="heatglow" id="cg"></div>
          <div class="center">
            <div class="line big" id="k1">La demo ya está lista.</div>
            <div class="mega2 hot" id="k2">Se la mostramos en 15 minutos.</div>
            <div class="wa-num" id="k3">WhatsApp {WHATSAPP}</div>
            <div class="sig" id="k4">Rodrigo Herrera · Casa Digital</div>
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
          </div>'''),
    ])
    fx = (f'<div class="fx clip" data-start="0" data-duration="{TOTAL}" data-track-index="2">{ember_html}{"".join(sparks)}'
          f'<div class="flash" id="flash"></div></div>')

    price_js = json.dumps([[lo, hi] for _, lo, hi in TARIFAS])
    js = (JS.replace("$SCENES", json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])).replace("$SPARKS", "\n".join(spark_js))
          .replace("$EMBERS", ember_js).replace("$TOTAL", str(TOTAL)).replace("$PRICES", price_js)
          .replace("$NVERBS", str(len(VERBS))).replace("$NPIECES", str(len(PIECES))))
    html = (HTML.replace("$body", body + "\n" + fx).replace("$css", CSS).replace("$js", js)
            .replace("$total", str(TOTAL)).replace("$title", "Casa Digital x Steel Works"))
    open(os.path.join(OUT, "index.html"), "w").write(html)
    return OUT


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
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="$total" data-fade-out="3" data-track-index="1"></audio>
$body
<div class="vig clip" data-start="0" data-duration="$total" data-track-index="3"></div>
</div>
<script>$js</script>
</body>
</html>
'''

CSS = r'''
@font-face{font-family:"BSD";src:url("assets/fonts/bsd-800.woff2") format("woff2");font-weight:800;}
@font-face{font-family:"BSD";src:url("assets/fonts/bsd-600.woff2") format("woff2");font-weight:600;}
@font-face{font-family:"AR";src:url("assets/fonts/ar-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"AR";src:url("assets/fonts/ar-500.woff2") format("woff2");font-weight:500;}
@font-face{font-family:"AR";src:url("assets/fonts/ar-700.woff2") format("woff2");font-weight:700;}
@font-face{font-family:"IT";src:url("assets/fonts/it-300.woff2") format("woff2");font-weight:300;}
@font-face{font-family:"IT";src:url("assets/fonts/it-600.woff2") format("woff2");font-weight:600;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1920px;height:1080px;overflow:hidden;background:#0B0C0D;}
#root{position:relative;width:1920px;height:1080px;background:#0B0C0D;color:#E8EBED;font-family:"AR",sans-serif;-webkit-font-smoothing:antialiased;}
.scene{position:absolute;inset:0;overflow:hidden;background:#131415;}
.scene.light{background:#E7E5E1;color:#17191B;}
.cam{position:absolute;inset:0;transform-origin:50% 50%;}
.center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 160px;}
.w{display:inline-block;}
.pre{font:500 44px/1.2 "AR";color:#A7AEB4;}
.mega{font:800 230px/.9 "BSD";text-transform:uppercase;}
.mega2{font:800 140px/.95 "BSD";text-transform:uppercase;max-width:1640px;}
.line{margin-top:34px;font:500 60px/1.15 "AR";letter-spacing:-.01em;}
.line.big{font:800 110px/1 "BSD";text-transform:uppercase;margin:0 0 14px;}
.line.dim{color:#A7AEB4;margin-top:16px;}
.hot{color:#E8EBED;}
.heatglow{position:absolute;left:460px;top:240px;width:1000px;height:1000px;border-radius:50%;background:radial-gradient(closest-side,rgba(255,106,19,.30),rgba(255,106,19,0));}
.forge{position:absolute;left:740px;top:60px;width:440px;height:440px;opacity:.9;}
.forge .fp{stroke:#FFC46B;stroke-width:10;}
.intro .pre{position:absolute;left:0;right:0;top:600px;}
.intro .mega{position:absolute;left:0;right:0;top:400px;}
/* lema: Todo, [their work] en hierro. */
.half{position:absolute;top:540px;transform:translateY(-50%);font:800 150px/.9 "BSD";text-transform:uppercase;white-space:nowrap;z-index:2;}
.ha{left:64px;}
.hb{right:64px;}
.reel{position:absolute;left:624px;top:0;width:672px;height:1080px;overflow:hidden;}
.track{position:absolute;left:0;top:0;width:672px;display:flex;flex-direction:column;gap:294px;}
.frame{width:672px;height:378px;border-radius:4px;overflow:hidden;flex:none;}
.frame img{width:100%;height:100%;object-fit:cover;}
.lsub{position:absolute;left:64px;bottom:64px;font:500 34px/1.3 "AR";color:#A7AEB4;}
/* verbs */
.vgroup{position:absolute;inset:0;opacity:0;}
.vgroup.light{background:#E7E5E1;color:#17191B;}
.vword{position:absolute;left:96px;top:300px;font:800 300px/.85 "BSD";text-transform:uppercase;}
.vsay{position:absolute;left:104px;top:600px;width:760px;font:500 46px/1.25 "AR";color:#A7AEB4;}
.light .vsay{color:#4D5359;}
.vpic{position:absolute;right:96px;top:90px;width:680px;height:900px;border-radius:4px;overflow:hidden;}
.vpic img{width:100%;height:100%;object-fit:cover;}
.vtrio{position:absolute;right:120px;top:180px;width:760px;height:720px;display:flex;align-items:flex-end;justify-content:space-between;}
.vtrio img{width:30%;height:auto;}
.vtrio img:nth-child(2){width:18%;}
.vchat{position:absolute;right:560px;bottom:120px;width:560px;display:flex;flex-direction:column;gap:14px;}
.bub{max-width:100%;padding:16px 20px 10px;border-radius:4px;font:400 28px/1.35 "AR";color:#E9EDEF;background:#202C33;align-self:flex-start;opacity:0;}
.bub.out{background:#005C4B;align-self:flex-end;}
.bub time{display:block;text-align:right;font-size:18px;color:rgba(233,237,239,.55);margin-top:4px;}
.bub b{color:#FFFFFF;}
.gal{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px;}
.gal figure{margin:0;}
.gal img{width:100%;aspect-ratio:3/4;object-fit:cover;border-radius:4px;display:block;}
.gal b{display:block;font:500 20px "AR";margin-top:6px;}
/* price */
.ph2{position:absolute;left:96px;top:120px;font:800 120px/.95 "BSD";text-transform:uppercase;}
.size{position:absolute;left:100px;top:330px;display:flex;align-items:baseline;gap:22px;}
.size .pl{font:500 30px "AR";color:#A7AEB4;}
.size b{font:800 120px/1 "BSD";color:#E8EBED;min-width:170px;font-variant-numeric:tabular-nums;}
.size .px{font:800 70px "BSD";color:#A7AEB4;}
.prows{position:absolute;left:100px;right:100px;top:560px;}
.prow{display:grid;grid-template-columns:300px 1fr auto;align-items:baseline;padding:24px 0;font:500 40px/1 "AR";}
.prow .pk{color:#A7AEB4;}
.prow .pv{font:800 76px/1 "BSD";font-variant-numeric:tabular-nums;}
.pnote{position:absolute;left:100px;bottom:70px;font:500 30px "AR";color:#A7AEB4;}
/* pieces */
.pieces{position:absolute;left:96px;right:96px;top:150px;font:800 104px/1.12 "BSD";text-transform:uppercase;color:#4D5359;}
.pn{display:inline-block;}
.pn.lead{color:#17191B;}
.fr{display:inline-block;height:.82em;width:.9em;margin:0 .04em 0 .14em;vertical-align:-.06em;}
.fr img{width:100%;height:100%;object-fit:contain;}
.pnote2{position:absolute;left:100px;bottom:80px;font:500 40px "AR";color:#17191B;}
/* site */
.browser{position:absolute;left:96px;top:110px;width:1300px;height:860px;border-radius:4px;overflow:hidden;background:#1D1F21;}
.bbar{height:44px;background:#26292C;display:flex;align-items:center;gap:9px;padding:0 18px;}
.bbar i{width:13px;height:13px;border-radius:50%;background:#4A4D50;}
.bbar span{margin-left:auto;margin-right:auto;font:500 19px "AR";color:#A7AEB4;}
.bview{position:relative;height:816px;overflow:hidden;}
.bview img{position:absolute;left:0;top:0;width:1300px;height:auto;}
.iph{position:absolute;left:1470px;top:150px;width:370px;height:780px;border-radius:56px;background:#050505;padding:12px;}
.iph-scr{width:100%;height:100%;border-radius:44px;overflow:hidden;}
.iph-scr img{width:100%;height:auto;display:block;}
.scap{position:absolute;left:100px;bottom:40px;font:500 32px "AR";color:#A7AEB4;}
/* offer */
.offh{position:absolute;left:96px;top:110px;font:800 100px/.95 "BSD";text-transform:uppercase;}
.offers{position:absolute;left:96px;right:96px;top:330px;display:grid;grid-template-columns:1fr 1fr;gap:70px 90px;}
.of b{display:block;font:800 74px/.95 "BSD";text-transform:uppercase;}
.of span{display:block;margin-top:18px;font:400 34px/1.35 "AR";color:#A7AEB4;max-width:760px;}
/* cta */
.wa-num{margin-top:64px;font:600 78px/1 "AR";letter-spacing:-.01em;color:#FF6A13;}
.sig{margin-top:40px;font:500 32px "AR";color:#A7AEB4;}
#cta .mega2{font-size:120px;}
/* end */
#end{background:#000;}
.endglow{position:absolute;width:1300px;height:1300px;left:310px;top:-110px;border-radius:50%;background:radial-gradient(closest-side,rgba(90,130,255,.30),rgba(0,0,0,0));}
.ribwrap{position:absolute;left:420px;top:-420px;width:1080px;height:1920px;transform:rotate(90deg);}
.rib{position:absolute;inset:0;mix-blend-mode:screen;transform-origin:50% 50%;}
.rl{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible;}
.glowl{filter:blur(42px);opacity:.9;}
.corel{filter:blur(1.5px);}
.mark-wrap{width:330px;height:390px;}
.mark{width:100%;height:100%;overflow:visible;}
.lockup{margin-top:60px;font:600 64px "IT";letter-spacing:-.025em;white-space:nowrap;}
.by{font-weight:300;color:#86868B;display:inline-block;}
.ct{color:#F5F5F7;}
.lt{display:inline-block;}
/* fx */
.fx{position:absolute;inset:0;pointer-events:none;z-index:40;}
.spk{position:absolute;border-radius:50%;background:#FFD08A;box-shadow:0 0 10px 3px rgba(255,140,40,.85);opacity:0;}
.ember{position:absolute;border-radius:50%;background:#FF9A4A;box-shadow:0 0 8px 2px rgba(255,120,40,.6);opacity:0;}
.flash{position:absolute;inset:0;background:radial-gradient(60% 60% at 50% 60%,rgba(255,200,140,.5),rgba(255,140,60,0));opacity:0;}
.vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(120% 100% at 50% 50%,rgba(0,0,0,0) 60%,rgba(0,0,0,.45) 100%);z-index:50;}
'''

JS = r'''
const tl = gsap.timeline({ paused: true });
const P0 = 0.0012, BAR = 8 * 0.3092783, K = k => +(P0 + BAR * k).toFixed(3);
const SOFT = "expo.out";
function rise(sel, t, o) {
  o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y || 50, filter: "blur(" + (o.blur || 16) + "px)" },
    { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d || 1.3, ease: SOFT, stagger: o.st || 0.08 }, t);
}
// metal out of the fire: glowing orange, then cools to steel white
function forge(sel, t, o) {
  o = o || {};
  const cold = o.cold || "#E8EBED";
  tl.fromTo(sel, { opacity: 0, scale: o.s || 1.06, color: "#FFE2B0", textShadow: "0 0 40px rgba(255,130,40,1), 0 0 90px rgba(255,90,20,.8)", filter: "blur(14px)" },
    { opacity: 1, scale: 1, filter: "blur(0px)", duration: .9, ease: "power3.out" }, t);
  tl.to(sel, { color: "#FF9A4A", textShadow: "0 0 26px rgba(255,110,30,.8), 0 0 60px rgba(255,80,20,.4)", duration: .7, ease: "sine.out" }, t + .5);
  tl.to(sel, { color: cold, textShadow: "0 0 0px rgba(255,110,30,0), 0 0 0px rgba(255,80,20,0)", duration: o.cool || 2.2, ease: "power2.inOut" }, t + 1.3);
}
function out(sel, t, d) { tl.to(sel, { opacity: 0, filter: "blur(12px)", duration: d || .7, ease: "power2.in" }, t); }
function hit(t, a) { tl.fromTo("#flash", { opacity: a || .5 }, { opacity: 0, duration: .9, ease: "expo.out" }, t); }
function shake(sel, t) { tl.fromTo(sel, { x: 0, y: 0 }, { keyframes: [{ x: 9, y: -6, duration: .05 }, { x: -7, y: 5, duration: .06 }, { x: 4, y: -2, duration: .07 }, { x: 0, y: 0, duration: .1 }], ease: "none" }, t); }
function spark(sel, t, dx, dy, d) {
  tl.set(sel, { x: 0, y: 0, opacity: 1 }, t);
  tl.to(sel, { x: dx, duration: d, ease: "power2.out" }, t);
  tl.to(sel, { y: dy, duration: d * .45, ease: "power2.out" }, t);
  tl.to(sel, { y: dy + 520, duration: d * .55, ease: "power2.in" }, t + d * .45);
  tl.to(sel, { opacity: 0, duration: d * .5, ease: "power1.in" }, t + d * .5);
}
function ember(sel, t, d, dx) {
  tl.fromTo(sel, { x: 0, y: 0, opacity: 0 }, { x: dx, y: -620, duration: d, ease: "none" }, t);
  tl.to(sel, { opacity: .8, duration: d * .2 }, t);
  tl.to(sel, { opacity: 0, duration: d * .4 }, t + d * .6);
}
const SC = $SCENES;
SC.forEach(([id, s, e]) => tl.fromTo("#cam-" + id, { scale: 1.0 }, { scale: 1.03, duration: e - s, ease: "none" }, s));

// 1 · intro: an iron scroll forged out of the dark, then the name
const fps = document.querySelectorAll("#forge .fp");
fps.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
tl.fromTo("#ig", { opacity: 0, scale: .5 }, { opacity: 1, scale: 1, duration: 4, ease: "sine.out" }, 0);
tl.to("#forge .fp", { strokeDashoffset: 0, duration: 3.4, ease: "power2.inOut", stagger: .25 }, .3);
tl.fromTo("#forge", { filter: "drop-shadow(0 0 30px rgba(255,140,40,1))" }, { filter: "drop-shadow(0 0 0px rgba(255,140,40,0))", duration: 3, ease: "power2.inOut" }, K(2));
tl.to("#forge .fp", { stroke: "#6E767D", duration: 3, ease: "power2.inOut" }, K(2));
tl.to("#forge", { y: 150, scale: 1.9, opacity: .16, duration: 2.6, ease: "power2.inOut" }, K(2) - .4);
rise("#ik .w", K(1), { st: .1, d: 1.4 });
out("#ik", K(2) - .5, .5);
forge("#iname", K(2), { s: 1.12, cool: 1.1 });
hit(K(2), .7); shake("#cam-intro", K(2));
out("#cam-intro .center", K(3) - .6, .6);

// 2 · hook
forge("#h1", K(3));
hit(K(3), .4);
rise("#h2", K(4), { d: 1.2 });
rise("#h3", K(5) - .4, { d: 1.2 });

// 3 · lema: the two words hold while their work passes between them, one photo per bar
forge("#la", K(6)); forge("#lb", K(6) + .15);
hit(K(6), .45);
tl.fromTo("#lreel", { clipPath: "inset(50% 0 50% 0)" }, { clipPath: "inset(0% 0 0% 0)", duration: 1.4, ease: "power3.inOut" }, K(6) + .3);
const STEP = 378 + 294, Y0 = 540 - 189;
tl.set("#ltrack", { y: Y0 }, 0);
[1, 2, 3].forEach(i => tl.to("#ltrack", { y: Y0 - i * STEP, duration: 1.1, ease: "power3.inOut" }, K(6 + i) - .55));
rise("#lsub", K(7), { d: 1.2, y: 24 });
out("#cam-lema", K(10) - .5, .5);

// 4 · verbs: one step per two bars
for (let i = 0; i < $NVERBS; i++) {
  const t = K(10 + i * 2), g = "#vg" + i;
  tl.set(g, { opacity: 1 }, t);
  forge("#vw" + i, t, { cold: i === 4 ? "#17191B" : "#E8EBED", s: 1.08 });
  hit(t, i === 4 ? .2 : .35);
  rise("#vs" + i, t + .6, { d: 1.1, y: 30 });
  tl.fromTo("#vp" + i, { opacity: 0, x: 80, clipPath: "inset(0 0 0 100%)" }, { opacity: 1, x: 0, clipPath: "inset(0 0 0 0%)", duration: 1.3, ease: "power3.out" }, t + .15);
  tl.fromTo("#vp" + i + " img", { scale: 1.12 }, { scale: 1, duration: 5, ease: "power2.out" }, t + .15);
  document.querySelectorAll(g + " .bub").forEach((b, j) =>
    tl.fromTo(b, { opacity: 0, y: 30, scale: .96 }, { opacity: 1, y: 0, scale: 1, duration: .5, ease: "back.out(1.6)" }, t + BAR * (.5 + j * .5)));
  if (i < $NVERBS - 1) out(g, K(12 + i * 2) - .4, .4);
}
out("#cam-verbs", K(20) - .45, .45);

// 5 · price: the size changes, the three prices follow
const PR = $PRICES, fmt = n => "L " + (Math.round(n / 100) * 100).toLocaleString("en-US");
rise("#ph", K(20), { d: 1.2 });
rise("#psize", K(20) + .4, { d: 1.1 });
[0, 1, 2].forEach(i => rise("#pr" + i, K(20.5) + i * .15, { d: 1, y: 30 }));
rise("#pnote", K(21), { d: 1, y: 20 });
const dim = { w: 3, h: 2.2 }, pw = document.getElementById("pw"), ph = document.getElementById("phh");
const pvs = [0, 1, 2].map(i => document.getElementById("pv" + i));
function paint() {
  pw.textContent = dim.w.toFixed(1); ph.textContent = dim.h.toFixed(1);
  PR.forEach(([lo, hi], i) => pvs[i].textContent = fmt(lo * dim.w * dim.h) + " a " + fmt(hi * dim.w * dim.h));
}
tl.to(dim, { w: 4, h: 2.5, duration: 2.2, ease: "power2.inOut", onUpdate: paint }, K(22));
tl.fromTo(".pv", { color: "#E8EBED" }, { color: "#FF6A13", duration: .3, yoyo: true, repeat: 1 }, K(22) + 2.2);
out("#cam-price", K(24) - .5, .5);

// 6 · pieces, by name
rise("#pnl", K(24), { d: 1, y: 30 });
for (let i = 0; i < $NPIECES; i++) rise("#pn" + i, K(24.25) + i * .28, { d: 1, y: 30, blur: 10 });
rise("#pn2", K(26) - .3, { d: 1, y: 20 });
out("#cam-pieces", K(27) - .5, .5);

// 7 · the new site in a browser, one view per half bar
tl.fromTo("#br", { opacity: 0, y: 120, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 1.6, ease: SOFT }, K(27));
["#sh1", "#sh2", "#sh3"].forEach((s, i) => tl.fromTo(s, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: .8, ease: "power3.out" }, K(27.75 + i * .6)));
tl.fromTo("#sph", { opacity: 0, x: 220, rotation: 5 }, { opacity: 1, x: 0, rotation: 0, duration: 1.5, ease: SOFT }, K(28));
rise("#scap", K(27.5), { d: 1, y: 20 });
out("#cam-site", K(30) - .5, .5);

// 8 · offer
rise("#offh", K(30), { d: 1.1 });
[0, 1, 2, 3].forEach(i => rise("#of" + i, K(30.25) + i * .35, { d: 1.1, y: 40 }));
out("#cam-offer", K(32) - .5, .5);

// 9 · CTA
tl.fromTo("#cg", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1.1, duration: 4, ease: "sine.out" }, K(32));
rise("#k1", K(32), { d: 1.1 });
forge("#k2", K(32) + .6);
hit(K(32), .45);
rise("#k3", K(33), { d: 1.2, y: 40 });
rise("#k4", K(33) + .5, { d: 1 });

// 10 · Clientia Tech: outline draws, locks on the next bar
function trails(rid, t0, dur, spin) {
  for (let i = 0; i < 6; i++) {
    const st = t0 + i * 0.22, len = 480 + (i % 3) * 170;
    tl.fromTo("." + rid + "-p" + i, { strokeDasharray: len + " 2000", strokeDashoffset: len }, { strokeDashoffset: -1000, duration: dur - i * 0.15, ease: "power2.inOut" }, st);
  }
  tl.fromTo("#" + rid, { rotation: spin[0], scale: spin[2], opacity: 0 }, { rotation: spin[1], scale: spin[3], opacity: 1, duration: dur, ease: "power1.inOut" }, t0);
}
const E0 = K(34), E1 = K(35);
const strokes = document.querySelectorAll("#mstroke path");
strokes.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
trails("re", E0 - 0.2, 2.6, [20, -8, 1.6, 0.9]);
tl.to("#re", { scale: 3.2, opacity: 0, duration: 1.1, ease: "expo.out" }, E1);
tl.to("#mstroke path", { strokeDashoffset: 0, duration: 2.2, ease: "power2.inOut" }, E0 + .1);
tl.fromTo("#mfill", { opacity: 0 }, { opacity: 1, duration: .5, ease: "power2.out" }, E1);
tl.to("#mstroke", { opacity: 0, duration: .5 }, E1);
tl.fromTo("#mwrap", { scale: .92 }, { scale: 1, duration: 2.4, ease: SOFT }, E0);
tl.fromTo("#mwrap", { filter: "drop-shadow(0 0 0px rgba(140,170,255,0))" }, { filter: "drop-shadow(0 0 60px rgba(140,170,255,.65))", duration: .35, ease: "power2.out", yoyo: true, repeat: 1 }, E1);
tl.fromTo("#eglow", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: 1.6, ease: SOFT }, E1);
tl.fromTo("#msweep", { x: -200 }, { x: 900, duration: 1.4, ease: "power2.inOut" }, E1 + .5);
rise("#lby", E1 + .5, { d: 1.2 });
rise(".lt", E1 + .7, { d: 1.2, st: .035, y: 40, blur: 12 });
tl.to("#end .center, #eglow", { opacity: 0, duration: 1.4, ease: "power2.in" }, $TOTAL - 1.6);

// sparks and embers (none over the light pieces scene)
$SPARKS
$EMBERS
tl.set(".fx", { opacity: 1 }, 0);
tl.to(".fx", { opacity: 0, duration: .3 }, K(24) - .3);
tl.to(".fx", { opacity: 1, duration: .3 }, K(27));
tl.to(".fx .ember", { opacity: 0, duration: .4 }, K(34));

window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
tl.seek(0);
'''

if __name__ == "__main__":
    print(build())
