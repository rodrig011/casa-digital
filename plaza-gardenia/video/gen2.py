#!/usr/bin/env python3
"""Plaza Gardenia v2 (2026-11-02): tomas a pantalla completa y más ritmo.

rodrigo dijo que el v1 (tarjetas sobre fondo blanco, gen.py) se veía mal. Aquí cada toma llena la
pantalla vertical: se recorta una ventana 9:16 del video original (832x480) que se va moviendo
despacio por la toma, y el texto grande va abajo sobre una sombra neutra. Cortes secos en cada
compás de "Stylish" (110 BPM). Mismos datos confirmados que el v1, sin precios. Diseño según
.claude/skills (una sola letra, sin etiquetas chiquitas, sin cursivas).

Uso: python3 gen2.py <video-original.mov> <carpeta-salida> <deps>
     cd <carpeta-salida>/plaza2 && hyperframes render . -o ../plaza-gardenia-vertical-v2.mp4 -q high
"""
import json, os, shutil, subprocess, sys

SRC_VIDEO, OUT, DEPS = sys.argv[1], sys.argv[2], sys.argv[3]
MUSIC = os.environ.get("MUSIC", "/mnt/project-files/musica/stylish-fassounds.mp3")
PHONE = "9338-1063"
P0, BAR = 0.035, 4 * 60 / 110
K = lambda k: round(P0 + BAR * k, 3)

# (id, compás inicio, compás fin, archivo, (inicio, fin) en el original, x inicial, x final de la ventana 270x480)
# Las tomas con el logo pegado del original (arriba a la izquierda) empiezan en x >= 150.
SHOTS = [
    ("a", 0, 2, "drone", (3.50, 4.90), 170, 420),
    ("b", 2, 4, "frente", (14.18, 17.44), 540, 230),
    ("c", 4, 6, "pylon", (25.58, 28.94), 420, 500),
    ("d", 6, 8, "interior", (28.99, 29.93), 40, 330),
    ("e", 8, 10, "atardecer", (32.62, 35.04), 20, 300),
    ("f", 10, 12, "calle", (35.10, 37.14), 180, 470),
    ("g", 12, 15, "drone2", (3.50, 4.90), 420, 230),
]
TEXT = {
    "a": ("Plaza Gardenia", "Locales comerciales en renta"),
    "b": ("Locales de 7 × 8 m", "Cada uno con su propio baño"),
    "c": ("Ya tiene buenos vecinos", "RNP, Pollo Chilero e INCOOLL Systems"),
    "d": ("56 m<sup>2</sup>", "Por local"),
    "e": ("27 parqueos", "Y un local con carril de drive-thru"),
    "f": ("Talanga", "Francisco Morazán"),
}
TOTAL = K(15)

proj = os.path.join(OUT, "plaza2")
A = os.path.join(proj, "assets")
os.makedirs(os.path.join(A, "fonts"), exist_ok=True)

for sid, s, e, name, (a, b), x0, x1 in SHOTS:
    out = os.path.join(A, name + ".mp4")
    if os.path.exists(out):
        continue
    dur = K(e) - K(s) + 0.2
    f = dur / (b - a)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", SRC_VIDEO, "-an", "-vf",
                    f"setpts={f}*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
                    f"crop=270:480:'{x0}+({x1}-{x0})*min(t/{dur},1)':0,"
                    "scale=1080:1920:flags=lanczos,unsharp=5:5:0.5,format=yuv420p",
                    "-c:v", "libx264", "-crf", "15", "-preset", "slow", "-r", "30", out], check=True)

nm = os.path.join(DEPS, "node_modules")
shutil.copy(os.path.join(nm, "gsap", "dist", "gsap.min.js"), A)
for w in (400, 500):
    shutil.copy(os.path.join(nm, "@fontsource", "hanken-grotesk", "files", f"hanken-grotesk-latin-{w}-normal.woff2"), os.path.join(A, "fonts", f"hg-{w}.woff2"))
shutil.copy(MUSIC, os.path.join(A, "musica.mp3"))
json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
           "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
           "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
json.dump({"id": "plaza-gardenia-v2", "name": "Plaza Gardenia"}, open(os.path.join(proj, "meta.json"), "w"))


def words(t):
    return " ".join(f'<span class="w">{x}</span>' for x in t.split())


