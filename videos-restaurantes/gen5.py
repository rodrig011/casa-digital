#!/usr/bin/env python3
"""Café Honoré audit video v2: slower, more readable cut of gen4 on rodrigo's second track
("Still Buggin", 194 BPM; one bar of 8 beats = 2.474 s). Every scene starts on a bar line.
Story: we visited the site like a new customer -> what we found (numbered findings on real
screenshots) -> what that costs -> the proposal explained -> why us -> Clientia Tech outro."""
import json, os, shutil
import gen3, gen4
from gen2 import MARK, words, rgba, lum, lift, hexrgb, ribbons, DEPS, HERE
from gen4 import MARKS, PID, shot_file, zoom_plan

OUT = os.path.join(HERE, "videos5")
P0, BAR = 0.0012, 8 * 0.3092783
K = lambda k: round(P0 + BAR * k, 3)
SCENES = [("intro", 0, 3), ("concept", 3, 6), ("home", 6, 9), ("look", 9, 15), ("links", 15, 19), ("order", 19, 24),
          ("calm", 24, 26), ("leak", 26, 30), ("prop", 30, 35), ("why", 35, 38), ("end", 38, 42)]
TOTAL = K(42)
SEQ = {
    "home": [("inicio", [7.5])],
    "look": [("anos", [10.3]), ("eventos", [11.6]), ("disfruta", [12.9, 14.1])],
    "links": [("menu-nav", [16.3]), ("noticias", [17.6])],
}
# findings are numbered in the order they appear
ORDER = [(n, i) for sc in ("home", "look", "links") for n, _ in SEQ[sc] for i in range(len(MARKS[n]))]
NFIND = len(ORDER) + 2   # + menu prices + WhatsApp orders


def shot_phone(name, proj):
    pid = PID(name)
    f = shot_file(name)
    ext = os.path.splitext(f)[1].lower()
    shutil.copy(f, os.path.join(proj, "assets", name + ext))
    boxes = "".join(f'<div class="mk" id="{pid}-mk{i}" style="left:{x*100}%;top:{y*100}%;width:{w*100}%;height:{h*100}%"></div>'
                    for i, (_, (x, y, w, h)) in enumerate(MARKS[name]))
    caps = "".join(f'<div class="cap" id="{pid}-cap{i}"><i></i><div><em>Hallazgo {ORDER.index((name, i)) + 1:02d}</em>'
                   f'<span class="cl">{words(label)}</span></div></div>' for i, (label, _) in enumerate(MARKS[name]))
    return (f'<div class="zoomer" id="{pid}-z"><div class="ph-stage audit"><div class="iph" id="{pid}"><div class="iph-scr"><div class="island"></div>'
            f'<div class="pan"><img class="shot" src="assets/{name}{ext}">{boxes}</div></div></div></div></div><div class="caps">{caps}</div>')


def seq_js(sc, headline):
    start = next(a for i, a, b in SCENES if i == sc)
    out, prev = [], None
    for n, beats in SEQ[sc]:
        bs = "[" + ", ".join(f"K({b})" for b in beats) + "]"
        if prev is None:
            out.append(f'audit("{PID(n)}", K({start}), {bs});')
            out.append(f'out("{headline}", K({beats[0]}) - 1.9, .9);')
        else:
            out.append(f'swap("{PID(prev[0])}", {len(prev[1])}, "{PID(n)}", {bs});')
        prev = (n, beats)
    return "\n".join(out)


