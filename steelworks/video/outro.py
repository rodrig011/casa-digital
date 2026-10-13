"""Clientia Tech outro pieces copied from videos-restaurantes/gen2.py (light trails behind the redrawn mark)."""
RIBBONS = [  # long sweeping curves through the center of a 1080x1920 frame, with stroke widths
    ("M -220,1750 C 300,1500 200,720 700,600 S 1300,200 1420,-120", 70),
    ("M -300,1180 C 200,1300 500,1100 560,900 S 900,300 1320,180", 46),
    ("M 1320,1820 C 820,1700 400,1300 520,960 S 300,300 -220,90", 90),
    ("M -220,560 C 300,480 820,900 600,1220 S 700,1900 1120,2120", 38),
    ("M 1420,1080 C 900,1220 720,820 540,960 S 200,1500 -220,1520", 60),
    ("M 180,2140 C 300,1500 920,1320 800,800 S 400,100 620,-220", 52),
]


def ribbons(rid, palette):
    """Apple TV style light trails: blurred bloom + gradient body + hot white core per curve."""
    grads, glow, body, core = [], [], [], []
    n = len(palette)
    for i, (d, w) in enumerate(RIBBONS):
        a, b, c3 = palette[i % n], palette[(i + 1) % n], palette[(i + 2) % n]
        gid = f"{rid}g{i}"
        grads.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="1920" x2="1080" y2="0">'
                     f'<stop offset="0" stop-color="{a}"/><stop offset=".5" stop-color="{b}"/><stop offset="1" stop-color="{c3}"/></linearGradient>')
        common = f'd="{d}" pathLength="1000" fill="none" stroke-linecap="round" class="{rid}-p{i}"'
        glow.append(f'<path {common} stroke="url(#{gid})" stroke-width="{w * 2.6}"/>')
        body.append(f'<path {common} stroke="url(#{gid})" stroke-width="{w}"/>')
        core.append(f'<path {common} stroke="#fff" stroke-opacity=".85" stroke-width="{max(3, w * .12):.0f}"/>')
    return (f'<div class="rib" id="{rid}">'
            f'<svg class="rl glowl" viewBox="0 0 1080 1920"><defs>{"".join(grads)}</defs>{"".join(glow)}</svg>'
            f'<svg class="rl" viewBox="0 0 1080 1920"><defs>{"".join(g.replace(f"id=\"{rid}g", f"id=\"{rid}h") for g in grads)}</defs>'
            f'{"".join(p.replace(f"url(#{rid}g", f"url(#{rid}h") for p in body)}</svg>'
            f'<svg class="rl corel" viewBox="0 0 1080 1920">{"".join(core)}</svg></div>')


