import puppeteer from 'puppeteer-core';
const out = process.argv[2];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const browser = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: false, defaultViewport: { width: 1500, height: 900 },
  userDataDir: `${out}/profile`, args: ['--no-sandbox', '--no-first-run', '--no-default-browser-check', '--window-size=1500,1000'] });
const page = (await browser.pages())[0] ?? await browser.newPage();
async function load(data = 'foot_128') {
  await page.goto('http://localhost:5195/', { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('canvas', { timeout: 60000 });
  await sleep(3000);
  await page.evaluate((d) => { const s = document.querySelector('select'); const o = [...s.options].find((x) => x.value.includes(d) || x.textContent.includes(d)); s.value = o.value; s.dispatchEvent(new Event('change', { bubbles: true })); }, data);
  await sleep(3500);
  await page.evaluate(() => { const d = [...document.querySelectorAll('details')].find((x) => /Tools/.test(x.textContent.slice(0, 20))); if (d) d.open = true; });
  await sleep(500);
}
const fs = (title) => `(() => [...document.querySelectorAll('fieldset')].find((f) => f.querySelector('legend')?.textContent.trim() === ${JSON.stringify(title)}))()`;
async function tick(title, cls = 'on') { await page.evaluate((t, c) => { const f = [...document.querySelectorAll('fieldset')].find((x) => x.querySelector('legend')?.textContent.trim() === t); const i = f.querySelector('input.' + c); i.click(); }, title, cls); }
async function range(title, cls, v) { await page.evaluate((t, c, v) => { const f = [...document.querySelectorAll('fieldset')].find((x) => x.querySelector('legend')?.textContent.trim() === t); const i = f.querySelector('input.' + c); i.value = v; i.dispatchEvent(new Event('input', { bubbles: true })); i.dispatchEvent(new Event('change', { bubbles: true })); }, title, cls, v); }
async function shot(name, title) { if (title) await page.evaluate((t) => { [...document.querySelectorAll('fieldset')].find((x) => x.querySelector('legend')?.textContent.trim() === t).scrollIntoView({ block: 'start' }); }, title); await sleep(2500); await page.screenshot({ path: `${out}/${name}.png` }); console.log('saved', name); }
async function zoom() { const b = await (await page.$('canvas')).boundingBox(); await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2); for (let i = 0; i < 6; i++) { await page.mouse.wheel({ deltaY: -300 }); await sleep(150); } await sleep(800); }
const gl = async () => page.evaluate(() => document.body.innerText.match(/WebGL renderer[\s\S]{0,120}/)?.[0]?.replace(/\n/g, ' '));
const box = async () => { const b = await (await page.$('canvas')).boundingBox(); return b; };

await load(); console.log(await gl());
await zoom(); await tick('Isosurface'); await range('Isosurface', 'v', 110);
await page.evaluate(() => { const l = [...document.querySelectorAll('label')].find((x) => /Show volume/.test(x.textContent)); l.querySelector('input').click(); });
await shot('iso', 'Isosurface');
await load(); await zoom(); await tick('Probe'); await page.mouse.click(890, 560); await sleep(800); await page.mouse.click(905, 600); await shot('probe', 'Probe');
await load(); await zoom(); await tick('Measure and export'); await sleep(500); await page.mouse.click(860, 440); await sleep(700); await page.mouse.click(960, 660); await sleep(700); await page.mouse.move(1200, 300); await shot('measure', 'Measure and export');
await browser.close();
