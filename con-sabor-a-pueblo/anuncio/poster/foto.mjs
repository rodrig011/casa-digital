// node foto.mjs            -> ../../con-sabor-a-pueblo-poster-whatsapp.png (versión elegida, 1080x1920)
// node foto.mjs --todas    -> build/poster-bagel.png
// A 1x a propósito: la foto es de 1080 px y no se agranda.
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import { mkdirSync } from "node:fs";
import path from "node:path";
const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const ELEGIDA = "bagel";
const todas = process.argv.includes("--todas");
mkdirSync(path.join(HERE, "build"), { recursive: true });
const b = await chromium.launch();
for (const v of todas ? ["bagel"] : [ELEGIDA]) {
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto(pathToFileURL(path.join(HERE, "poster.html")).href + "?v=" + v);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.screenshot({ path: todas ? path.join(HERE, "build", `poster-${v}.png`) : path.join(HERE, "..", "..", "con-sabor-a-pueblo-poster-whatsapp.png") });
}
await b.close();
