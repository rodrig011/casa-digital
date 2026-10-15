#!/usr/bin/env python3
"""Coco Chicken proposal video v6, vertical 1080x1920, built on the methods in
/mnt/project-files/propuestas/metodos-video.md (from rodrigo's "sell me this pen" reference, 2026-10-15):
hook with a real comment on their TikTok -> we won't pitch features -> we ask questions about their
business (each with real proof) -> "if any answer was 'I don't know', that's what we solve" -> the
solution as answers, in the same order -> bottom line -> clear call to action -> by Clientia Tech.
Big 2-4 word captions carry the story; a picture-in-picture card above illustrates each line."""
import json, os, re, shutil
from gen2 import MARK, DEPS, HERE
from gen6 import P0, BAR

SRC = os.path.join(HERE, "coco-src")
OUT = os.path.join(HERE, "videos11")
BEAT = BAR / 4
GOLD = "#F2B544"

# (caption, beats, pip). *word* = gold. pip None -> caption sits mid-screen.
LINES = [
    ("¿Qué significa", 3, "hook"), ("este *comentario?*", 3, "hook"),
    ("Que alguien *quería comprar*", 3, "hook"), ("y nadie *le contestó.*", 4, "hook"),
    ("Lo que *no* vamos a hacer", 3, None), ("es decirle que tenemos", 3, None), ("«el mejor sistema", 3, None), ("del mundo».", 3, None),
    ("Primero,", 2, None), ("le hacemos", 2, None), ("*preguntas.*", 3, None),
    ("¿Cuántos clientes", 3, "q1"), ("le escriben", 2, "q1"), ("*cada día?*", 3, "q1"),
    ("¿Cuántos", 2, "q2"), ("se quedan", 2, "q2"), ("*sin respuesta?*", 4, "q2"),
    ("¿Quién le avisa", 2, "q3"), ("al proveedor", 2, "q3"), ("cuando se acaba", 2, "q3"), ("*el plátano?*", 3, "q3"),
    ("¿Sabe cuánto", 2, "q4"), ("vendió hoy", 2, "q4"), ("*cada sucursal?*", 4, "q4"),
    ("Si alguna respuesta", 3, None), ("fue *«no sé»*,", 3, None), ("eso es lo que", 2, None), ("*resolvemos.*", 3, None),
    ("Su WhatsApp", 2, "s1"), ("*contesta solo*,", 3, "s1"), ("a cualquier hora.", 3, "s1"),
    ("*Cero clientes*", 2, "s2"), ("*sin respuesta.*", 4, "s2"),
    ("El panel", 2, "s3"), ("*le avisa*", 2, "s3"), ("al proveedor.", 3, "s3"),
    ("Y usted ve", 2, "s4"), ("sus 3 sucursales", 2, "s4"), ("*en un solo lugar.*", 4, "s4"),
    ("No le vendemos", 2, None), ("un sistema.", 3, None), ("Resolvemos lo que", 3, None), ("*Coco Chicken* necesita.", 4, None),
    ("Escríbanos", 2, "cta"), ("y le mostramos", 2, "cta"), ("*exactamente cómo.*", 6, "cta"),
]
START_BEAT = 3          # first caption after the video card lands
OUTRO_BEATS = 10


def cap_html(t):
    return re.sub(r"\*(.+?)\*", r'<em>\1</em>', t)


def timeline():
    t, rows = START_BEAT, []
    for i, (txt, b, pip) in enumerate(LINES):
        rows.append({"i": i, "txt": txt, "s": round(P0 + t * BEAT, 3), "e": round(P0 + (t + b) * BEAT, 3), "pip": pip})
        t += b
    end = round(P0 + (t + OUTRO_BEATS) * BEAT, 3)
    pips = {}
    for r in rows:
        if r["pip"]:
            p = pips.setdefault(r["pip"], {"s": r["s"], "e": r["e"], "lines": []})
            p["e"] = r["e"]; p["lines"].append(r)
    return rows, pips, round(P0 + t * BEAT, 3), end


