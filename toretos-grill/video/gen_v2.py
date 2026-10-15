#!/usr/bin/env python3
"""Toreto's Grill pitch video v2 (2026-10-15), vertical 1080x1920 for WhatsApp.
Built on the sales method rodrigo sent (the "sell me this pen" clip): don't open by pitching the product,
open with a hook, then ask the questions that uncover the need, one by one, and let each answer show the fix.
Captions come in short chunks, big and centered, like the reference. The close is a question, not a slogan.
Story: a real comment ("No contestan whats") over their own pinned video -> "the easy thing would be to sell
you the best bot in the world; first, some questions" -> how many times did you type your address by hand
(10, real) -> who answers WhatsApp while you're at the grill (the bot, example chat) -> how much cash does each
rider bring (example) -> when does the charcoal run out (example) -> how many lunches to 1,000 (his real quote)
-> all the answers on your phone (the real panel) -> "can I ask you these questions in person?" -> outro.
Reuses gen.py's styles and the Coco Chicken helpers (gen2/gen3/gen6)."""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "coco-chicken", "video"))
sys.path.insert(0, HERE)
import gen3, gen6  # noqa: E402
from gen2 import MARK, words, ribbons, DEPS  # noqa: E402
from gen6 import K, P0, BAR  # noqa: E402
import gen  # noqa: E402

SRC = os.path.join(HERE, "src")
OUT = os.path.join(HERE, "build")
SLUG = "toretos-grill-v2"
SCENES = [("hook", 0, 3), ("pitch", 3, 6), ("q1", 6, 9), ("q2", 9, 14), ("q3", 14, 17), ("q4", 17, 20),
          ("q5", 20, 23), ("panel", 23, 26), ("close", 26, 29), ("end", 29, 33)]
TOTAL = K(33)
ADDR_REPLY = "San Pedro Sula, colonia ideal 6 y 7 calle 15 avenida atrás de megamall 📲 9612-3466"  # verbatim, tiktok-respuestas.md


def cap(sid, chunks):
    """Big centered caption built chunk by chunk; a chunk starting with * is gold."""
    out = []
    for i, c in enumerate(chunks):
        g = c.startswith("*")
        t = c.lstrip("*")
        out.append(f'<div class="ch{" gold" if g else ""}" id="{sid}c{i}">{words(t)}</div>')
    return "".join(out)


