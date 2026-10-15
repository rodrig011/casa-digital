#!/usr/bin/env python3
"""Bocha's Grill pitch video (2026-10-15), vertical 1080x1920 for WhatsApp.

First video built on the sales playbook in /mnt/project-files/propuestas/metodos-video.md (from the
"sell me this pen" TikTok rodrigo sent): don't open with features, open with questions about THEIR business,
each backed by a real comment from their TikTok; bridge ("si alguna respuesta fue 'no sé'..."); answer each
question in the same order; "No vendemos un sistema"; clear call to action; "by Clientia Tech".

Format from the reference: a constant background (their own footage, blurred and dark), a picture-in-picture
window on top that illustrates each line, big centered captions of 2-4 words, a reply-to-comment hook card and
a WhatsApp "Escribir -> Enviado" button at the end. "Still Buggin", every scene on a bar line.
Conversations, stock, wait times and ratings are examples and are labelled on screen.
"""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.path.join(HERE, "..", "..", "coco-chicken", "video")
sys.path.insert(0, CC)
from gen2 import MARK, ribbons, DEPS  # noqa: E402
import gen3  # noqa: E402

SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "build")
SLUG = "bochas-grill-vertical"
P0, BAR = 0.0012, 8 * 0.3092783   # "Still Buggin": 194 BPM, a bar every 2.474 s
K = lambda k: round(P0 + BAR * k, 3)
CORAL = "#FF9F80"                 # the salmon of their logo, lifted to read on dark

# id, start bar, end bar
SCENES = [("hook", 0, 2.5), ("nosale", 2.5, 4.5), ("secret", 4.5, 5.5),
          ("q1", 5.5, 8), ("q2", 8, 10.5), ("q3", 10.5, 13), ("q4", 13, 15.5),
          ("bridge", 15.5, 17.5), ("r1", 17.5, 20), ("r2", 20, 22.5), ("r3", 22.5, 24.5), ("r4", 24.5, 27),
          ("gen", 27, 29.5), ("close", 29.5, 32), ("cta", 32, 34.5), ("end", 34.5, 38.5)]
SC = {i: (a, b) for i, a, b in SCENES}
TOTAL = K(38.5)

# captions: scene -> [(text, start bar, end bar)]; *word* = coral keyword
CAPS = {
    "hook": [("¿Franquicias?", .55, 1.25), ("Para llegar ahí,", 1.25, 1.85), ("primero, *unas preguntas.*", 1.85, 2.5)],
    "nosale": [("Le podríamos decir esto.", 2.6, 3.5), ("Pero *así no se vende.*", 3.5, 4.5)],
    "q1": [("¿Cuántos le preguntan", 5.6, 6.4), ("*el precio*", 6.4, 7.1), ("y se quedan sin respuesta?", 7.1, 8)],
    "q2": [("¿Se enteró a tiempo", 8.1, 8.9), ("de que Villanueva", 8.9, 9.6), ("se quedó *sin frijoles?*", 9.6, 10.5)],
    "q3": [("¿Sabe cuánto espera", 10.6, 11.4), ("hoy un cliente", 11.4, 12.1), ("*en Choloma?*", 12.1, 13)],
    "q4": [("¿Sus cinco sucursales", 13.1, 14.1), ("sirven *el mismo plato?*", 14.1, 15.5)],
    "bridge": [("Si alguna respuesta", 15.6, 16.3), ("fue *“no sé”,*", 16.3, 16.9), ("eso es lo que *resolvemos.*", 16.9, 17.5)],
    "r1": [("Su WhatsApp contesta", 17.6, 18.5), ("*en segundos,*", 18.5, 19.2), ("en las cinco sucursales.", 19.2, 20)],
    "r2": [("Se acaban los frijoles", 20.1, 21), ("y el proveedor", 21, 21.6), ("*ya lo sabe.*", 21.6, 22.5)],
    "r3": [("La espera de cada sucursal,", 22.6, 23.5), ("*en vivo.*", 23.5, 24.5)],
    "r4": [("Cada cliente califica", 24.6, 25.5), ("y usted se entera", 25.5, 26.2), ("*el mismo día.*", 26.2, 27)],
    "gen": [("Una franquicia funciona", 27.1, 27.9), ("cuando cada local", 27.9, 28.6), ("*hace lo mismo.*", 28.6, 29.5)],
    "close": [("No vendemos un sistema.", 29.6, 30.4), ("*Primero, preguntas.*", 30.4, 31.1), ("Después resolvemos lo que *Bocha's Grill necesita.*", 31.1, 32)],
}
LABEL = {"q1": "Pregunta 1", "q2": "Pregunta 2", "q3": "Pregunta 3", "q4": "Pregunta 4",
         "r1": "Respuesta 1", "r2": "Respuesta 2", "r3": "Respuesta 3", "r4": "Respuesta 4"}
