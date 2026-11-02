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
    ("s1", 0, 3, "drone", (3.50, 4.90), "692:400:140:80", (1000, 578)),
    ("s2", 3, 5, "pylon", (25.58, 28.94), "520:480:312:0", (900, 830)),
    ("s3", 5, 7, "frente", (14.18, 17.44), "676:480:156:0", (1000, 710)),
    ("s4", 7, 9, "interior", (28.99, 29.93), "832:480:0:0", (1000, 576)),
    ("s5", 9, 11, "atardecer", (32.62, 35.04), "832:480:0:0", (1000, 576)),
    ("s6", 11, 13, "calle", (35.10, 37.14), "832:480:0:0", (1000, 576)),
    ("s7", 13, 17, "dronefin", (3.50, 4.90), "692:400:140:80", (1000, 578)),
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
for w in (300, 400, 500):
    shutil.copy(os.path.join(nm, "@fontsource", "cormorant-garamond", "files", f"cormorant-garamond-latin-{w}-normal.woff2"), os.path.join(A, "fonts", f"cg-{w}.woff2"))
shutil.copy(os.path.join(nm, "@fontsource", "cormorant-garamond", "files", "cormorant-garamond-latin-400-italic.woff2"), os.path.join(A, "fonts", "cg-400i.woff2"))
for w in (300, 400, 500):
    shutil.copy(os.path.join(nm, "@fontsource", "inter", "files", f"inter-latin-{w}-normal.woff2"), os.path.join(A, "fonts", f"in-{w}.woff2"))
shutil.copy(MUSIC, os.path.join(A, "musica.mp3"))
json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
           "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
           "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
json.dump({"id": "plaza-gardenia-v1", "name": "Plaza Gardenia"}, open(os.path.join(proj, "meta.json"), "w"))


def words(t):
    return " ".join(f'<span class="w">{x}</span>' for x in t.split())


# Texto de cada escena: (arriba pequeño, titular, abajo)
TEXT = {
    "s1": ("Bienvenidos a", "Plaza Gardenia", "Locales comerciales en renta"),
    "s2": ("Ya están aquí", "Buenos vecinos", "RNP &nbsp;·&nbsp; Pollo Chilero &nbsp;·&nbsp; INCOOLL Systems"),
    "s3": ("Locales disponibles", "Su negocio, aquí", "Locales de 7 × 8 metros"),
    "s4": ("Cada local", "56 m²", "con su propio baño"),
    "s5": ("Pensada para sus clientes", "27 parqueos", "y un local con carril de drive-thru"),
    "s6": ("Ubicación", "Talanga", "Francisco Morazán"),
}

secs = []
for sid, s, e, name, _, _, (w, h) in SCENES:
    st, du = K(s), round(K(e) - K(s), 3)
    vids = (f'<video class="bgv" id="bg-{sid}" src="assets/{name}_bg.mp4" data-start="{st}" data-duration="{du}" data-media-start="0" muted playsinline></video>'
            f'<div class="shade"></div>')
    if sid != "s7":
        top, title, sub = TEXT[sid]
        card = (f'<div class="card" id="card-{sid}" style="width:{w}px;height:{h}px;left:{(1080 - w) // 2}px;top:{1040 - h // 2}px">'
                f'<video class="fg" id="v-{sid}" src="assets/{name}.mp4" data-start="{st}" data-duration="{du}" data-media-start="0" muted playsinline></video></div>')
        big = " big" if sid == "s4" else ""
        inner = (f'{vids}{card}<div class="top" style="bottom:{1920 - (1040 - h // 2) + 70}px">'
                 f'<div class="eb" id="eb-{sid}">{top}</div><div class="h1{big}" id="h-{sid}">{words(title)}</div></div>'
                 f'<div class="sub" id="sub-{sid}" style="top:{1040 + h // 2 + 70}px">{sub}</div>')
    else:
        inner = (f'{vids}<div class="endc">'
                 f'<div class="mono" id="mono">PG</div><div class="wm" id="wm">PLAZA GARDENIA</div>'
                 f'<div class="rule" id="rule"></div>'
                 f'<div class="h1" id="h-s7">{words("Rente su local")}</div>'
                 f'<div class="eb" id="eb-s7">Para información</div>'
                 f'<div class="tel" id="tel"><svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg><span>{PHONE}</span></div>'
                 f'<div class="loc" id="loc">Talanga, Francisco Morazán</div></div>')
    secs.append(f'<div id="{sid}" class="scene">{inner}</div>')

