#!/usr/bin/env python3
"""Plaza Gardenia v3 (2026-11-02): edición de reel de bienes raíces.

rodrigo dijo que el v2 se veía "insípido" y pidió buscar videos de bienes raíces. Lo que usan los reels
de propiedades que funcionan: gancho en los primeros 2 segundos con una pregunta en pantalla, tomas
cortas de 1 a 2 s, aceleraciones (speed ramp: entra rápido y frena), transiciones de barrido (whip)
con sonido de swoosh, golpes de sonido en los números, contadores, y al final el llamado a la acción con
el teléfono. Duración ~23 s. Mismos datos confirmados que v1/v2, sin precios.

Uso: python3 gen3.py <video-original.mov> <carpeta-salida> <deps>
     cd <carpeta-salida>/plaza3 && hyperframes render . -o ../plaza-gardenia-vertical-v3.mp4 -q high
"""
import json, os, shutil, subprocess, sys

SRC_VIDEO, OUT, DEPS = sys.argv[1], sys.argv[2], sys.argv[3]
MUSIC = os.environ.get("MUSIC", "/mnt/project-files/musica/stylish-fassounds.mp3")
PHONE = "9338-1063"
P0, BAR = 0.035, 4 * 60 / 110
H = BAR / 2  # medio compás
T = lambda h: round(P0 + H * h, 3)

# (id, medio-compás inicio, fin, archivo, (inicio, fin) en el original, x inicial, x final de la ventana 270x480)
SHOTS = [
    ("a", 0, 2, "drone", (3.50, 4.90), 380, 200),
    ("b", 2, 4, "frente", (14.18, 15.90), 560, 300),
    ("c", 4, 6, "pylon", (25.58, 28.94), 520, 440),
    ("d", 6, 8, "interior", (28.99, 29.93), 10, 330),
    ("e", 8, 10, "frente2", (15.80, 17.44), 250, 170),
    ("f", 10, 12, "atardecer", (32.62, 35.04), 20, 300),
    ("g", 12, 13, "carretera", (4.96, 5.92), 300, 470),
    ("h", 13, 14, "calle", (35.10, 37.14), 160, 470),
    ("i", 14, 21, "cierre", (3.50, 4.90), 170, 420),
]
TOTAL = T(21)
# texto: (titular, frase, contador opcional (desde, hasta, plantilla))
TEXT = {
    "a": ("¿Busca local en Talanga?", "", None),
    "b": ("Plaza Gardenia", "Locales comerciales en renta", None),
    "c": ("Ya tiene vecinos", "RNP, Pollo Chilero e INCOOLL Systems", None),
    "d": ("", "metros cuadrados por local", (0, 56, "{} m²")),
    "e": ("7 × 8 m", "Cada local con su propio baño", None),
    "f": ("", "Y un local con carril de drive-thru", (0, 27, "{} parqueos")),
    "g": ("Talanga,", "", None),
    "h": ("Francisco Morazán", "", None),
}
IMPACT = ["a", "d", "f", "i"]  # golpe de sonido al entrar

proj = os.path.join(OUT, "plaza3")
A = os.path.join(proj, "assets")
os.makedirs(os.path.join(A, "fonts"), exist_ok=True)


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


for sid, s, e, name, (a, b), x0, x1 in SHOTS:
    out = os.path.join(A, name + ".mp4")
    if os.path.exists(out):
        continue
    dur = T(e) - T(s) + 0.25
    src = b - a
    # speed ramp: el primer 35 % de la toma pasa rápido (0.3 s), el resto se frena hasta llenar la escena
    fast_src, fast_out = src * 0.35, min(0.3, dur * 0.25)
    slow_src, slow_out = src - fast_src, dur - fast_out
    fc = (f"[0:v]trim=0:{fast_src:.3f},setpts=PTS-STARTPTS,setpts={fast_out / fast_src:.4f}*PTS[f];"
          f"[0:v]trim={fast_src:.3f}:{src:.3f},setpts=PTS-STARTPTS,setpts={slow_out / slow_src:.4f}*PTS[s];"
          f"[f][s]concat=n=2:v=1,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
          f"crop=270:480:'{x0}+({x1}-{x0})*min(t/{dur:.3f},1)':0,"
          "scale=1080:1920:flags=lanczos,unsharp=5:5:0.5,eq=contrast=1.06:saturation=1.12,format=yuv420p[v]")
    run(["-ss", str(a), "-t", f"{src:.3f}", "-i", SRC_VIDEO, "-an", "-filter_complex", fc, "-map", "[v]",
         "-c:v", "libx264", "-crf", "15", "-preset", "slow", "-r", "30", out])

