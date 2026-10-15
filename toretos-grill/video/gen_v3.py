#!/usr/bin/env python3
"""Toreto's Grill pitch video v3 (2026-10-15), vertical 1080x1920 for WhatsApp.
rodrigo liked the v2 pitch (questions first, the "sell me this pen" method) but not its editing (short centered
captions, opening on the owner's TikTok clip). v3 keeps the v2 script and goes back to the look of the first
vertical video (gen.py --vertical): their logo intro, eyebrow + big left-aligned headline + sub sentence, gold
keywords, soft lights, the visual under the text.
Story: intro -> real comments, answered one by one -> "we could tell you we have the best bot; better, some
questions first" -> 5 questions, each answered on screen (address typed by hand 10 times, who answers WhatsApp,
rider cash, charcoal, the 1,000 lunches) -> "if any answer was 'I don't know', that's what we solve" (real panel)
-> "we don't sell a system" + WhatsApp -> outro."""
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
SLUG = "toretos-grill-v3"
SCENES = [("intro", 0, 3), ("asks", 3, 7), ("pitch", 7, 10), ("q1", 10, 13), ("q2", 13, 19), ("q3", 19, 22),
          ("q4", 22, 25), ("q5", 25, 28), ("panel", 28, 31), ("us", 31, 34), ("end", 34, 38)]
TOTAL = K(38)
ADDR_REPLY = "San Pedro Sula, colonia ideal 6 y 7 calle 15 avenida atrás de megamall 📲 9612-3466"  # verbatim, tiktok-respuestas.md


def gold(t):
    return f'<span class="gold">{words(t)}</span>'


def head(p, eb, lines, sub=None, m=True):
    """Eyebrow, headline lines (a line starting with * is gold) and an optional sub sentence, like the first video."""
    h = f'<div class="eb g" id="{p}0">{eb}</div>'
    for i, l in enumerate(lines):
        h += f'<div class="h1{" m" if m else ""}" id="{p}{i + 1}">{gold(l[1:]) if l.startswith("*") else words(l)}</div>'
    if sub:
        h += f'<div class="sub" id="{p}s">{words(sub)}</div>'
    return h


