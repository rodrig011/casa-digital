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

# Each shot: list of (label, box) where box = (x, y, w, h) in fractions of the screenshot, or None.
# 'pan' scrolls a tall screenshot from pan[0] to pan[1] (fraction of the overflow).
MARKS = {
    "shot1": [("Sin teléfono, dirección ni horario", (0.06, 0.55, 0.88, 0.2))],
    "shot4": [("Un producto sin nombre, a Lps.0", (0.05, 0.22, 0.9, 0.12)), ("“Build Your Salad”, sin precio", (0.05, 0.45, 0.9, 0.12)),
              ("Un set de putter de golf, en el menú del restaurante", (0.05, 0.68, 0.9, 0.12))],
    "shot3": [("“Menú” no lleva a ningún lado", (0.08, 0.3, 0.6, 0.07)), ("“Reserva en” tampoco", (0.08, 0.45, 0.6, 0.07))],
    "shot2": [("La última noticia es de la Navidad de 2021", (0.05, 0.35, 0.9, 0.3))],
    "shot5": [("Cada pedido es un WhatsApp que alguien tiene que contestar", (0.06, 0.5, 0.88, 0.14))],
}
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
             ("Quiere reservar la terraza", "El botón no lleva a ningún lado."),
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
          {shot_phone("shot1", "pa", proj)}
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
          {shot_phone("shot4", "pm", proj)}
          <div class="left narrow">
            <div class="h1" id="m1">{words("Un cliente")}</div>
            <div class="h1" id="m2">{words("abre el menú")}</div>
            <div class="h1" id="m3">{words("y encuentra")} {hl("esto.")}</div>
          </div>'''),
        scene("links", f'''
          <div class="wash w4"></div>
          {shot_phone("shot3", "pl1", proj)}{shot_phone("shot2", "pl2", proj)}
          <div class="left narrow">
            <div class="h1" id="l1">{words("Botones que")}</div>
            <div class="h1" id="l2">{words("no llevan a")}</div>
            <div class="h1" id="l3">{hl("ningún lado.")}</div>
          </div>'''),
        scene("order", f'''
          <div class="wash w5"></div>
          {shot_phone("shot5", "po", proj)}
          <div class="left narrow">
            <div class="h1" id="d1">{words("Cada pedido")}</div>
            <div class="h1" id="d2">{words("espera a que")}</div>
            <div class="h1" id="d3">{words("alguien")} {hl("conteste.")}</div>
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
    zp = {pid: zoom_plan(pid, n) for pid, n in (("pa", "shot1"), ("pm", "shot4"), ("pl1", "shot3"), ("pl2", "shot2"), ("po", "shot5"))}
    js = JS.replace("$zp", json.dumps(zp))
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
function audit(pid, t0, beats) {
  tl.fromTo("#" + pid, { y: 700, rotationY: -18, rotationX: 8, opacity: 0 }, { y: 0, rotationY: -6, rotationX: 2, opacity: 1, duration: 1.8, ease: SOFT }, t0);
  beats.forEach((b, i) => {
    const z = ZP[pid][i];
    if (i === 0) tl.to("#" + pid, { rotationY: 0, rotationX: 0, duration: 1.1, ease: "power3.inOut" }, b - 1.1);
    tl.to("#" + pid + "-z", { x: z.x, y: z.y, scale: z.s, duration: 1.1, ease: "power3.inOut" }, b - 1.1);
    tl.fromTo("#" + pid + "-mk" + i, { opacity: 0, scale: 1.3 }, { opacity: 1, scale: 1, duration: .45, ease: "back.out(2)" }, b);
    if (i > 0) tl.to("#" + pid + "-cap" + (i - 1), { opacity: 0, y: -20, duration: .3, ease: "power2.in" }, b - .3);
    if (i > 0) tl.to("#" + pid + "-mk" + (i - 1), { opacity: .35, duration: .3 }, b - .6);
    tl.fromTo("#" + pid + "-cap" + i, { opacity: 0, y: 40, filter: "blur(10px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: .7, ease: SOFT }, b);
    tl.fromTo("#" + pid + "-cap" + i + " .w", { opacity: 0 }, { opacity: 1, duration: .4, stagger: .03 }, b);
  });
}

// 1 · intro
tl.fromTo(".w1", { x: -200, opacity: 0 }, { x: 100, opacity: 1, duration: 8, ease: "sine.inOut" }, 0);
tl.fromTo(".w2", { x: 200, opacity: 0 }, { x: -100, opacity: 1, duration: 8, ease: "sine.inOut" }, 0);
rise("#icd", 0.6, { d: 1.8 });
rise("#ipres .w", at(2.5), { d: 1.4, st: .12 });
tl.fromTo("#iname", { opacity: 0, scale: 1.08, filter: "blur(24px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 2.2, ease: SOFT }, at(4.5));

// 2 · home page
rise("#h1 .w", at(8)); rise("#h2 .w", at(8.5));
audit("pa", at(8), [at(14)]);
out("#hg2", at(14) - 1.1, .6);
out("#hg1", at(11) - .7);
rise("#h3 .w", at(11)); rise("#h4 .w", at(11.5));
swipe("#h4 .hlbg", at(12.2));

// 3 · menu errors
rise("#m1 .w", at(16)); rise("#m2 .w", at(16.6)); rise("#m3 .w", at(17.2));
swipe("#m3 .hlbg", at(18));
audit("pm", at(16), [at(18.5), at(20), at(22)]);
out("#m1, #m2, #m3", at(18.5) - 1.1, .6);

// 4 · dead links + 2021 news
rise("#l1 .w", at(24)); rise("#l2 .w", at(24.4)); rise("#l3 .w", at(24.8));
swipe("#l3 .hlbg", at(25.6));
audit("pl1", at(24), [at(26), at(27)]);
out("#l1, #l2, #l3", at(26) - 1.1, .6);
tl.to("#pl1-z, #pl1-cap1", { opacity: 0, filter: "blur(16px)", duration: .5, ease: "power2.in" }, at(28) - .5);
tl.set("#pl2-z", { x: ZP.pl2[0].x, y: ZP.pl2[0].y, scale: ZP.pl2[0].s }, at(28) - .5);
tl.fromTo("#pl2-z", { opacity: 0, filter: "blur(16px)" }, { opacity: 1, filter: "blur(0px)", duration: .6, ease: SOFT }, at(28) - .3);
tl.set("#pl2", { opacity: 1 }, at(28) - .5);
tl.fromTo("#pl2-mk0", { opacity: 0, scale: 1.3 }, { opacity: 1, scale: 1, duration: .45, ease: "back.out(2)" }, at(28.5));
tl.fromTo("#pl2-cap0", { opacity: 0, y: 40, filter: "blur(10px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: .7, ease: SOFT }, at(28.5));

// 5 · manual WhatsApp orders
rise("#d1 .w", at(30)); rise("#d2 .w", at(30.4)); rise("#d3 .w", at(30.8));
swipe("#d3 .hlbg", at(31.6));
audit("po", at(30), [at(32.5)]);
out("#d1, #d2, #d3", at(32.5) - 1.1, .6);

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