# picture-in-picture clips (their own TikTok videos, cropped, never upscaled)
PIPV = {"hook": "p-hook", "q1": "p-precio", "q2": "p-villa", "q3": "p-mostrador", "q4": "p-aderezo",
        "bridge": "p-locales", "gen": "p-bocha"}
NOTE = {"hook": "Comentario real en su TikTok", "q1": "Comentarios reales en su TikTok @bochasgrill",
        "q2": "Comentario real en su TikTok", "q3": "Comentario real en su TikTok", "q4": "Comentarios reales en su TikTok",
        "bridge": "Sus sucursales, en su propio video", "r1": "Ejemplo · pregunta real de un cliente", "r2": "Ejemplo",
        "r3": "Ejemplo", "r4": "Ejemplo", "gen": "Cita real de @bochas10 en TikTok"}


def cap_html(t):
    return re.sub(r"\*(.+?)\*", r'<span class="k">\1</span>', t)


def comment(name, text, cid, cls=""):
    return (f'<div class="cmt {cls}" id="{cid}"><div class="av">{name[0].upper()}</div><div><b>{name}</b>'
            f'<p>{text}</p></div></div>')


def wa(head_name, msgs, wid):
    head = (f'<div class="wh"><span class="bk">‹</span><div class="wav"><img src="assets/logo.png"></div>'
            f'<div><b>{head_name}</b><span>en línea</span></div></div>')
    return (f'<div class="wa" id="{wid}">{head}<div class="wm">'
            + "".join(f'<div class="slot" id="{i}">{h}</div>' for i, h in msgs) + '</div></div>')


