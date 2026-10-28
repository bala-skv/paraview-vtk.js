// Extra E8: open the notebook in JupyterLab (port 8888), run all cells, screenshot. Needs jupyter lab --expose-app-in-browser.
import puppeteer from "puppeteer-core";
const out = process.argv[2] || "report/figures/extra_e8_jupyter.png";
const b = await puppeteer.launch({ executablePath: "/usr/bin/google-chrome", headless: "new",
  args: ["--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"], defaultViewport: { width: 1400, height: 1000 } });
const p = await b.newPage();
p.on("console", m => { if (m.type() === "error") console.log("console.error:", m.text().slice(0, 200)); });
await p.goto("http://localhost:8888/lab/tree/notebooks/trame_in_jupyter.ipynb?reset", { waitUntil: "networkidle2", timeout: 120000 });
await p.waitForFunction("window.jupyterapp && document.querySelector('.jp-Notebook')", { timeout: 120000 });
await new Promise(r => setTimeout(r, 15000));
await p.evaluate("jupyterapp.commands.execute('notebook:run-all-cells')");
await p.waitForSelector("iframe.trame-iframe", { timeout: 300000 });
await new Promise(r => setTimeout(r, 40000));
const fr = p.frames().find(f => f.url().includes("trame-jupyter-server"));
console.log("iframe url:", fr && fr.url());
await p.screenshot({ path: out });
if (fr) { // move slider by keyboard and re-shoot
  await p.evaluate("document.querySelector('iframe.trame-iframe').scrollIntoView()");
  const s = await fr.$(".v-slider-thumb"); 
  if (s) { await s.focus(); for (let i = 0; i < 40; i++) await p.keyboard.press("ArrowRight"); await new Promise(r => setTimeout(r, 15000)); await p.screenshot({ path: out.replace(".png", "_slider.png") }); }
  else console.log("no slider thumb found");
}
await b.close();
