// Renderiza index.html a MP4 1080x1920 sin HyperFrames: Playwright saca cada cuadro y ffmpeg los une con la música.
//   node render.mjs                 -> build/alitas-aleman-corto.mp4
//   node render.mjs --hoja          -> build/hoja.jpg (un cuadro por escena, para revisar)
// La música no va en el repo: copiar /mnt/project-files/musica/stylish-fassounds.mp3 a src/musica.mp3
import { createRequire } from "node:module";
import { spawn, execFileSync } from "node:child_process";
import { mkdirSync, existsSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, "build");
const FPS = 30;
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.join(HERE, "index.html")).href);
await page.waitForFunction("window.READY === true");
const total = await page.evaluate("window.TOTAL");

if (process.argv.includes("--hoja")) {
  const times = (process.env.T || "1.2,5.2,8.6,11.5,14.6,17,21.8,24.5,26.5,29.5,31,33.5,37").split(",").map(Number);
  let i = 0;
  for (const t of times) {
    await page.evaluate(t => window.seek(t), t);
    await page.screenshot({ path: path.join(OUT, `cuadro${String(i++).padStart(2, "0")}.jpg`), type: "jpeg", quality: 85 });
  }
  await browser.close();
  execFileSync("ffmpeg", ["-v", "error", "-y", "-pattern_type", "glob", "-i", path.join(OUT, "cuadro*.jpg"), "-vf", `scale=360:-1,tile=${Math.ceil(times.length / 2)}x2`, "-frames:v", "1", path.join(OUT, "hoja.jpg")]);
  console.log("hoja lista", total.toFixed(2) + " s");
  process.exit(0);
}

const music = path.join(HERE, "src", "musica.mp3");
const mp4 = path.join(OUT, "alitas-aleman-corto.mp4");
const n = Math.round(total * FPS);
const args = ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-"];
if (existsSync(music)) args.push("-i", music, "-af", `afade=t=in:d=0.05,afade=t=out:st=${(total - 1.6).toFixed(2)}:d=1.6`, "-c:a", "aac", "-b:a", "192k", "-shortest");
args.push("-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-t", total.toFixed(3), mp4);
const ff = spawn("ffmpeg", args, { stdio: ["pipe", "inherit", "inherit"] });
for (let f = 0; f < n; f++) {
  await page.evaluate(t => window.seek(t), f / FPS);
  const buf = await page.screenshot({ type: "jpeg", quality: 96 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  if (f % 150 === 0) console.log(`${f}/${n}`);
}
ff.stdin.end();
await new Promise(r => ff.on("close", r));
await browser.close();
console.log("listo:", mp4, existsSync(music) ? "" : "(sin música: falta src/musica.mp3)");
