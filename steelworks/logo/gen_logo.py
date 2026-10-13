#!/usr/bin/env python3
"""Steel Works · logo en vectores (voluta forjada sobre barra + «STEEL WORKS / HONDURAS»).

Todo sale como trazos rellenos (sin fuentes ni líneas con grosor), listo para imprimir, cortar en CNC o bordar.
Genera SVG, PDF y PNG en tres versiones (horizontal, vertical, símbolo) y seis colores.
Requisitos: pip install fonttools brotli skia-pathops cairosvg; fuentes de @fontsource (big-shoulders-display, archivo).

    python3 gen_logo.py
"""
import math, os
import pathops, cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
FS = os.environ.get("FONTS", "/tmp/claude-0/deps/node_modules/@fontsource")
DISPLAY = os.path.join(FS, "big-shoulders-display/files/big-shoulders-display-latin-800-normal.woff2")
BODY = os.path.join(FS, "archivo/files/archivo-latin-600-normal.woff2")

COLORES = {  # nombre: (fondo de la vista previa, símbolo, palabra, subtítulo)
    "naranja-sobre-negro": ("#131415", "#E8732C", "#EEEBE6", "#9AA1A7"),
    "naranja-sobre-blanco": ("#FFFFFF", "#E8732C", "#16181A", "#555B61"),
    "negro": ("#FFFFFF", "#16181A", "#16181A", "#16181A"),
    "blanco": ("#131415", "#FFFFFF", "#FFFFFF", "#FFFFFF"),
    "acero": ("#131415", "#9AA1A7", "#9AA1A7", "#9AA1A7"),
    "naranja": ("#FFFFFF", "#E8732C", "#E8732C", "#E8732C"),
}

# --- symbol: forged C-scroll on a bar (same geometry as the website, 48-unit grid) ---
def spiral(cx, cy, r, turns, end, s, n=160):
    return [(cx + r * (0.1 + 0.9 * t) * math.cos(end + s * (1 - t) * turns * 2 * math.pi),
             cy + r * (0.1 + 0.9 * t) * math.sin(end + s * (1 - t) * turns * 2 * math.pi)) for t in [i / n for i in range(n + 1)]]

