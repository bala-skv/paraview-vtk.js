import puppeteer from 'puppeteer-core';
const out = process.argv[2];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: false, defaultViewport: { width: 1500, height: 900 },
  userDataDir: `${out}/profile`, args: ['--no-sandbox', '--no-first-run', '--no-default-browser-check', '--window-size=1500,1000'] });
const p = (await b.pages())[0] ?? await b.newPage();
await p.goto('http://localhost:8130/', { waitUntil: 'domcontentloaded' });
await p.waitForFunction(() => window.trame?.state?.state?.stats?.triangles > 0, { timeout: 120000 });
await sleep(6000);
const set = async (o, wait = 5000) => { await p.evaluate((o) => window.trame.state.update(o), o); await sleep(wait); };
const shot = async (n) => { await p.screenshot({ path: `${out}/${n}.png` }); console.log('saved', n, await p.evaluate(() => JSON.stringify(window.trame.state.state.stats))); };
const drag = async (dx, dy) => { await p.mouse.move(900, 500); await p.mouse.down(); for (let i = 1; i <= 12; i++) { await p.mouse.move(900 + dx * i / 12, 500 + dy * i / 12); await sleep(60); } await p.mouse.up(); await sleep(3000); };
await set({ local_rendering: false, kind: 'Slice', color_by: 'RTData', cmap: 'Viridis', bar: true }, 14000); await drag(120, -80); await shot('slice_remote_bar');
await b.close();
