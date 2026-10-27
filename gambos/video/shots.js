// Panel screenshots for the video: phone width (390 css px, 2x), demo session open. node shots.js
const {chromium} = require("playwright");
const path = require("path");
const PANEL = "file://" + path.join(__dirname, "..", "panel", "dist", "gambos-panel.html");
const SHOTS = [["hoy", "panel-hoy.jpg", [".kpis", ".days", ".recs"]], ["cupos", "panel-cupos.jpg", ["[data-dsel='6']", ".wait", ".tbl.resv"]],
  ["insumos", "panel-insumos.jpg", [".card", ".dish", ".tbl"]]];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport: {width: 390, height: 844}, deviceScaleFactor: 2});
  await p.goto(PANEL); await p.fill("#gMail", "demo@gambos.hn"); await p.fill("#gPass", "boil2026"); await p.click("#gateForm button"); await p.waitForTimeout(800);
  for (const [v, f, sels] of SHOTS) {
    await p.evaluate(h => { location.hash = h; }, v); await p.waitForTimeout(300);
    const ys = await p.evaluate(ss => ss.map(s => Math.round(document.querySelector("#main " + s).getBoundingClientRect().top + scrollY)), sels);
    const h = await p.evaluate(() => document.documentElement.scrollHeight);
    await p.screenshot({path: path.join(__dirname, "src", f), fullPage: true, type: "jpeg", quality: 88});
    console.log(v, f, h, ys);
  }
  await b.close();
})();
