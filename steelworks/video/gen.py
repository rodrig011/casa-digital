#!/usr/bin/env python3
"""Steel Works · video de propuesta (HyperFrames, 1920x1080).

Estilo "forja": fondo negro de taller, texto que entra al rojo vivo y se enfría a acero,
chispas en cada golpe, placas metálicas estampadas para los hallazgos. Cierra con el outro
de Clientia Tech (logo redibujado + estelas de luz) de los videos anteriores.

Música: "Still Buggin" (194 BPM). Un compás de 8 tiempos = 2.474 s; toda escena empieza en
una línea de compás K(n). Requisitos junto al script: musica.mp3, capturas/*.png y
deps/node_modules con gsap@3.14.2 y @fontsource/{big-shoulders-display,archivo,jetbrains-mono,inter-tight}.

    python3 gen.py && cd build && hyperframes render . -o ../steelworks-propuesta.mp4 -q high
"""
import json, os, shutil, random
from outro import ribbons

HERE = os.path.dirname(os.path.abspath(__file__))
DEPS = os.environ.get("DEPS", os.path.join(HERE, "deps", "node_modules"))
OUT = os.path.join(HERE, "build")
WHATSAPP = "+1 (765) 543-4251"
MARK = json.load(open(os.path.join(HERE, "clientia-mark.json")))
P0, BAR = 0.0012, 8 * 0.3092783
K = lambda k: round(P0 + BAR * k, 3)
SCENES = [("intro", 0, 3), ("hook", 3, 6), ("audit", 6, 11), ("thesis", 11, 13), ("site", 13, 19),
          ("bot", 19, 25), ("flow", 25, 29), ("offer", 29, 32), ("cta", 32, 34), ("end", 34, 37)]
TOTAL = K(37)

FINDINGS = [
    ("Enlaces que no llevan a nada", "FQA  →  #\nEnvíos  →  #", "«Preguntas» y «Envíos» del menú no abren nada."),
    ("Teléfonos que no marcan", "tel:TGU:(504)3265-8800", "Desde el celular, tocar el número da error."),
    ("Código suelto en pantalla", ".path{fill:none;stroke:#333…}", "Estilos del tema aparecen como texto."),
    ("Un error a la vista", "error: Content is protected !!", "El aviso del plugin se ve en la página."),
    ("Google no sabe qué venden", "Just another WordPress site", "Es la descripción que leen los buscadores."),
    ("Sin WhatsApp, sin horario", "WhatsApp: —   Formulario: #", "El botón de «Enviar un mensaje» no abre nada."),
]


def words(text, cls="w"):
    return " ".join(f'<span class="{cls}">{w}</span>' for w in text.split())


def bubble(bid, side, html):
    return f'<div class="bub {side}" id="{bid}">{html}<time>9:41</time></div>'