def simbolo():
    x, y, h, turns = 24, 8, 30, 1.2
    r = h * .27; cx = x + r
    top = spiral(cx, y + r, r, turns, math.pi, 1)
    bot = list(reversed(spiral(cx, y + h - r, r, turns, math.pi, -1)))
    line = pathops.Path()
    pts = top + bot
    line.moveTo(*pts[0])
    for p in pts[1:]:
        line.lineTo(*p)
    bar = pathops.Path(); bar.moveTo(24, 44); bar.lineTo(24, 4)
    out = pathops.Path()
    for p in (line, bar):
        p.stroke(3.2, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        p.convertConicsToQuads()
        out = pathops.op(out, p, pathops.PathOp.UNION)
    return out

def bounds(p):
    return p.bounds  # (xmin, ymin, xmax, ymax)

def to_d(p):
    from fontTools.pens.svgPathPen import SVGPathPen as _P
    pen = _P(None)
    p.draw(pen)
    return pen.getCommands()

# --- text to outlines ---
def texto(font_path, text, size, tracking_em, x0, baseline):
    f = TTFont(font_path)
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    sc = size / upm
    pen = SVGPathPen(gs)
    x = x0
    for ch in text:
        g = cmap[ord(ch)]
        TPen = TransformPen(pen, (sc, 0, 0, -sc, x, baseline))
        gs[g].draw(TPen)
        x += gs[g].width * sc + tracking_em * size
    return pen.getCommands(), x - tracking_em * size - x0

def text_path(font_path, text, size, tracking_em, x0, baseline):
    """Return the text as a pathops Path so we can measure it exactly."""
    from fontTools.pens.pointPen import SegmentToPointPen  # noqa
    d, w = texto(font_path, text, size, tracking_em, x0, baseline)
    return d, w

def svg(view, parts, bg=None):
    vb = " ".join(f"{v:.2f}" for v in view)
    body = "".join(f'<path fill="{c}" d="{d}"/>' for c, d in parts)
    rect = f'<rect x="{view[0]:.2f}" y="{view[1]:.2f}" width="{view[2]:.2f}" height="{view[3]:.2f}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{rect}{body}</svg>'

def build():
    sym = simbolo()
    sx0, sy0, sx1, sy1 = bounds(sym)
    sym_d = to_d(sym)
    # horizontal: symbol 48 tall, wordmark to the right (proportions from the website nav)
    word_d, word_w = texto(DISPLAY, "STEEL WORKS", 34, .05, 0, 0)
    sub_d, sub_w = texto(BODY, "HONDURAS", 11.5, .32, 0, 0)
    out = {}
    # horizontal layout coordinates
    gap = 14
    tx = sx1 + gap
    H = {"word": texto(DISPLAY, "STEEL WORKS", 34, .05, tx, 30)[0], "sub": texto(BODY, "HONDURAS", 11.5, .32, tx + 1, 45)[0]}
    hw = tx + max(word_w, sub_w) - sx0
    pad = 6
    out["horizontal"] = ((sx0 - pad, 2 - pad, hw + 2 * pad, 46 + 2 * pad), [("sym", sym_d), ("word", H["word"]), ("sub", H["sub"])])
    # vertical: symbol scaled up on top, centred text below
    k = 2.0
    sym_v = pathops.Path(); sym.transform  # noqa
    from fontTools.pens.transformPen import TransformPen as TP
    vw = max(word_w, sub_w) + 20
    cx = vw / 2
    scx = (sx0 + sx1) / 2
    pen = SVGPathPen(None)
    sym.draw(TP(pen, (k, 0, 0, k, cx - scx * k, -sy0 * k)))
    symV = pen.getCommands()
    top = (sy1 - sy0) * k + 16
    V = {"word": texto(DISPLAY, "STEEL WORKS", 34, .05, cx - word_w / 2, top + 28)[0],
         "sub": texto(BODY, "HONDURAS", 11.5, .32, cx - sub_w / 2, top + 46)[0]}
    out["vertical"] = ((-pad, -pad, vw + 2 * pad, top + 50 + 2 * pad), [("sym", symV), ("word", V["word"]), ("sub", V["sub"])])
    # symbol only, square
    side = max(sx1 - sx0, sy1 - sy0) + 8
    out["simbolo"] = (((sx0 + sx1) / 2 - side / 2, (sy0 + sy1) / 2 - side / 2, side, side), [("sym", sym_d)])

    files = []
    for nombre, (bg, cs, cw, csub) in COLORES.items():
        col = {"sym": cs, "word": cw, "sub": csub}
        for lay, (view, parts) in out.items():
            base = f"steelworks-logo-{lay}-{nombre}"
            d = os.path.join(HERE, lay)
            os.makedirs(d, exist_ok=True)
            s = svg(view, [(col[k], p) for k, p in parts])
            open(os.path.join(d, base + ".svg"), "w").write(s)
            cairosvg.svg2pdf(bytestring=s.encode(), write_to=os.path.join(d, base + ".pdf"))
            cairosvg.svg2png(bytestring=s.encode(), write_to=os.path.join(d, base + ".png"), output_width=2000 if lay != "simbolo" else 1024)
            files.append((lay, nombre, bg, s, view))
    # preview sheet
    cells = []
    for i, (lay, nombre, bg, s, view) in enumerate(files):
        cells.append((lay, nombre, bg, s))
    rows = []
    for lay in out:
        row = [c for c in cells if c[0] == lay]
        rows.append(row)
    W, cw, ch = 6 * 420, 420, 260
    sheet = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {len(rows) * ch}" width="{W}" height="{len(rows) * ch}">']
    for r, row in enumerate(rows):
        for c, (lay, nombre, bg, s) in enumerate(row):
            x, y = c * cw, r * ch
            inner = s.replace('<svg xmlns="http://www.w3.org/2000/svg"', f'<svg x="{x + 40}" y="{y + 40}" width="{cw - 80}" height="{ch - 80}"')
            sheet.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{bg}"/>{inner}')
    sheet.append("</svg>")
    cairosvg.svg2png(bytestring="".join(sheet).encode(), write_to=os.path.join(HERE, "vista-previa.png"))
    print(len(files), "versiones")

if __name__ == "__main__":
    build()
