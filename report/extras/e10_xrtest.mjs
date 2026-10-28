import { createRequire } from 'module'; const puppeteer = createRequire('/home/bala/myfiles/sem5/Scientific Vis/evaluation of vis/vtkjs-pvweb-eval/bench/x.js')('puppeteer-core');
import fs from 'fs';
const S = process.argv[2];
const iwer = fs.readFileSync(S + '/iwer/node_modules/iwer/build/iwer.min.js', 'utf8');
const inject = iwer + `
;(function(){
 const { XRDevice, metaQuest3 } = window.IWER;
 const dev = new XRDevice(metaQuest3);
 dev.installRuntime({ forceInstall: true });
 window.__dev = dev;
 window.__xr = { req: 0, frames: 0, ended: 0, types: [] };
 const rs = navigator.xr.requestSession.bind(navigator.xr);
 navigator.xr.requestSession = async (t, o) => { window.__xr.req++; window.__xr.types.push(t); const s = await rs(t, o);
   const raf = s.requestAnimationFrame.bind(s);
   s.requestAnimationFrame = (cb) => raf((t2, f) => { window.__xr.frames++; return cb(t2, f); });
   s.addEventListener('end', () => window.__xr.ended++); return s; };
})();`;
const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new',
  args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage();
await p.setViewport({ width: 1280, height: 800 });
p.on('console', (m) => console.log('[page]', m.text().slice(0, 300)));
p.on('pageerror', (e) => console.log('[pageerror]', e.message));
if (process.argv[3] !== 'noxr') await p.evaluateOnNewDocument(inject);
await p.goto('http://localhost:5192/?xr=1', { waitUntil: 'load', timeout: 120000 });
await p.waitForSelector('#dataset');
await p.select('#dataset', 'foot_64.vti');
await new Promise((r) => setTimeout(r, 15000));
await p.evaluate(() => document.querySelector('#tools').open = true);
await new Promise((r) => setTimeout(r, 2000));
const st = () => p.evaluate(() => ({ btn: document.querySelector('.xr')?.textContent, dis: document.querySelector('.xr')?.disabled, msg: document.querySelector('.xrmsg')?.textContent, xr: window.__xr, size: [document.querySelector('#view canvas')?.width, document.querySelector('#view canvas')?.height] }));
console.log('before', JSON.stringify(await st()));
await p.screenshot({ path: S + '/xr_before.png' });
if (process.argv[3] === 'noxr') { await b.close(); process.exit(0); }
await p.click('.xr');
await new Promise((r) => setTimeout(r, 15000));
console.log('in-xr', JSON.stringify(await st()));
await p.screenshot({ path: S + '/xr_in.png' });
await new Promise((r) => setTimeout(r, 5000));
console.log('in-xr+5s', JSON.stringify((await st()).xr));
await p.evaluate(() => document.querySelector('.xr').click());
await new Promise((r) => setTimeout(r, 8000));
console.log('after', JSON.stringify(await st()));
await p.screenshot({ path: S + '/xr_after.png' });
await b.close();