CSS5 = r'''
.cap{align-items:center;width:max-content;max-width:1100px;}
.cap em{display:block;font-style:normal;font-size:22px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#FF6961;margin-bottom:8px;}
.cap .cl{display:block;}
.mk{box-shadow:0 0 0 6px rgba(255,59,48,.18),0 0 40px rgba(255,59,48,.35);}
.urlbar{position:absolute;left:1000px;top:420px;width:820px;height:120px;border-radius:60px;background:#fff;box-shadow:0 40px 100px rgba(0,0,0,.14),0 0 0 1px rgba(0,0,0,.05);display:flex;align-items:center;padding:0 50px;gap:22px;font-size:40px;color:#111113;}
.urlbar .lock{font-size:34px;color:#86868B;}
.url{white-space:nowrap;overflow:hidden;display:inline-block;}
.caret{width:4px;height:52px;background:#0A84FF;border-radius:2px;}
.findn{position:absolute;left:1000px;top:600px;width:820px;font-size:42px;line-height:1.25;font-weight:500;color:#86868B;}
.findn b{color:#FF3B30;font-weight:700;}
.props{margin-top:46px;display:flex;flex-direction:column;gap:30px;}
.pr{display:flex;gap:26px;align-items:flex-start;}
.pr i{flex:none;width:64px;height:64px;border-radius:20px;background:#111113;color:#FFD60A;font-style:normal;font-size:30px;font-weight:700;display:flex;align-items:center;justify-content:center;}
.pr b{display:block;font-size:44px;font-weight:600;letter-spacing:-.025em;line-height:1.1;}
.pr span{display:block;font-size:30px;color:#6E6E73;margin-top:6px;}
#prop .left{width:900px;}
#prop .h1{font-size:100px;}
.eyebrow2{font-size:34px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#86868B;margin-bottom:16px;}
#why .ctacard{left:1180px;}
'''