CSS_3 = r'''
.h1.m{font-size:80px;}
.sub{font-size:33px;}
/* the easy pitch, crossed out */
.easy{position:relative;display:inline-block;}
.dimh{color:#6E6E73;}
.strike{position:absolute;left:-8px;right:-8px;top:54%;height:8px;margin-top:-4px;border-radius:4px;background:#FF5E57;transform-origin:0 50%;}
.then{margin-top:60px;}
#pitch .left{top:520px;}
/* q1: the address, typed by hand */
.addrs{position:absolute;left:90px;right:90px;top:860px;height:420px;}
.ad{position:absolute;left:0;right:0;background:linear-gradient(180deg,#161618,#111113);border-radius:26px;padding:22px 28px;box-shadow:0 0 0 1px rgba(255,255,255,.07),0 24px 60px rgba(0,0,0,.55);}
.ad .h{display:flex;align-items:center;gap:12px;font-size:22px;color:#8E8E93;font-weight:500;}
.ad .h img{width:36px;height:36px;border-radius:50%;}
.ad p{margin-top:10px;font-size:32px;line-height:1.3;color:#F5F5F7;font-weight:500;}
.tally{position:absolute;left:90px;right:90px;top:1330px;}
.tally b{font-size:150px;font-weight:600;letter-spacing:-.05em;line-height:1;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;font-variant-numeric:tabular-nums;}
.tally b span{display:inline;}
.tally>span{display:block;font-size:30px;color:#8E8E93;margin-top:4px;}
/* q2: question, then the answer, in the same place */
#q2 .lgrp{top:50%;}
.goal .row b span{font-size:inherit;color:inherit;}
/* panel on the owner's phone */
.shot{top:820px;height:1000px;overflow:hidden;box-shadow:0 60px 140px rgba(0,0,0,.7);}
.shot img{height:972px;}
/* the close */
#us .left{top:110px;height:760px;}
.cta2{left:260px;top:960px;height:660px;}
.sendb{position:relative;margin-top:22px;width:300px;height:64px;border-radius:40px;background:#F5F5F7;color:#0B0B0C;font-size:26px;font-weight:600;}
.sendb span{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;}
.sendb .s2{opacity:0;}
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
    for n in ("logo.jpg", "pv-hoy-m.jpg"):
        shutil.copy(os.path.join(SRC, n), A(n))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "toretos-grill-v3", "name": "Casa Digital x Toreto's Grill v3"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    sp = lambda c, top: f'<div class="sp sp-{c}" style="left:-260px;top:{top}px;width:1600px;height:1600px"></div>'
    comments = ["donde estan ubicados?", "y pa domicilio", "Dan factura con rtn ?", "No contestan whats"]  # verbatim
    cms = "".join(f'<div class="cm" id="cm{i}"><div class="cm-h"><i></i>Comentario en su TikTok</div><p>{t}</p></div>' for i, t in enumerate(comments))
    wa_head = ('<div class="wa-h"><span class="bk">‹</span><div class="wa-av"><img src="assets/logo.jpg"></div>'
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
    wa = (f'<div class="wa">{wa_head}<div class="wa-msgs">' + "".join(f'<div class="slot" id="{i}">{h}</div>' for i, h in msgs)
          + '</div><div class="wa-in">Mensaje</div></div>')
    ads = "".join(f'<div class="ad" id="ad{i}" style="top:{i * 74}px"><div class="h"><img src="assets/logo.jpg">toretosgrills · respuesta en TikTok</div><p>{ADDR_REPLY}</p></div>' for i in range(3))
    whys = ["Ya lo armamos con su menú y su dirección.", "Se instala en 14 días.", "Soporte por WhatsApp, en español."]
    whys_html = "".join(f'<div class="wy2" id="wy{i}"><i>✓</i><span>{words(t)}</span></div>' for i, t in enumerate(whys))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          {sp("red", -500)}{sp("gold", 900)}
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("una propuesta para")}</div>
            <div class="ilogo" id="ilogo"><img src="assets/logo.jpg"></div>
            <div class="iname" id="iname">Toreto's Grill</div>
          </div>'''),
        scene("asks", f'''
          {sp("gold", 700)}
          <div class="cms">{cms}</div>
          <div class="left">
            <div class="lgrp" id="ag1">{head("a", "Comentarios reales", ["Todos los días", "le preguntan."], m=False)}</div>
            <div class="lgrp" id="ag2">{head("b", "Hoy", ["Contestan a mano,", "*uno por uno."], m=False)}</div>
          </div>'''),
        scene("pitch", f'''
          {sp("red", -500)}
          <div class="left">
            <div class="eb g" id="p0">Antes de venderle nada</div>
            <div class="h1 m dimh" id="p1"><span class="easy">{words("Podríamos decirle")}<i class="strike" id="strike"></i></span></div><div class="h1 m dimh" id="p2"><span class="easy">{words("“tenemos el mejor bot”.")}<i class="strike" id="strike2"></i></span></div>
            <div class="then"><div class="h1 m" id="p3">{words("Mejor, primero,")}</div><div class="h1 m" id="p4">{gold("unas preguntas.")}</div></div>
          </div>'''),
        scene("q1", f'''
          {sp("gold", 700)}
          <div class="left">{head("q1", "Pregunta 1", ["¿Cuántas veces", "escribió su dirección", "*a mano?"])}</div>
          <div class="addrs">{ads}</div>
          <div class="tally" id="tally"><b><span id="n1">0</span> veces</b><span>la misma dirección, escrita a mano en sus respuestas de TikTok. El bot la manda sola, con el pin del mapa.</span></div>'''),
        scene("q2", f'''
          {sp("green", 700)}
          <div class="ph-stage">{gen3.phone(wa, "phw", dark=True)}</div>
          <div class="left">
            <div class="lgrp" id="qg1">{head("q2", "Pregunta 2", ["¿Quién contesta", "su WhatsApp mientras", "*usted está en la parrilla?"])}</div>
            <div class="lgrp" id="qg2">{head("r2", "La respuesta", ["Su WhatsApp,", "*que contesta solo."], "Dirección, horario, menú del día y pedidos a domicilio, a cualquier hora.")}</div>
          </div>
          <div class="demo" id="q2d">Conversación de ejemplo · dirección, horario y precio reales</div>'''),
        scene("q3", f'''
          {sp("gold", -500)}
          <div class="left">{head("q3", "Pregunta 3", ["¿Cuánto efectivo", "*trae cada motorista?"], "Cada entrega queda anotada con lo que cobró. Al volver, el efectivo se cuadra con un clic.")}</div>
          <div class="riders" id="riders"><div class="k">Motoristas · hoy</div>
            <div class="rd" id="rd0"><div class="n">Motorista 1<span>9 entregas</span></div><div class="c">L1,240</div><div class="st ok" id="rs0">✓ Cuadrado</div></div>
            <div class="rd" id="rd1"><div class="n">Motorista 2<span>7 entregas</span></div><div class="c">L980</div><div class="st ok" id="rs1">✓ Cuadrado</div></div>
            <div class="rd" id="rd2"><div class="n">Motorista 3<span>2 en camino</span></div><div class="c">L360</div><div class="st go" id="rs2">Trae L360</div></div>
            <div class="rtot" id="rtot"><span>Efectivo cobrado hoy</span><b>L<span id="ncash">0</span></b></div></div>
          <div class="demo" id="q3d">Ejemplo</div>'''),
        scene("q4", f'''
          {sp("red", 700)}
          <div class="left">{head("q4", "Pregunta 4", ["¿Sabe cuándo", "*se le acaba el carbón?"], "El panel ve el inventario y le escribe solo al proveedor. La parrilla nunca se queda sin fuego.")}</div>
          <div class="stk" id="stk"><div class="k">Inventario · Toreto's Grill</div>
            <div class="row"><b>Carbón</b><span id="pl">3 <small>sacos</small></span></div>
            <div class="bar"><i id="plb"></i></div><div class="min">Mínimo: 6 sacos</div></div>
          <div class="chat2" id="chat2"><div class="hd"><i>🔥</i><div>Carbón<span>proveedor</span></div></div>
            <div class="b out" id="pm1"><div class="tag">Aviso automático</div>Buenas, le escribe Toreto's Grill. Se nos acaba el carbón: quedan 3 sacos, necesitamos 9. ¿A qué hora nos los trae?<small>11:42 am <em>✓✓</em></small></div>
            <div class="b in" id="pm2">Claro, se los llevo a las 4.<small>11:50 am</small></div></div>
          <div class="demo" id="q4d">Ejemplo</div>'''),
        scene("q5", f'''
          {sp("gold", -500)}
          <div class="left">{head("q5", "Pregunta 5", ["¿Cuántos almuerzos", "*faltan para los 1,000?"], "Para llegar ahí, cada pedido tiene que entrar, salir y cobrarse sin depender de que alguien lo vea a tiempo.")}</div>
          <div class="quote" id="quote"><div class="h"><img src="assets/logo.jpg">Toretos Grills, respondiendo en TikTok</div><p>“Pronto 🔜 cuando vendamos 1000 almuerzos diarios en sps nos vamos a tegus”</p></div>
          <div class="goal" id="goal"><div class="k">Almuerzos al día · promedio de la semana</div>
            <div class="row"><b><span id="ng">0</span></b><span>de 1,000</span></div>
            <div class="bar"><i id="gb"></i></div><div class="s">El panel lleva la cuenta todos los días.</div></div>
          <div class="demo" id="q5d">Cita real · conteo de ejemplo</div>'''),
        scene("panel", f'''
          {sp("red", -500)}
          <div class="shot" id="shot"><img src="assets/pv-hoy-m.jpg"></div>
          <div class="left">{head("pn", "Panel del dueño", ["Si alguna respuesta", "fue “no sé”,", "*eso resolvemos."], "Pedidos, motoristas, inventario y facturas con RTN, en su celular.")}</div>
          <div class="demo" id="pnd">Datos de ejemplo</div>'''),
        scene("us", f'''
          {sp("gold", 700)}
          <div class="left">
            {head("u", "Casa Digital", ["No vendemos un sistema.", "*Resolvemos lo que", "*Toreto's necesita."])}
            <div class="whys2">{whys_html}</div>
          </div>
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
    css += gen.CSS_BASE + gen.CSS_T + gen.CSS_V + CSS_3
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    j6 = gen6.JS
    # gen6's outro starts at bar 37; ours at 34
    js = (j6[:j6.index("// 1 · intro")] + gen.JS_T[:gen.JS_T.index("// 1 · intro")] + JS_3
          + re.sub(r"K\((\d+(?:\.\d+)?)\)", lambda m: f"K({float(m.group(1)) - 3:g})", j6[j6.index("// 11 · outro"):])
          ).replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = (gen3.HTML.replace("$title", "Casa Digital x Toreto's Grill").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)).replace('data-fade-out="2.5"', 'data-fade-out="4"')
            .replace('content="width=1920, height=1080"', 'content="width=1080, height=1920"')
            .replace('data-width="1920" data-height="1080"', 'data-width="1080" data-height="1920"')
            .replace('data-resolution="landscape"', 'data-resolution="portrait"'))
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


JS_3 = r'''
// headline in the first video's rhythm: eyebrow, then each line, then the sub sentence
function title(p, n, t, sub) {
  rise("#" + p + "0", t, { d: 1.2 });
  for (let i = 1; i <= n; i++) rise("#" + p + i + " .w", t + .3 * i, i === n ? { d: 1.8 } : {});
  if (sub !== undefined) rise("#" + p + "s .w", sub, { st: .03 });
}

// 1 · intro
rise("#icd", 0.4, { d: 2 });
rise("#ipres .w", K(.9), { d: 1.6, st: .12 });
tl.fromTo("#ilogo", { opacity: 0, scale: .86, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(1.3));
tl.fromTo("#iname", { opacity: 0, y: 30, filter: "blur(20px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.4, ease: SOFT }, K(1.7));

// 2 · real comments, answered by hand
title("a", 2, K(3));
[3.3, 3.8, 4.3, 4.8].forEach((k, i) => rise("#cm" + i, K(k), { y: 40, d: 1.6 }));
out("#ag1", K(5.4) - .8);
title("b", 2, K(5.4));

// 3 · the easy pitch, crossed out; questions first
title("p", 2, K(7));
tl.fromTo("#strike", { scaleX: 0 }, { scaleX: 1, duration: .7, ease: "power3.inOut" }, K(8));
tl.fromTo("#strike2", { scaleX: 0 }, { scaleX: 1, duration: .7, ease: "power3.inOut" }, K(8) + .5);
rise("#p3 .w", K(8.5)); rise("#p4 .w", K(8.5) + .4, { d: 1.8 });

// 4 · question 1: the address typed by hand
title("q1", 3, K(10));
[0, 1, 2].forEach(i => tl.fromTo("#ad" + i, { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.2, ease: SOFT }, K(10.7) + i * .45));
rise("#tally", K(11.4), { d: 1.4 });
count("n1", 0, 10, K(11.4) + .2, n => String(n), 1.8);

// 5 · question 2: who answers WhatsApp at the grill; then the answer, and the bot at work
title("q2", 3, K(13));
tl.fromTo("#phw", { y: 700, rotationY: -16, rotationX: 6 }, { y: 0, rotationY: -6, rotationX: 2, duration: 2.4, ease: SOFT }, K(13.6));
tl.to("#phw", { rotationY: 4, rotationX: 0, duration: K(19) - K(14.6), ease: "sine.inOut" }, K(14.6));
rise("#q2d", K(14), { d: 1.2 });
out("#qg1", K(15.2) - .8);
title("r2", 2, K(15.2), K(15.2) + 1.2);
show("m1", K(14.2)); show("t1", K(14.7)); dots("t1", K(14.7) + .3); hide("t1", K(15.2)); show("m2", K(15.2)); show("m3", K(15.8));
show("m4", K(16.4)); show("t2", K(16.9)); dots("t2", K(16.9) + .3); hide("t2", K(17.4)); show("m5", K(17.4));
tl.fromTo("#okbtn", { opacity: 0 }, { opacity: 1, duration: .25, yoyo: true, repeat: 1 }, K(18));
show("m6", K(18.1)); show("t3", K(18.4)); hide("t3", K(18.7)); show("m7", K(18.7));

// 6 · question 3: rider cash
title("q3", 2, K(19), K(20.2));
tl.fromTo("#riders", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(19) + .3);
[19.8, 20.2, 20.6].forEach((k, i) => rise("#rd" + i, K(k), { y: 20, d: 1.2 }));
[0, 1, 2].forEach(i => tl.fromTo("#rs" + i, { opacity: 0, scale: .85 }, { opacity: 1, scale: 1, duration: .9, ease: SOFT }, K(21) + i * .35));
rise("#rtot", K(21), { y: 20, d: 1.2 });
count("ncash", 0, 2580, K(21) + .3, n => n.toLocaleString("en-US"), 1.6);
rise("#q3d", K(19.6), { d: 1.2 });

// 7 · question 4: the charcoal
title("q4", 2, K(22), K(23.1));
tl.fromTo("#stk", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(22) + .3);
tl.fromTo("#plb", { scaleX: 1 }, { scaleX: .5, duration: 1.6, ease: FINE }, K(22.5));
tl.fromTo("#chat2", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.6, ease: SOFT }, K(23));
rise("#pm1", K(23.3), { y: 20, d: 1.2 });
rise("#pm2", K(24.1), { y: 20, d: 1.2 });
rise("#q4d", K(22.6), { d: 1.2 });

// 8 · question 5: the 1,000 lunches
title("q5", 2, K(25), K(26.2));
tl.fromTo("#quote", { opacity: 0, y: 60, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2, ease: SOFT }, K(25) + .3);
tl.fromTo("#goal", { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.8, ease: SOFT }, K(25.8));
tl.fromTo("#gb", { scaleX: 0 }, { scaleX: .187, duration: 2.4, ease: FINE }, K(26.3));
count("ng", 0, 187, K(26.3), n => String(n), 2.4);
rise("#q5d", K(25.6), { d: 1.2 });

// 9 · the bridge: the real panel
title("pn", 3, K(28), K(29.3));
tl.fromTo("#shot", { opacity: 0, y: 80, filter: "blur(16px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 2.2, ease: SOFT }, K(28) + .2);
tl.fromTo("#shot img", { objectPosition: "50% 0%" }, { objectPosition: "50% 20%", duration: K(31) - K(29.5), ease: FINE }, K(29.5));
rise("#pnd", K(28.5), { d: 1.2 });

// 10 · we don't sell a system
title("u", 3, K(31));
[32, 32.4, 32.8].forEach((k, i) => rise("#wy" + i + " .w, #wy" + i + " i", K(k), { st: .04, d: 1.3 }));
tl.fromTo("#cta", { opacity: 0, y: 90, scale: .95 }, { opacity: 1, y: 0, scale: 1, duration: 2.2, ease: SOFT }, K(31.5));
tl.fromTo("#sendb", { scale: 1 }, { scale: .92, duration: .18, yoyo: true, repeat: 1, ease: "power2.out" }, K(33.1));
tl.to("#sb1", { opacity: 0, duration: .3 }, K(33.1) + .2); tl.fromTo("#sb2", { opacity: 0 }, { opacity: 1, duration: .4 }, K(33.1) + .3);
tl.to("#sendb", { background: "#2C2C2E", color: "#F5F5F7", duration: .4 }, K(33.1) + .2);

'''

if __name__ == "__main__":
    print(build())