CSS = r'''
@font-face{font-family:"IT";src:url("assets/fonts/it-400.woff2") format("woff2");font-weight:400;}
@font-face{font-family:"IT";src:url("assets/fonts/it-500.woff2") format("woff2");font-weight:500;}
@font-face{font-family:"IT";src:url("assets/fonts/it-600.woff2") format("woff2");font-weight:600;}
@font-face{font-family:"IT";src:url("assets/fonts/it-700.woff2") format("woff2");font-weight:700;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1920px;overflow:hidden;background:#070708;}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:#070708;font-family:"IT",sans-serif;color:#F5F5F7;-webkit-font-smoothing:antialiased;}
.bg{position:absolute;inset:-80px;background:url(assets/f30.png) center/cover;filter:blur(46px) brightness(.32) saturate(1.2);}
.shade{position:absolute;inset:0;background:radial-gradient(120% 70% at 50% 30%,rgba(7,7,8,0) 0%,rgba(7,7,8,.55) 60%,rgba(7,7,8,.92) 100%);}
.glow{position:absolute;border-radius:50%;pointer-events:none;}
/* captions */
.cap{position:absolute;left:60px;right:60px;text-align:center;font-weight:700;font-size:92px;line-height:1.08;letter-spacing:-.03em;color:#fff;
  text-shadow:0 4px 18px rgba(0,0,0,.65),0 1px 3px rgba(0,0,0,.8);opacity:0;}
.cap.mid{top:50%;font-size:108px;}
.cap.low{top:1330px;}
.cap em{font-style:normal;background:linear-gradient(100deg,#FFE7B3 0%,#F2B544 55%,#D98E1C 100%);-webkit-background-clip:text;background-clip:text;color:transparent;
  text-shadow:none;filter:drop-shadow(0 4px 14px rgba(0,0,0,.6));}
.tagline{position:absolute;left:0;right:0;bottom:70px;text-align:center;font-size:24px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:#6E6E73;}
.note{position:absolute;left:80px;right:80px;top:1245px;text-align:center;font-size:24px;font-weight:500;color:#8E8E93;opacity:0;}
/* pip cards */
.pip{position:absolute;left:90px;right:90px;top:170px;height:1030px;display:flex;align-items:center;justify-content:center;opacity:0;}
.card{width:100%;background:linear-gradient(180deg,#18181A,#0F0F10);border-radius:44px;box-shadow:0 0 0 1px rgba(255,255,255,.09),0 50px 120px rgba(0,0,0,.7);padding:46px 50px;}
.k{font-size:24px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:#8E8E93;}
/* hook */
.vcard{position:relative;width:560px;height:996px;border-radius:40px;overflow:hidden;box-shadow:0 0 0 1px rgba(255,255,255,.12),0 60px 140px rgba(0,0,0,.75);}
.vcard video{width:100%;height:100%;object-fit:cover;display:block;}
.cmt{position:absolute;left:-30px;right:-30px;top:120px;background:#fff;border-radius:26px;padding:22px 26px;display:flex;gap:18px;align-items:center;box-shadow:0 20px 50px rgba(0,0,0,.45);color:#161616;}
.cmt .av{flex:none;width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#D8261C,#F2B544);}
.cmt b{display:block;font-size:22px;font-weight:600;color:#8A8A8E;}
.cmt p{font-size:31px;font-weight:600;line-height:1.25;letter-spacing:-.01em;margin-top:2px;}
/* q1 comments */
.cm{background:#1C1C1E;border-radius:28px;padding:26px 30px;margin-top:20px;}
.cm:first-child{margin-top:0;}
.cm .h{font-size:20px;font-weight:600;color:#8E8E93;letter-spacing:.06em;}
.cm p{font-size:38px;font-weight:600;letter-spacing:-.02em;margin-top:8px;}
.cm .l{font-size:22px;color:#FF6B5E;font-weight:600;margin-top:8px;}
/* q2 tally */
.tr{display:flex;align-items:center;gap:30px;padding:26px 0;border-top:1px solid rgba(255,255,255,.08);}
.tr:first-of-type{border-top:0;}
.tr b{flex:none;width:150px;font-size:96px;font-weight:700;letter-spacing:-.05em;line-height:1;background:linear-gradient(100deg,#FFE7B3,#F2B544 55%,#D98E1C);-webkit-background-clip:text;background-clip:text;color:transparent;}
.tr>span{font-size:34px;font-weight:500;line-height:1.25;color:#E5E5EA;}
.tr>span em{display:block;font-style:normal;font-size:28px;color:#8E8E93;margin-top:4px;}
/* q3 stock */
.row{display:flex;justify-content:space-between;align-items:baseline;margin-top:22px;}
.row b{font-size:56px;font-weight:700;letter-spacing:-.03em;}
.row span{font-size:56px;font-weight:700;color:#FF6B5E;}
.row span small{font-size:28px;color:#8E8E93;font-weight:500;}
.bar{height:14px;border-radius:7px;background:rgba(255,255,255,.08);margin-top:24px;overflow:hidden;}
.bar i{display:block;height:100%;width:63%;background:#FF6B5E;border-radius:7px;transform-origin:left;}
.min{font-size:28px;color:#8E8E93;margin-top:16px;}
.who{margin-top:40px;padding-top:34px;border-top:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:20px;font-size:34px;font-weight:600;}
.who i{flex:none;width:58px;height:58px;border-radius:50%;background:#2A2A2D;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:30px;color:#8E8E93;}
/* q4 branches */
.br{display:flex;justify-content:space-between;align-items:center;padding:30px 0;border-top:1px solid rgba(255,255,255,.08);font-size:42px;font-weight:600;letter-spacing:-.02em;}
.br:first-of-type{border-top:0;}
.br .dot{display:inline-block;width:18px;height:18px;border-radius:50%;margin-right:20px;}
.br span.q{font-size:64px;font-weight:700;color:#5A5A5F;}
/* s1 chat */
.chat{background:#0B141A;border-radius:44px;overflow:hidden;box-shadow:0 0 0 1px rgba(255,255,255,.09),0 50px 120px rgba(0,0,0,.7);width:100%;padding-bottom:30px;}
.chat .hd{display:flex;align-items:center;gap:18px;padding:26px 32px;background:#1F2C34;}
.chat .hd img{width:64px;height:64px;border-radius:50%;object-fit:cover;object-position:50% 30%;background:#fff;}
.chat .hd .pv{width:64px;height:64px;border-radius:50%;background:#2A3942;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:34px;}
.chat .hd b{display:block;font-size:30px;font-weight:600;}
.chat .hd span{display:block;font-size:22px;color:#8696A0;}
.wb{margin:22px 30px 0;padding:18px 24px 14px;border-radius:24px;font-size:32px;line-height:1.35;max-width:740px;width:fit-content;}
.wb.out{margin-left:auto;background:#005C4B;border-top-right-radius:6px;}
.wb.in{background:#1F2C34;border-top-left-radius:6px;}
.wb small{display:block;text-align:right;font-size:19px;color:rgba(255,255,255,.6);margin-top:6px;}
.wb small em{font-style:normal;color:#53BDEB;}
.wb .tag{display:block;font-size:19px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#25D366;margin-bottom:6px;}
/* s2 zero */
.zero{text-align:center;padding:60px 50px 64px;}
.zero .big{font-size:400px;font-weight:700;letter-spacing:-.06em;line-height:.9;margin-top:20px;background:linear-gradient(100deg,#FFE7B3,#F2B544 55%,#D98E1C);-webkit-background-clip:text;background-clip:text;color:transparent;font-variant-numeric:tabular-nums;}
.zero .ok{display:inline-flex;gap:12px;align-items:center;margin-top:34px;padding:14px 28px;border-radius:40px;background:rgba(37,211,102,.12);box-shadow:0 0 0 1px rgba(37,211,102,.35);color:#25D366;font-size:30px;font-weight:600;}
/* s4 panel shot */
.shot{width:100%;border-radius:26px;overflow:hidden;box-shadow:0 0 0 1px rgba(255,255,255,.12),0 50px 120px rgba(0,0,0,.7);background:#fff;}
.shot img{display:block;width:100%;}
/* cta */
.cta{text-align:center;padding:64px 50px 60px;}
.cta .ic{width:150px;height:150px;border-radius:42px;background:#F5F5F7;color:#0B0B0C;display:flex;align-items:center;justify-content:center;margin:0 auto;}
.cta .ic svg{width:90px;height:90px;}
.cta .t{margin-top:34px;font-size:64px;font-weight:700;letter-spacing:-.03em;}
.cta .s{margin-top:10px;font-size:32px;color:#8E8E93;}
.cta .num{margin-top:44px;font-size:56px;font-weight:700;letter-spacing:-.02em;}
.cta .btn{position:relative;margin:30px auto 0;width:520px;height:104px;border-radius:60px;background:#25D366;color:#fff;font-size:40px;font-weight:700;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.cta .btn span{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;}
.cta .btn .b2{background:#1F2C34;color:#25D366;opacity:0;}
.cta .who2{margin-top:30px;font-size:26px;color:#6E6E73;}
/* outro */
.outro{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;background:#050507;}
.outro svg{width:300px;height:auto;}
.outro .by{margin-top:40px;font-size:44px;font-weight:500;color:#8E8E93;letter-spacing:-.01em;}
.outro .by b{color:#F5F5F7;font-weight:600;}
.oglow{position:absolute;left:190px;top:560px;width:700px;height:700px;border-radius:50%;background:radial-gradient(closest-side,rgba(110,140,255,.28),rgba(5,5,7,0));}
'''

