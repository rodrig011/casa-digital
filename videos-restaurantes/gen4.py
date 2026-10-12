#!/usr/bin/env python3
"""Café Honoré audit video: real screenshots of their current site with the problems marked,
where customers are lost, and why Casa Digital. Same look and beat grid as gen3 (cuts on
downbeats, 120 BPM, offset 0.017 s); keeps the v2/v3 Clientia Tech outro.

Screenshots go in shots/cafe-honore/shot1..shot5 (.png/.jpg). Until they exist the phone shows a
'pendiente' placeholder. Marks are fractions of the screenshot: (x, y, w, h)."""
import glob, json, os, shutil, sys
import gen3
from gen2 import MARK, words, rgba, lum, lift, hexrgb, ribbons, DEPS, HERE

OUT = os.path.join(HERE, "videos4")
SHOTS = os.path.join(HERE, "shots", "cafe-honore")
WHATSAPP = gen3.WHATSAPP
B, TOTAL = 0.017, 64.0
SCENES = [("intro", 0, 8), ("home", 8, 16), ("menu", 16, 24), ("links", 24, 30), ("order", 30, 36),
          ("calm", 36, 40), ("leak", 40, 48), ("why", 48, 56), ("end", 56, 64)]

# Marks per screenshot: (caption, (x, y, w, h)) with the box in fractions of the screenshot.
MARKS = {
    "inicio": [("Ni teléfono, ni dirección, ni horario", (0.02, 0.14, 0.96, 0.37))],
    "anos": [("Dice “más de 20 años”. Desde 1993 ya son 33.", (0.20, 0.088, 0.59, 0.068))],
    "eventos": [("El título se sale de la pantalla", (0.42, 0.298, 0.47, 0.048))],
    "disfruta": [("Una foto encimada sobre otra", (0.585, 0.383, 0.39, 0.175)), ("Y media pantalla en blanco", (0.03, 0.645, 0.94, 0.32))],
    "menu-nav": [("“Visión y Misión”: (Pronto)", (0.4, 0.67, 0.47, 0.037))],
    "noticias": [("La última noticia: la Navidad de 2021", (0.2, 0.652, 0.6, 0.054))],
    "menu-rest": [("Un producto sin nombre, a Lps.0", (0.05, 0.25, 0.9, 0.1)), ("Un set de putter de golf, en el menú", (0.05, 0.55, 0.9, 0.1))],
    "domicilio": [("Para pedir: un link de WhatsApp y esperar", (0.06, 0.5, 0.88, 0.14))],
}
# Screenshots shown in each scene, with the song second each mark lands on (downbeats / half bars).
SEQ = {
    "home": [("inicio", [14])],
    "menu": [("anos", [19]), ("eventos", [20.5]), ("disfruta", [22, 23])],
    "links": [("menu-nav", [27]), ("noticias", [29])],
}
PID = lambda n: "s_" + n.replace("-", "_")
SCR_X, SCR_Y, SCR_W, SCR_H = 884, 104, 402, 872   # phone screen at rest, in scene px


def shot_file(name):
    hits = sorted(glob.glob(os.path.join(SHOTS, name + ".*")))
    return hits[0] if hits else None


def shot_phone(name, pid, proj):
    """Phone with a real screenshot inside a full-scene zoom layer, plus big captions for each mark."""
    f = shot_file(name)
    if f:
        ext = os.path.splitext(f)[1].lower()
        shutil.copy(f, os.path.join(proj, "assets", name + ext))
        img = f'<img class="shot" src="assets/{name}{ext}">'
    else:
        img = f'<div class="shot pending"><b>Captura pendiente</b><span>{name}</span></div>'
    boxes = "".join(f'<div class="mk" id="{pid}-mk{i}" style="left:{x*100}%;top:{y*100}%;width:{w*100}%;height:{h*100}%"></div>'
                    for i, (_, (x, y, w, h)) in enumerate(MARKS[name]))
    caps = "".join(f'<div class="cap" id="{pid}-cap{i}"><i></i><span>{words(label)}</span></div>' for i, (label, _) in enumerate(MARKS[name]))
    return (f'<div class="zoomer" id="{pid}-z"><div class="ph-stage audit"><div class="iph" id="{pid}"><div class="iph-scr"><div class="island"></div>'
            f'<div class="pan">{img}{boxes}</div></div></div></div></div><div class="caps">{caps}</div>')