def build():
    proj = os.path.join(OUT, SLUG)
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    A = lambda *p: os.path.join(proj, "assets", *p)
    for n in ["musica.mp3", "bg.mp4", "logo.png"] + [v + ".mp4" for v in PIPV.values()]:
        shutil.copy(os.path.join(SRC, n), A(n))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), A("gsap.min.js"))
    for w in (400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"), A("fonts", f"it-{w}.woff2"))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "bochas-grill-v1", "name": "Casa Digital x Bocha's Grill"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = SC[sid]
        caps = "".join(f'<div class="cap" id="c-{sid}-{i}">{cap_html(t)}</div>' for i, (t, a, b) in enumerate(CAPS.get(sid, [])))
        lab = f'<div class="lab" id="lab-{sid}">{LABEL[sid]}</div>' if sid in LABEL else ""
        note = f'<div class="note" id="n-{sid}">{NOTE[sid]}</div>' if sid in NOTE else ""
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0">{inner}{lab}<div class="caps">{caps}</div>{note}</section>')

    # PiP videos live outside the scenes so the renderer can sample them; each sits in a framed window
    vids = []
    for n, (sid, clip) in enumerate(PIPV.items()):
        s, e = SC[sid]
        vids.append(f'<div class="pipv" id="pv-{sid}"><video id="vid-{sid}" src="assets/{clip}.mp4" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                    f'data-media-start="0" data-track-index="{3 + n}" muted playsinline></video></div>')

    # the reply-to-comment hook, real comment on their "Empezamos con una idea" video (139K views)
    hook = comment("Alfredo Castro8043", "tienen franquicias ??", "hk", "hookc")
    hook = hook.replace('<div class="cmt hookc"', '<div class="cmt hookc"').replace("<div><b>", '<div><span class="rt">Respuesta a</span><b>', 1)
    nosale = ('<div class="pitch" id="pitch"><span>“El mejor sistema</span><span>para restaurantes</span><span>del mundo”</span>'
              '<i class="strike" id="strike"></i></div>')
    secret = '<div class="big" id="sec">Primero,<br><span class="k">preguntas.</span></div>'
    q1 = "".join(comment(n, t, f"q1c{i}", "pc") for i, (n, t) in enumerate(
        [("Nicolas Portillo", "cuanto vale??"), ("Soraya Beltran", "precio"), ("santos m.l", "pero cual es el precio"), ("user12345", "alguien sabe los precios")]))
    q1 = f'<div class="stackc">{q1}</div>'
    q2 = comment("Kei", "Fui al local de Villanueva, y no tenian NI FRIJOLES, NI CARNE ASADA NI INCURTIDO!", "q2c", "pc lowc")
    q3 = comment("Jeidy Rodriguez", "ayer fui a Bonchas Choloma y me dijeron que debía esperar 50 minutos por la orden", "q3c", "pc lowc")
    q4 = ('<div class="stackc low2">' + comment("n_gueva", "hoy pedí y ni el aderezo me pusieron", "q4c0", "pc")
          + comment("jenissem", "varias veces me e quejado x carne tan reseca y dura en la stibys", "q4c1", "pc") + '</div>')
    bridge = '<div class="pill" id="brp">San Pedro Sula · El Progreso · Villanueva · Choloma</div>'
    r1 = '<div class="pipw">' + wa("Bocha's Grill", [
        ("r1m1", '<div class="wb out">Esos L.139 ya con el envío? o hay q sumarle el delivery?<small>7:15 p. m.</small></div>'),
        ("r1t", '<div class="typ"><i></i><i></i><i></i></div>'),
        ("r1m2", '<div class="wb in">Los L139 eran el Económico de Costilla o de Carne por Bip Bip, lunes, miércoles y viernes de septiembre. El envío lo cobra Bip Bip aparte.<small>7:15 p. m.</small></div>'),
        ("r1m3", '<div class="wb in">Hoy le puedo ofrecer los nuevos Chicharrones de Carne 🔥 ¿Le mando el enlace?<small>7:15 p. m.</small></div>')], "wa1") + '</div>'
    r2 = ('<div class="pipw dk"><div class="stk" id="stk"><div class="kk">Inventario · Villanueva</div>'
          '<div class="row"><b>Frijoles</b><span><span id="nfr">15</span> lb</span></div><div class="bar"><i id="frb"></i></div>'
          '<div class="mn">Mínimo: 15 lb</div></div>'
          '<div class="pchat" id="pchat"><div class="pb out" id="pm1"><div class="tag">Aviso automático</div>Buenas, le escribe Bocha\'s Grill Villanueva. Nos quedan 4 lb de frijoles. ¿Nos trae 30 lb mañana temprano?<small>6:10 pm ✓✓</small></div>'
          '<div class="pb in" id="pm2">Claro, mañana a las 9 se los llevo.<small>6:14 pm</small></div></div></div>')
    rows = [("SPS Stibys", 18), ("SPS Calpules", 16), ("El Progreso", 22), ("Villanueva", 19), ("Choloma", 41)]
    r3 = ('<div class="pipw dk"><div class="tbl2"><div class="th"><span>Sucursal</span><span>Espera ahora</span></div>'
          + "".join(f'<div class="tr {"hot" if m > 25 else ""}" id="tr{i}"><span>{n}</span><b>{m} min</b></div>' for i, (n, m) in enumerate(rows))
          + '<div class="act" id="act"><span>Choloma: 6 pedidos en cocina</span><em id="actb">Avisar a los 6</em></div></div></div>')
    r4 = '<div class="pipw">' + wa("Bocha's Grill", [
        ("r4m1", '<div class="wb in">¿Cómo estuvo su pedido de Bocha\'s Choloma? Califíquenos del 1 al 5 ⭐<small>8:02 p. m.</small></div>'),
        ("r4m2", '<div class="wb out">2. me tocó sin aderezo<small>8:03 p. m.</small></div>'),
        ("r4m3", '<div class="wb in">Gracias por avisarnos. Ya se lo pasé al encargado de Choloma 🙏<small>8:03 p. m.</small></div>')], "wa4") + (
        '<div class="alert" id="alert"><div class="ai">!</div><div><b>Panel · Choloma</b><span>3 clientes hoy: faltó el aderezo</span></div></div></div>')
    gen = ('<div class="quote" id="quote"><div class="qh"><div class="av">B</div>Bocha10 · @bochas10</div>'
           '<p>“Quiero compartirles mi emprendimiento que hoy en día va hacia una franquicia”</p></div>')
    cta = ('<div class="ctab"><div class="ct1" id="ct1">Escríbanos y le mostramos<br><span class="k">exactamente cómo.</span></div>'
           f'<div class="wbtn" id="wbtn"><span class="wi">{WA_SVG}</span><span class="wt"><span id="wt1">Escribir</span><span id="wt2">Enviado ✓</span></span></div>'
           f'<div class="num" id="wnum">WhatsApp {gen3.WHATSAPP}</div>'
           f'<div class="cdl" id="cdl">{gen3.HOUSE}<span>Casa Digital</span><em>Rodrigo Herrera</em></div></div>')
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])
    end = f'''<div class="endglow" id="eglow"></div>
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
          </div>'''

    body = "\n".join([
        f'<video class="bgv" id="bgv" src="assets/bg.mp4" data-start="0" data-duration="{round(K(34.5) + 1, 3)}" data-media-start="0" data-track-index="2" muted playsinline></video>',
        '<div class="shade"></div>',
        "\n".join(vids),
        scene("hook", hook), scene("nosale", nosale), scene("secret", secret),
        scene("q1", q1), scene("q2", q2), scene("q3", q3), scene("q4", q4), scene("bridge", bridge),
        scene("r1", r1), scene("r2", r2), scene("r3", r3), scene("r4", r4), scene("gen", gen),
        scene("close", ""), scene("cta", cta), scene("end", end, "endscene"),
    ])
    html = (HTML.replace("$css", CSS.replace("$coral", CORAL)).replace("$body", body).replace("$total", str(TOTAL))
            .replace("$js", JS.replace("$P0", str(P0)).replace("$BAR", str(BAR))
                     .replace("$caps", json.dumps({k: [[a, b] for _, a, b in v] for k, v in CAPS.items()}))
                     .replace("$pip", json.dumps({k: [K(SC[k][0]), K(SC[k][1])] for k in PIPV}))
                     .replace("$scenes", json.dumps([[i, K(a), K(b)] for i, a, b in SCENES]))))
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