HOUSE = ('<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">'
         '<path d="M9 29 L32 10 L55 29 V54 H9 Z"/><path d="M26 54 V40 H38 V54"/></svg>')


def build():
    rows, pips, cap_end, total = timeline()
    proj = os.path.join(OUT, "coco-chicken")
    if os.path.exists(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "assets", "fonts"))
    A = lambda *p: os.path.join(proj, "assets", *p)
    shutil.copy(os.path.join(HERE, "musica2.mp3"), A("musica.mp3"))
    shutil.copy(os.path.join(DEPS, "gsap", "dist", "gsap.min.js"), A("gsap.min.js"))
    for w in (400, 500, 600, 700):
        shutil.copy(os.path.join(DEPS, "@fontsource", "inter-tight", "files", f"inter-tight-latin-{w}-normal.woff2"), A("fonts", f"it-{w}.woff2"))
    for n in ("tiktok.mp4", "logo.png", "f30.png"):
        shutil.copy(os.path.join(SRC, n), A(n))
    shutil.copy(os.path.join(SRC, "panel", "pv-hoy-v.png"), A("pv-hoy.png"))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    json.dump({"id": "coco-chicken-v6", "name": "Casa Digital x Coco Chicken (vertical)"}, open(os.path.join(proj, "meta.json"), "w"))

    h = pips["hook"]
    vid = (f'<video id="tkvid" class="clip" src="assets/tiktok.mp4" data-start="0" data-duration="{round(h["e"] + 1, 3)}" '
           f'data-media-start="0" data-track-index="2" muted playsinline></video>')
    P = {
        "hook": f'<div class="vcard" id="vcard">{vid}<div class="cmt" id="cmt"><div class="av"></div><div><b>Comentario real en @cocochiken1</b>'
                f'<p>Yo quierooooooo pero nunca me responden 😞😞</p></div></div></div>',
        "q1": '<div style="width:100%">' + "".join(
            f'<div class="cm" id="c{i}"><div class="h">COMENTARIO EN SU TIKTOK</div><p>{t}</p>' + (f'<div class="l">♥ {l} me gusta</div>' if l else "") + '</div>'
            for i, (t, l) in enumerate([("Incluye refresco ese combo ?", "3,071"), ("Y al fin bro dnd Estan ubicados", "50"),
                                        ("Hacen envíos??", None), ("amigo de dónde son", None)])) + '</div>',
        "q2": '<div class="card"><div class="k">De 506 comentarios en su TikTok</div>' + "".join(
            f'<div class="tr" id="t{i}"><b><span class="cnt" data-n="{n}">0</span></b><span>{a}<em>{b}</em></span></div>'
            for i, (n, a, b) in enumerate([(87, "piden sucursal en su ciudad", "“cuando para Tegucigalpa”"),
                                           (56, "preguntan precio o combo", "“precio?”"),
                                           (25, "preguntan dónde están", "“Donde están ubicados”")])) + '</div>',
        "q3": '<div class="card"><div class="k">Inventario · Colonia Satélite</div><div class="row"><b>Plátano verde</b><span>95 <small>unid.</small></span></div>'
              '<div class="bar"><i id="plb"></i></div><div class="min">Mínimo: 150 unid.</div>'
              '<div class="who"><i>?</i>¿Quién le escribe al proveedor?</div></div>',
        "q4": '<div class="card"><div class="k">Ventas de hoy</div>' + "".join(
            f'<div class="br" id="b{i}"><span><i class="dot" style="background:{c}"></i>{n}</span><span class="q">L ?</span></div>'
            for i, (n, c) in enumerate([("Barrio Cabañas", "#2E844A"), ("Colonia Satélite", "#0176D3"), ("Barrio Medina", "#FE9339")])) + '</div>',
        "s1": '<div class="chat"><div class="hd"><img src="assets/logo.png"><div><b>Coco Chicken</b><span>en línea</span></div></div>'
              '<div class="wb out" id="w1">Buenas, ¿dónde están ubicados?<small>11:48 p. m.</small></div>'
              '<div class="wb in" id="w2">¡Hola! Tenemos 3 sucursales: Barrio Cabañas, Colonia Satélite y Barrio Medina. Abrimos de lunes a domingo, de 9 am a 10 pm.<small>11:48 p. m.</small></div>'
              '<div class="wb in" id="w3">¿Le dejo algo listo para recoger mañana?<small>11:48 p. m.</small></div></div>',
        "s2": '<div class="card zero"><div class="k">Sin contestar hoy</div><div class="big"><span id="nz">3</span></div><div class="ok" id="zok">✓ Todos contestados</div></div>',
        "s3": '<div class="chat"><div class="hd"><i class="pv">🥬</i><div><b>Verdulería</b><span>proveedor</span></div></div>'
              '<div class="wb out" id="v1"><span class="tag">Aviso automático</span>Buenas, le escribe Coco Chicken. Se nos acaba el plátano verde en Satélite: necesitamos 205 unid. ¿A qué hora nos lo trae?<small>4:52 pm <em>✓✓</em></small></div>'
              '<div class="wb in" id="v2">Claro, se lo llevo a las 6.<small>4:58 pm</small></div></div>',
        "s4": '<div class="shot" id="shot"><img src="assets/pv-hoy.png"></div>',
        "cta": f'<div class="card cta"><div class="ic">{HOUSE}</div><div class="t">Casa Digital</div><div class="s">Hecho por hondureños, para negocios hondureños.</div>'
               '<div class="num">+1 (765) 543-4251</div><div class="btn" id="cbtn"><span class="b1">Escribir por WhatsApp</span><span class="b2" id="cb2">Enviado ✓</span></div>'
               '<div class="who2">Rodrigo Herrera · Clientia Tech</div></div>',
    }
    NOTES = {"q1": "Comentarios reales de su TikTok", "q2": "Conteo de comentarios reales, octubre 2026", "q3": "Ejemplo",
             "s1": "Conversación de ejemplo · sucursales y horario reales", "s2": "Ejemplo", "s3": "Ejemplo", "s4": "Panel de Coco Chicken · datos de ejemplo"}
    pip_html = "".join(f'<div class="pip" id="p-{k}">{P[k]}</div>' for k in pips)
    note_html = "".join(f'<div class="note" id="n-{k}">{v}</div>' for k, v in NOTES.items())
    cap_html_all = "".join(f'<div class="cap {"low" if r["pip"] else "mid"}" id="cap{r["i"]}">{cap_html(r["txt"])}</div>' for r in rows)
    mark_paths = "".join(f'<path d="{d}"/>' for d in MARK["paths"])
    body = f'''
<div class="bg"></div><div class="shade"></div>
<div class="glow" style="left:-300px;top:-400px;width:1300px;height:1300px;background:radial-gradient(closest-side,rgba(216,38,28,.22),rgba(7,7,8,0))"></div>
<div class="glow" style="left:200px;top:1100px;width:1100px;height:1100px;background:radial-gradient(closest-side,rgba(242,181,68,.12),rgba(7,7,8,0))"></div>
{pip_html}{note_html}{cap_html_all}
<div class="tagline" id="tagl">Casa Digital × Coco Chicken</div>
<div class="outro" id="outro"><div class="oglow"></div>
  <svg viewBox="{MARK["viewBox"]}"><defs><linearGradient id="mf" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#C9D6FF"/><stop offset=".55" stop-color="#fff"/></linearGradient></defs>
  <g id="mstroke" fill="none" stroke="#fff" stroke-width="1.6" stroke-linejoin="round">{mark_paths}</g><g id="mfill" fill="url(#mf)" opacity="0">{mark_paths}</g></svg>
  <div class="by" id="oby">by <b>Clientia Tech</b></div></div>'''

    js = JS.replace("$rows", json.dumps(rows)).replace("$pips", json.dumps({k: [v["s"], v["e"]] for k, v in pips.items()})) \
        .replace("$capend", str(cap_end)).replace("$total", str(total)).replace("$beat", str(BEAT))
    html = f'''<!doctype html>
<html lang="es" data-resolution="portrait">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" /><title>Casa Digital x Coco Chicken</title>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
<audio id="music" data-timeline-role="music" src="assets/musica.mp3" data-start="0" data-duration="{total}" data-fade-out="3" data-track-index="1"></audio>
{body}
</div>
<script>{js}</script>
</body></html>'''
    open(os.path.join(proj, "index.html"), "w").write(html)
    return proj, total


