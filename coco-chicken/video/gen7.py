#!/usr/bin/env python3
"""Coco Chicken pitch video v2 (2026-10-14). Same look, music and bar grid as gen6, new story:
they have no riders, so delivery stays with PedidosYa and Bip Bip; what they lack is seeing all of it
together -> owner panel (real screenshots of the demo panel, labelled demo data): recommended actions,
commission per app and weekly deposits, pickup orders via WhatsApp, till closing -> why us -> outro."""
import json, os, shutil, sys
from PIL import Image
import gen3, gen6
from gen2 import MARK, words, rgba, lift, hexrgb, ribbons, DEPS, HERE
from gen6 import K, P0, BAR, R, RED, ORG, BRANCHES

SRC = os.path.join(HERE, "coco-src")
OUT = os.path.join(HERE, "videos7")
gen6.SCENES[:] = [("intro", 0, 3), ("fame", 3, 8), ("local", 8, 11), ("apps", 11, 16), ("calm", 16, 18),
                  ("panel", 18, 23), ("ventas", 23, 27), ("pickup", 27, 31), ("caja", 31, 34), ("why", 34, 37), ("end", 37, 41)]
SCENES = gen6.SCENES
TOTAL = K(41)
hl = gen3.hl

# panel crops, in CSS px of the 1440x900 screenshot (image is 2x): name -> (file, x, y, w, h)
CROPS = {"recs": ("pv-hoy.png", 0, 362, 830, 480), "canal": ("pv-ventas.png", 0, 362, 830, 452),
         "recoger": ("pv-recoger.png", 365, 250, 720, 600), "caja": ("pv-caja.png", 0, 250, 830, 400)}

CSS7 = r'''
.left.narrow .h2{font-size:40px;margin-top:34px;}
.pshot{position:absolute;background:#fff;border-radius:26px;overflow:hidden;box-shadow:0 40px 100px rgba(0,0,0,.16),0 0 0 1px rgba(0,0,0,.06);}
.pshot .lbl{height:52px;background:#F3F3F3;display:flex;align-items:center;padding:0 22px;gap:9px;font-size:19px;font-weight:600;color:#6E6E73;border-bottom:1px solid #E5E5E5;}
.pshot .lbl i{width:12px;height:12px;border-radius:50%;background:#D1D1D6;}
.pshot .lbl em{font-style:normal;margin-left:12px;}
.pshot .body{position:relative;}
.pshot img{display:block;}
.mk2.blue{border-color:#0176D3;box-shadow:0 0 0 8px rgba(1,118,211,.16),0 0 40px rgba(1,118,211,.25);}
'''