CSS = r'''
@font-face{font-family:"CG";src:url("assets/fonts/cg-300.woff2") format("woff2");font-weight:300;}
@font-face{font-family:"CG";src:url("assets/fonts/cg-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"CG";src:url("assets/fonts/cg-500.woff2") format("woff2");font-weight:500;}
@font-face{font-family:"CG";src:url("assets/fonts/cg-400i.woff2") format("woff2");font-weight:400;font-style:italic;}
@font-face{font-family:"IN";src:url("assets/fonts/in-300.woff2") format("woff2");font-weight:300;}
@font-face{font-family:"IN";src:url("assets/fonts/in-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"IN";src:url("assets/fonts/in-500.woff2") format("woff2");font-weight:500;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:#0A0D0B;}
#root{position:relative;width:1080px;height:1920px;background:#0A0D0B;color:#F3EEE4;font-family:"IN",sans-serif;-webkit-font-smoothing:antialiased;}
.scene{position:absolute;inset:0;overflow:hidden;background:#0A0D0B;opacity:0;}
.bgv{position:absolute;left:-180px;top:-120px;width:1440px;height:2160px;object-fit:cover;filter:blur(36px) saturate(1.1);opacity:.55;transform:scale(1.1);}
.shade{position:absolute;inset:0;background:radial-gradient(120% 70% at 50% 52%,rgba(10,13,11,.15),rgba(10,13,11,.85) 70%),linear-gradient(180deg,rgba(10,13,11,.7),rgba(10,13,11,.1) 35%,rgba(10,13,11,.1) 65%,rgba(10,13,11,.75));}
.card{position:absolute;border-radius:30px;overflow:hidden;box-shadow:0 50px 120px rgba(0,0,0,.6),0 0 0 1px rgba(243,238,228,.14);}
.card video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:50% 50%;}
.top{position:absolute;left:60px;right:60px;text-align:center;}
.eb{font-family:"IN";font-weight:500;font-size:30px;letter-spacing:.32em;text-transform:uppercase;color:#C9D8C5;margin-bottom:18px;}
.h1{font-family:"CG";font-weight:400;font-size:112px;line-height:1.02;letter-spacing:-.01em;color:#F7F2E8;}
.h1.big{font-size:190px;font-weight:300;line-height:.95;}
.w{display:inline-block;}
.sub{position:absolute;left:60px;right:60px;text-align:center;font-family:"CG";font-style:italic;font-weight:400;font-size:58px;line-height:1.25;color:#E8E1D3;}
.endc{position:absolute;left:0;right:0;top:0;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.mono{font-family:"CG";font-weight:300;font-size:170px;line-height:1;letter-spacing:-.06em;color:#F7F2E8;}
.wm{font-family:"CG";font-weight:500;font-size:40px;letter-spacing:.42em;margin:8px 0 0 .42em;color:#E8E1D3;}
.rule{width:140px;height:1px;background:#C9D8C5;margin:70px 0 70px;transform-origin:50% 50%;}
#h-s7{margin-bottom:60px;}
.tel{display:flex;align-items:center;gap:26px;padding:26px 52px;border-radius:999px;border:1px solid rgba(243,238,228,.35);background:rgba(243,238,228,.06);}
.tel svg{width:50px;height:50px;fill:#C9D8C5;}
.tel span{font-family:"IN";font-weight:300;font-size:78px;letter-spacing:.04em;color:#F7F2E8;}
.loc{margin-top:46px;font-family:"CG";font-style:italic;font-size:46px;color:#E8E1D3;}
'''

JS = r'''
const tl = gsap.timeline({ paused: true });
const SOFT = "expo.out";
const K = k => +(P0 + BAR * k).toFixed(3);
function rise(sel, t, o) { o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y ?? 26, filter: "blur(14px)" },
    { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d || 1.6, ease: SOFT, stagger: o.st ?? .1 }, t); }
SC.forEach(([id, s, e]) => {
  const a = K(s), b = K(e), len = b - a;
  tl.fromTo("#" + id, { opacity: 0 }, { opacity: 1, duration: .55, ease: "power1.out" }, a);
  if (id !== "s7") tl.to("#" + id, { opacity: 0, duration: .5, ease: "power1.in" }, b - .5);
  else tl.to("#" + id, { opacity: 0, duration: 1.2, ease: "power1.in" }, b - 1.2);
  if (id === "s7") return;
  tl.fromTo("#card-" + id, { opacity: 0, y: 50, scale: .97, filter: "blur(10px)" },
    { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 1.8, ease: SOFT }, a + .05);
  tl.fromTo("#v-" + id, { scale: 1.0 }, { scale: 1.07, duration: len, ease: "none" }, a);
  rise("#eb-" + id, a + .3, { d: 1.4 });
  rise("#h-" + id + " .w", a + .5, { d: 1.8, st: .12 });
  rise("#sub-" + id, a + 1.1, { d: 1.6 });
});
// cierre
const e0 = K(13);
rise("#mono", e0 + .3, { d: 2.2, y: 0 });
rise("#wm", e0 + .7, { d: 2 });
tl.fromTo("#rule", { scaleX: 0 }, { scaleX: 1, duration: 1.6, ease: "power2.inOut" }, e0 + 1.2);
rise("#h-s7 .w", K(14), { d: 1.8, st: .14 });
rise("#eb-s7", K(14.6), { d: 1.4 });
rise("#tel", K(14.8), { d: 1.8 });
rise("#loc", K(15.3), { d: 1.6 });
window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
'''.replace("P0", str(P0)).replace("BAR", str(BAR)).replace("SC.", json.dumps([[sid, s, e] for sid, s, e, *_ in SCENES]) + ".")

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