JS = r'''
const tl = gsap.timeline({ paused: true });
const ROWS = $rows, PIPS = $pips, BEAT = $beat, CAPEND = $capend, TOTAL = $total;
const SOFT = "expo.out";
const at = (id, k) => ROWS.find(r => r.pip === id).s + k * BEAT; // k beats after a pip opens
function rise(sel, t, o) { o = o || {};
  tl.fromTo(sel, { opacity: 0, y: o.y || 30, filter: "blur(" + (o.blur || 10) + "px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: o.d || 1, ease: SOFT, stagger: o.st || 0 }, t); }

// captions: each chunk eases in and hands over to the next one
ROWS.forEach((r, i) => {
  const el = "#cap" + r.i, mid = !r.pip;
  tl.fromTo(el, { opacity: 0, yPercent: mid ? -44 : 0, y: mid ? 0 : 22, scale: .96, filter: "blur(8px)" },
                { opacity: 1, yPercent: mid ? -50 : 0, y: 0, scale: 1, filter: "blur(0px)", duration: .32, ease: "power3.out" }, r.s);
  tl.to(el, { opacity: 0, filter: "blur(6px)", duration: .22, ease: "power2.in" }, r.e - .2);
});

// picture-in-picture cards, one per group of lines
Object.entries(PIPS).forEach(([k, [s, e]]) => {
  const el = "#p-" + k;
  if (k === "hook") tl.fromTo(el, { opacity: 0, scale: .9, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 1.4, ease: SOFT }, 0.1);
  else tl.fromTo(el, { opacity: 0, y: 50, scale: .95, filter: "blur(14px)" }, { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: .9, ease: SOFT }, s - .15);
  tl.to(el, { opacity: 0, y: -30, scale: .97, filter: "blur(10px)", duration: .55, ease: "power2.in" }, e - .45);
  const n = document.getElementById("n-" + k);
  if (n) { tl.fromTo(n, { opacity: 0 }, { opacity: 1, duration: .6 }, s + .4); tl.to(n, { opacity: 0, duration: .4 }, e - .45); }
});

// hook: the real comment drops onto their video
tl.fromTo("#cmt", { opacity: 0, y: -40, scale: .9 }, { opacity: 1, y: 0, scale: 1, duration: .8, ease: "back.out(1.6)" }, 0.9);
// q1: comments stack in
[0, 1, 2, 3].forEach(i => rise("#c" + i, at("q1", .3 + i * 1.6), { y: 40, d: .9 }));
// q2: real counts
[0, 1, 2].forEach(i => rise("#t" + i, at("q2", .3 + i * 1.5), { y: 30, d: .9 }));
document.querySelectorAll("#p-q2 .cnt").forEach((el, i) => { const o = { v: 0 }, n = +el.dataset.n;
  tl.fromTo(o, { v: 0 }, { v: n, duration: 1.1, ease: "power2.out", onUpdate: () => { el.textContent = Math.round(o.v); } }, at("q2", .4 + i * 1.5)); });
// q3: stock bar drains below the minimum
tl.fromTo("#plb", { scaleX: 1.58 }, { scaleX: 1, duration: 1.6, ease: "power2.inOut" }, at("q3", .5));
// q4: branches
[0, 1, 2].forEach(i => rise("#b" + i, at("q4", .3 + i * 1.2), { y: 24, d: .8 }));
// s1: the bot answers
rise("#w1", at("s1", .4), { y: 20, d: .8 }); rise("#w2", at("s1", 2.2), { y: 20, d: .8 }); rise("#w3", at("s1", 4.6), { y: 20, d: .8 });
// s2: one tween drives the counter, so any seek lands on the right number
const zo = { p: 0 }, zn = document.getElementById("nz");
tl.fromTo(zo, { p: 0 }, { p: 1, duration: 3 * BEAT, ease: "none", onUpdate: () => { zn.textContent = String(Math.max(0, 3 - Math.floor(zo.p * 3 + 1e-6))); } }, at("s2", .6));
rise("#zok", at("s2", 4), { y: 20, d: .8 });
// s3: notice to the supplier and the answer
rise("#v1", at("s3", .4), { y: 20, d: .8 }); rise("#v2", at("s3", 4), { y: 20, d: .8 });
// s4: slow push on the real panel
tl.fromTo("#shot img", { scale: 1 }, { scale: 1.06, duration: PIPS.s4[1] - PIPS.s4[0], ease: "none", transformOrigin: "20% 20%" }, PIPS.s4[0]);
// cta: tap -> sent
tl.fromTo("#cbtn", { scale: 1 }, { scale: .94, duration: .15, yoyo: true, repeat: 1, ease: "power2.inOut" }, at("cta", 6));
tl.fromTo("#cb2", { opacity: 0 }, { opacity: 1, duration: .3 }, at("cta", 6.3));

// outro
tl.to("#tagl", { opacity: 0, duration: .5 }, CAPEND - .5);
tl.fromTo("#outro", { opacity: 0 }, { opacity: 1, duration: .8, ease: "power2.out" }, CAPEND - .2);
const strokes = document.querySelectorAll("#mstroke path");
strokes.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
tl.to("#mstroke path", { strokeDashoffset: 0, duration: 2, ease: "power2.inOut" }, CAPEND + .2);
tl.to("#mfill", { opacity: 1, duration: .7 }, CAPEND + 1.9);
tl.to("#mstroke", { opacity: 0, duration: .6 }, CAPEND + 2.1);
rise("#oby", CAPEND + 2.2, { d: 1.4 });
tl.to("#outro svg, #oby", { opacity: 0, duration: 1.4, ease: "power2.in" }, TOTAL - 1.6);

window.__timelines = window.__timelines || {};
window.__timelines["main"] = tl;
tl.seek(0);
'''

if __name__ == "__main__":
    print(build())
