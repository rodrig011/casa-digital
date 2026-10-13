/* Dibujos de hierro forjado generados por código (portones, volutas, piezas del catálogo).
 * Todo es trazo (stroke="currentColor"), así el color lo decide el CSS: acero frío o hierro al rojo.
 * En la versión final se reemplazan las miniaturas por las fotos reales de Steel Works. */
(function (root) {
  const TAU = Math.PI * 2;
  const f = n => Math.round(n * 10) / 10;
  const poly = pts => "M" + pts.map(p => f(p[0]) + " " + f(p[1])).join(" L");

  // archimedean spiral from the eye outward, ending at endAngle with radius r
  function spiral(cx, cy, r, turns, endAngle, s) {
    const pts = [];
    for (let i = 0; i <= 64; i++) {
      const t = i / 64, a = endAngle + s * (1 - t) * turns * TAU, rr = r * (0.1 + 0.9 * t);
      pts.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]);
    }
    return pts;
  }
  // C-scroll of height h whose spine sits at x; side=1 opens to the right, -1 to the left
  function cscroll(x, y, h, side, turns) {
    turns = turns || 1.15;
    const r = h * 0.27, cx = x + side * r;
    const top = spiral(cx, y + r, r, turns, side > 0 ? Math.PI : 0, side > 0 ? 1 : -1);
    const bot = spiral(cx, y + h - r, r, turns, side > 0 ? Math.PI : 0, side > 0 ? -1 : 1).reverse();
    return poly(top.concat(bot));
  }
  // S-scroll: top eye curls one way, bottom eye the other
  function sscroll(x, y, h, side, rr) {
    const r = rr || h * 0.25;
    const top = spiral(x + side * r, y + r, r, 1.1, side > 0 ? Math.PI : 0, side > 0 ? 1 : -1);
    const bot = spiral(x - side * r, y + h - r, r, 1.1, side > 0 ? 0 : Math.PI, side > 0 ? 1 : -1).reverse();
    return poly(top.concat(bot));
  }
  const P = (d, w, extra) => `<path d="${d}" stroke-width="${w}" ${extra || ""}/>`;
  const svg = (vb, inner, cls) => `<svg viewBox="${vb}" class="${cls || ""}" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${inner}</svg>`;

  function spear(x, y, s) { // lance tip pointing up, base at y
    return `M${f(x)} ${f(y)} L${f(x)} ${f(y - s * .55)} M${f(x - s * .22)} ${f(y - s * .45)} Q${f(x)} ${f(y - s * 1.25)} ${f(x + s * .22)} ${f(y - s * .45)} Q${f(x)} ${f(y - s * .62)} ${f(x - s * .22)} ${f(y - s * .45)}`;
  }

  /* gate(W, H, style): portón visto de frente. style: "forjado" | "liso" | "cnc" */
  function gate(W, H, style, opts) {
    opts = opts || {};
    const sw = Math.max(W, H) / 150, m = sw * 2;
    const out = [];
    const x0 = m, x1 = W - m, yb = H - m;
    const leaves = W / H > 1.25 ? 2 : 1;
    const archH = style === "forjado" ? H * .14 : 0;
    const yt = m + archH + (style === "forjado" ? H * .06 : 0);
    // frame
    out.push(P(`M${x0} ${yb} L${x0} ${yt} M${x1} ${yb} L${x1} ${yt} M${x0} ${yb} L${x1} ${yb}`, sw * 1.6));
    if (leaves === 2) out.push(P(`M${W / 2} ${yb} L${W / 2} ${yt - archH * .9}`, sw * 1.3));
    if (style === "liso") {
      out.push(P(`M${x0} ${yt} L${x1} ${yt}`, sw * 1.6));
      const n = Math.max(6, Math.round((yb - yt) / (sw * 7)));
      for (let i = 1; i < n; i++) { const y = yt + (yb - yt) * i / n; out.push(P(`M${x0} ${f(y)} L${x1} ${f(y)}`, sw * 2.2, 'class="slat"')); }
      out.push(P(`M${x0 + sw * 6} ${f(yt + (yb - yt) * .5)} L${x0 + sw * 6} ${f(yt + (yb - yt) * .62)}`, sw * 1.2));
    } else if (style === "cnc") {
      out.push(P(`M${x0} ${yt} L${x1} ${yt}`, sw * 1.6));
      const cols = Math.max(3, Math.round((x1 - x0) / ((yb - yt) / 4))), cw = (x1 - x0) / cols;
      const rows = Math.max(3, Math.round((yb - yt) / cw)), rh = (yb - yt) / rows;
      for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
        // calado: a ring per cell that touches its neighbours, with an eight-petal rosette cut inside
        const cx = x0 + cw * (i + .5), cy = yt + rh * (j + .5), R = Math.min(cw, rh) * .5, r = R * .78;
        out.push(`<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(R * .97)}" stroke-width="${f(sw * .8)}" class="ring"/>`);
        for (let k = 0; k < 8; k++) {
          const a = k * Math.PI / 4, tip = [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
          const c1 = [cx + Math.cos(a - .42) * r * .62, cy + Math.sin(a - .42) * r * .62], c2 = [cx + Math.cos(a + .42) * r * .62, cy + Math.sin(a + .42) * r * .62];
          out.push(P(`M${f(cx + Math.cos(a) * r * .2)} ${f(cy + Math.sin(a) * r * .2)} Q${f(c1[0])} ${f(c1[1])} ${f(tip[0])} ${f(tip[1])} Q${f(c2[0])} ${f(c2[1])} ${f(cx + Math.cos(a) * r * .2)} ${f(cy + Math.sin(a) * r * .2)}`, sw * .6, 'class="petal"'));
        }
        out.push(`<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(r * .16)}" stroke-width="${f(sw * .7)}"/>`);
      }
    } else {
      // forjado clásico: arched top rail, bars with lance tips, scroll band and rings
      const peak = m + H * .02;
      out.push(P(`M${x0} ${yt} Q${W / 2} ${f(peak - archH * .2)} ${x1} ${yt}`, sw * 1.5));
      const yRail = yt + (yb - yt) * .14, yBand = yb - (yb - yt) * .2;
      out.push(P(`M${x0} ${f(yRail)} L${x1} ${f(yRail)} M${x0} ${f(yBand)} L${x1} ${f(yBand)}`, sw * 1.3));
      const n = Math.max(6, Math.round((x1 - x0) / (sw * 9))), gap = (x1 - x0) / n;
      for (let i = 1; i < n; i++) {
        const x = x0 + gap * i;
        const u = (x - W / 2) / (W / 2), ytop = yt - archH * (1 - u * u) * .95;
        out.push(P(`M${f(x)} ${yb} L${f(x)} ${f(ytop)}`, sw, 'class="bar"'));
        out.push(P(spear(x, ytop, gap * .9), sw * .9, 'class="tip"'));
      }
      // scroll band between the lower rails
      const bh = Math.min((yb - yBand) - sw * 3, gap * .8);
      for (let i = 0; i < n; i++) {
        const xa = x0 + gap * (i + .5), ya = yBand + ((yb - yBand) - bh) / 2;
        [-1, 1].forEach(sd => out.push(P(cscroll(xa, ya, bh, sd, .9), sw * .75, 'class="scroll"')));
      }
      // rings under the top rail
      for (let i = 0; i < n; i++) {
        const cx = x0 + gap * (i + .5), cy = yRail + (yb - yt) * .07, r = Math.min(gap * .38, (yb - yt) * .05);
        out.push(`<circle cx="${f(cx)}" cy="${f(cy)}" r="${f(r)}" stroke-width="${f(sw * .8)}" class="ring"/>`);
      }
      // centre medallion
      const mc = [W / 2, yt + (yb - yt) * .5], mr = Math.min(W, H) * .1;
      [-1, 1].forEach(sd => out.push(P(cscroll(mc[0] + sd * mr * .15, mc[1] - mr, mr * 2, sd, 1.3), sw * 1.1, 'class="scroll"')));
    }
    return svg(`0 0 ${W} ${H}`, out.join(""), opts.cls);
  }

  function balcony(W, H) {
    const sw = W / 160, out = [];
    out.push(P(`M${sw * 2} ${sw * 3} L${W - sw * 2} ${sw * 3} M${sw * 2} ${H - sw * 2} L${W - sw * 2} ${H - sw * 2}`, sw * 2));
    const n = 7, gw = (W - sw * 4) / n;
    for (let i = 0; i <= n; i++) out.push(P(`M${f(sw * 2 + gw * i)} ${sw * 3} L${f(sw * 2 + gw * i)} ${H - sw * 2}`, sw * 1.2));
    for (let i = 0; i < n; i++) {
      const x = sw * 2 + gw * (i + .5);
      out.push(P(sscroll(x, sw * 6, H - sw * 11, i % 2 ? 1 : -1, gw * .22), sw, 'class="scroll"'));
    }
    return svg(`0 0 ${W} ${H}`, out.join(""));
  }

  // catalog thumbnails, one drawing per family; seed varies the details
  function thumb(cat, seed) {
    seed = seed || 0;
    const v = (seed % 5) / 5;
    let inner = "";
    if (cat === "Adornos de barra") {
      inner = P("M50 92 L50 46", 3) + P(spear(50, 46, 26 + v * 10), 2.4) +
        P(cscroll(47, 52, 26 + v * 6, -1, 1), 2) + P(cscroll(53, 52, 26 + v * 6, 1, 1), 2);
    } else if (cat === "Adornos de poste") {
      inner = P("M44 92 L44 54 M56 92 L56 54 M40 54 L60 54", 3) + `<circle cx="50" cy="${36 - v * 4}" r="${13 + v * 3}" stroke-width="2.6"/>` + P(`M50 ${22 - v * 7} L50 ${12 - v * 7}`, 2.6);
    } else if (cat === "Llamadores") {
      inner = `<circle cx="50" cy="24" r="9" stroke-width="2.6"/><circle cx="50" cy="${58 + v * 3}" r="${24 - v * 4}" stroke-width="3.4"/>` + P("M50 33 L50 36", 3) + `<circle cx="50" cy="${83 - v * 2}" r="3.5" stroke-width="2.4"/>`;
    } else if (cat === "Tubos forjados") {
      const a = [], b = [];
      for (let i = 0; i <= 40; i++) { const y = 10 + i * 2, w = Math.sin(i * (.55 + v * .2)) * 9; a.push([50 + w, y]); b.push([50 - w, y]); }
      inner = P(poly(a), 2.4) + P(poly(b), 2.4) + P("M38 10 L62 10 M38 90 L62 90", 3);
    } else {
      inner = P("M24 40 L76 40 L76 82 L24 82 Z", 2.6) + P("M24 40 L50 24 L76 40", 2.6) + P("M36 60 L64 60", 2.2) + P(cscroll(50, 64, 14, 1, 1), 1.8);
    }
    return svg("0 0 100 100", inner, "thumb");
  }

  root.Hierro = { gate, balcony, thumb, cscroll, sscroll, spiral, svg, P };
})(typeof window !== "undefined" ? window : globalThis);
