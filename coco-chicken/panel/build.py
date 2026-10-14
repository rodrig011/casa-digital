#!/usr/bin/env python3
"""Inline the logo so the panel is one self-contained file: dist/coco-chicken-panel.html"""
import base64, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "panel.html"), encoding="utf-8").read()
logo = base64.b64encode(open(os.path.join(HERE, "logo-160.png"), "rb").read()).decode()
os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
out = os.path.join(HERE, "dist", "coco-chicken-panel.html")
open(out, "w", encoding="utf-8").write(src.replace('src="logo.png"', f'src="data:image/png;base64,{logo}"'))
print(out)
