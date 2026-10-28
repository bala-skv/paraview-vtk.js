import puppeteer from 'puppeteer-core';
import { execSync } from 'node:child_process';
const [variant, size, out] = [process.argv[2], Number(process.argv[3]), process.argv[4]];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const args = ['--no-sandbox', '--no-first-run', '--no-default-browser-check', '--window-size=1593,1000'];
if (variant === 'devtools') args.push('--auto-open-devtools-for-tabs');
const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: false, ignoreDefaultArgs: ['--disable-background-timer-throttling', '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding'], defaultViewport: variant === 'emul' ? { width: 1593, height: 934 } : null, userDataDir: `${out}/prof_${variant}_${size}`, args });
const p = (await b.pages())[0] ?? await b.newPage();
await p.goto('http://localhost:8140/', { waitUntil: 'domcontentloaded' });
await p.waitForFunction(() => window.trame?.state?.state?.stats?.triangles > 0, { timeout: 120000 });
await p.evaluate((s) => { window.trame.state.set('local_rendering', false); window.trame.state.set('size', s); }, size);
await sleep(8000);
await p.bringToFront();
if (variant === 'maxi') { const c = await b.target().createCDPSession(); const { windowId } = await c.send('Browser.getWindowForTarget', { targetId: p.target()._targetId }); await c.send('Browser.setWindowBounds', { windowId, bounds: { windowState: 'maximized' } }); await sleep(2500); }
await p.evaluate(() => window.trame.state.set('orbit_report', ''));
await sleep(500);
const t0 = Date.now();
let cpu = [];
const sampler = setInterval(() => { try { cpu.push(execSync("ps -C pvpython-real -o %cpu= | head -1").toString().trim()); } catch {} }, 1000);
if (variant === 'hidden') { const o = await b.newPage(); await o.goto('about:blank'); await o.bringToFront(); }
await p.evaluate(() => [...document.querySelectorAll('button')].find((x) => /benchmark orbit/i.test(x.textContent))?.click());
await p.waitForFunction(() => window.trame.state.state.orbit_report, { timeout: 400000 }).catch(() => {});
clearInterval(sampler);
const rep = await p.evaluate(() => window.trame.state.state.orbit_report);
const vp = await p.evaluate(() => `${innerWidth}x${innerHeight}`);
console.log(`${variant} size=${size} viewport=${vp} wall=${((Date.now() - t0) / 1000).toFixed(1)}s report="${rep}" pvpython_cpu%=[${cpu.join(',')}]`);
await b.close();