def seq_html(sc, proj):
    return "".join(shot_phone(n, PID(n), proj) for n, _ in SEQ[sc])


def seq_js(sc, headline):
    """First screenshot enters on the scene start; later ones cross-fade in already zoomed."""
    start = next(a for i, a, b in SCENES if i == sc)
    out, prev = [], None
    for n, beats in SEQ[sc]:
        bs = "[" + ", ".join(f"at({b})" for b in beats) + "]"
        if prev is None:
            out.append(f'audit("{PID(n)}", at({start}), {bs});')
            out.append(f'out("{headline}", at({beats[0]}) - 1.1, .6);')
        else:
            out.append(f'swap("{PID(prev[0])}", {len(prev[1])}, "{PID(n)}", {bs});')
        prev = (n, beats)
    return "\n".join(out)


def zoom_plan(pid, name):
    """Camera targets per mark: put the box centre at (1180, 500) and scale it to ~900 px wide."""
    plan = []
    for _, (x, y, w, h) in MARKS[name]:
        cx, cy = SCR_X + (x + w / 2) * SCR_W, SCR_Y + (y + h / 2) * SCR_H
        S = max(2.2, min(4.0, 900 / (w * SCR_W), 520 / (h * SCR_H)))
        plan.append({"s": round(S, 3), "x": round(1180 - S * cx, 1), "y": round(500 - S * cy, 1)})
    return plan


EXTRA_CSS = r'''
.left.narrow{width:680px;z-index:0;}
.zoomer{z-index:1;}.caps{z-index:2;}
.left.narrow .h1{font-size:92px;}
.left.narrow .h2{font-size:44px;}
.ph-stage.audit{left:700px;width:1220px;}
.ph-stage.audit .iph{left:170px;}
.pan{position:absolute;left:0;right:0;top:0;}
.shot{display:block;width:100%;}
.shot.pending{height:872px;background:repeating-linear-gradient(135deg,#F2F2F4 0 24px,#E9E9EC 24px 48px);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:#8E8E93;}
.shot.pending b{font-size:30px;color:#6E6E73;}.shot.pending span{font-size:20px;}
.mk{position:absolute;border:4px solid #FF3B30;border-radius:14px;box-shadow:0 0 0 6px rgba(255,59,48,.18);}
.zoomer{position:absolute;inset:0;transform-origin:0 0;}
.mk{border-width:3px;border-radius:10px;}
.caps{position:absolute;left:120px;bottom:110px;width:1100px;height:200px;}
.cap{position:absolute;left:0;bottom:0;max-width:1100px;display:flex;align-items:center;gap:26px;background:rgba(17,17,19,.92);color:#fff;font-weight:600;font-size:56px;line-height:1.12;letter-spacing:-.025em;padding:34px 48px 34px 40px;border-radius:36px;box-shadow:0 40px 90px rgba(0,0,0,.35);backdrop-filter:blur(20px);}
.cap i{flex:none;width:26px;height:26px;border-radius:50%;background:#FF3B30;box-shadow:0 0 0 10px rgba(255,59,48,.25);}
.dim{position:absolute;inset:0;background:radial-gradient(60% 60% at 61% 46%,rgba(0,0,0,0),rgba(0,0,0,.28));opacity:0;}
.leaks{position:absolute;left:1040px;top:170px;width:760px;display:flex;flex-direction:column;gap:26px;}
.lk{background:#14161F;border-radius:30px;padding:30px 34px;display:flex;gap:26px;align-items:flex-start;box-shadow:0 0 0 1px rgba(255,255,255,.06);}
.lk-n{flex:none;width:58px;height:58px;border-radius:50%;background:rgba(255,69,58,.16);color:#FF6961;font-weight:700;font-size:28px;display:flex;align-items:center;justify-content:center;}
.lk b{display:block;color:#fff;font-size:32px;font-weight:600;letter-spacing:-.01em;}
.lk span{display:block;color:rgba(235,235,245,.6);font-size:25px;margin-top:6px;}
.whys{margin-top:40px;display:flex;flex-direction:column;gap:22px;}
.wy{display:flex;gap:22px;align-items:center;font-size:40px;font-weight:500;letter-spacing:-.02em;}
.wy i{flex:none;width:52px;height:52px;border-radius:50%;background:#111113;color:#FFD60A;font-style:normal;font-size:28px;font-weight:700;display:flex;align-items:center;justify-content:center;}
.wa-small{margin-top:46px;display:inline-flex;align-self:flex-start;background:#25D366;color:#fff;font-weight:600;font-size:30px;padding:16px 30px;border-radius:40px;}
.qcard{position:absolute;left:1000px;top:250px;width:820px;background:#fff;border-radius:40px;padding:44px 48px;box-shadow:0 40px 100px rgba(0,0,0,.14),0 0 0 1px rgba(0,0,0,.05);}
.qc-k{font-size:22px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#86868B;margin-bottom:10px;}
.qrow{position:relative;display:flex;align-items:baseline;gap:20px;padding:30px 0 46px;border-bottom:1.5px solid #EEE;font-size:30px;}
.qrow span{flex:1;font-family:Georgia,serif;color:#333;}.qrow .noname{color:#B0B0B5;font-style:italic;}
.qrow b{font-weight:500;color:#555;font-family:Georgia,serif;}
.qrow em{position:absolute;left:0;bottom:10px;font-style:normal;font-size:20px;font-weight:600;color:#FF3B30;}
#chat2{left:1060px;top:260px;width:720px;height:560px;}
.tk{font-style:normal;font-size:22px;color:#8696A0;margin-left:10px;}
.wait{align-self:center;margin-top:30px;background:rgba(255,255,255,.85);border-radius:16px;padding:12px 22px;font-size:24px;color:#54656F;}
'''