# efectos de sonido hechos aquí mismo (sin descargar nada): swoosh de ruido filtrado y golpe grave
run(["-f", "lavfi", "-i", "anoisesrc=d=0.5:c=pink:a=0.9", "-af",
     "highpass=f=300,lowpass=f=7000,afade=t=in:d=0.32:curve=exp,afade=t=out:st=0.32:d=0.18,volume=0.9",
     os.path.join(A, "whoosh.wav")])
run(["-f", "lavfi", "-i", "sine=f=48:d=0.9", "-f", "lavfi", "-i", "anoisesrc=d=0.08:c=white:a=0.6", "-filter_complex",
     "[0]afade=t=out:st=0:d=0.9:curve=exp,volume=2.2[a];[1]lowpass=f=2500,afade=t=out:st=0:d=0.08[b];[a][b]amix=inputs=2:normalize=0",
     os.path.join(A, "impact.wav")])

nm = os.path.join(DEPS, "node_modules")
shutil.copy(os.path.join(nm, "gsap", "dist", "gsap.min.js"), A)
for w in (500, 700):
    shutil.copy(os.path.join(nm, "@fontsource", "hanken-grotesk", "files", f"hanken-grotesk-latin-{w}-normal.woff2"), os.path.join(A, "fonts", f"hg-{w}.woff2"))
shutil.copy(MUSIC, os.path.join(A, "musica.mp3"))
json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
           "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
           "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
json.dump({"id": "plaza-gardenia-v3", "name": "Plaza Gardenia"}, open(os.path.join(proj, "meta.json"), "w"))


def words(t):
    return " ".join(f'<span class="w">{x}</span>' for x in t.split())


secs, sfx = [], []
for k, (sid, s, e, name, *_) in enumerate(SHOTS):
    st, du = T(s), round(T(e) - T(s) + 0.25, 3)
    if k == 0:
        st, du = 0, round(du + T(0), 3)  # la primera toma se ve desde el cuadro 0 (es la portada)
    vid = f'<video class="full" id="v-{sid}" src="assets/{name}.mp4" data-start="{st}" data-duration="{du}" data-media-start="0" muted playsinline></video>'
    if sid in TEXT:
        t, sub, cnt = TEXT[sid]
        hook = " hook" if sid == "a" else ""
        head = (f'<div class="num" id="n-{sid}"><span id="c-{sid}">{cnt[2].format(cnt[0])}</span></div>' if cnt
                else f'<div class="h1{hook}" id="h-{sid}">{words(t)}</div>')
        txt = (f'<div class="scrim"></div><div class="txt{hook}">{head}'
               + (f'<p class="sub" id="s-{sid}">{sub}</p>' if sub else "") + '</div>')
    else:
        txt = (f'<div class="dim" id="dim"></div><div class="endc">'
               f'<div class="h1" id="h-i">{words("Rente su local hoy")}</div>'
               f'<p class="sub" id="s-i">Plaza Gardenia, Talanga</p>'
               f'<div class="tel" id="tel"><svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg><span>{PHONE}</span></div>'
               f'<p class="sub small" id="s-i2">Llame para más información</p></div>')
    secs.append(f'<div id="{sid}" class="scene">{vid}{txt}</div>')
    if k > 0:
        sfx.append(f'<audio id="w-{sid}" src="assets/whoosh.wav" data-start="{max(st - 0.3, 0):.3f}" data-duration="0.5" data-volume="0.55" data-track-index="2"></audio>')
    if sid in IMPACT:
        sfx.append(f'<audio id="i-{sid}" src="assets/impact.wav" data-start="{st + (0.05 if sid != "a" else 0.1):.3f}" data-duration="0.9" data-volume="0.9" data-track-index="3"></audio>')

