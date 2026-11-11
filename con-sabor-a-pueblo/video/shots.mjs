// Cuadros de revisión sin renderizar todo: node shots.mjs 2,8,12  -> build/rev.jpg
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const proj = path.join(HERE, "build", "con-sabor-a-pueblo-vertical");
const ts = (process.argv[2] || "5,10,20").split(",").map(Number);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto(pathToFileURL(path.join(proj, "index.html")).href);
await p.waitForTimeout(1500);
let i = 0;
for (const t of ts) {
  await p.evaluate(t => {
    const tl = Object.values(window.__timelines)[0]; tl.pause(); tl.seek(t, false);
    document.querySelectorAll(".clip").forEach(c => { const s = +c.dataset.start, d = +c.dataset.duration; c.style.visibility = t >= s && t < s + d ? "visible" : "hidden"; c.style.display = t >= s && t < s + d ? "" : "none"; });
  }, t);
  await p.screenshot({ path: path.join(HERE, "build", `r${String(i++).padStart(2, "0")}.jpg`), type: "jpeg", quality: 80 });
}
await b.close();
execFileSync("ffmpeg", ["-v", "error", "-y", "-pattern_type", "glob", "-i", path.join(HERE, "build", "r*.jpg"), "-vf", `scale=360:-1,tile=${Math.ceil(ts.length / 2)}x2`, "-frames:v", "1", path.join(HERE, "build", "rev.jpg")]);
