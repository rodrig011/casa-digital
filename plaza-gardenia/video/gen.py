#!/usr/bin/env python3
"""Plaza Gardenia (Talanga): video vertical para conseguir inquilinos (2026-11-02).

Rehace el video que hizo el papá de rodrigo con sus mismas tomas reales (dron, rótulo, locales, interior,
atardecer, calle de Talanga). Sin datos inventados: solo lo que dice el video original y lo que confirmó
rodrigo (locales de 7 x 8 m = 56 m2 con baño propio, un local con carril de drive-thru, 27 parqueos,
RNP, Pollo Chilero e INCOOLL Systems en el rótulo, teléfono del video original). Sin precios.

Uso:
  python3 gen.py <video-original.mov> <carpeta-salida> [<deps>]
  cd <carpeta-salida>/plaza && hyperframes render . -o ../plaza-gardenia-vertical.mp4 -q high
<deps> es una carpeta con node_modules/gsap y node_modules/@fontsource/{cormorant-garamond,inter}.
Música: "Stylish" (FASSounds), 110 BPM, la canción oficial; los cortes caen en compases.
"""
import json, os, shutil, subprocess, sys

SRC_VIDEO, OUT = sys.argv[1], sys.argv[2]
DEPS = sys.argv[3] if len(sys.argv) > 3 else os.path.join(OUT, "..", "deps")
MUSIC = os.environ.get("MUSIC", "/mnt/project-files/musica/stylish-fassounds.mp3")
PHONE = os.environ.get("PLAZA_TEL", "9338-1063")  # el que sale en el video original

P0, BAR = 0.035, 4 * 60 / 110
K = lambda k: round(P0 + BAR * k, 3)

# (id, compás inicio, compás fin, toma, (inicio, fin) en el original, recorte w:h:x:y, tamaño en pantalla)
# Los recortes quitan el logo que el video original pone arriba a la izquierda.
SCENES = [
    ("s1", 0, 3, "drone", (3.50, 4.90), "692:480:140:0", (1000, 694)),
    ("s2", 3, 5, "pylon", (25.58, 28.94), "520:480:312:0", (900, 830)),
    ("s3", 5, 7, "frente", (14.18, 17.44), "676:480:156:0", (1000, 710)),
    ("s4", 7, 9, "interior", (28.99, 29.93), "832:480:0:0", (1000, 576)),
    ("s5", 9, 11, "atardecer", (32.62, 35.04), "832:480:0:0", (1000, 576)),
    ("s6", 11, 13, "calle", (35.10, 37.14), "832:480:0:0", (1000, 576)),
    ("s7", 13, 17, "dronefin", (3.50, 4.90), "692:480:140:0", (1000, 694)),
]
TOTAL = K(17)

proj = os.path.join(OUT, "plaza")
A = os.path.join(proj, "assets")
os.makedirs(os.path.join(A, "fonts"), exist_ok=True)


def cut(name, a, b, crop, size, dur):
    f = dur / (b - a)
    out = os.path.join(A, name + ".mp4")
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", SRC_VIDEO, "-an", "-vf",
                        f"crop={crop},setpts={f}*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
                        f"scale={size[0]}:{size[1]}:flags=lanczos,format=yuv420p",
                        "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-r", "30", out], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-vf", "scale=180:-2,boxblur=10:2",
                        "-c:v", "libx264", "-crf", "24", os.path.join(A, name + "_bg.mp4")], check=True)


for sid, s, e, name, (a, b), crop, size in SCENES:
    cut(name, a, b, crop, size, K(e) - K(s) + 0.3)

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


# Una sola letra (Hanken Grotesk), en minúscula normal, alineada a la izquierda. Sin etiquetas
# chiquitas arriba del titular, sin cursivas, sin líneas finas, sin sombras ni degradados
# (reglas de taste-skill e impeccable en .claude/skills).
# Texto de cada escena: (titular, frase)
TEXT = {
    "s1": ("Plaza Gardenia", "Locales comerciales en renta en Talanga."),
    "s2": ("Ya tiene buenos vecinos", "RNP, Pollo Chilero e INCOOLL Systems ya están aquí."),
    "s3": ("Locales de 7 × 8 metros", "Cada uno con su propio baño."),
    "s4": ("56 m<sup>2</sup>", "Por local, con luz natural."),
    "s5": ("27 parqueos", "Y un local con carril de drive-thru."),
    "s6": ("En Talanga, Francisco Morazán", ""),
}
L = 40  # margen izquierdo: el mismo borde de la foto