def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    A = os.path.join(OUT, "assets")
    os.makedirs(os.path.join(A, "fonts"))
    shutil.copy(os.path.join(HERE, "musica.mp3"), os.path.join(A, "musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), os.path.join(A, "gsap.min.js"))
    fs = os.path.join(DEPS, "@fontsource")
    for src, dst in [("big-shoulders-display/files/big-shoulders-display-latin-800-normal.woff2", "bsd-800"),
                     ("big-shoulders-display/files/big-shoulders-display-latin-600-normal.woff2", "bsd-600"),
                     ("jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2", "jbm-500")] + \
            [(f"archivo/files/archivo-latin-{w}-normal.woff2", f"ar-{w}") for w in (400, 500, 600, 700)] + \
            [(f"inter-tight/files/inter-tight-latin-{w}-normal.woff2", f"it-{w}") for w in (300, 600)]:
        shutil.copy(os.path.join(fs, src), os.path.join(A, "fonts", dst + ".woff2"))
    for f in os.listdir(os.path.join(HERE, "capturas")):
        shutil.copy(os.path.join(HERE, "capturas", f), os.path.join(A, f))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(OUT, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "steelworks-propuesta", "name": "Casa Digital x Steel Works"}, open(os.path.join(OUT, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    # hand-forged C-scroll for the intro (same geometry as the website's logo)
    import math
    def spiral(cx, cy, r, turns, end, s):
        return [(cx + r * (0.1 + 0.9 * t) * math.cos(end + s * (1 - t) * turns * 2 * math.pi),
                 cy + r * (0.1 + 0.9 * t) * math.sin(end + s * (1 - t) * turns * 2 * math.pi)) for t in [i / 80 for i in range(81)]]
    def cscroll(x, y, h, side, turns=1.2):
        r = h * .27; cx = x + side * r
        top = spiral(cx, y + r, r, turns, math.pi if side > 0 else 0, 1 if side > 0 else -1)
        bot = list(reversed(spiral(cx, y + h - r, r, turns, math.pi if side > 0 else 0, -1 if side > 0 else 1)))
        return "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in top + bot)
    scroll_paths = "".join(f'<path class="fp" d="{cscroll(300 + sd * 8, 40, 520, sd)}"/>' for sd in (-1, 1)) + '<path class="fp" d="M300 600 L300 0"/>'

    plates = "".join(f'''<div class="plate" id="pl{i}"><div class="stamp">{i + 1:02d}</div><div class="pt">{t}</div>
        <pre class="snip">{s}</pre><div class="pc">{c}</div></div>''' for i, (t, s, c) in enumerate(FINDINGS))

    chat = "".join([
        bubble("c0", "out", "Hola, buenas"),
        bubble("c1", "in", "¡Hola! 👋 Soy el asistente de <b>Steel Works</b>. ¿En qué te ayudo?"
               '<div class="opts"><span>Buscar una pieza</span><span>Cotizar fabricación</span><span>Pedido rápido de taller</span></div>'),
        bubble("c2", "out", '<span class="mono">120-1048 x 20<br>130-1024 x 50</span>'),
        bubble("c3", "in", 'Listo, armé tu pedido:<br><span class="mono">20 × 120-1048 · L 1,629.40<br>50 × 130-1024 · L 571.00</span><br><b>Total: L 2,200.40</b> con IVA'),
        bubble("c4", "out", "Retiro en Tegucigalpa"),
        bubble("c5", "in", '🧾 <b>Pedido SW-1049</b> listo para retirar.<div class="pay"><span>Pago con tarjeta</span><b>Pagar L 2,200.40</b></div>'),
        bubble("c6", "out", "Y quiero cotizar un portón forjado de 3.6 x 2.4"),
        bubble("c7", "in", '📐 <b>Solicitud COT-2248</b><br>Portón · 8.64 m² · forjado clásico<br>Ya la tiene el taller. Un asesor te escribe con el precio.'),
    ])

    flow_right = [("Pieza por código", "Precio y existencia al instante"), ("Pedido y pago", "Total con IVA y enlace de pago"),
                  ("Fabricación", "Ficha con medidas y foto al taller"), ("Caso especial", "Pasa a un asesor con todo el contexto")]
    flow_nodes = "".join(f'<div class="fn r" id="fr{i}" style="top:{150 + i * 170}px"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(flow_right))
    flow_lines = "".join(f'<path class="fl" id="fl{i}" d="M 905 540 C 1040 540, 1040 {195 + i * 170}, 1160 {195 + i * 170}"/>' for i in range(4))
    flow_lines += '<path class="fl" id="fl4" d="M 560 540 L 655 540"/>' + "".join(
        f'<path class="fl" id="fo{i}" d="M 1520 {195 + i * 170} C 1600 {195 + i * 170}, 1600 540, 1660 540"/>' for i in range(4))

    offer = [("Sitio nuevo con catálogo vivo", "Buscador por código, precio, existencia y pedido en línea."),
             ("Asistente de WhatsApp", "Responde 24/7, arma pedidos, cotiza fabricación y pasa a un asesor."),
             ("Cuenta de taller", "Pedido rápido por lista, precio por volumen y repetir compras."),
             ("Pagos y avisos", "Pago con tarjeta y aviso automático cuando vuelve una pieza agotada.")]
    offer_html = "".join(f'<div class="of" id="of{i}"><div class="stamp">{i + 1:02d}</div><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(offer))

    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    # sparks: deterministic bursts (seeded) + ambient embers
    rnd = random.Random(7)
    BURSTS = [("b0", K(2) + .05, 960, 700, 34), ("b1", K(3), 960, 560, 26), ("b2", K(6), 420, 300, 20),
              ("b3", K(13), 960, 900, 26), ("b4", K(19), 1500, 900, 24), ("b5", K(25), 780, 540, 24),
              ("b6", K(29), 960, 980, 26), ("b7", K(32), 960, 640, 30)]
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
    for j in range(40):
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
            <div class="kick" id="ik">{words("Casa Digital presenta")}</div>
            <div class="sub" id="is">{words("una propuesta para")}</div>
            <div class="mega hot" id="iname">Steel Works</div>
          </div>'''),
        scene("hook", '''
          <div class="center">
            <div class="mega2 hot" id="h1">Más de 750 piezas.</div>
            <div class="line" id="h2">Cada una con su código.</div>
            <div class="line dim" id="h3">Y ninguna forma rápida de <em class="redhot">pedirla</em>.</div>
          </div>'''),
        scene("audit", f'''
          <div class="aud-l">
            <div class="kick">{words("Diagnóstico")}</div>
            <div class="h2" id="ah">{words("Visitamos steelworkshn.com como un cliente.")}</div>
            <div class="counter"><b id="acount">0</b><span>problemas que le cuestan ventas</span></div>
          </div>
          <div class="plates">{plates}</div>'''),
        scene("thesis", '''
          <div class="center">
            <div class="line big" id="t1">Tus clientes ya saben lo que quieren.</div>
            <div class="line big hot" id="t2">Tienen el código.</div>
            <div class="line dim" id="t3">Solo necesitan dónde escribirlo.</div>
          </div>'''),
        scene("site", f'''
          <div class="kick sitek" id="sk">{words("La nueva steelworkshn.com")}</div>
          <div class="browser" id="br"><div class="bbar"><i></i><i></i><i></i><span>steelworkshn.com</span></div>
            <div class="bview">
              <img id="sh0" src="assets/web-hero.png"><img id="sh1" src="assets/web-lineas.png"><img id="sh2" src="assets/web-fabricacion.png"><img id="sh3" src="assets/web-taller.png">
            </div></div>
          <div class="iph site-ph" id="sph"><div class="iph-scr"><img src="assets/movil-hero.png"></div><div class="island"></div></div>
          <div class="caps2">
            <div class="cap2" id="sc0"><b>Todo, en hierro.</b><span>Una portada que se siente como su taller.</span></div>
            <div class="cap2" id="sc1"><b>Catálogo por familia y código</b><span>Precio con IVA y existencia de cada pieza.</span></div>
            <div class="cap2" id="sc2"><b>Cotizador de portones</b><span>El cliente ve el boceto con sus medidas al instante.</span></div>
            <div class="cap2" id="sc3"><b>Cuenta de taller</b><span>El herrero pega su lista y el pedido se arma solo.</span></div>
          </div>'''),
        scene("bot", f'''
          <div class="bot-l">
            <div class="kick">{words("Asistente de WhatsApp")}</div>
            <div class="h2" id="bh">{words("Atiende 24/7, con el catálogo real.")}</div>
            <div class="steps">
              <div class="stp" id="bs0"><i>1</i>Recibe la lista de códigos</div>
              <div class="stp" id="bs1"><i>2</i>Calcula el total con IVA</div>
              <div class="stp" id="bs2"><i>3</i>Cierra el pedido con pago</div>
              <div class="stp" id="bs3"><i>4</i>Pasa la cotización al taller</div>
            </div>
          </div>
          <div class="iph bot-ph" id="bph"><div class="iph-scr wa">
            <div class="wa-top"><div class="av">SW</div><div><b>Steel Works</b><span>en línea</span></div></div>
            <div class="wa-body"><div class="wa-scroll" id="wsc">{chat}</div></div>
          </div><div class="island"></div></div>'''),
        scene("flow", f'''
          <div class="kick flowk">{words("Cómo funciona")}</div>
          <svg class="flines" viewBox="0 0 1920 1080">{flow_lines}</svg>
          <div class="fn l" id="fc"><b>El cliente escribe</b><span>a cualquier hora, desde cualquier ciudad</span></div>
          <div class="fn mid" id="fm"><div class="ring"></div><b>Asistente<br>Steel Works</b><span>conectado al catálogo</span></div>
          {flow_nodes}
          <div class="fn end" id="fe"><b>Sucursal<br>TGU · SPS</b><span>recibe todo ordenado</span></div>
          <div class="flow-note" id="fnote">{words("Ventas deja de copiar precios a mano y atiende lo que sí necesita una persona.")}</div>'''),
        scene("offer", f'''
          <div class="kick offk">{words("Lo que construimos para Steel Works")}</div>
          <div class="offers">{offer_html}</div>'''),
        scene("cta", f'''
          <div class="heatglow" id="cg"></div>
          <div class="center">
            <div class="line big" id="k1">La demo ya está lista.</div>
            <div class="mega2 hot" id="k2">Se la mostramos en 15 minutos.</div>
            <div class="wa-pill" id="k3"><span>WhatsApp</span>{WHATSAPP}</div>
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

    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    js = (JS.replace("$SCENES", scenes_js).replace("$SPARKS", "\n".join(spark_js)).replace("$EMBERS", ember_js)
          .replace("$TOTAL", str(TOTAL)))
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
@font-face{font-family:"AR";src:url("assets/fonts/ar-600.woff2") format("woff2");font-weight:600;}
@font-face{font-family:"AR";src:url("assets/fonts/ar-700.woff2") format("woff2");font-weight:700;}
@font-face{font-family:"JBM";src:url("assets/fonts/jbm-500.woff2") format("woff2");font-weight:500;}
@font-face{font-family:"IT";src:url("assets/fonts/it-300.woff2") format("woff2");font-weight:300;}
@font-face{font-family:"IT";src:url("assets/fonts/it-600.woff2") format("woff2");font-weight:600;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1920px;height:1080px;overflow:hidden;background:#070708;}
#root{position:relative;width:1920px;height:1080px;background:#070708;color:#EEEBE6;font-family:"AR",sans-serif;-webkit-font-smoothing:antialiased;}
.scene{position:absolute;inset:0;overflow:hidden;background:radial-gradient(120% 90% at 50% 110%,#1E1611 0%,#0B0B0C 55%,#070708 100%);}
.cam{position:absolute;inset:0;transform-origin:50% 50%;}
.center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 160px;}
.w{display:inline-block;}
.kick{font:600 26px/1 "AR";letter-spacing:.24em;text-transform:uppercase;color:#E8732C;}
.sub{margin-top:26px;font:400 44px/1.2 "AR";color:#9DA4AA;}
.mega{margin-top:18px;font:800 230px/.9 "BSD";text-transform:uppercase;letter-spacing:.01em;}
.mega2{font:800 150px/.95 "BSD";text-transform:uppercase;max-width:1600px;}
.line{margin-top:30px;font:500 64px/1.15 "AR";letter-spacing:-.01em;}
.line.big{font:800 120px/1 "BSD";text-transform:uppercase;margin-top:14px;}
.line.dim{color:#9DA4AA;}
.redhot{font-style:normal;color:#FF8A3D;text-shadow:0 0 30px rgba(255,110,30,.7);}
.h2{margin-top:26px;font:800 96px/.95 "BSD";text-transform:uppercase;}
.hot{color:#EEEBE6;}
.heatglow{position:absolute;left:460px;top:240px;width:1000px;height:1000px;border-radius:50%;background:radial-gradient(closest-side,rgba(232,115,44,.35),rgba(232,115,44,0));}
.forge{position:absolute;left:740px;top:70px;width:440px;height:440px;opacity:.9;}
.forge .fp{stroke:#FFC46B;stroke-width:10;}
.intro .kick{margin-top:500px;}
.intro .mega{position:absolute;left:0;right:0;top:420px;margin:0;}
/* audit */
.aud-l{position:absolute;left:110px;top:150px;width:640px;}
#audit .h2{font-size:84px;}
.counter{margin-top:60px;display:flex;align-items:baseline;gap:22px;}
.counter b{font:800 220px/1 "BSD";color:#FF8A3D;text-shadow:0 0 40px rgba(255,110,30,.45);}
.counter span{font:500 34px/1.2 "AR";color:#9DA4AA;max-width:300px;}
.plates{position:absolute;left:800px;top:100px;width:1020px;display:grid;grid-template-columns:1fr 1fr;gap:20px;}
.plate{position:relative;height:276px;border-radius:10px;padding:24px 30px 20px 96px;
  background:repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,rgba(0,0,0,0) 1px 4px),linear-gradient(180deg,#2B2E31,#1A1C1E);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.10),0 30px 60px rgba(0,0,0,.45);}
.plate::before,.plate::after{content:"";position:absolute;width:12px;height:12px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#8A9097,#2A2D30);top:16px;right:16px;}
.plate::after{top:auto;bottom:16px;}
.stamp{position:absolute;left:24px;top:22px;font:800 54px/1 "BSD";color:#FF8A3D;}
.pt{font:700 29px/1.1 "AR";}
.snip{margin-top:12px;font:500 20px/1.4 "JBM";color:#FFC46B;background:rgba(0,0,0,.35);border-radius:6px;padding:10px 14px;white-space:pre-wrap;}
.pc{margin-top:10px;font:400 21px/1.3 "AR";color:#9DA4AA;}
/* site */
.sitek{position:absolute;left:120px;top:76px;}
.browser{position:absolute;left:120px;top:130px;width:1300px;height:854px;border-radius:16px;overflow:hidden;background:#141516;box-shadow:0 60px 120px rgba(0,0,0,.6),0 0 0 1px rgba(255,255,255,.08);}
.bbar{height:42px;background:#232527;display:flex;align-items:center;gap:9px;padding:0 18px;}
.bbar i{width:13px;height:13px;border-radius:50%;background:#4A4D50;}
.bbar span{margin-left:auto;margin-right:auto;font:500 18px "AR";color:#9DA4AA;background:#141516;border-radius:8px;padding:5px 120px;}
.bview{position:relative;height:812px;overflow:hidden;}
.bview img{position:absolute;left:0;top:0;width:1300px;height:auto;}
.iph{position:absolute;border-radius:62px;background:#0A0A0B;padding:14px;box-shadow:0 0 0 2px #3A3D40,0 60px 120px rgba(0,0,0,.6);}
.iph-scr{width:100%;height:100%;border-radius:48px;overflow:hidden;position:relative;background:#000;}
.iph-scr img{width:100%;height:auto;display:block;}
.island{position:absolute;left:50%;top:26px;width:120px;height:34px;margin-left:-60px;border-radius:20px;background:#000;}
.site-ph{left:1470px;top:180px;width:360px;height:760px;}
.caps2{position:absolute;left:1470px;top:960px;width:400px;height:100px;}
.cap2{position:absolute;left:0;top:0;width:430px;}
.cap2 b{display:block;font:700 28px/1.15 "AR";}
.cap2 span{display:block;margin-top:6px;font:400 22px/1.3 "AR";color:#9DA4AA;}
#site .caps2{left:120px;top:1000px;width:1300px;}
#site .cap2{width:1300px;display:flex;gap:16px;align-items:baseline;}
#site .cap2 span{margin:0;}
/* bot */
.bot-l{position:absolute;left:140px;top:200px;width:820px;}
.steps{margin-top:56px;display:flex;flex-direction:column;gap:22px;}
.stp{display:flex;align-items:center;gap:22px;font:500 38px/1.2 "AR";color:#6B7177;}
.stp i{font-style:normal;width:58px;height:58px;border-radius:50%;border:2px solid #3A3D40;display:flex;align-items:center;justify-content:center;font:800 30px "BSD";}
.stp.on{color:#EEEBE6;}
.stp.on i{border-color:#FF8A3D;color:#FF8A3D;box-shadow:0 0 24px rgba(255,110,30,.5);}
.bot-ph{left:1180px;top:60px;width:480px;height:960px;}
.wa{background:#0B141A;display:flex;flex-direction:column;}
.wa-top{height:150px;background:#1F2C34;display:flex;align-items:flex-end;gap:16px;padding:0 26px 20px;}
.wa-top .av{width:56px;height:56px;border-radius:50%;background:#141516;color:#E8732C;display:flex;align-items:center;justify-content:center;font:800 24px "BSD";}
.wa-top b{display:block;font:600 26px "AR";}
.wa-top span{font:400 18px "AR";color:#8696A0;}
.wa-body{flex:1;position:relative;overflow:hidden;}
.wa-scroll{position:absolute;left:0;right:0;top:0;padding:18px 16px;display:flex;flex-direction:column;gap:12px;}
.bub{max-width:84%;padding:12px 14px 8px;border-radius:14px;font:400 21px/1.35 "AR";color:#E9EDEF;}
.bub.in{background:#202C33;align-self:flex-start;border-top-left-radius:0;}
.bub.out{background:#005C4B;align-self:flex-end;border-top-right-radius:0;}
.bub time{display:block;text-align:right;font-size:14px;color:rgba(233,237,239,.5);margin-top:2px;}
.bub .mono{font:500 19px/1.5 "JBM";}
.opts{margin-top:10px;display:flex;flex-direction:column;gap:6px;}
.opts span{background:rgba(255,255,255,.06);border-radius:8px;padding:8px;text-align:center;color:#53BDEB;font-size:19px;}
.pay{margin-top:10px;background:rgba(0,0,0,.3);border-radius:8px;padding:10px 12px;display:flex;justify-content:space-between;align-items:center;font-size:17px;color:#8696A0;}
.pay b{color:#53BDEB;font-size:19px;}
/* flow */
.flowk{position:absolute;left:120px;top:90px;}
.flines{position:absolute;inset:0;width:1920px;height:1080px;}
.fl{fill:none;stroke:#FF8A3D;stroke-width:3;filter:drop-shadow(0 0 8px rgba(255,110,30,.7));}
.fn{position:absolute;border-radius:14px;padding:24px 28px;background:linear-gradient(180deg,#2B2E31,#1A1C1E);box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 30px 60px rgba(0,0,0,.5);}
.fn b{display:block;font:700 30px/1.1 "AR";}
.fn span{display:block;margin-top:8px;font:400 21px/1.3 "AR";color:#9DA4AA;}
.fn.l{left:120px;top:470px;width:440px;}
.fn.mid{left:655px;top:410px;width:250px;height:260px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.fn.mid b{font:800 40px/1 "BSD";text-transform:uppercase;color:#FFC46B;}
.fn.mid .ring{position:absolute;inset:-14px;border-radius:50%;border:2px solid rgba(255,138,61,.6);}
.fn.r{left:1160px;width:360px;padding:18px 24px;}
.fn.end{left:1660px;top:450px;width:200px;height:180px;display:flex;flex-direction:column;justify-content:center;}
.fn.end b{font:800 40px/1 "BSD";text-transform:uppercase;}
.flow-note{position:absolute;left:120px;bottom:70px;width:1100px;font:500 32px/1.3 "AR";color:#9DA4AA;}
/* offer */
.offk{position:absolute;left:120px;top:120px;}
.offers{position:absolute;left:120px;top:200px;width:1680px;display:grid;grid-template-columns:1fr 1fr;gap:28px;}
.of{position:relative;height:330px;border-radius:12px;padding:44px 48px 40px 150px;background:repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,rgba(0,0,0,0) 1px 4px),linear-gradient(180deg,#2B2E31,#1A1C1E);box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 30px 60px rgba(0,0,0,.45);}
.of .stamp{left:46px;top:40px;font-size:80px;}
.of b{display:block;font:800 66px/.95 "BSD";text-transform:uppercase;}
.of span{display:block;margin-top:20px;font:400 30px/1.35 "AR";color:#9DA4AA;max-width:600px;}
/* cta */
.wa-pill{margin-top:60px;padding:30px 70px;border-radius:999px;background:linear-gradient(160deg,rgba(255,255,255,.14),rgba(255,255,255,.04));box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.16);font:600 70px/1 "AR";letter-spacing:-.01em;}
.wa-pill span{display:block;font:500 26px "AR";color:#30D158;margin-bottom:12px;}
.sig{margin-top:40px;font:500 30px "AR";color:#9DA4AA;}
#cta .mega2{font-size:120px;margin-top:20px;}
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
.flash{position:absolute;inset:0;background:radial-gradient(60% 60% at 50% 60%,rgba(255,200,140,.55),rgba(255,140,60,0));opacity:0;}
.vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(120% 100% at 50% 50%,rgba(0,0,0,0) 55%,rgba(0,0,0,.6) 100%);z-index:50;}
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
  tl.fromTo(sel, { opacity: 0, scale: o.s || 1.06, color: "#FFE2B0", textShadow: "0 0 40px rgba(255,130,40,1), 0 0 90px rgba(255,90,20,.8)", filter: "blur(14px)" },
    { opacity: 1, scale: 1, filter: "blur(0px)", duration: .9, ease: "power3.out" }, t);
  tl.to(sel, { color: "#FF9A4A", textShadow: "0 0 26px rgba(255,110,30,.8), 0 0 60px rgba(255,80,20,.4)", duration: .7, ease: "sine.out" }, t + .5);
  tl.to(sel, { color: "#EEEBE6", textShadow: "0 0 0px rgba(255,110,30,0), 0 0 0px rgba(255,80,20,0)", duration: o.cool || 2.4, ease: "power2.inOut" }, t + 1.3);
}
function out(sel, t, d) { tl.to(sel, { opacity: 0, filter: "blur(12px)", duration: d || .7, ease: "power2.in" }, t); }
function hit(t, a) { // hammer strike: warm flash + small camera jolt
  tl.fromTo("#flash", { opacity: a || .55 }, { opacity: 0, duration: .9, ease: "expo.out" }, t);
}
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
  tl.to(sel, { opacity: .85, duration: d * .2 }, t);
  tl.to(sel, { opacity: 0, duration: d * .4 }, t + d * .6);
}
const SC = $SCENES;
SC.forEach(([id, s, e]) => tl.fromTo("#cam-" + id, { scale: 1.0 }, { scale: 1.035, duration: e - s, ease: "none" }, s));

// 1 · intro: an iron scroll forged out of the dark
const fps = document.querySelectorAll("#forge .fp");
fps.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
tl.fromTo("#ig", { opacity: 0, scale: .5 }, { opacity: 1, scale: 1, duration: 4, ease: "sine.out" }, 0);
tl.to("#forge .fp", { strokeDashoffset: 0, duration: 3.4, ease: "power2.inOut", stagger: .25 }, .3);
tl.fromTo("#forge", { filter: "drop-shadow(0 0 30px rgba(255,140,40,1))" }, { filter: "drop-shadow(0 0 0px rgba(255,140,40,0))", duration: 3, ease: "power2.inOut" }, K(2));
tl.to("#forge .fp", { stroke: "#6E767D", duration: 3, ease: "power2.inOut" }, K(2));
tl.to("#forge", { y: 150, scale: 1.9, opacity: .16, duration: 2.6, ease: "power2.inOut" }, K(2) - .4);
rise("#ik .w", K(1), { st: .12, d: 1.4 });
rise("#is .w", K(1.5), { st: .1, d: 1.3 });
out("#ik, #is", K(2) - .5, .5);
forge("#iname", K(2), { s: 1.12, cool: 1.1 });
hit(K(2), .7); shake("#cam-intro", K(2));
out("#cam-intro .center", K(3) - .6, .6);

// 2 · hook
forge("#h1", K(3));
hit(K(3), .4);
rise("#h2", K(4), { d: 1.2 });
rise("#h3", K(5) - .4, { d: 1.2 });
tl.fromTo(".redhot", { textShadow: "0 0 0px rgba(255,110,30,0)" }, { textShadow: "0 0 34px rgba(255,110,30,.9)", duration: .5, yoyo: true, repeat: 3 }, K(5) + .8);

// 3 · audit: plates are stamped in, one every 3/4 bar
rise("#audit .kick .w", K(6), {});
rise("#ah .w", K(6) + .2, { st: .07 });
rise(".counter", K(6) + .8, { d: 1 });
const cnt = { v: 0 }, cEl = document.getElementById("acount");
[0, 1, 2, 3, 4, 5].forEach(i => {
  const t = K(6.75 + i * .7);
  tl.fromTo("#pl" + i, { opacity: 0, scale: 1.12, y: -30, filter: "blur(10px) brightness(2.2)" }, { opacity: 1, scale: 1, y: 0, filter: "blur(0px) brightness(1)", duration: .55, ease: "power4.out" }, t);
  tl.fromTo("#pl" + i + " .stamp", { textShadow: "0 0 30px rgba(255,140,40,1)" }, { textShadow: "0 0 0px rgba(255,140,40,0)", duration: 1.6 }, t);
  tl.to(cnt, { v: i + 1, duration: .3, onUpdate: () => { cEl.textContent = Math.round(cnt.v); } }, t);
  hit(t, .22);
});
tl.to("#audit .plates", { y: -20, duration: 4, ease: "sine.inOut" }, K(9.5));
out("#cam-audit", K(11) - .5, .5);

// 4 · thesis
rise("#t1", K(11), { d: 1.3 });
forge("#t2", K(11.5));
rise("#t3", K(12.25), { d: 1.2 });

// 5 · new site in a browser, scrolls through four views
rise("#sk .w", K(13), {});
tl.fromTo("#br", { opacity: 0, y: 140, rotationX: 14, scale: .94 }, { opacity: 1, y: 0, rotationX: 0, scale: 1, duration: 1.8, ease: SOFT }, K(13));
hit(K(13), .3);
["#sh1", "#sh2", "#sh3"].forEach((s, i) => tl.fromTo(s, { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: .9, ease: "power3.out" }, K(14.5 + i * 1.25)));
tl.fromTo("#sh0", { y: 0 }, { y: -40, duration: 3.5, ease: "none" }, K(13));
["#sc0", "#sc1", "#sc2", "#sc3"].forEach((s, i) => {
  rise(s, K(13.4 + i * 1.25) + (i ? .3 : 0), { d: .9, y: 24, blur: 8 });
  if (i < 3) out(s, K(14.5 + i * 1.25) - .1, .4);
});
tl.fromTo("#sph", { opacity: 0, x: 260, rotation: 6 }, { opacity: 1, x: 0, rotation: 0, duration: 1.6, ease: SOFT }, K(17.2));
tl.to("#br", { x: -40, scale: .97, duration: 1.6, ease: "power2.inOut" }, K(17.2));
out("#cam-site", K(19) - .5, .5);

// 6 · WhatsApp assistant, one message per half bar
rise("#bot .kick .w", K(19), {});
rise("#bh .w", K(19) + .2, { st: .07 });
tl.fromTo("#bph", { opacity: 0, y: 200, rotationY: -18 }, { opacity: 1, y: 0, rotationY: -6, duration: 1.8, ease: SOFT }, K(19));
tl.to("#bph", { rotationY: 4, duration: 12, ease: "sine.inOut" }, K(19) + 1.8);
const CH = [19.5, 20, 20.75, 21.5, 22.25, 23, 23.75, 24.25];
CH.forEach((b, i) => tl.fromTo("#c" + i, { opacity: 0, y: 30, scale: .96 }, { opacity: 1, y: 0, scale: 1, duration: .45, ease: "back.out(1.6)" }, K(b)));
tl.set(".bub", { opacity: 0 }, 0);
// scroll the chat up as it fills (measured once)
const wsc = document.getElementById("wsc"), body = wsc.parentNode;
const bubs = [...wsc.children];
CH.forEach((b, i) => {
  const bottom = bubs[i].offsetTop + bubs[i].offsetHeight + 24, shift = Math.max(0, bottom - body.clientHeight);
  if (shift > 0) tl.to(wsc, { y: -shift, duration: .5, ease: "power2.out" }, K(b) - .1);
});
[[20.75, 0], [21.5, 1], [23, 2], [24.25, 3]].forEach(([b, i]) => {
  tl.to("#bs" + i, { color: "#EEEBE6", duration: .4 }, K(b) + .2);
  tl.to("#bs" + i + " i", { borderColor: "#FF8A3D", color: "#FF8A3D", boxShadow: "0 0 24px rgba(255,110,30,.5)", duration: .4 }, K(b) + .2);
});
out("#cam-bot", K(25) - .5, .5);

// 7 · how it works: heat runs through the lines
rise("#flow .kick .w", K(25), {});
rise("#fc", K(25) + .2, { d: 1 });
const fls = document.querySelectorAll(".fl");
fls.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
tl.to("#fl4", { strokeDashoffset: 0, duration: .6, ease: "power2.inOut" }, K(25.5));
tl.fromTo("#fm", { opacity: 0, scale: .7 }, { opacity: 1, scale: 1, duration: .9, ease: "back.out(1.5)" }, K(25.75));
hit(K(25.75), .25);
tl.fromTo("#fm .ring", { scale: 1, opacity: 1 }, { scale: 1.25, opacity: 0, duration: 1.4, repeat: 4, ease: "power2.out" }, K(26));
[0, 1, 2, 3].forEach(i => {
  tl.to("#fl" + i, { strokeDashoffset: 0, duration: .6, ease: "power2.inOut" }, K(26.25 + i * .4));
  tl.fromTo("#fr" + i, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: .7, ease: SOFT }, K(26.25 + i * .4) + .4);
  tl.to("#fo" + i, { strokeDashoffset: 0, duration: .5, ease: "power2.inOut" }, K(27.9) + i * .1);
});
tl.fromTo("#fe", { opacity: 0, scale: .85 }, { opacity: 1, scale: 1, duration: .9, ease: SOFT }, K(28.1));
rise("#fnote .w", K(28.1) + .2, { st: .04, d: 1 });
out("#cam-flow", K(29) - .5, .5);

// 8 · offer
rise("#offer .kick .w", K(29), {});
[0, 1, 2, 3].forEach(i => {
  tl.fromTo("#of" + i, { opacity: 0, y: 60, filter: "blur(12px) brightness(1.8)" }, { opacity: 1, y: 0, filter: "blur(0px) brightness(1)", duration: 1, ease: SOFT }, K(29.25 + i * .6));
  tl.fromTo("#of" + i + " .stamp", { textShadow: "0 0 30px rgba(255,140,40,1)" }, { textShadow: "0 0 0px rgba(255,140,40,0)", duration: 1.6 }, K(29.25 + i * .6));
});
out("#cam-offer", K(32) - .5, .5);

// 9 · CTA
tl.fromTo("#cg", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1.1, duration: 4, ease: "sine.out" }, K(32));
rise("#k1", K(32), { d: 1.1 });
forge("#k2", K(32) + .6);
hit(K(32), .45);
tl.fromTo("#k3", { opacity: 0, y: 60, scale: .95, filter: "blur(12px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 1.2, ease: SOFT }, K(33));
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

// sparks and embers
$SPARKS
$EMBERS
tl.set(".fx", { opacity: 1 }, 0);
tl.to(".fx .ember", { opacity: 0, duration: .4 }, K(34));

window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
tl.seek(0);
'''

if __name__ == "__main__":
    print(build())