WA_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 00-8.6 15.1L2 22l5-1.3A10 10 0 1012 2zm0 18.2a8.2 8.2 0 01-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1112 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 01-3.3-2.9c-.3-.4.3-.4.7-1.4a.5.5 0 000-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 00-.7.3 3 3 0 00-.9 2.2 5.2 5.2 0 001.1 2.7 11.8 11.8 0 004.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 001.8-1.2 2.2 2.2 0 00.1-1.2c0-.1-.2-.2-.5-.3z"/></svg>')

HTML = r'''<!doctype html>
<html lang="es" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>Casa Digital x Bocha's Grill</title>
<script src="assets/gsap.min.js"></script>
<style>$css</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="$total" data-width="1080" data-height="1920">
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="$total" data-fade-out="4" data-track-index="1"></audio>
$body
</div>
<script>$js</script>
</body>
</html>
'''

CSS = r'''
@font-face{font-family:"IT";src:url("assets/fonts/it-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"IT";src:url("assets/fonts/it-500.woff2") format("woff2");font-weight:500;}
@font-face{font-family:"IT";src:url("assets/fonts/it-600.woff2") format("woff2");font-weight:600;}
@font-face{font-family:"IT";src:url("assets/fonts/it-700.woff2") format("woff2");font-weight:700;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000;}
#root{position:relative;width:1080px;height:1920px;background:#0A0A0B;color:#fff;font-family:"IT",sans-serif;-webkit-font-smoothing:antialiased;overflow:hidden;}
.bgv{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:0;}
.shade{position:absolute;inset:0;z-index:1;background:linear-gradient(180deg,rgba(0,0,0,.35) 0%,rgba(0,0,0,.15) 45%,rgba(0,0,0,.55) 100%);}
.scene{position:absolute;inset:0;z-index:3;}
.k{color:$coral;}
/* the picture-in-picture window, top of the frame */
.pipv,.pipw{position:absolute;left:80px;top:150px;width:920px;height:860px;border-radius:44px;overflow:hidden;
  box-shadow:0 0 0 2px rgba(255,255,255,.14),0 50px 120px rgba(0,0,0,.6);}
.pipv{z-index:2;opacity:0;background:#111;}
.pipv video{width:920px;height:860px;object-fit:cover;display:block;}
.pipw{background:#0B141A;}
.pipw.dk{background:linear-gradient(180deg,#17171A,#0E0E10);}
/* captions: one line at a time, big, centered */
.caps{position:absolute;left:60px;right:60px;top:1270px;height:300px;}
.cap{position:absolute;left:0;right:0;top:0;text-align:center;font-weight:700;font-size:92px;line-height:1.08;letter-spacing:-.03em;opacity:0;
  text-shadow:0 4px 24px rgba(0,0,0,.65),0 2px 4px rgba(0,0,0,.5);}
.lab{position:absolute;left:0;right:0;top:1150px;text-align:center;font-size:30px;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:$coral;opacity:0;text-shadow:0 2px 12px rgba(0,0,0,.6);}
.note{position:absolute;left:0;right:0;bottom:70px;text-align:center;font-size:24px;font-weight:500;color:rgba(255,255,255,.62);opacity:0;}
/* comment cards, TikTok style */
.cmt{display:flex;gap:18px;align-items:flex-start;background:#fff;color:#111;border-radius:26px;padding:22px 28px;box-shadow:0 24px 60px rgba(0,0,0,.4);}
.cmt .av{width:58px;height:58px;border-radius:50%;flex:none;background:linear-gradient(135deg,#FF9F80,#C9583C);color:#fff;font-weight:700;font-size:28px;display:flex;align-items:center;justify-content:center;}
.cmt b{display:block;font-size:24px;font-weight:600;color:#6E6E73;}
.cmt p{font-size:36px;font-weight:500;line-height:1.2;margin-top:4px;color:#111;}
.cmt .rt{display:block;font-size:20px;color:#A1A1A6;font-weight:500;}
.hookc{position:absolute;left:120px;right:120px;top:70px;z-index:5;}
.stackc{position:absolute;left:120px;right:120px;top:300px;display:flex;flex-direction:column;gap:18px;}
.stackc.low2{top:560px;}
.lowc{position:absolute;left:120px;right:120px;top:110px;}
/* "lo que no hay que hacer" */
.pitch{position:absolute;left:110px;right:110px;top:380px;height:420px;border-radius:40px;background:rgba(255,255,255,.08);box-shadow:0 0 0 2px rgba(255,255,255,.14);
  display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:66px;font-weight:600;letter-spacing:-.02em;line-height:1.15;color:rgba(255,255,255,.9);}
.strike{position:absolute;left:70px;right:70px;top:50%;height:10px;border-radius:5px;background:#FF453A;transform-origin:0 50%;transform:scaleX(0) rotate(-6deg);box-shadow:0 0 30px rgba(255,69,58,.6);}
.big{position:absolute;left:0;right:0;top:640px;text-align:center;font-size:150px;font-weight:700;line-height:1.02;letter-spacing:-.045em;text-shadow:0 6px 30px rgba(0,0,0,.6);}
.pill{position:absolute;left:110px;right:110px;top:900px;text-align:center;background:rgba(0,0,0,.55);border-radius:40px;padding:18px 20px;font-size:28px;font-weight:600;color:#fff;box-shadow:0 0 0 1px rgba(255,255,255,.18);}
/* WhatsApp inside the window */
.wa{position:absolute;inset:0;display:flex;flex-direction:column;}
.wh{height:118px;background:#1F2C34;display:flex;align-items:center;gap:20px;padding:0 30px;flex:none;}
.wh .bk{font-size:56px;color:#E9EDEF;margin-top:-8px;}
.wav{width:70px;height:70px;border-radius:50%;overflow:hidden;background:#fff;}
.wav img{width:100%;height:100%;object-fit:contain;}
.wh b{display:block;font-size:32px;font-weight:600;color:#E9EDEF;}
.wh span{font-size:22px;color:#8696A0;}
.wm{flex:1;padding:26px 30px;display:flex;flex-direction:column;justify-content:flex-start;gap:0;background:#0B141A;}
.slot{overflow:hidden;height:0;}
.wb{max-width:720px;padding:16px 22px 12px;border-radius:22px;font-size:32px;line-height:1.28;color:#E9EDEF;margin-bottom:16px;}
.wb small{display:block;text-align:right;font-size:18px;color:#8696A0;margin-top:4px;}
.wb.in{background:#202C33;border-top-left-radius:6px;}
.wb.out{background:#005C4B;margin-left:auto;border-top-right-radius:6px;}
.slot:has(.out){display:flex;}
.typ{display:inline-flex;gap:10px;background:#202C33;border-radius:22px;padding:22px 26px;margin-bottom:16px;}
.typ i{width:14px;height:14px;border-radius:50%;background:#8696A0;}
.alert{position:absolute;left:40px;right:40px;bottom:36px;display:flex;gap:20px;align-items:center;background:#fff;color:#111;border-radius:26px;padding:22px 26px;box-shadow:0 20px 50px rgba(0,0,0,.5);opacity:0;}
.alert .ai{width:56px;height:56px;border-radius:14px;background:#EA001E;color:#fff;font-weight:700;font-size:34px;display:flex;align-items:center;justify-content:center;flex:none;}
.alert b{display:block;font-size:24px;color:#6E6E73;font-weight:600;}
.alert span{font-size:32px;font-weight:600;}
/* stock + supplier */
.stk{position:absolute;left:50px;right:50px;top:50px;background:#1C1C1F;border-radius:30px;padding:30px 36px;box-shadow:0 0 0 1px rgba(255,255,255,.08);}
.kk{font-size:22px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#8E8E93;}
.stk .row{display:flex;justify-content:space-between;align-items:baseline;margin-top:14px;font-size:46px;font-weight:600;}
.stk .row span{font-variant-numeric:tabular-nums;}
.stk .bar{height:14px;border-radius:7px;background:rgba(255,255,255,.1);margin-top:18px;overflow:hidden;}
.stk .bar i{display:block;height:100%;width:100%;background:linear-gradient(90deg,#FF453A,#FF9F80);transform-origin:0 50%;border-radius:7px;}
.stk .mn{font-size:24px;color:#8E8E93;margin-top:12px;}
.pchat{position:absolute;left:50px;right:50px;top:340px;display:flex;flex-direction:column;gap:18px;}
.pb{max-width:720px;padding:18px 24px 12px;border-radius:24px;font-size:31px;line-height:1.28;opacity:0;}
.pb.out{background:#005C4B;color:#E9EDEF;margin-left:auto;border-top-right-radius:6px;}
.pb.in{background:#2A2A2E;color:#F2F2F7;border-top-left-radius:6px;}
.pb small{display:block;text-align:right;font-size:18px;color:rgba(255,255,255,.55);margin-top:4px;}
.pb .tag{font-size:19px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#7FE0B9;margin-bottom:6px;}
/* wait times table */
.tbl2{position:absolute;left:50px;right:50px;top:50px;}
.th{display:flex;justify-content:space-between;font-size:22px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#8E8E93;padding:0 26px 16px;}
.tr{display:flex;justify-content:space-between;align-items:center;height:104px;padding:0 26px;border-radius:22px;font-size:40px;font-weight:600;opacity:0;}
.tr b{font-variant-numeric:tabular-nums;color:#7FE0B9;}
.tr.hot{background:rgba(255,69,58,.14);box-shadow:0 0 0 2px rgba(255,69,58,.5);}
.tr.hot b{color:#FF6B5E;}
.act{margin-top:26px;display:flex;justify-content:space-between;align-items:center;gap:18px;background:#1C1C1F;border-radius:22px;padding:22px 26px;font-size:28px;color:#D1D1D6;opacity:0;}
.act em{font-style:normal;background:#25D366;color:#062;font-weight:700;border-radius:999px;padding:12px 24px;font-size:26px;white-space:nowrap;}
/* the owner's own words */
.quote{position:absolute;left:120px;right:120px;top:610px;background:rgba(255,255,255,.96);color:#111;border-radius:30px;padding:28px 32px;box-shadow:0 24px 60px rgba(0,0,0,.45);z-index:5;}
.quote .qh{display:flex;align-items:center;gap:16px;font-size:24px;font-weight:600;color:#6E6E73;}
.quote .av{width:52px;height:52px;border-radius:50%;background:#111;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:24px;}
.quote p{font-size:38px;font-weight:500;line-height:1.25;margin-top:14px;}
/* call to action */
.ctab{position:absolute;left:0;right:0;top:330px;display:flex;flex-direction:column;align-items:center;text-align:center;}
.ct1{font-size:76px;font-weight:700;line-height:1.08;letter-spacing:-.035em;text-shadow:0 4px 24px rgba(0,0,0,.6);opacity:0;}
.wbtn{margin-top:110px;height:150px;width:640px;border-radius:999px;background:#fff;color:#111;display:flex;align-items:center;justify-content:center;gap:24px;font-size:54px;font-weight:700;box-shadow:0 30px 80px rgba(0,0,0,.5);opacity:0;position:relative;overflow:hidden;}
.wbtn .wi{width:68px;height:68px;color:#25D366;display:flex;}
.wbtn .wi svg{width:100%;height:100%;}
.wt{position:relative;display:inline-block;width:330px;height:66px;text-align:left;}
.wt span{position:absolute;left:0;top:0;white-space:nowrap;line-height:66px;}
#wt2{opacity:0;}
.num{margin-top:40px;font-size:40px;font-weight:600;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6);opacity:0;}
.cdl{margin-top:180px;display:flex;align-items:center;gap:18px;font-size:38px;font-weight:600;opacity:0;}
.cdl .house{width:50px;height:50px;}
.cdl em{font-style:normal;font-weight:500;color:rgba(255,255,255,.6);font-size:28px;margin-left:10px;}
/* outro, as in the other Casa Digital videos */
.endscene{background:#000;color:#F5F5F7;z-index:6;}
.center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.endglow{position:absolute;width:1300px;height:1300px;left:-110px;top:310px;border-radius:50%;background:radial-gradient(closest-side,rgba(90,130,255,.30),rgba(0,0,0,0));}
.ribwrap{position:absolute;left:0;top:0;width:1080px;height:1920px;}
.rib{position:absolute;inset:0;mix-blend-mode:screen;transform-origin:50% 50%;}
.rl{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible;}
.glowl{filter:blur(42px);opacity:.9;}
.corel{filter:blur(1.5px);}
.mark-wrap{width:330px;height:390px;}
.mark{width:100%;height:100%;overflow:visible;}
.lockup{margin-top:60px;font-size:64px;letter-spacing:-.025em;white-space:nowrap;}
.by{font-weight:400;color:#86868B;display:inline-block;}
.ct{font-weight:600;color:#F5F5F7;}
.lt{display:inline-block;}
'''