def build(r):
    c = r["colors"]; f = r["fonts"]
    hero = c["primary"] if lum(c["primary"]) < 0.45 else c["accent"]
    acc = lift(c["accent"], 0.5); pri = lift(c["primary"], 0.38)
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
    json.dump({"id": r["slug"] + "-auditoria", "name": f"Casa Digital x {r['name']} · auditoría"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        start = 0 if s == 0 else round(s + B, 3)
        end = TOTAL if e == 64 else round(e + B, 3)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{start}" data-duration="{round(end - start, 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

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
    whys = ["Hecha a la medida, no una plantilla.", "Pedidos con carrito y pago con tarjeta.",
            "0% de comisión por pedido.", "Lista en 14 días, con su dominio."]
    whys_html = "".join(f'<div class="wy" id="wy{i}"><i>✓</i><span>{words(t)}</span></div>' for i, t in enumerate(whys))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    body = "\n".join([
        scene("intro", f'''
          <div class="wash w1"></div><div class="wash w2"></div>
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("revisó la página de")}</div>
            <div class="disp intro-name" id="iname">{r["name"]}</div>
          </div>'''),
        scene("home", f'''
          <div class="wash w4"></div>
          {seq_html("home", proj)}
          <div class="left narrow">
            <div class="grp" id="hg1">
              <div class="h1" id="h1">{words("Más de 30 años")}</div>
              <div class="h1" id="h2">{words("en Palmira.")}</div>
            </div>
            <div class="grp" id="hg2">
              <div class="h1" id="h3">{words("Y una página")}</div>
              <div class="h1" id="h4">{words("que no")} {hl("vende.")}</div>
            </div>
          </div>'''),
        scene("menu", f'''
          <div class="wash w3"></div>
          {seq_html("menu", proj)}
          <div class="left narrow">
            <div class="h1" id="m1">{words("Al bajar,")}</div>
            <div class="h1" id="m2">{words("la página")}</div>
            <div class="h1" id="m3">{words("se ve")} {hl("olvidada.")}</div>
          </div>'''),
        scene("links", f'''
          <div class="wash w4"></div>
          {seq_html("links", proj)}
          <div class="left narrow">
            <div class="h1" id="l1">{words("Una página")}</div>
            <div class="h1" id="l2">{words("que se quedó")}</div>
            <div class="h1" id="l3">{words("en")} {hl("2021.")}</div>
          </div>'''),
        scene("order", f'''
          <div class="wash w5"></div>
          <div class="qcard" id="qc">
            <div class="qc-k">Copiado de su menú en línea</div>
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
            <div class="grp" id="og2"><div class="h1" id="d3">{words("Para pedir,")}</div><div class="h1" id="d4">{words("un")} {hl("WhatsApp.")}</div><div class="h2 gray" id="d5">{words("Y esperar a que alguien conteste.")}</div></div>
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
        scene("why", f'''
          <div class="wash w8"></div>
          <div class="ph-stage">{gen3.phone(site_html, "ph1")}</div>
          <div class="left">
            <div class="h1" id="y1">{words("Por qué")} {hl("nosotros.")}</div>
            <div class="whys">{whys_html}</div>
            <div class="wa-small" id="ywa">WhatsApp {WHATSAPP}</div>
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
           .replace("$introsizepx", str(r.get("introSize3", 150)) + "px")) + EXTRA_CSS
    zp = {PID(n): zoom_plan(PID(n), n) for sc in SEQ for n, _ in SEQ[sc]}
    js = (JS.replace("$zp", json.dumps(zp)).replace("$seq_home", seq_js("home", "#hg2"))
          .replace("$seq_menu", seq_js("menu", "#m1, #m2, #m3")).replace("$seq_links", seq_js("links", "#l1, #l2, #l3"))
)
    html = (gen3.HTML.replace("$title", f"Casa Digital x {r['name']} · auditoría").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)))
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


def hl(text):
    return gen3.hl(text)


JS = r'''
const tl = gsap.timeline({ paused: true });
const B = 0.017, at = s => s + B;
const SOFT = "expo.out";
function rise(sel, t, o) {
  o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y || 50, filter: "blur(" + (o.blur || 14) + "px)" },
    { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d || 1.2, ease: SOFT, stagger: o.st || 0.08 }, t);
}
function out(sel, t, d) { tl.to(sel, { opacity: 0, y: -40, filter: "blur(12px)", duration: d || .7, ease: "power2.in" }, t); }
function swipe(sel, t) { tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: .7, ease: "power3.inOut" }, t); }
function float(sel, t, d) { tl.fromTo(sel, { y: 0 }, { y: -26, duration: d, ease: "sine.inOut" }, t); }
[["intro",0,8],["home",8,16],["menu",16,24],["links",24,30],["order",30,36],["calm",36,40],["leak",40,48],["why",48,56],["end",56,64]]
  .forEach(([id, s, e]) => tl.fromTo("#cam-" + id, { scale: 1.0 }, { scale: 1.03, duration: e - s, ease: "none" }, s === 0 ? 0 : at(s)));

// phone with a real screenshot: enters, pans, then each mark draws and its chip pops on a beat
const ZP = $zp;
function marks(pid, beats, preset) {
  beats.forEach((b, i) => {
    const z = ZP[pid][i];
    const d = i > 0 ? Math.min(1.1, (b - beats[i - 1]) * .6) : 1.1;
    if (!(preset && i === 0)) tl.to("#" + pid + "-z", { x: z.x, y: z.y, scale: z.s, duration: d, ease: "power3.inOut" }, b - d);
    tl.fromTo("#" + pid + "-mk" + i, { opacity: 0, scale: 1.3 }, { opacity: 1, scale: 1, duration: .45, ease: "back.out(2)" }, b);
    if (i > 0) tl.to("#" + pid + "-cap" + (i - 1), { opacity: 0, y: -20, duration: .3, ease: "power2.in" }, b - .3);
    if (i > 0) tl.to("#" + pid + "-mk" + (i - 1), { opacity: .35, duration: .3 }, b - .6);
    tl.fromTo("#" + pid + "-cap" + i, { opacity: 0, y: 40, filter: "blur(10px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: .7, ease: SOFT }, b);
  });
}
function audit(pid, t0, beats) {
  tl.fromTo("#" + pid, { y: 700, rotationY: -18, rotationX: 8, opacity: 0 }, { y: 0, rotationY: -6, rotationX: 2, opacity: 1, duration: 1.8, ease: SOFT }, t0);
  tl.to("#" + pid, { rotationY: 0, rotationX: 0, duration: 1.1, ease: "power3.inOut" }, beats[0] - 1.1);
  marks(pid, beats, false);
}
function swap(prev, nprev, pid, beats) {
  const b0 = beats[0], z = ZP[pid][0];
  tl.to("#" + prev + "-z, #" + prev + "-cap" + (nprev - 1), { opacity: 0, filter: "blur(16px)", duration: .5, ease: "power2.in" }, b0 - .8);
  tl.set("#" + pid + "-z", { x: z.x, y: z.y, scale: z.s }, b0 - .8);
  tl.fromTo("#" + pid + "-z", { opacity: 0, filter: "blur(16px)" }, { opacity: 1, filter: "blur(0px)", duration: .6, ease: SOFT }, b0 - .5);
  marks(pid, beats, true);
}

// 1 · intro
tl.fromTo(".w1", { x: -200, opacity: 0 }, { x: 100, opacity: 1, duration: 8, ease: "sine.inOut" }, 0);
tl.fromTo(".w2", { x: 200, opacity: 0 }, { x: -100, opacity: 1, duration: 8, ease: "sine.inOut" }, 0);
rise("#icd", 0.6, { d: 1.8 });
rise("#ipres .w", at(2.5), { d: 1.4, st: .12 });
tl.fromTo("#iname", { opacity: 0, scale: 1.08, filter: "blur(24px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, at(4.5));

// 2 · home page
rise("#h1 .w", at(8)); rise("#h2 .w", at(8.5));
$seq_home
out("#hg1", at(11) - .7);
rise("#h3 .w", at(11)); rise("#h4 .w", at(11.5));
swipe("#h4 .hlbg", at(12.2));

// 3 · menu errors
rise("#m1 .w", at(16)); rise("#m2 .w", at(16.4)); rise("#m3 .w", at(16.8));
swipe("#m3 .hlbg", at(17.4));
$seq_menu

// 4 · dead links + 2021 news
rise("#l1 .w", at(24)); rise("#l2 .w", at(24.3)); rise("#l3 .w", at(24.6));
swipe("#l3 .hlbg", at(25));
$seq_links
tl.fromTo("#pl2-cap0", { opacity: 0, y: 40, filter: "blur(10px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: .7, ease: SOFT }, at(28.5));

// 5 · manual WhatsApp orders
rise("#d1 .w", at(30)); rise("#d2 .w", at(30.4));
swipe("#d2 .hlbg", at(31));
tl.fromTo("#qc", { opacity: 0, x: 120 }, { opacity: 1, x: 0, duration: 1.2, ease: SOFT }, at(30));
[30.5, 31, 31.5].forEach((t, i) => {
  rise("#qr" + i, at(t), { y: 24, blur: 6, d: .8 });
  tl.fromTo("#qr" + i + " em", { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: .5, ease: "back.out(2)" }, at(t) + .5);
});
out("#og1", at(33) - .7);
tl.to("#qc", { opacity: 0, x: -80, filter: "blur(12px)", duration: .6, ease: "power2.in" }, at(33) - .6);
rise("#d3 .w", at(33)); rise("#d4 .w", at(33.4));
swipe("#d4 .hlbg", at(34));
rise("#d5 .w", at(34.5), { st: .04 });
tl.fromTo("#chat2", { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 1.2, ease: SOFT }, at(33));
rise("#cb1", at(33.5), { y: 20, blur: 4, d: .6 });
rise("#cb2", at(34.5), { y: 20, blur: 4, d: .8 });

// 6 · break
rise("#k1 .w", at(36), { d: 1.6, st: .14 });
rise("#k2 .w", at(37), { d: 1.6, st: .14 });

// 7 · where customers are lost
rise("#q1 .w", at(40)); rise("#q2 .w", at(40.4)); rise("#q3 .w", at(40.8));
swipe("#q3 .hlbg", at(41.6));
tl.fromTo("#q3 .w", { color: "#ffffff" }, { color: "#111113", duration: .4 }, at(41.6) + .25);
[40, 42, 44, 46].forEach((s, i) => tl.fromTo("#lk" + i, { opacity: 0, x: 80, filter: "blur(10px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 1, ease: SOFT }, at(s) + (i === 0 ? .4 : 0)));

// 8 · why us + the renewed site
rise("#y1 .w", at(48));
swipe("#y1 .hlbg", at(48.8));
[49, 50, 52, 54].forEach((s, i) => rise("#wy" + i + " .w, #wy" + i + " i", at(s) + (i === 0 ? .2 : 0), { st: .04, d: 1 }));
rise("#ywa", at(54) + .6, { d: 1 });
tl.fromTo("#ph1", { y: 700, rotationY: -24, rotationX: 10 }, { y: 0, rotationY: -12, rotationX: 4, duration: 2, ease: SOFT }, at(48));
tl.to("#ph1", { rotationY: 6, rotationX: 0, duration: 6, ease: "sine.inOut" }, at(50));
tl.fromTo("#notif", { y: -160, opacity: 0 }, { y: 0, opacity: 1, duration: .8, ease: "back.out(1.4)" }, at(52));
tl.to("#notif", { y: -160, opacity: 0, duration: .6, ease: "power2.in" }, at(54.6));

// 9 · outro (kept from v2/v3)
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
    print(build(next(r for r in data if r["slug"] == "cafe-honore")))
