#!/usr/bin/env python3
"""Arma una versión de un solo archivo del sitio (fuentes y scripts incrustados): dist/steelworks-sitio.html"""
import base64, glob, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
# real photos (fotos/*.jpg) go in as data URIs; the page reads them through window.FOTOS
FOTOS = {os.path.basename(f)[:-4]: "data:image/jpeg;base64," + base64.b64encode(open(f, "rb").read()).decode()
         for f in sorted(glob.glob(os.path.join(HERE, "fotos", "*.jpg")))}
FOTOS.update({"r-" + os.path.basename(f)[:-4]: "data:image/png;base64," + base64.b64encode(open(f, "rb").read()).decode()
              for f in sorted(glob.glob(os.path.join(HERE, "fotos", "recortes", "*.png")))})
def fotos(html):
    html = re.sub(r"\.\./logo/([\w/-]+)\.svg", lambda m: "data:image/svg+xml;base64," + base64.b64encode(open(os.path.join(HERE, "logo", m.group(1) + ".svg"), "rb").read()).decode(), html)
    html = re.sub(r"\.\./fotos/recortes/([\w-]+)\.png", lambda m: FOTOS["r-" + m.group(1)], html)
    html = re.sub(r"\.\./fotos/([\w-]+)\.jpg", lambda m: FOTOS[m.group(1)], html)
    return html.replace("window.FOTOS = window.FOTOS || null;", "window.FOTOS = " + json.dumps(FOTOS) + ";")
src = open(os.path.join(HERE, "sitio", "index.html"), encoding="utf-8").read()
def font(m):
    data = base64.b64encode(open(os.path.join(HERE, "sitio", m.group(1)), "rb").read()).decode()
    return f'url("data:font/woff2;base64,{data}")'
src = re.sub(r'url\("(fonts/[^"]+)"\)', font, src)
for tag, path in [('<script src="hierro.js"></script>', "sitio/hierro.js"), ('<script src="../bot/engine.js"></script>', "bot/engine.js")]:
    src = src.replace(tag, "<script>\n" + open(os.path.join(HERE, path), encoding="utf-8").read() + "\n</script>")
os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
out = os.path.join(HERE, "dist", "steelworks-sitio.html")
open(out, "w", encoding="utf-8").write(fotos(src))
print(out, os.path.getsize(out) // 1024, "KB")

# propuesta (página publicable): capturas incrustadas como data URI + motor del bot
import json, sys
imgs_path = os.path.join(HERE, "propuesta", "imgs.json")
if os.path.exists(imgs_path):
    imgs = json.load(open(imgs_path))
    p = open(os.path.join(HERE, "propuesta", "index.html"), encoding="utf-8").read()
    p = re.sub(r"\{\{IMG:([\w-]+)\}\}", lambda m: imgs[m.group(1)], p)
    p = p.replace("{{HIERRO}}", open(os.path.join(HERE, "sitio", "hierro.js"), encoding="utf-8").read())
    p = p.replace("{{ENGINE}}", open(os.path.join(HERE, "bot", "engine.js"), encoding="utf-8").read())
    out = os.path.join(HERE, "dist", "steelworks-propuesta.html")
    open(out, "w", encoding="utf-8").write(fotos(p))
    print(out, os.path.getsize(out) // 1024, "KB")
