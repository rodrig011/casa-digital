// Renderiza index.html a MP4 1080x1920 con desenfoque de movimiento real: por cada cuadro del video se sacan
// SUB sub-cuadros (240 por segundo) y ffmpeg mezcla 6 de cada 8, como un obturador de cámara abierto 270°.
//   node render.mjs                 -> build/loca-luna-casa-digital-v4.mp4
//   node render.mjs --hoja          -> build/hoja.jpg (cuadros sueltos para revisar; T="1,2.5,..." elige los tiempos)
//   A=10 B=16 node render.mjs       -> solo ese tramo, sin música (build/tramo.mp4)
// La música no va en el repo: copiar /mnt/project-files/musica/better-times-are-coming-mixkit.mp3 a src/musica.mp3
import { createRequire } from "node:module";
import { spawn, execFileSync } from "node:child_process";
import { mkdirSync, existsSync, writeFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import os from "node:os";
import path from "node:path";

const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, "build");
const FPS = 30, SUB = 8;
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const abrir = async () => {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(path.join(HERE, "index.html")).href);
  await page.waitForFunction("window.READY === true");
  return page;
};
const page0 = await abrir();
const total = await page0.evaluate("window.TOTAL");

if (process.argv.includes("--hoja")) {
  const times = (process.env.T || "1.5,3.6,4.2,5.6,7,8.3,9.8,12,14.6,15.6,18.5,20.6,21.2,24.8,28.6,31,34,36.5,40.5,42.6,45.5,47.6,52").split(",").map(Number);
  let i = 0;
  for (const t of times) {
    await page0.evaluate(t => window.seek(t), t);
    await page0.screenshot({ path: path.join(OUT, `cuadro${String(i++).padStart(3, "0")}.jpg`), type: "jpeg", quality: 85 });
  }
  await browser.close();
  const cols = +(process.env.COLS || 6);
  execFileSync("ffmpeg", ["-v", "error", "-y", "-start_number", "0", "-i", path.join(OUT, "cuadro%03d.jpg"), "-frames:v", String(times.length), "-vf", `scale=${process.env.W || 330}:-1,tile=${cols}x${Math.ceil(times.length / cols)}`, "-frames:v", "1", path.join(OUT, "hoja.jpg")]);
  console.log("hoja lista", total.toFixed(2) + " s");
  process.exit(0);
}

const f0 = Math.round((+process.env.A || 0) * FPS), f1 = Math.round((process.env.B ? +process.env.B : total) * FPS);
const N = Math.max(1, Math.min(+(process.env.N || os.cpus().length), 6));
const paso = Math.ceil((f1 - f0) / N);
let hechos = 0;
const partes = await Promise.all(Array.from({ length: N }, async (_, w) => {
  const a = f0 + w * paso, b = Math.min(f1, a + paso);
  if (a >= b) return null;
  const page = w ? await abrir() : page0;
  const file = path.join(OUT, `parte${w}.mp4`);
  const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS * SUB), "-c:v", "mjpeg", "-i", "-",
    "-vf", `tmix=frames=6:weights='1 1 1 1 1 1',select='eq(mod(n\\,${SUB})\\,${SUB - 1})',setpts=N/${FPS}/TB`, "-r", String(FPS),
    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", file], { stdio: ["pipe", "inherit", "inherit"] });
  for (let f = a; f < b; f++) for (let s = 0; s < SUB; s++) {
    await page.evaluate(t => window.seek(t), (f + s / SUB) / FPS);
    const buf = await page.screenshot({ type: "jpeg", quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (s === 0 && ++hechos % 150 === 0) console.log(`${hechos}/${f1 - f0}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  return file;
}));
await browser.close();

const lista = path.join(OUT, "partes.txt");
writeFileSync(lista, partes.filter(Boolean).map(f => `file '${f}'`).join("\n"));
const tramo = process.env.A || process.env.B;
const music = path.join(HERE, "src", "musica.mp3");
const mp4 = path.join(OUT, tramo ? "tramo.mp4" : "loca-luna-casa-digital-v4.mp4");
const args = ["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista];
if (!tramo && existsSync(music)) args.push("-i", music, "-af", `afade=t=in:d=0.05,afade=t=out:st=${(total - 1.8).toFixed(2)}:d=1.8`, "-c:a", "aac", "-b:a", "192k", "-t", total.toFixed(3));
args.push("-c:v", "copy", "-movflags", "+faststart", mp4);
execFileSync("ffmpeg", args, { stdio: "inherit" });
console.log("listo:", mp4, existsSync(music) ? "" : "(sin música: falta src/musica.mp3)");