def build():
    c = R["colors"]; f = R["fonts"]; hero = RED
    acc = lift(c["accent"], 0.5); pri = lift(c["primary"], 0.38)
    proj = os.path.join(OUT, R["slug"])
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    A = lambda *p: os.path.join(proj, "assets", *p)
    shutil.copy(os.path.join(HERE, "musica2.mp3"), A("musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), A("gsap.min.js"))
    shutil.copy(os.path.join(DEPS, "@fontsource", "archivo-black", "files", f["displayFile"]), A("fonts", "display.woff2"))
    for w in (300, 400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"), A("fonts", f"it-{w}.woff2"))
    for n in ("tiktok.mp4", "local.jpg", "logo.png", "tk-perfil.png"):
        shutil.copy(os.path.join(SRC, n), A(n))
    for k, (fn, x, y, w, h) in CROPS.items():
        Image.open(os.path.join(SRC, "panel", fn)).crop((2 * x, 2 * y, 2 * (x + w), 2 * (y + h))).save(A(f"p-{k}.png"))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "coco-chicken-v2", "name": "Casa Digital x Coco Chicken"}, open(os.path.join(proj, "meta.json"), "w"))

    def scene(sid, inner, cls=""):
        s, e = next((a, b) for i, a, b in SCENES if i == sid)
        return (f'<section id="{sid}" class="clip scene {cls}" data-start="{K(s)}" data-duration="{round(K(e) - K(s), 3)}" '
                f'data-track-index="0"><div class="cam" id="cam-{sid}">{inner}</div></section>')

    def shotc(sid, img, w, h, lbl, x, y, marks):
        mk = "".join(f'<div class="mk2" id="{sid}-mk{i}" style="left:{a}px;top:{b}px;width:{cw}px;height:{ch}px"></div>'
                     for i, (a, b, cw, ch) in enumerate(marks))
        return (f'<div class="shotc" id="{sid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h + 58}px">'
                f'<div class="lbl"><i></i><i></i><i></i>&nbsp;&nbsp;{lbl}</div>'
                f'<div class="body"><img src="assets/{img}" style="width:{w}px;height:{h}px">{mk}</div></div>')

    def pshot(sid, key, width, x, tab, marks):
        _, _, _, cw, ch = CROPS[key]; s = width / cw; h = round(ch * s)
        y = round((1080 - h - 52) / 2)
        mk = "".join(f'<div class="mk2 blue" id="{sid}-mk{i}" style="left:{round(a * s)}px;top:{round(b * s)}px;width:{round(mw * s)}px;height:{round(mh * s)}px"></div>'
                     for i, (a, b, mw, mh) in enumerate(marks))
        return (f'<div class="pshot" id="{sid}" style="left:{x}px;top:{y}px;width:{width}px">'
                f'<div class="lbl"><i></i><i></i><i></i><em>Panel Coco Chicken · {tab}</em></div>'
                f'<div class="body"><img src="assets/p-{key}.png" style="width:{width}px;height:{h}px">{mk}</div></div>')

    vid = (f'<video id="tkvid" class="vid" src="assets/tiktok.mp4" data-start="{K(3)}" data-duration="{round(K(8) - K(3), 3)}" '
           f'data-media-start="0" data-track-index="2" muted playsinline></video>')
    stats = [("204.9K", "seguidores en TikTok"), ("3.1M", "me gusta en TikTok"), ("127K", "seguidores en Facebook"),
             ("871.5K", "vistas: «¿Pollos a 15 lempiras?»")]
    stats_html = "".join(f'<div class="st" id="st{i}"><b>{a}</b><span>{b}</span></div>' for i, (a, b) in enumerate(stats))
    chips = "".join(f'<div class="chip" id="cp{i}"><i></i>{b}</div>' for i, b in enumerate(BRANCHES))
    chips += '<div class="chip hrs" id="cp3"><i></i>Lunes a domingo · 9 am a 10 pm</div>'

    tk = shotc("shtk", "tk-perfil.png", 620, 230, "tiktok.com/@cocochiken1", 1130, 230, [(200, 140, 196, 50)])
    s = 0.68  # storefront photo (their Facebook cover): Bip Bip on the big sign and on the window poster
    loc = shotc("shloc", "local.jpg", round(1250 * s), round(462 * s), "Facebook · portada de Coco Chicken", 960, 220,
                [(round(130 * s), round(15 * s), round(132 * s), round(60 * s)), (round(945 * s), round(145 * s), round(50 * s), round(40 * s))])

    whys = ["Hecho a la medida de Coco Chicken.", "PedidosYa y Bip Bip siguen igual.", "En la compu y en el celular.", "Listo en 14 días."]
    whys_html = "".join(f'<div class="wy" id="wy{i}"><i>✓</i><span>{words(t)}</span></div>' for i, t in enumerate(whys))
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])

    def left(pref, eyebrow, lines, sub=None):
        out = f'<div class="eyebrow2" id="{pref}0">{eyebrow}</div>' if eyebrow else ""
        for i, t in enumerate(lines):
            out += f'<div class="h1" id="{pref}{i + 1}">{hl(t[1:]) if t.startswith("*") else words(t)}</div>'
        if sub:
            out += f'<div class="h2 gray" id="{pref}s">{words(sub)}</div>'
        return f'<div class="left narrow">{out}</div>'

    body = "\n".join([
        scene("intro", f'''
          <div class="wash w1"></div><div class="wash w2"></div>
          <div class="center">
            <div class="cd" id="icd">{gen3.HOUSE}<span>Casa Digital</span></div>
            <div class="sub-g" id="ipres">{words("una propuesta para")}</div>
            <div class="disp intro-name" id="iname">Coco Chicken</div>
          </div>'''),
        scene("fame", f'''
          <div class="wash w3"></div>
          <div class="tagv" id="tagv">Su video fijado en TikTok</div>
          <div class="left narrow">
            <div class="h1" id="f1">{words("Ya tienen")}</div>
            <div class="h1" id="f2">{words("lo más difícil:")}</div>
            <div class="h1" id="f3">{hl("la atención.")}</div>
            <div class="stats">{stats_html}</div>
          </div>'''),
        scene("local", f'''
          <div class="wash w6"></div>
          <div class="top"><div class="h1" id="l1">{words("Tres sucursales.")} {hl("Todos los días.")}</div></div>
          <div class="photo" id="photo"><img src="assets/local.jpg"></div>
          <div class="chips">{chips}</div>'''),
        scene("apps", f'''
          <div class="wash w4"></div>
          {tk}{loc}
          <div class="quote" id="qtk"><span>Su bio en TikTok</span><b>“Pagas 3 El 4 Es Gratis<br>En Pedidos Ya”</b></div>
          <div class="quote" id="qloc" style="top:640px;left:960px;width:850px"><span>En el letrero de su local</span><b>Bip Bip</b></div>
          <div class="left narrow">
            <div class="grp" id="pg1"><div class="stepn" id="pa0">Hoy, a domicilio</div><div class="h1" id="pa1">{words("Venden por")}</div><div class="h1" id="pa2">{words("PedidosYa")}</div><div class="h1" id="pa3">{hl("y Bip Bip.")}</div></div>
            <div class="grp" id="pg2"><div class="h1" id="pa4">{words("Dos apps,")}</div><div class="h1" id="pa5">{words("dos tabletas,")}</div><div class="h1" id="pa6">{words("dos depósitos")}</div><div class="h1" id="pa7">{hl("que revisar.")}</div></div>
          </div>'''),
        scene("calm", f'''
          <div class="wash w6"></div>
          <div class="center">
            <div class="h1" id="k1">{words("Las apps ponen al repartidor.")}</div>
            <div class="h1" id="k2">{words("Lo que falta es")} <span class="kname">{words("ver todo junto.")}</span></div>
          </div>'''),
        scene("panel", f'''
          <div class="wash w8"></div>
          {pshot("ps1", "recs", 900, 960, "Inicio", [(12, 9, 806, 465)])}
          {left("n", "La propuesta", ["Un panel para", "*las 3 sucursales."], "Cada mañana le dice qué atender primero.")}
          <div class="demo" id="ndemo">Datos de ejemplo</div>'''),
        scene("ventas", f'''
          <div class="wash w4"></div>
          {pshot("ps2", "canal", 900, 960, "Ventas", [(12, 108, 806, 90)])}
          {left("v", None, ["Cuánto se lleva", "cada app,", "*cada semana."], "Con la comisión de su contrato y lo que le deben depositar.")}
          <div class="demo" id="vdemo">Datos de ejemplo</div>'''),
        scene("pickup", f'''
          <div class="wash w8"></div>
          {pshot("ps3", "recoger", 840, 1000, "Pedidos", [(362, 106, 345, 492)])}
          {left("u", None, ["Para recoger,", "*sin comisión."], "Piden por WhatsApp, la cocina lo ve y el cliente recibe aviso cuando está listo.")}
          <div class="demo" id="udemo">Datos de ejemplo</div>'''),
        scene("caja", f'''
          <div class="wash w4"></div>
          {pshot("ps4", "caja", 900, 960, "Caja", [(13, 86, 805, 35)])}
          {left("c", None, ["La caja,", "*revisada", "*cada noche."], "Si falta dinero en una sucursal, el panel le avisa.")}
          <div class="demo" id="cdemo">Datos de ejemplo</div>'''),
        scene("why", f'''
          <div class="wash w8"></div>
          <div class="left">
            <div class="h1" id="w1">{words("Por qué")} {hl("nosotros.")}</div>
            <div class="whys">{whys_html}</div>
          </div>
          <div class="ctacard" id="cta">
            <div class="cta-ic">{gen3.HOUSE}</div>
            <div class="cta-t">Casa Digital</div>
            <div class="cta-s">Se lo mostramos en 15 minutos.</div>
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
        f'<div class="ph-stage" id="fstage" style="opacity:0">{gen3.phone(vid, "phv", dark=True)}</div>',
    ])

    css = (gen3.CSS.replace("$heroB", "rgb(%d,%d,%d)" % tuple(int(v * .22) for v in hexrgb(hero))).replace("$hero", hero).replace("$acc", acc).replace("$pri", pri)
           .replace("$washA", rgba(hero, .12)).replace("$washB", rgba(ORG, .18)).replace("$sitebg", c["bg"]).replace("$siteink", c["ink"])
           .replace("$dweight", str(f["displayWeight"])).replace("$dcase", f["displayCase"]).replace("$dtrack", f["displayTracking"])
           .replace("$italface", "").replace("$ital", '"Display"').replace("$introsizepx", "150px"))
    css += gen6.GEN5_CSS + gen6.CSS6.replace("$hero", hero) + CSS7
    scenes_js = json.dumps([[i, K(a), K(b)] for i, a, b in SCENES])
    j6 = gen6.JS
    js = (j6[:j6.index("// 4 ·")] + JS7 + j6[j6.index("// 11 · outro"):]).replace("$scenes", scenes_js).replace("$P0", str(P0)).replace("$BAR", str(BAR))
    html = (gen3.HTML.replace("$title", "Casa Digital x Coco Chicken").replace("$css", css).replace("$body", body)
            .replace("$js", js).replace("$total", str(TOTAL)).replace('data-fade-out="2.5"', 'data-fade-out="4"'))
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj


JS7 = r'''
// 4 · delivery today: PedidosYa (their TikTok bio) and Bip Bip (their storefront sign)
rise("#pa0", K(11), { d: 1.2 }); rise("#pa1 .w", K(11) + .2); rise("#pa2 .w", K(11) + .5); rise("#pa3 .w", K(11) + .8);
swipe("#pa3 .hlbg", K(11.6));
tl.fromTo("#shtk", { opacity: 0, y: 70, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(11.3));
box("#shtk-mk0", K(12.1));
rise("#qtk", K(12.4), { d: 1.4 });
out("#qtk", K(13.4) - 1);
tl.to("#shtk", { opacity: 0, y: -40, filter: "blur(14px)", duration: .9, ease: "power2.in" }, K(13.4) - 1);
tl.fromTo("#shloc", { opacity: 0, y: 70, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(13.4) - .2);
box("#shloc-mk0", K(13.9)); box("#shloc-mk1", K(14.3));
rise("#qloc", K(14.1), { d: 1.4 });
out("#pg1", K(14) - .9);
rise("#pa4 .w", K(14)); rise("#pa5 .w", K(14) + .4); rise("#pa6 .w", K(14) + .8); rise("#pa7 .w", K(14) + 1.2);
swipe("#pa7 .hlbg", K(14.8));

// 5 · break
rise("#k1 .w", K(16), { d: 2, st: .12 });
rise("#k2 .w", K(16.8), { d: 2, st: .14 });

// 6-9 · the owner panel, one real screen per scene
function pscene(p, sh, t0, nl, marks, demo) {
  if (document.querySelector("#" + p + "0")) rise("#" + p + "0", K(t0), { d: 1.2 });
  for (let i = 1; i <= nl; i++) rise("#" + p + i + " .w", K(t0) + .3 * i);
  document.querySelectorAll("[id^=" + p + "] .hlbg").forEach((el, i) => swipe(el, K(t0 + .6) + i * .4));
  rise("#" + p + "s .w", K(t0 + 1.2), { st: .04 });
  tl.fromTo("#" + sh, { opacity: 0, y: 70, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.8, ease: SOFT }, K(t0) + .2);
  marks.forEach((k, i) => box("#" + sh + "-mk" + i, K(k)));
  rise("#" + demo, K(t0) + 1, { d: 1.2 });
}
pscene("n", "ps1", 18, 2, [19.6], "ndemo");
pscene("v", "ps2", 23, 3, [24.6], "vdemo");
pscene("u", "ps3", 27, 2, [28.6], "udemo");
pscene("c", "ps4", 31, 3, [32.3], "cdemo");

// 10 · why us + call to action
rise("#w1 .w", K(34));
swipe("#w1 .hlbg", K(34.4));
[34.6, 35.1, 35.6, 36.1].forEach((k, i) => rise("#wy" + i + " .w, #wy" + i + " i", K(k), { st: .04, d: 1.2 }));
tl.fromTo("#cta", { opacity: 0, y: 100, scale: .94 }, { opacity: 1, y: 0, scale: 1, duration: 2, ease: SOFT }, K(34.5));
float("#cta", K(35.3), K(37) - K(35.3));

'''

if __name__ == "__main__":
    print(build())