CSS_2 = r'''
html,body,#root{width:1080px !important;height:1920px !important;}
#hook{background:transparent;}
.caps{position:absolute;left:70px;right:70px;top:150px;text-align:center;}
.ch{font-weight:600;font-size:88px;line-height:1.08;letter-spacing:-.04em;color:#F5F5F7;}
.ch.gold .w{background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;padding-bottom:.08em;}
.qn{display:inline-block;margin-bottom:30px;font-size:26px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:#E3A94A;padding:12px 24px;border-radius:40px;box-shadow:0 0 0 1px rgba(242,181,68,.4);background:rgba(242,181,68,.08);}
.demo{left:70px;right:70px;bottom:26px;text-align:center;font-size:17px;}
/* hook: their own video, full screen */
.bgv{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,0) 48%,rgba(0,0,0,.82) 78%,rgba(0,0,0,.92) 100%);}
.reply{position:absolute;left:90px;right:90px;top:150px;background:#fff;color:#161823;border-radius:28px;padding:26px 30px;display:flex;gap:20px;align-items:flex-start;box-shadow:0 30px 80px rgba(0,0,0,.45);}
.reply .av{flex:none;width:64px;height:64px;border-radius:50%;background:#D9D9DE;}
.reply b{display:block;font-size:24px;font-weight:600;color:#6B6B75;}
.reply p{font-size:46px;font-weight:600;letter-spacing:-.02em;margin-top:6px;}
.reply span{display:block;font-size:20px;color:#8A8B91;margin-top:8px;}
#hook .caps{top:auto;bottom:250px;}
.byline{position:absolute;left:0;right:0;bottom:120px;text-align:center;font-size:26px;font-weight:500;color:#C7C7CC;}
.byline b{color:#F5F5F7;font-weight:600;}
/* pitch: the easy way, crossed out */
#pitch .caps{top:420px;}
.easy{position:relative;display:inline-block;}
.strike{position:absolute;left:-10px;right:-10px;top:50%;height:8px;margin-top:-4px;border-radius:4px;background:#FF5E57;transform-origin:0 50%;}
.dim .ch{color:#6E6E73;}
#pitch .then{margin-top:110px;}
/* q1: the address, typed by hand */
.addrs{position:absolute;left:90px;right:90px;top:800px;height:760px;}
.ad{position:absolute;left:0;right:0;background:linear-gradient(180deg,#161618,#111113);border-radius:26px;padding:22px 28px;box-shadow:0 0 0 1px rgba(255,255,255,.07),0 24px 60px rgba(0,0,0,.55);}
.ad .h{display:flex;align-items:center;gap:12px;font-size:21px;color:#8E8E93;font-weight:500;}
.ad .h img{width:34px;height:34px;border-radius:50%;}
.ad p{margin-top:10px;font-size:30px;line-height:1.3;color:#F5F5F7;font-weight:500;}
.tally{position:absolute;left:0;right:0;top:1270px;text-align:center;}
.tally b{font-size:150px;font-weight:600;letter-spacing:-.05em;line-height:1;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;font-variant-numeric:tabular-nums;}
.tally b span{display:inline;}
.tally>span{display:block;font-size:30px;color:#8E8E93;margin-top:4px;}
/* q2: phone under the question */
.ph-stage{left:160px;top:700px;height:1100px;transform:scale(1.15);transform-origin:50% 0;}
.ans{position:absolute;left:0;right:0;text-align:center;}
.chip{display:inline-flex;align-items:center;gap:14px;padding:16px 30px;border-radius:44px;background:rgba(37,211,102,.12);box-shadow:0 0 0 1px rgba(37,211,102,.4);font-size:32px;font-weight:600;color:#25D366;}
.chip i{width:14px;height:14px;border-radius:50%;background:#25D366;box-shadow:0 0 0 6px rgba(37,211,102,.22);}
.chip.gold{background:rgba(242,181,68,.1);box-shadow:0 0 0 1px rgba(242,181,68,.4);color:#F2B544;}
.chip.gold i{background:#F2B544;box-shadow:0 0 0 6px rgba(242,181,68,.2);}
/* cards under the question (riders, stock, goal) */
#q1 .caps,#q3 .caps,#q4 .caps,#q5 .caps{top:330px;}
.riders{left:90px;top:810px;width:900px;}
.riders .k{font-size:23px;}
.rd{grid-template-columns:1fr 170px 200px;}
.rd .n{font-size:40px;}.rd .n span{font-size:27px;}.rd .c{font-size:42px;}.rd .st{font-size:26px;}
.rtot{font-size:32px;}.rtot b{font-size:60px;}
.stk{left:90px;top:800px;width:900px;}
.stk .k{font-size:23px;}.stk .row b,.stk .row span{font-size:46px;}.stk .min{font-size:24px;}
.chat2{left:90px;top:1090px;width:900px;}
.chat2 .hd{font-size:28px;}.chat2 .b{font-size:31px;max-width:700px;}.chat2 .b small{font-size:18px;}.chat2 .tag{font-size:18px;}
.quote{left:90px;top:700px;width:900px;}
.quote p{font-size:46px;}.quote .h{font-size:24px;}
.goal{left:90px;top:1010px;width:900px;}
.goal .k{font-size:23px;}.goal .s{font-size:25px;}
/* panel on the owner's phone */
.shot{position:absolute;left:300px;top:720px;width:480px;height:1040px;border-radius:64px;overflow:hidden;padding:14px;background:linear-gradient(145deg,#3A3A3C,#0C0C0D 40%,#1C1C1E 70%,#48484A);box-shadow:0 60px 140px rgba(0,0,0,.7);}
.shot img{display:block;width:452px;height:1012px;border-radius:52px;object-fit:cover;object-position:50% 0;}
/* close */
#close .caps{top:170px;}
.cta2{left:260px;top:780px;height:660px;}
.sendb{position:relative;margin-top:22px;width:300px;height:64px;border-radius:40px;background:#F5F5F7;color:#0B0B0C;font-size:26px;font-weight:600;}
.sendb span{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;}
.sendb .s2{opacity:0;}
.ribwrap{left:0;top:0;transform:none;}
.endglow{left:-110px;top:310px;}
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
    for n in ("tiktok.mp4", "logo.jpg", "pv-hoy-m.jpg"):
        shutil.copy(os.path.join(SRC, n), A(n))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "toretos-grill-v2", "name": "Casa Digital x Toreto's Grill v2"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    vid = (f'<video id="bgv" class="bgv" src="assets/tiktok.mp4" data-start="0" data-duration="{K(3)}" '
           f'data-media-start="2" data-track-index="2" muted playsinline></video>')

    head = ('<div class="wa-h"><span class="bk">‹</span><div class="wa-av"><img src="assets/logo.jpg"></div>'
            '<div><b>Toreto\'s Grill</b><span>en línea</span></div></div>')
    order = ('<div class="oc-in"><div class="oc-k">Pedido #2311</div><div class="oc-t">A domicilio</div>'
             '<div class="oc-s">Col. Trejo · lo lleva su motorista</div>'
             '<div class="oc-r"><span>3 × Almuerzo</span><b>L240</b></div>'
             '<div class="oc-s" style="margin-top:6px">2 con carne, 1 con pollo · más el envío</div></div>')
    msgs = [("m1", '<div class="wb out">donde estan ubicados?<small>1:40 p. m.</small></div>'),
            ("t1", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m2", f'<div class="wb in">¡Hola! Estamos en San Pedro Sula, {gen.ADDR}. Abrimos de lunes a domingo, de 11 am a 10:30 pm.<small>1:40 p. m.</small></div>'),
            ("m3", '<div class="wb in">Hoy hay almuerzo de L80 hasta las 3. ¿Se lo llevamos?<small>1:40 p. m.</small></div>'),
            ("m4", '<div class="wb out">si, 3 almuerzos a la colonia Trejo. 2 carne 1 pollo<small>1:41 p. m.</small></div>'),
            ("t2", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m5", f'<div class="ocard">{order}<div class="oc-b"><i id="okbtn"></i>Confirmar pedido</div></div>'),
            ("m6", '<div class="wb out">Confirmar pedido<small>1:41 p. m.</small></div>'),
            ("t3", '<div class="typ"><i></i><i></i><i></i></div>'),
            ("m7", '<div class="wb in">¡Listo! Ya está en la cocina. Le aviso cuando salga el motorista.<small>1:41 p. m.</small></div>')]
    wa = (f'<div class="wa">{head}<div class="wa-msgs">' + "".join(f'<div class="slot" id="{i}">{h}</div>' for i, h in msgs)
          + '</div><div class="wa-in">Mensaje</div></div>')
    ads = "".join(f'<div class="ad" id="ad{i}" style="top:{i * 70}px"><div class="h"><img src="assets/logo.jpg">toretosgrills · respuesta</div><p>{ADDR_REPLY}</p></div>' for i in range(4))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])
    sp = lambda c, top: f'<div class="sp sp-{c}" style="left:-260px;top:{top}px;width:1600px;height:1600px"></div>'

    body = "\n".join([
        vid,
        scene("hook", f'''
          <div class="shade"></div>
          <div class="reply" id="reply"><div class="av"></div><div><b>Comentario en su TikTok</b><p>No contestan whats</p><span>Respuesta del negocio: “Pida 9612-3466 yo le contesto”</span></div></div>
          <div class="caps">{cap("h", ["Un cliente", "*le escribió esto."])}</div>
          <div class="byline" id="hby">Casa Digital · para <b>Toreto's Grill</b></div>'''),
        scene("pitch", f'''
          {sp("red", -500)}
          <div class="caps">
            <div class="dim" id="easy"><div class="easy">{cap("p", ["Lo fácil sería", "venderle “el mejor", "bot del mundo”."])}<div class="strike" id="strike"></div></div></div>
            <div class="then">{cap("pt", ["Mejor primero,", "*unas preguntas."])}</div>
          </div>'''),
        scene("q1", f'''
          {sp("gold", 700)}
          <div class="caps"><div class="qn" id="q1n">Pregunta 1</div>{cap("q1", ["¿Cuántas veces", "escribió su dirección", "*a mano?"])}</div>
          <div class="addrs">{ads}</div>
          <div class="tally" id="tally"><b><span id="n1">0</span> veces</b><span>solo en sus respuestas de TikTok</span></div>'''),
        scene("q2", f'''
          {sp("green", 700)}
          <div class="caps"><div class="qn" id="q2n">Pregunta 2</div>{cap("q2", ["¿Quién contesta", "su WhatsApp mientras", "*usted está en la parrilla?"])}</div>
          <div class="ph-stage">{gen3.phone(wa, "phw", dark=True)}</div>
          <div class="ans" style="top:600px"><div class="chip" id="q2a"><i></i>Su WhatsApp, solo. A cualquier hora.</div></div>
          <div class="demo" id="q2d">Conversación de ejemplo · dirección, horario y precio reales</div>'''),
        scene("q3", f'''
          {sp("gold", -500)}
          <div class="caps"><div class="qn" id="q3n">Pregunta 3</div>{cap("q3", ["¿Cuánto efectivo", "*trae cada motorista?"])}</div>
          <div class="ans" style="top:680px"><div class="chip gold" id="q3a"><i></i>Cada entrega, anotada. Cuadra con un clic.</div></div>
          <div class="riders" id="riders"><div class="k">Motoristas · hoy</div>
            <div class="rd" id="rd0"><div class="n">Motorista 1<span>9 entregas</span></div><div class="c">L1,240</div><div class="st ok" id="rs0">✓ Cuadrado</div></div>
            <div class="rd" id="rd1"><div class="n">Motorista 2<span>7 entregas</span></div><div class="c">L980</div><div class="st ok" id="rs1">✓ Cuadrado</div></div>
            <div class="rd" id="rd2"><div class="n">Motorista 3<span>2 en camino</span></div><div class="c">L360</div><div class="st go" id="rs2">Trae L360</div></div>
            <div class="rtot" id="rtot"><span>Efectivo cobrado hoy</span><b>L<span id="ncash">0</span></b></div></div>
          <div class="demo" id="q3d">Ejemplo</div>'''),
        scene("q4", f'''
          {sp("red", 700)}
          <div class="caps"><div class="qn" id="q4n">Pregunta 4</div>{cap("q4", ["¿Sabe cuándo", "*se le acaba el carbón?"])}</div>
          <div class="ans" style="top:680px"><div class="chip gold" id="q4a"><i></i>El panel le avisa solo al proveedor.</div></div>
          <div class="stk" id="stk"><div class="k">Inventario · Toreto's Grill</div>
            <div class="row"><b>Carbón</b><span id="pl">3 <small>sacos</small></span></div>
            <div class="bar"><i id="plb"></i></div><div class="min">Mínimo: 6 sacos</div></div>
          <div class="chat2" id="chat2"><div class="hd"><i>🔥</i><div>Carbón<span>proveedor</span></div></div>
            <div class="b out" id="pm1"><div class="tag">Aviso automático</div>Buenas, le escribe Toreto's Grill. Se nos acaba el carbón: quedan 3 sacos, necesitamos 9. ¿A qué hora nos los trae?<small>11:42 am <em>✓✓</em></small></div>
            <div class="b in" id="pm2">Claro, se los llevo a las 4.<small>11:50 am</small></div></div>
          <div class="demo" id="q4d">Ejemplo</div>'''),
        scene("q5", f'''
          {sp("gold", -500)}
          <div class="caps"><div class="qn" id="q5n">Pregunta 5</div>{cap("q5", ["¿Cuántos almuerzos", "*faltan para los 1,000?"])}</div>
          <div class="quote" id="quote"><div class="h"><img src="assets/logo.jpg">Toretos Grills, respondiendo en TikTok</div><p>“Pronto 🔜 cuando vendamos 1000 almuerzos diarios en sps nos vamos a tegus”</p></div>
          <div class="goal" id="goal"><div class="k">Almuerzos al día · promedio de la semana</div>
            <div class="row"><b><span id="ng">0</span></b><span>de 1,000</span></div>
            <div class="bar"><i id="gb"></i></div><div class="s">El panel lleva la cuenta todos los días.</div></div>
          <div class="demo" id="q5d">Cita real · conteo de ejemplo</div>'''),
        scene("panel", f'''
          {sp("red", -500)}
          <div class="caps">{cap("pn", ["Si alguna respuesta", "fue “no sé”,", "*eso resolvemos."])}</div>
          <div class="shot" id="shot"><img src="assets/pv-hoy-m.jpg"></div>
          <div class="demo" id="pnd">Panel Toreto's Grill · datos de ejemplo</div>'''),
        scene("close", f'''
          {sp("gold", 700)}
          <div class="caps">{cap("cl", ["No vendemos", "un sistema.", "*Resolvemos lo que", "*Toreto's necesita."])}</div>
          <div class="cta2" id="cta">
            <div class="ic">{gen3.HOUSE}</div>
            <div class="t">Casa Digital</div>
            <div class="s">Escríbanos y se lo mostramos.</div>
            <div class="wa2"><span>WhatsApp</span>{gen3.WHATSAPP}</div>
            <div class="sendb" id="sendb"><span class="s1" id="sb1">Escribir</span><span class="s2" id="sb2">Enviado ✓</span></div>
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

    css = (gen3.CSS.replace("$heroB", "#2a0806").replace("$hero", "#D8261C").replace("$acc", gen.GOLD).replace("$pri", gen.GOLD)
           .replace("$washA", "rgba(0,0,0,0)").replace("$washB", "rgba(0,0,0,0)").replace("$sitebg", "#0B141A").replace("$siteink", "#fff")
           .replace("$dweight", "400").replace("$dcase", "uppercase").replace("$dtrack", "-0.01em")
           .replace("$italface", "").replace("$ital", '"Display"').replace("$introsizepx", "112px"))
    css += gen.CSS_BASE + gen.CSS_T + CSS_2
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    j6 = gen6.JS
    # gen6's outro starts at bar 37; ours at 29
    js = (j6[:j6.index("// 1 · intro")] + gen.JS_T[:gen.JS_T.index("// 1 · intro")] + JS_2
          + re.sub(r"K\((\d+(?:\.\d+)?)\)", lambda m: f"K({float(m.group(1)) - 8:g})", j6[j6.index("// 11 · outro"):])
          ).replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = (gen3.HTML.replace("$title", "Casa Digital x Toreto's Grill").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)).replace('data-fade-out="2.5"', 'data-fade-out="4"')
            .replace('content="width=1920, height=1080"', 'content="width=1080, height=1920"')
            .replace('data-width="1920" data-height="1080"', 'data-width="1080" data-height="1920"')
            .replace('data-resolution="landscape"', 'data-resolution="portrait"'))
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


JS_2 = r'''
function say(p, n, t, gap) { for (let i = 0; i < n; i++) rise("#" + p + "c" + i + " .w", t + i * (gap || .55), { d: 1.3, st: .06, y: 30 }); }

// 1 · hook: a real comment over their own pinned video
tl.fromTo("#reply", { opacity: 0, y: -40, scale: .96 }, { opacity: 1, y: 0, scale: 1, duration: 1.2, ease: "back.out(1.4)" }, .5);
say("h", 2, K(1), .6);
rise("#hby", K(1.8), { d: 1.4 });
tl.to("#bgv", { opacity: .35, duration: 1.5, ease: "power1.inOut" }, K(2.3));

// 2 · the easy pitch, crossed out; questions first
say("p", 3, K(3) + .2, .45);
tl.fromTo("#strike", { scaleX: 0 }, { scaleX: 1, duration: .8, ease: "power3.inOut" }, K(4.2));
say("pt", 2, K(4.6), .55);

// 3 · how many times did you type the address
rise("#q1n", K(6), { d: 1.1 }); say("q1", 3, K(6) + .3, .45);
[0, 1, 2, 3].forEach(i => tl.fromTo("#ad" + i, { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1, ease: SOFT }, K(6.9) + i * .35));
rise("#tally", K(7.5), { d: 1.2 });
count("n1", 0, 10, K(7.5) + .2, n => String(n), 1.8);

// 4 · who answers WhatsApp while you're at the grill
rise("#q2n", K(9), { d: 1.1 }); say("q2", 3, K(9) + .3, .5);
tl.fromTo("#phw", { y: 700, rotationY: -14, rotationX: 6 }, { y: 0, rotationY: -4, rotationX: 2, duration: 2.2, ease: SOFT }, K(9.6));
tl.to("#phw", { rotationY: 4, rotationX: 0, duration: K(14) - K(10.6), ease: "sine.inOut" }, K(10.6));
rise("#q2a", K(10.4), { d: 1.2 });
rise("#q2d", K(10), { d: 1.2 });
show("m1", K(10.3)); show("t1", K(10.7)); dots("t1", K(10.7) + .2); hide("t1", K(11.1)); show("m2", K(11.1)); show("m3", K(11.6));
show("m4", K(12.1)); show("t2", K(12.5)); dots("t2", K(12.5) + .2); hide("t2", K(12.9)); show("m5", K(12.9));
tl.fromTo("#okbtn", { opacity: 0 }, { opacity: 1, duration: .25, yoyo: true, repeat: 1 }, K(13.3));
show("m6", K(13.4)); show("t3", K(13.6)); hide("t3", K(13.8)); show("m7", K(13.8));

// 5 · how much cash does each rider bring
rise("#q3n", K(14), { d: 1.1 }); say("q3", 2, K(14) + .3, .5);
rise("#q3a", K(15), { d: 1.2 });
tl.fromTo("#riders", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(14.6));
[14.9, 15.2, 15.5].forEach((k, i) => rise("#rd" + i, K(k), { y: 20, d: 1.1 }));
[0, 1, 2].forEach(i => tl.fromTo("#rs" + i, { opacity: 0, scale: .85 }, { opacity: 1, scale: 1, duration: .8, ease: SOFT }, K(15.9) + i * .3));
rise("#rtot", K(15.9), { y: 20, d: 1.1 });
count("ncash", 0, 2580, K(15.9) + .3, n => n.toLocaleString("en-US"), 1.5);
rise("#q3d", K(14.6), { d: 1.2 });

// 6 · when does the charcoal run out
rise("#q4n", K(17), { d: 1.1 }); say("q4", 2, K(17) + .3, .5);
rise("#q4a", K(18), { d: 1.2 });
tl.fromTo("#stk", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.6, ease: SOFT }, K(17.6));
tl.fromTo("#plb", { scaleX: 1 }, { scaleX: .5, duration: 1.4, ease: FINE }, K(17.9));
tl.fromTo("#chat2", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.4, ease: SOFT }, K(18.3));
rise("#pm1", K(18.5), { y: 20, d: 1.1 });
rise("#pm2", K(19.2), { y: 20, d: 1.1 });
rise("#q4d", K(17.6), { d: 1.2 });