def build(r):
    c = r["colors"]; f = r["fonts"]
    hero = c["primary"] if lum(c["primary"]) < 0.45 else c["accent"]
    acc = lift(c["accent"], 0.5); pri = lift(c["primary"], 0.38)
    proj = os.path.join(OUT, r["slug"])
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    shutil.copy(os.path.join(HERE, "musica2.mp3"), os.path.join(proj, "assets", "musica.mp3"))
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
    json.dump({"id": r["slug"] + "-auditoria", "name": f"Casa Digital x {r['name']} · auditoría"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    hl = gen3.hl
    site_html = (f'<div class="ph-scroll" id="phs"><div class="site"><div class="site-nav"><b>{r["name"]}</b><span>Menú&nbsp;&nbsp;Reservas</span></div>'
                 f'<div class="site-name">{"<br>".join(r["nameLines"])}</div><div class="site-tag">{r["tagline"]}</div>'
                 f'<div class="site-btns"><span class="b1">Pedir ahora</span><span class="b2">Reservar</span></div></div></div>'
                 '<div class="notif" id="notif"><div class="n-ic">' + gen3.HOUSE + '</div><div><b>Casa Digital</b>'
                 '<span>Nuevo pedido pagado con tarjeta ✓</span></div><i>ahora</i></div>')
    leaks = [("Busca el horario o el teléfono", "No aparece en la página. Llama a otro lugar."),
             ("Abre el menú para pedir", "Ve precios vacíos y un putter de golf. Desconfía."),
             ("Busca promociones o novedades", "La última noticia es de la Navidad de 2021."),
             ("Pide a domicilio a las 9 pm", "Escribe al WhatsApp y espera a que alguien conteste.")]
    leaks_html = "".join(f'<div class="lk" id="lk{i}"><div class="lk-n">{i + 1}</div><div><b>{a}</b><span>{b}</span></div></div>'
                         for i, (a, b) in enumerate(leaks))
    props = [("Pedidos y pagos en línea", "El pedido llega armado y pagado con tarjeta."),
             ("Un menú vivo", "Lo cambian desde el celular, sin errores."),
             ("Reservas, eventos y tienda gourmet", "Todo en un solo lugar, con su dominio.")]
    props_html = "".join(f'<div class="pr" id="pr{i}"><i>{i + 1}</i><div><b>{a}</b><span>{b}</span></div></div>' for i, (a, b) in enumerate(props))
    whys = ["Hecha a la medida, no una plantilla.", "0% de comisión por pedido.", "Lista en 14 días.", "Garantía: 50 pedidos pagados en 90 días."]
    whys_html = "".join(f'<div class="wy" id="wy{i}"><i>✓</i><span>{words(t)}</span></div>' for i, t in enumerate(whys))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])
    seq = lambda sc: "".join(shot_phone(n, proj) for n, _ in SEQ[sc])

    body = "\n".join([
        scene("intro", f'''
          <div class="wash w1"></div><div class="wash w2"></div>
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("una propuesta para")}</div>
            <div class="disp intro-name" id="iname">{r["name"]}</div>
          </div>'''),
        scene("concept", f'''
          <div class="wash w4"></div>
          <div class="urlbar" id="ub"><span class="lock">🔒</span><span class="url" id="url">honorelifestyle.com/cafe-honore</span><span class="caret" id="caret"></span></div>
          <div class="findn" id="fn">Encontramos <b>{NFIND} cosas</b> que le cuestan clientes.</div>
          <div class="left narrow">
            <div class="grp" id="cg1"><div class="h1" id="c1">{words("Entramos a")}</div><div class="h1" id="c2">{words("su página")}</div><div class="h1" id="c3">{words("como un")} {hl("cliente nuevo.")}</div></div>
          </div>'''),
        scene("home", f'''
          <div class="wash w4"></div>
          {seq("home")}
          <div class="left narrow">
            <div class="grp" id="hg2"><div class="h1" id="h3">{words("Lo primero")}</div><div class="h1" id="h4">{words("que")} {hl("ve.")}</div></div>
          </div>'''),
        scene("look", f'''
          <div class="wash w3"></div>
          {seq("look")}
          <div class="left narrow">
            <div class="h1" id="m1">{words("Al bajar,")}</div>
            <div class="h1" id="m2">{words("se ve")}</div>
            <div class="h1" id="m3">{hl("olvidada.")}</div>
          </div>'''),
        scene("links", f'''
          <div class="wash w4"></div>
          {seq("links")}
          <div class="left narrow">
            <div class="h1" id="l1">{words("Una página")}</div>
            <div class="h1" id="l2">{words("que se quedó")}</div>
            <div class="h1" id="l3">{words("en")} {hl("2021.")}</div>
          </div>'''),
        scene("order", f'''
          <div class="wash w5"></div>
          <div class="qcard" id="qc">
            <div class="qc-k">Hallazgo {len(ORDER) + 1:02d} · copiado de su menú en línea</div>
            <div class="qrow" id="qr0"><span>Build Your Salad</span><b>Lps.</b><em>sin precio</em></div>
            <div class="qrow" id="qr1"><span class="noname">(sin nombre)</span><b>Lps.0</b><em>sin nombre</em></div>
            <div class="qrow" id="qr2"><span>ACE EXECUTIVE PUTTER SET WITH WOODEN CASE</span><b>Lps.1445.00</b><em>un putter de golf</em></div>
          </div>
          <div class="chat" id="chat2">
            <div class="ch-head"><div class="ch-av" style="background:{hero}">C</div><div><b>Café Honoré · Pedidos</b><span>WhatsApp</span></div></div>
            <div class="ch-body">
              <div class="bub out" id="cb1">Quiero Hacer un pedido <i class="tk">✓✓</i></div>
              <div class="wait" id="cb2">Costo de envío según zona</div>
            </div>
          </div>
          <div class="left narrow">
            <div class="grp" id="og1"><div class="h1" id="d1">{words("Y en su menú")}</div><div class="h1" id="d2">{hl("en línea…")}</div></div>
            <div class="grp" id="og2"><div class="eyebrow2" id="d0">Hallazgo {len(ORDER) + 2:02d}</div><div class="h1" id="d3">{words("Para pedir,")}</div><div class="h1" id="d4">{words("un")} {hl("WhatsApp.")}</div><div class="h2 gray" id="d5">{words("Y esperar a que alguien conteste.")}</div></div>
          </div>'''),
        scene("calm", f'''
          <div class="wash w6"></div>
          <div class="center">
            <div class="h1" id="k1">{words("Cada error")}</div>
            <div class="h1" id="k2">{words("es un cliente")} <span class="kname">{words("que se va.")}</span></div>
          </div>'''),
        scene("leak", f'''
          <div class="navy"></div><div class="wash w7"></div>
          <div class="leaks">{leaks_html}</div>
          <div class="left narrow">
            <div class="h1 white" id="q1">{words("Dónde se")}</div>
            <div class="h1 white" id="q2">{words("pierden clientes")}</div>
            <div class="h1" id="q3">{hl("hoy.")}</div>
          </div>''', "darkscene"),
        scene("prop", f'''
          <div class="wash w8"></div>
          <div class="ph-stage">{gen3.phone(site_html, "ph1")}</div>
          <div class="left">
            <div class="eyebrow2" id="y0">La propuesta</div>
            <div class="h1" id="y1">{words("Una página que")}</div>
            <div class="h1" id="y2">{hl("vende sola.")}</div>
            <div class="props">{props_html}</div>
          </div>'''),
        scene("why", f'''
          <div class="wash w8"></div>
          <div class="left">
            <div class="h1" id="w1">{words("Por qué")} {hl("nosotros.")}</div>
            <div class="whys">{whys_html}</div>
          </div>
          <div class="ctacard" id="cta">
            <div class="cta-ic">{gen3.HOUSE}</div>
            <div class="cta-t">Casa Digital</div>
            <div class="cta-s">Se la mostramos en 15 minutos.</div>
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
    ])

    css = (gen3.CSS.replace("$heroB", "rgb(%d,%d,%d)" % tuple(int(v * .22) for v in hexrgb(hero))).replace("$hero", hero).replace("$acc", acc).replace("$pri", pri)
           .replace("$washA", rgba(hero, .16)).replace("$washB", rgba(acc, .22)).replace("$sitebg", c["bg"]).replace("$siteink", c["ink"])
           .replace("$dweight", str(f["displayWeight"])).replace("$dcase", f.get("displayCase", "none")).replace("$dtrack", f["displayTracking"])
           .replace("$italface", '@font-face{font-family:"DisplayI";src:url("assets/fonts/display-italic.woff2") format("woff2");font-style:italic;}' if f.get("italicFile") else "")
           .replace("$ital", '"DisplayI"' if f.get("italicFile") else '"Display"')
           .replace("$introsizepx", str(r.get("introSize3", 150)) + "px")) + gen4.EXTRA_CSS + CSS5
    zp = {PID(n): zoom_plan(PID(n), n) for sc in SEQ for n, _ in SEQ[sc]}
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    js = (JS.replace("$zp", json.dumps(zp)).replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
          .replace("$seq_home", seq_js("home", "#hg2")).replace("$seq_look", seq_js("look", "#m1, #m2, #m3"))
          .replace("$seq_links", seq_js("links", "#l1, #l2, #l3")))
    html = (gen3.HTML.replace("$title", f"Casa Digital x {r['name']} · auditoría").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)).replace('data-fade-out="2.5"', 'data-fade-out="4"'))
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


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
$scenes.forEach(([id, s, e]) => tl.fromTo("#cam-" + id, { scale: 1.0 }, { scale: 1.025, duration: e - s, ease: "none" }, s));

const ZP = $zp;
function marks(pid, beats, preset) {
  beats.forEach((b, i) => {
    const z = ZP[pid][i];
    const d = i > 0 ? Math.min(1.8, (b - beats[i - 1]) * .6) : 1.8;
    if (!(preset && i === 0)) tl.to("#" + pid + "-z", { x: z.x, y: z.y, scale: z.s, duration: d, ease: FINE }, b - d);
    tl.fromTo("#" + pid + "-mk" + i, { opacity: 0, scale: 1.12 }, { opacity: 1, scale: 1, duration: .8, ease: "power3.out" }, b);
    if (i > 0) tl.to("#" + pid + "-cap" + (i - 1), { opacity: 0, y: -20, filter: "blur(8px)", duration: .6, ease: "power2.in" }, b - d);
    if (i > 0) tl.to("#" + pid + "-mk" + (i - 1), { opacity: .3, duration: .6 }, b - d);
    tl.fromTo("#" + pid + "-cap" + i, { opacity: 0, y: 40, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.2, ease: SOFT }, b + .1);
  });
}
function audit(pid, t0, beats) {
  tl.fromTo("#" + pid, { y: 600, rotationY: -14, rotationX: 6, opacity: 0 }, { y: 0, rotationY: -6, rotationX: 2, opacity: 1, duration: 2.2, ease: SOFT }, t0);
  tl.to("#" + pid, { rotationY: 0, rotationX: 0, duration: 1.8, ease: FINE }, beats[0] - 1.8);
  marks(pid, beats, false);
}
function swap(prev, nprev, pid, beats) {
  const b0 = beats[0], z = ZP[pid][0];
  tl.to("#" + prev + "-z, #" + prev + "-cap" + (nprev - 1), { opacity: 0, filter: "blur(14px)", duration: .8, ease: "power2.in" }, b0 - 1.3);
  tl.set("#" + pid + "-z", { x: z.x, y: z.y + 60, scale: z.s }, b0 - 1.3);
  tl.fromTo("#" + pid + "-z", { opacity: 0, filter: "blur(14px)" }, { opacity: 1, filter: "blur(0px)", duration: 1, ease: SOFT }, b0 - .6);
  tl.to("#" + pid + "-z", { y: z.y, duration: 1.6, ease: FINE }, b0 - .6);
  marks(pid, beats, true);
}

// 1 · intro
tl.fromTo(".w1", { x: -200, opacity: 0 }, { x: 100, opacity: 1, duration: K(3), ease: "sine.inOut" }, 0);
tl.fromTo(".w2", { x: 200, opacity: 0 }, { x: -100, opacity: 1, duration: K(3), ease: "sine.inOut" }, 0);
rise("#icd", 0.4, { d: 2 });
rise("#ipres .w", K(1), { d: 1.6, st: .14 });
tl.fromTo("#iname", { opacity: 0, scale: 1.06, filter: "blur(24px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.6, ease: SOFT }, K(1.5));

// 2 · concept: we visited the site as a new customer
rise("#c1 .w", K(3)); rise("#c2 .w", K(3) + .4); rise("#c3 .w", K(3) + .8);
swipe("#c3 .hlbg", K(4) - .3);
tl.fromTo("#ub", { opacity: 0, y: 60, scale: .96 }, { opacity: 1, y: 0, scale: 1, duration: 1.6, ease: SOFT }, K(3) + .3);
tl.fromTo("#url", { width: 0 }, { width: "auto", duration: 2.2, ease: "steps(31)" }, K(3.5));
tl.fromTo("#caret", { opacity: 1 }, { opacity: 0, duration: .3, repeat: 9, yoyo: true, ease: "steps(1)" }, K(3));
rise("#fn", K(5), { d: 1.4 });

// 3 · home
rise("#h3 .w", K(6)); rise("#h4 .w", K(6) + .5);
swipe("#h4 .hlbg", K(6.6));
$seq_home

// 4 · looks forgotten
rise("#m1 .w", K(9)); rise("#m2 .w", K(9) + .4); rise("#m3 .w", K(9) + .8);
swipe("#m3 .hlbg", K(9.4));
$seq_look

// 5 · stuck in 2021
rise("#l1 .w", K(15)); rise("#l2 .w", K(15) + .4); rise("#l3 .w", K(15) + .8);
swipe("#l3 .hlbg", K(15.4));
$seq_links

// 6 · menu text + WhatsApp orders
rise("#d1 .w", K(19)); rise("#d2 .w", K(19) + .5);
swipe("#d2 .hlbg", K(19.5));
tl.fromTo("#qc", { opacity: 0, x: 100 }, { opacity: 1, x: 0, duration: 1.8, ease: SOFT }, K(19));
[19.5, 20.2, 20.9].forEach((k, i) => {
  rise("#qr" + i, K(k), { y: 20, blur: 6, d: 1.2 });
  tl.fromTo("#qr" + i + " em", { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: .8, ease: "power3.out" }, K(k) + .7);
});
out("#og1", K(21.5) - .9);
tl.to("#qc", { opacity: 0, x: -60, filter: "blur(12px)", duration: .9, ease: "power2.in" }, K(21.5) - .9);
rise("#d0", K(21.5), { d: 1.2 }); rise("#d3 .w", K(21.5) + .2); rise("#d4 .w", K(21.5) + .6);
swipe("#d4 .hlbg", K(22.2));
rise("#d5 .w", K(22.7), { st: .05 });
tl.fromTo("#chat2", { opacity: 0, y: 70 }, { opacity: 1, y: 0, duration: 1.8, ease: SOFT }, K(21.5));
rise("#cb1", K(22), { y: 20, blur: 4, d: 1 });
rise("#cb2", K(22.8), { y: 20, blur: 4, d: 1.2 });

// 7 · break
rise("#k1 .w", K(24), { d: 2, st: .16 });
rise("#k2 .w", K(24.8), { d: 2, st: .16 });

// 8 · where customers are lost
rise("#q1 .w", K(26)); rise("#q2 .w", K(26) + .4); rise("#q3 .w", K(26) + .8);
swipe("#q3 .hlbg", K(26.5));
tl.fromTo("#q3 .w", { color: "#ffffff" }, { color: "#111113", duration: .5 }, K(26.5) + .4);
[26.4, 27, 28, 29].forEach((k, i) => tl.fromTo("#lk" + i, { opacity: 0, x: 60, filter: "blur(10px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 1.4, ease: SOFT }, K(k)));

// 9 · the proposal, explained
rise("#y0", K(30), { d: 1.2 }); rise("#y1 .w", K(30) + .3); rise("#y2 .w", K(30) + .7);
swipe("#y2 .hlbg", K(30.6));
[31.2, 32.2, 33.2].forEach((k, i) => rise("#pr" + i, K(k), { y: 30, d: 1.4 }));
tl.fromTo("#ph1", { y: 700, rotationY: -20, rotationX: 8 }, { y: 0, rotationY: -10, rotationX: 3, duration: 2.4, ease: SOFT }, K(30));
tl.to("#ph1", { rotationY: 4, rotationX: 0, duration: K(35) - K(31), ease: "sine.inOut" }, K(31));
tl.fromTo("#notif", { y: -160, opacity: 0 }, { y: 0, opacity: 1, duration: 1, ease: "back.out(1.3)" }, K(31.2));
tl.to("#notif", { y: -160, opacity: 0, duration: .8, ease: "power2.in" }, K(33));

// 10 · why us + call to action
rise("#w1 .w", K(35));
swipe("#w1 .hlbg", K(35.4));
[35.6, 36.1, 36.6, 37.1].forEach((k, i) => rise("#wy" + i + " .w, #wy" + i + " i", K(k), { st: .04, d: 1.2 }));
tl.fromTo("#cta", { opacity: 0, y: 100, scale: .94 }, { opacity: 1, y: 0, scale: 1, duration: 2, ease: SOFT }, K(35.5));
float("#cta", K(36.3), K(38) - K(36.3));

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
trails("re", K(38) - 0.3, 3, [20, -8, 1.6, 0.9]);
tl.to("#re", { scale: 3.2, opacity: 0, duration: 1.3, ease: "expo.out" }, K(39));
tl.to("#mstroke path", { strokeDashoffset: 0, duration: 2.3, ease: FINE }, K(38) + .1);
tl.fromTo("#mfill", { opacity: 0 }, { opacity: 1, duration: .6, ease: "power2.out" }, K(39));
tl.to("#mstroke", { opacity: 0, duration: .6 }, K(39));
tl.fromTo("#mwrap", { scale: .92 }, { scale: 1, duration: 2.6, ease: SOFT }, K(38));
tl.fromTo("#mwrap", { filter: "drop-shadow(0 0 0px rgba(140,170,255,0))" }, { filter: "drop-shadow(0 0 60px rgba(140,170,255,.65))", duration: .4, ease: "power2.out", yoyo: true, repeat: 1 }, K(39));
tl.fromTo("#eglow", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: 2, ease: SOFT }, K(39));
tl.fromTo("#msweep", { x: -200 }, { x: 900, duration: 1.8, ease: FINE }, K(39.5));
rise("#lby", K(39.5), { d: 1.6 });
rise(".lt", K(39.5) + .3, { d: 1.6, st: .04, y: 36, blur: 12 });
tl.to("#end .center, #eglow", { opacity: 0, duration: 2, ease: "power2.in" }, K(41.1));

window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
tl.seek(0);
'''

if __name__ == "__main__":
    data = json.load(open(os.path.join(HERE, "restaurants.json")))
    print(build(next(r for r in data if r["slug"] == "cafe-honore")))
