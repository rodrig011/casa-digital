#!/usr/bin/env python3
"""Inline the logo and the two dish photos so the panel is one self-contained file: dist/libbys-cajun-panel.html"""
import base64, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "panel.html"), encoding="utf-8").read()
for name in ("logo.jpg", "foto-mariscada.jpg", "foto-sopa.jpg"):
    f = "logo-160.jpg" if name == "logo.jpg" else name
    b64 = base64.b64encode(open(os.path.join(HERE, f), "rb").read()).decode()
    src = src.replace(f'src="{name}"', f'src="data:image/jpeg;base64,{b64}"')
os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
out = os.path.join(HERE, "dist", "libbys-cajun-panel.html")
open(out, "w", encoding="utf-8").write(src)
print(out)
