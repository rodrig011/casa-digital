#!/usr/bin/env python3
"""Arma versiones de un solo archivo (fuentes, fotos y scripts incrustados):
dist/steelworks-sitio.html y dist/steelworks-propuesta.html"""
import base64, glob, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
rd = lambda *p: open(os.path.join(HERE, *p), encoding="utf-8").read()
def uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()

FOTOS = {os.path.basename(f)[:-4]: uri(f, "image/jpeg") for f in sorted(glob.glob(os.path.join(HERE, "fotos", "*.jpg")))}
FONTS = lambda s: re.sub(r'url\("(fonts/[^"]+)"\)', lambda m: f'url("{uri(os.path.join(HERE, "sitio", m.group(1)), "font/woff2")}")', s)
SCRIPTS = {"../bot/engine.js": rd("bot", "engine.js"), "chat.js": rd("sitio", "chat.js"), "../sitio/chat.js": rd("sitio", "chat.js")}
CSS = rd("sitio", "chat.css")

def inline(src):
    src = FONTS(src)
    src = re.sub(r"\.\./fotos/([\w-]+)\.jpg", lambda m: FOTOS[m.group(1)], src)
    for name, code in SCRIPTS.items():
        src = src.replace(f'<script src="{name}"></script>', "<script>\n" + code + "\n</script>")
    # the chat builds image URLs at runtime: hand it the photos it can show
    for name in ("chat.css", "../sitio/chat.css"):
        src = src.replace(f'<link rel="stylesheet" href="{name}">', "<style>\n" + CSS + "\n</style>")
    return src.replace("window.FOTOS = window.FOTOS || null;", "window.FOTOS = " + json.dumps(FOTOS) + ";")

os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
for src, out in [(("sitio", "index.html"), "steelworks-sitio.html"), (("propuesta", "index.html"), "steelworks-propuesta.html")]:
    html = rd(*src)
    if src[0] == "propuesta":
        caps = json.load(open(os.path.join(HERE, "propuesta", "imgs.json")))
        html = re.sub(r"\{\{IMG:([\w-]+)\}\}", lambda m: caps[m.group(1)], html)
    path = os.path.join(HERE, "dist", out)
    open(path, "w", encoding="utf-8").write(inline(html))
    print(path, os.path.getsize(path) // 1024, "KB")
