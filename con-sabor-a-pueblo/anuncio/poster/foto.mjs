// node foto.mjs -> ../../con-sabor-a-pueblo-poster-whatsapp.png (1080x1920) (a 1x: la foto es de 1080 px y no se agranda)
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
const { chromium } = createRequire(import.meta.url)("playwright");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const b = await chromium.launch();
for (const [esc, nombre] of [[1, "con-sabor-a-pueblo-poster-whatsapp.png"]]) {
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: esc });
  await p.goto(pathToFileURL(path.join(HERE, "poster.html")).href);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(HERE, "..", "..", nombre) });
}
await b.close();
