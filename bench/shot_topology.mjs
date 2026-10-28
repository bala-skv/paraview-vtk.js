// Dev screenshots of showcase-b/app_topology.py: node shot_topology.mjs  (needs the app on :8120)
import puppeteer from 'puppeteer-core';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const out = (n) => `../report/figures/feat_d_${n}.png`;
const b = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: true,
  defaultViewport: { width: 1400, height: 1000 }, args: ['--no-sandbox'] });
const p = await b.newPage();
p.on('console', (m) => { if (m.type() === 'error') console.log('console.error', m.text()); });
await p.goto('http://localhost:8120/', { waitUntil: 'load', timeout: 120000 });
const set = async (k, v, wait) => { await p.evaluate((k, v) => window.trame.state.set(k, v), k, v); await sleep(wait); };
const txt = () => p.evaluate(() => document.body.innerText.match(/\d+ of \d+ persistence pairs[^\n]*\n[^\n]*/)?.[0]);
await sleep(20000);
console.log('wavelet th0.02:', await txt());
await p.screenshot({ path: out('wavelet_th002') });
await set('th_ui', 0.08, 0); await set('th', 0.08, 15000);
console.log('wavelet th0.08:', await txt());
await p.screenshot({ path: out('wavelet_th008') });
await set('source', 'Gaussians (known: 5 maxima)', 25000);
await set('th_ui', 0.05, 0); await set('th', 0.05, 12000);
console.log('gauss th0.05:', await txt(), await p.evaluate(() => window.trame.state.get('counts')));
await p.screenshot({ path: out('gaussians_th005') });
await set('show0', false, 0); await set('show1', false, 0); await set('show2', false, 6000);
await p.screenshot({ path: out('gaussians_maxima_only') });
await set('show0', true, 0); await set('show1', true, 0); await set('show2', true, 3000);
await set('source', 'aneurism.vti', 40000);
console.log('aneurism:', await txt(), await p.evaluate(() => window.trame.state.get('counts')));
await p.screenshot({ path: out('aneurism') });
await b.close();