// 7 · how many lunches to reach his 1,000
rise("#q5n", K(20), { d: 1.1 }); say("q5", 2, K(20) + .3, .5);
tl.fromTo("#quote", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(20.6));
tl.fromTo("#goal", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.6, ease: SOFT }, K(21.2));
tl.fromTo("#gb", { scaleX: 0 }, { scaleX: .187, duration: 2.2, ease: FINE }, K(21.5));
count("ng", 0, 187, K(21.5), n => String(n), 2.2);
rise("#q5d", K(20.6), { d: 1.2 });

// 8 · every answer on his phone: the real panel
say("pn", 3, K(23) + .2, .55);
tl.fromTo("#shot", { opacity: 0, y: 120, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(23.5));
tl.fromTo("#shot img", { objectPosition: "50% 0%" }, { objectPosition: "50% 22%", duration: K(26) - K(24.5), ease: FINE }, K(24.5));
rise("#pnd", K(23.8), { d: 1.2 });

// 9 · close with a question
say("cl", 4, K(26) + .2, .45);
tl.fromTo("#sendb", { scale: 1 }, { scale: .92, duration: .18, yoyo: true, repeat: 1, ease: "power2.out" }, K(28.1));
tl.to("#sb1", { opacity: 0, duration: .3 }, K(28.1) + .2); tl.fromTo("#sb2", { opacity: 0 }, { opacity: 1, duration: .4 }, K(28.1) + .3);
tl.to("#sendb", { background: "#2C2C2E", color: "#F5F5F7", duration: .4 }, K(28.1) + .2);
tl.fromTo("#cta", { opacity: 0, y: 90, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 2, ease: SOFT }, K(27));
float("#cta", K(27.8), K(29) - K(27.8));

'''

if __name__ == "__main__":
    print(build())