secs = []
for sid, s, e, name, _, _, (w, h) in SCENES:
    st, du = K(s), round(K(e) - K(s), 3)
    if sid != "s7":
        title, sub = TEXT[sid]
        top = 1000 - h // 2
        card = (f'<div class="card" id="card-{sid}" style="width:{w}px;height:{h}px;left:{L}px;top:{top}px">'
                f'<video class="fg" id="v-{sid}" src="assets/{name}.mp4" data-start="{st}" data-duration="{du}" data-media-start="0" muted playsinline></video></div>')
        big = " big" if sid == "s4" else ""
        inner = (f'{card}<div class="h1{big}" id="h-{sid}" style="bottom:{1920 - top + 56}px">{words(title)}</div>'
                 + (f'<p class="sub" id="sub-{sid}" style="top:{top + h + 48}px">{sub}</p>' if sub else ""))
    else:
        inner = (f'<div class="card" id="card-s7" style="width:{w}px;height:{h}px;left:{L}px;top:300px">'
                 f'<video class="fg" id="v-s7" src="assets/{name}.mp4" data-start="{st}" data-duration="{du}" data-media-start="0" muted playsinline></video></div>'
                 f'<div class="endc" style="top:{300 + h + 72}px">'
                 f'<div class="h1 end" id="h-s7">{words("Rente su local en Plaza Gardenia")}</div>'
                 f'<p class="sub2" id="call">Llame para más información</p>'
                 f'<div class="tel" id="tel"><svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg><span>{PHONE}</span></div>'
                 f'</div>')
    secs.append(f'<div id="{sid}" class="scene">{inner}</div>')

CSS = r"""
@font-face{font-family:"HG";src:url("assets/fonts/hg-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"HG";src:url("assets/fonts/hg-500.woff2") format("woff2");font-weight:500;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:#F4F5F1;}
#root{position:relative;width:1080px;height:1920px;background:#F4F5F1;color:#1C3326;font-family:"HG",sans-serif;-webkit-font-smoothing:antialiased;font-kerning:normal;}
.scene{position:absolute;inset:0;overflow:hidden;background:#F4F5F1;opacity:0;}
.card{position:absolute;border-radius:6px;overflow:hidden;background:#DDE2DA;}
.card video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:50% 50%;}
.h1{position:absolute;left:36px;right:40px;font-weight:500;font-size:112px;line-height:.96;letter-spacing:-.045em;color:#1C3326;}
.h1.big{font-size:300px;line-height:.85;letter-spacing:-.06em;left:28px;}
.w{display:inline-block;}
sup{font-size:.42em;vertical-align:.95em;letter-spacing:0;margin-left:.04em;}
.sub{position:absolute;left:40px;right:80px;font-weight:400;font-size:58px;line-height:1.25;letter-spacing:-.02em;color:#4D6457;}
.endc{position:absolute;left:0;right:0;}
.h1.end{position:relative;font-size:104px;}
.sub2{margin:56px 40px 0;font-weight:400;font-size:58px;letter-spacing:-.015em;color:#4D6457;}
.tel{display:flex;align-items:center;gap:28px;margin:28px 40px 0;padding:34px 48px;width:max-content;border-radius:6px;background:#1C3326;}
.tel svg{width:58px;height:58px;fill:#F4F5F1;}
.tel span{font-weight:500;font-size:96px;letter-spacing:-.02em;color:#F4F5F1;font-variant-numeric:tabular-nums;}
"""

JS = r"""
const tl = gsap.timeline({ paused: true });
const SOFT = "expo.out";
const K = k => +(P0 + BAR * k).toFixed(3);
function rise(sel, t, o) { o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y ?? 40 },
    { opacity: 1, y: 0, duration: o.d || 1.4, ease: SOFT, stagger: o.st ?? .08 }, t); }
SC.forEach(([id, s, e]) => {
  const a = K(s), b = K(e), len = b - a, end = id === "s7" ? 1.4 : .45;
  tl.fromTo("#" + id, { opacity: 0 }, { opacity: 1, duration: .45, ease: "power1.out" }, a);
  tl.to("#" + id, { opacity: 0, duration: end, ease: "power1.in" }, b - end);
  tl.fromTo("#card-" + id, { clipPath: "inset(0 0 100% 0)" }, { clipPath: "inset(0 0 0% 0)", duration: 1.5, ease: "expo.inOut" }, a);
  tl.fromTo("#v-" + id, { scale: 1.12 }, { scale: 1.0, duration: len, ease: "power1.out" }, a);
  if (id === "s7") return;
  rise("#h-" + id + " .w", a + .45);
  rise("#sub-" + id, a + 1.0, { y: 24 });
});
rise("#h-s7 .w", K(13) + .5);
rise("#call", K(14), { y: 24 });
rise("#tel", K(14.3), { y: 30 });
window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
""".replace("P0", str(P0)).replace("BAR", str(BAR)).replace("SC.", json.dumps([[sid, s, e] for sid, s, e, *_ in SCENES]) + ".")

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
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="{TOTAL}" data-fade-out="3" data-track-index="1"></audio>
{chr(10).join(secs)}
</div>
<script>{JS}</script>
</body>
</html>
'''
open(os.path.join(proj, "index.html"), "w").write(HTML)
print(proj, TOTAL)