CSS = r"""
@font-face{font-family:"HG";src:url("assets/fonts/hg-500.woff2") format("woff2");font-weight:500;}
@font-face{font-family:"HG";src:url("assets/fonts/hg-700.woff2") format("woff2");font-weight:700;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000;}
#root{position:relative;width:1080px;height:1920px;background:#000;color:#fff;font-family:"HG",sans-serif;-webkit-font-smoothing:antialiased;font-kerning:normal;}
.scene{position:absolute;inset:0;overflow:hidden;opacity:0;}
.full{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;transform-origin:50% 50%;}
.scrim{position:absolute;left:0;right:0;bottom:0;height:1050px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.55) 45%,rgba(0,0,0,.85));}
.txt{position:absolute;left:64px;right:64px;bottom:260px;}
.txt.hook{bottom:auto;top:640px;}
.h1{font-weight:700;font-size:142px;line-height:.92;letter-spacing:-.05em;color:#fff;text-wrap:balance;}
.hook .h1{font-size:168px;}
.num{display:inline-block;padding:10px 34px 18px;border-radius:10px;background:#fff;}
.num span{white-space:nowrap;font-weight:700;font-size:190px;line-height:1;letter-spacing:-.06em;color:#14281C;font-variant-numeric:tabular-nums;}
.w{display:inline-block;}
.sub{margin-top:34px;font-weight:500;font-size:58px;line-height:1.15;letter-spacing:-.025em;color:#fff;}
.dim{position:absolute;inset:0;background:rgba(10,22,15,.74);}
.endc{position:absolute;left:64px;right:64px;top:600px;}
.tel{display:flex;align-items:center;gap:28px;margin-top:44px;padding:36px 52px;width:max-content;border-radius:10px;background:#fff;}
.tel svg{width:66px;height:66px;fill:#14281C;}
.tel span{font-weight:700;font-size:112px;letter-spacing:-.03em;color:#14281C;font-variant-numeric:tabular-nums;}
.sub.small{font-size:48px;color:rgba(255,255,255,.85);}
#n-f span{font-size:140px;}
"""

JS = r"""
const tl = gsap.timeline({ paused: true });
const T = h => +(P0 + H * h).toFixed(3);
function punch(sel, t, o) { o = o || {};
  tl.fromTo(sel, { opacity: 0, scale: o.sc ?? 1.35, y: o.y ?? 0 },
    { opacity: 1, scale: 1, y: 0, duration: o.d || .45, ease: "power4.out", stagger: o.st ?? .06, transformOrigin: "0% 100%" }, t); }
function count(id, a, b, tpl, t, d) {
  const o = { v: a }, el = document.getElementById(id);
  tl.to(o, { v: b, duration: d, ease: "power3.out", onUpdate: () => { el.textContent = tpl.replace("{}", Math.round(o.v)); } }, t);
  tl.call(() => { el.textContent = tpl.replace("{}", b); }, null, t + d);
}
const W = .2;  // duración del barrido
SC.forEach(([id, s, e], k) => {
  const a = T(s), b = T(e), dir = k % 2 ? -1 : 1;
  tl.set("#" + id, { opacity: 1 }, k ? a : 0);
  if (k > 0) tl.fromTo("#" + id, { x: 700 * dir, filter: "blur(40px)" }, { x: 0, filter: "blur(0px)", duration: W, ease: "power2.out" }, a);
  if (id !== "i") {
    tl.to("#" + id, { x: -700 * dir, filter: "blur(40px)", duration: W, ease: "power2.in" }, b - W);
    tl.set("#" + id, { opacity: 0 }, b);
  }
  tl.fromTo("#v-" + id, { scale: 1.18 }, { scale: 1.0, duration: b - a, ease: "power3.out" }, a);
  if (id === "i") return;
  if (CNT[id]) { punch("#n-" + id, a + .08, { sc: 1.5 }); count("c-" + id, CNT[id][0], CNT[id][1], CNT[id][2], a + .08, .9); }
  else if (id === "a") tl.fromTo("#h-a", { scale: 1.1 }, { scale: 1, duration: .8, ease: "power3.out", transformOrigin: "0% 100%" }, 0);
  else punch("#h-" + id + " .w", a + .06);
  punch("#s-" + id, a + .35, { sc: 1, y: 40, d: .5 });
});
const g = T(14);
tl.fromTo("#dim", { opacity: 0 }, { opacity: 1, duration: .6, ease: "power2.out" }, g + .1);
punch("#h-i .w", g + .2);
punch("#s-i", g + .7, { sc: 1, y: 40, d: .5 });
punch("#tel", g + 1.0, { sc: 1.25 });
punch("#s-i2", g + 1.5, { sc: 1, y: 30, d: .5 });
tl.fromTo("#tel", { scale: 1 }, { scale: 1.05, duration: .27, yoyo: true, repeat: 5, ease: "sine.inOut" }, T(18));
tl.to("#i", { opacity: 0, duration: 1.0, ease: "power1.in" }, T(21) - 1.0);
window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
""".replace("P0", str(P0)).replace("H *", f"{H} *").replace("SC.", json.dumps([[sid, s, e] for sid, s, e, *_ in SHOTS]) + ".").replace(
    "CNT[", "(" + json.dumps({k: [v[2][0], v[2][1], v[2][2]] for k, v in TEXT.items() if v[2]}, ensure_ascii=False) + ")[")

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
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="{TOTAL}" data-fade-out="2" data-track-index="1"></audio>
{chr(10).join(sfx)}
{chr(10).join(secs)}
</div>
<script>{JS}</script>
</body>
</html>
'''
open(os.path.join(proj, "index.html"), "w").write(HTML)
print(proj, TOTAL)