secs = []
for sid, s, e, name, *_ in SHOTS:
    st, du = K(s), round(K(e) - K(s), 3)
    vid = f'<video class="full" id="v-{sid}" src="assets/{name}.mp4" data-start="{st}" data-duration="{du}" data-media-start="0" muted playsinline></video>'
    if sid in TEXT:
        t, sub = TEXT[sid]
        big = " big" if sid == "d" else ""
        txt = (f'<div class="scrim"></div><div class="txt"><div class="h1{big}" id="h-{sid}">{words(t)}</div>'
               + (f'<p class="sub" id="s-{sid}">{sub}</p>' if sub else "") + '</div>')
    else:
        txt = (f'<div class="dim" id="dim"></div><div class="endc">'
               f'<div class="h1" id="h-g">{words("Rente su local en Plaza Gardenia")}</div>'
               f'<p class="sub" id="s-g">Llame para más información</p>'
               f'<div class="tel" id="tel"><svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg><span>{PHONE}</span></div>'
               f'</div>')
    secs.append(f'<div id="{sid}" class="scene">{vid}{txt}</div>')

CSS = r"""
@font-face{font-family:"HG";src:url("assets/fonts/hg-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"HG";src:url("assets/fonts/hg-500.woff2") format("woff2");font-weight:500;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000;}
#root{position:relative;width:1080px;height:1920px;background:#000;color:#fff;font-family:"HG",sans-serif;-webkit-font-smoothing:antialiased;font-kerning:normal;}
.scene{position:absolute;inset:0;overflow:hidden;opacity:0;}
.full{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;transform-origin:50% 50%;}
.scrim{position:absolute;left:0;right:0;bottom:0;height:1000px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.6) 45%,rgba(0,0,0,.82));}
.txt{position:absolute;left:64px;right:64px;bottom:250px;}
.h1{font-weight:500;font-size:132px;line-height:.95;letter-spacing:-.045em;color:#fff;text-wrap:balance;}
.h1.big{font-size:330px;line-height:.85;letter-spacing:-.06em;margin-left:-.04em;}
sup{font-size:.42em;vertical-align:.95em;letter-spacing:0;margin-left:.04em;}
.w{display:inline-block;}
.sub{margin-top:32px;font-weight:400;font-size:56px;line-height:1.2;letter-spacing:-.02em;color:rgba(255,255,255,.88);}
.dim{position:absolute;inset:0;background:rgba(12,24,17,.72);}
.endc{position:absolute;left:64px;right:64px;top:560px;}
.tel{display:flex;align-items:center;gap:28px;margin-top:36px;padding:34px 50px;width:max-content;border-radius:8px;background:#fff;}
.tel svg{width:60px;height:60px;fill:#1C3326;}
.tel span{font-weight:500;font-size:104px;letter-spacing:-.02em;color:#1C3326;font-variant-numeric:tabular-nums;}
"""

JS = r"""
const tl = gsap.timeline({ paused: true });
const K = k => +(P0 + BAR * k).toFixed(3);
function rise(sel, t, o) { o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y ?? 70 }, { opacity: 1, y: 0, duration: o.d || 1.0, ease: "expo.out", stagger: o.st ?? .07 }, t); }
SC.forEach(([id, s, e]) => {
  const a = K(s), b = K(e);
  tl.set("#" + id, { opacity: 1 }, a);
  if (id !== "g") tl.set("#" + id, { opacity: 0 }, b);
  tl.fromTo("#v-" + id, { scale: 1.08 }, { scale: 1.0, duration: b - a, ease: "power2.out" }, a);
  if (id === "g") return;
  rise("#h-" + id + " .w", a + .12);
  rise("#s-" + id, a + .55, { y: 40 });
});
const g = K(12);
tl.fromTo("#dim", { opacity: 0 }, { opacity: 1, duration: 1.2, ease: "power2.out" }, g);
rise("#h-g .w", g + .4);
rise("#s-g", g + 1.3, { y: 40 });
rise("#tel", g + 1.7, { y: 50 });
tl.to("#g", { opacity: 0, duration: 1.4, ease: "power1.in" }, K(15) - 1.4);
window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
""".replace("P0", str(P0)).replace("BAR", str(BAR)).replace("SC.", json.dumps([[sid, s, e] for sid, s, e, *_ in SHOTS]) + ".")

HTML = f'''<!doctype html>
<html lang="es" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>Plaza Gardenia</title>
<script src="assets/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="{TOTAL}" data-fade-out="2.5" data-track-index="1"></audio>
{chr(10).join(secs)}
</div>
<script>{JS}</script>
</body>
</html>
'''
open(os.path.join(proj, "index.html"), "w").write(HTML)
print(proj, TOTAL)