JS = r'''
const tl = gsap.timeline({ paused: true });
const K = k => $P0 + $BAR * k;
const SOFT = "expo.out", FINE = "power2.inOut";
const CAPS = $caps, PIP = $pip, SCENES = $scenes;
function rise(sel, t, o) {
  o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y || 40, filter: "blur(" + (o.blur || 12) + "px)" },
    { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d || 1.2, ease: SOFT, stagger: o.st || 0.1 }, t);
}
function out(sel, t, d) { tl.to(sel, { opacity: 0, y: -24, filter: "blur(8px)", duration: d || .45, ease: "power2.in" }, t); }
function show(id, t) {
  tl.fromTo("#" + id, { height: 0 }, { height: "auto", duration: .5, ease: "power2.out" }, t);
  tl.fromTo("#" + id + " > *", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .55, ease: SOFT }, t + .12);
}
function hide(id, t) { tl.to("#" + id, { height: 0, duration: .3, ease: "power2.in" }, t); }
function dots(id, t) { tl.fromTo("#" + id + " i", { opacity: .25 }, { opacity: 1, duration: .25, stagger: .1, repeat: 2, yoyo: true, ease: "sine.inOut" }, t); }

// captions: each line rises in on its bar and leaves just before the next one, never cut mid-read
Object.entries(CAPS).forEach(([sid, list]) => list.forEach(([a, b], i) => {
  const sel = "#c-" + sid + "-" + i;
  rise(sel, K(a), { y: 30, d: .8, blur: 10 });
  const last = i === list.length - 1;
  out(sel, K(b) - (last ? .55 : .4), last ? .5 : .38);
}));
// scene furniture: label and source note fade with the scene
SCENES.forEach(([sid, s, e]) => {
  if (document.getElementById("lab-" + sid)) { rise("#lab-" + sid, s + .1, { y: 16, d: .9 }); out("#lab-" + sid, e - .55, .5); }
  if (document.getElementById("n-" + sid)) { rise("#n-" + sid, s + .5, { y: 10, d: .9 }); out("#n-" + sid, e - .55, .5); }
});
// PiP windows: soft in, soft out, slow push-in on the footage
Object.entries(PIP).forEach(([sid, [s, e]]) => {
  tl.fromTo("#pv-" + sid, { opacity: 0, y: 50, scale: .97 }, { opacity: 1, y: 0, scale: 1, duration: .9, ease: SOFT }, s);
  tl.fromTo("#pv-" + sid + " video", { scale: 1 }, { scale: 1.05, duration: e - s, ease: "none" }, s);
  tl.to("#pv-" + sid, { opacity: 0, duration: .55, ease: "power2.in" }, e - .55);
});
function win(sel, s, e) {
  tl.fromTo(sel, { opacity: 0, y: 50, scale: .97 }, { opacity: 1, y: 0, scale: 1, duration: .9, ease: SOFT }, s);
  tl.to(sel, { opacity: 0, duration: .55, ease: "power2.in" }, e - .55);
}
const S = id => SCENES.find(x => x[0] === id);

// 1 · hook: reply to a real comment
rise("#hk", K(0) + .3, { y: -30, d: 1.2 });
out("#hk", K(2.5) - .55, .5);

// 2 · what not to do: the salesman line, struck out
rise("#pitch", K(2.6), { d: 1 });
tl.to("#strike", { scaleX: 1, duration: .7, ease: "power3.inOut" }, K(3.4));
tl.to("#pitch span", { opacity: .35, duration: .6 }, K(3.6));
out("#pitch", K(4.5) - .55, .5);

// 3 · the refrain
rise("#sec", K(4.55), { d: 1.1, y: 50 });
out("#sec", K(5.5) - .5, .45);

// 4-7 · the four questions, each with its real comment(s)
[0, 1, 2, 3].forEach(i => rise("#q1c" + i, K(5.9) + i * .55, { y: 30, d: .9 }));
out("#q1 .stackc", K(8) - .55, .5);
rise("#q2c", K(8.6), { y: 30, d: 1 }); out("#q2c", K(10.5) - .55, .5);
rise("#q3c", K(11.1), { y: 30, d: 1 }); out("#q3c", K(13) - .55, .5);
rise("#q4c0", K(13.5), { y: 30, d: 1 }); rise("#q4c1", K(14.2), { y: 30, d: 1 }); out("#q4 .stackc", K(15.5) - .55, .5);

// 8 · bridge over their own storefronts
rise("#brp", K(15.9), { y: 20, d: 1 }); out("#brp", K(17.5) - .55, .5);

// 9 · answer 1: WhatsApp answers on its own
win("#r1 .pipw", K(17.5), K(20));
show("r1m1", K(17.8)); show("r1t", K(18.3)); dots("r1t", K(18.3) + .3); hide("r1t", K(18.8)); show("r1m2", K(18.8)); show("r1m3", K(19.3));

// 10 · answer 2: stock drops, the supplier is told by itself
win("#r2 .pipw", K(20), K(22.5));
tl.fromTo("#frb", { scaleX: 1 }, { scaleX: .27, duration: 1.6, ease: FINE }, K(20.3));
(() => { const o = { v: 15 }, el = document.getElementById("nfr"); tl.fromTo(o, { v: 15 }, { v: 4, duration: 1.6, ease: FINE, onUpdate: () => { el.textContent = Math.round(o.v); } }, K(20.3)); })();
tl.to("#stk .row span", { color: "#FF6B5E", duration: .3 }, K(20.3) + 1.6);
rise("#pm1", K(21), { y: 20, d: .9 }); rise("#pm2", K(21.7), { y: 20, d: .9 });

// 11 · answer 3: wait times live, Choloma flags itself
win("#r3 .pipw", K(22.5), K(24.5));
[0, 1, 2, 3, 4].forEach(i => rise("#tr" + i, K(22.7) + i * .22, { y: 16, d: .8, blur: 6 }));
tl.fromTo("#tr4", { scale: 1 }, { scale: 1.03, duration: .4, yoyo: true, repeat: 1, ease: "sine.inOut" }, K(23.5));
rise("#act", K(23.6), { y: 20, d: .9 });
tl.fromTo("#actb", { scale: 1 }, { scale: 1.08, duration: .25, yoyo: true, repeat: 1 }, K(24.1));

// 12 · answer 4: every customer rates, the owner hears it the same day
win("#r4 .pipw", K(24.5), K(27));
show("r4m1", K(24.8)); show("r4m2", K(25.4)); show("r4m3", K(25.9));
tl.fromTo("#alert", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: .8, ease: "back.out(1.3)" }, K(26.2));

// 13 · his own words: a franchise
rise("#quote", K(27.4), { y: 30, d: 1.1 }); out("#quote", K(29.5) - .55, .5);

// 15 · call to action: "Escribir" -> "Enviado"
rise("#ct1", K(32.1), { d: 1 });
tl.fromTo("#wbtn", { opacity: 0, y: 60, scale: .94 }, { opacity: 1, y: 0, scale: 1, duration: 1, ease: SOFT }, K(32.4));
tl.to("#wbtn", { scale: .95, duration: .14, yoyo: true, repeat: 1, ease: "power2.inOut" }, K(33.3));
tl.to("#wt1", { opacity: 0, y: -30, duration: .3 }, K(33.35));
tl.fromTo("#wt2", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .35 }, K(33.45));
tl.to("#wbtn", { backgroundColor: "#25D366", color: "#fff", duration: .35 }, K(33.45));
tl.to("#wbtn .wi", { color: "#fff", duration: .35 }, K(33.45));
rise("#wnum", K(32.9), { y: 20, d: .9 });
rise("#cdl", K(33.2), { y: 20, d: .9 });
out("#cta .ctab", K(34.5) - .6, .55);

// 16 · outro: trails converge, mark draws, fills on the bar
const E0 = K(34.5);
function trails(rid, t0, dur, spin) {
  for (let i = 0; i < 6; i++) {
    const st = t0 + i * 0.22, len = 480 + (i % 3) * 170;
    tl.fromTo("." + rid + "-p" + i, { strokeDasharray: len + " 2000", strokeDashoffset: len }, { strokeDashoffset: -1000, duration: dur - i * 0.15, ease: "power2.inOut" }, st);
  }
  tl.fromTo("#" + rid, { rotation: spin[0], scale: spin[2], opacity: 0 }, { rotation: spin[1], scale: spin[3], opacity: 1, duration: dur, ease: "power1.inOut" }, t0);
}
const strokes = document.querySelectorAll("#mstroke path");
strokes.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
tl.fromTo("#end", { opacity: 0 }, { opacity: 1, duration: .5, ease: "power1.out" }, E0);
trails("re", E0 - 0.3 + .3, 3, [20, -8, 1.6, 0.9]);
tl.to("#re", { scale: 3.2, opacity: 0, duration: 1.3, ease: "expo.out" }, K(35.5));
tl.to("#mstroke path", { strokeDashoffset: 0, duration: 2.3, ease: FINE }, E0 + .1);
tl.fromTo("#mfill", { opacity: 0 }, { opacity: 1, duration: .6, ease: "power2.out" }, K(35.5));
tl.to("#mstroke", { opacity: 0, duration: .6 }, K(35.5));
tl.fromTo("#mwrap", { scale: .92 }, { scale: 1, duration: 2.6, ease: SOFT }, E0);
tl.fromTo("#mwrap", { filter: "drop-shadow(0 0 0px rgba(140,170,255,0))" }, { filter: "drop-shadow(0 0 60px rgba(140,170,255,.65))", duration: .4, ease: "power2.out", yoyo: true, repeat: 1 }, K(35.5));
tl.fromTo("#eglow", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: 2, ease: SOFT }, K(35.5));
tl.fromTo("#msweep", { x: -200 }, { x: 900, duration: 1.8, ease: FINE }, K(36));
rise("#lby", K(36), { d: 1.6 });
rise(".lt", K(36) + .3, { d: 1.6, st: .04, y: 36, blur: 12 });
tl.to("#end .center, #eglow", { opacity: 0, duration: 2, ease: "power2.in" }, K(37.6));

window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
tl.seek(0);
'''

if __name__ == "__main__":
    print(build())
