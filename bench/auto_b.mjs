// Optional helper for Showcase B runs: scripted 10 s orbit with the same mouse path every time.
// Measures WebSocket bytes, image-frame rate (remote) and page rAF rate (local), then prints an
// add_row.py command. Needs a running Showcase B (scripts/run_b.sh --size N --mode local|remote).
//
//   cd bench && npm ci
//   node auto_b.mjs --mode remote --size 128 --rep 1 [--port 8080] [--width 1280 --height 720] [--shot card.png] [--headless] [--chrome /path] [--seconds 10]
import puppeteer from 'puppeteer-core';
import { existsSync } from 'node:fs';

const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i < 0 ? d : (process.argv[i + 1]?.startsWith('--') || i + 1 >= process.argv.length ? true : process.argv[i + 1]); };
const mode = arg('mode', 'remote');
const size = Number(arg('size', 128));
const rep = Number(arg('rep', 1));
const port = Number(arg('port', 8080));
const seconds = Number(arg('seconds', 10));
const headless = arg('headless', false) === true;
const width = Number(arg('width', 1280));
const height = Number(arg('height', 720));
const hidden = arg('hidden', false) === true; // test: put the page in a background tab while the orbit runs
const shot = arg('shot', ''); // optional: save a screenshot of the Server stats card after the orbit
const emit = arg('emit', false) === true; // print one machine-readable RESULT line (used by run_all_b.sh)
const candidates = [arg('chrome', ''), process.env.CHROME, '/usr/bin/google-chrome',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'].filter(Boolean);
const executablePath = candidates.find((p) => existsSync(p));
if (!executablePath) throw new Error('Chrome/Edge not found: pass --chrome <path> or set CHROME');
if (!['remote', 'local'].includes(mode)) throw new Error('--mode must be remote or local');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const median = (a) => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.floor((s.length - 1) / 2)] : NaN; };

const browser = await puppeteer.launch({ executablePath, headless, defaultViewport: { width, height },
  args: ['--no-sandbox', `--window-size=${width},${height + 100}`, '--disk-cache-size=1', '--aggressive-cache-discard'] });
const page = await browser.newPage();
await page.setCacheEnabled(false);
const cdp = await page.createCDPSession();
await cdp.send('Network.enable');
let bytes = 0, binFrames = [], measuring = false, setupBytes = 0, inSetup = false;
cdp.on('Network.webSocketFrameReceived', (e) => {
  if (inSetup) setupBytes += e.response.opcode === 2 ? Math.ceil(e.response.payloadData.length * 3 / 4) : Buffer.byteLength(e.response.payloadData);
  if (!measuring) return;
  const r = e.response;
  const n = r.opcode === 2 ? Math.ceil(r.payloadData.length * 3 / 4) : Buffer.byteLength(r.payloadData);
  bytes += n;
  if (r.opcode === 2 && n > 1000) binFrames.push(performance.now());
});
cdp.on('Network.webSocketFrameSent', (e) => { if (measuring) bytes += Buffer.byteLength(e.response.payloadData); });

const t0 = performance.now();
await page.goto(`http://localhost:${port}/?_=${Date.now()}`, { waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => window.trame?.state?.state?.stats?.triangles > 0, { timeout: 60000 });
await page.waitForFunction(() => document.querySelector('canvas'), { timeout: 60000 });
const ttfr = performance.now() - t0;

// set mode and size through trame state, then let it settle (bytes here = cost of the switch / geometry push)
inSetup = true;
await page.evaluate((m, s) => { window.trame.state.set('local_rendering', m === 'local'); window.trame.state.set('size', s); }, mode, size);
await sleep(5000);
inSetup = false;
const stats = await page.evaluate(() => window.trame.state.state.stats);
if (stats.triangles <= 0) throw new Error('no triangles in stats; is the server up?');

await page.evaluate(() => { window.__raf = []; const f = (t) => { window.__raf.push(t); requestAnimationFrame(f); }; requestAnimationFrame(f); });
const box = await (await page.$('.v-main')).boundingBox(); // remote view is an <img>, local a <canvas>: use the content area
const cx = box.x + box.width / 2, cy = box.y + box.height / 2, R = Math.min(box.width, box.height) / 4;
measuring = true; bytes = 0; binFrames = [];
const tStart = performance.now();
await page.mouse.move(cx + R, cy);
await page.mouse.down();
let k = 0;
while (performance.now() - tStart < seconds * 1000) {
  const a = (k++ * 2 * Math.PI) / 120;
  await page.mouse.move(cx + R * Math.cos(a), cy + R * Math.sin(a));
  await sleep(8);
}
await page.mouse.up();
measuring = false;
const raf = await page.evaluate(() => window.__raf);
const mem = await page.metrics();

function perSecond(times) {
  const bins = new Array(Math.floor(seconds)).fill(0);
  for (const t of times) { const i = Math.floor((t - tStart) / 1000); if (i >= 0 && i < bins.length) bins[i]++; }
  return bins;
}
const rafBins = perSecond(raf.map((t) => tStart + (t - raf[0])));
const imgBins = perSecond(binFrames);
const bins = mode === 'remote' ? imgBins : rafBins;
const p5 = Math.min(...bins);
const out = {
  mode, size, rep, seconds, ws_bytes: bytes, ws_bytes_setup: setupBytes, ttfr_ms: Math.round(ttfr),
  fps_median: median(bins), fps_p5_min_of_1s_bins: p5,
  fps_source: mode === 'remote' ? 'binary image frames received per second' : 'page rAF callbacks per second',
  rAF_fps_median: median(rafBins), image_frames_total: binFrames.length,
  client_mem_mb: +(mem.JSHeapUsedSize / 2 ** 20).toFixed(1),
  triangles: stats.triangles, geometry_kb: stats.geometry_kb, server_rss_mb: stats.rss_mb,
  browser: (await browser.version()), gpu_note: 'record chrome://gpu renderer in --gpu-renderer',
};
// remote mode: also press Benchmark orbit once so server_events.csv gets an 'orbit' row
if (mode === 'remote') {
  await page.evaluate(() => [...document.querySelectorAll('button')].find((b) => /benchmark orbit/i.test(b.textContent))?.click());
  if (hidden) { const other = await browser.newPage(); await other.goto('about:blank'); await other.bringToFront(); }
  await page.waitForFunction(() => window.trame.state.state.orbit_report, { timeout: 300000 }).catch(() => {});
  out.orbit_report = await page.evaluate(() => window.trame.state.state.orbit_report);
  out.viewport = `${width}x${height}`;
  if (shot) { const card = await page.evaluateHandle(() => [...document.querySelectorAll('.v-card')].find((c) => /Server stats/.test(c.textContent))); await card.asElement()?.screenshot({ path: shot }); }
}
if (emit) { console.log('RESULT ' + JSON.stringify(out)); await browser.close(); process.exit(0); }
console.log(JSON.stringify(out, null, 2));
console.log('\nadd to results.csv (edit machine id / gpu / notes first):\n' +
  `.venv/bin/python bench/add_row.py --showcase B --condition B-${mode} --dataset wavelet --size ${size} --rep ${rep} ` +
  `--ttfr-ms ${out.ttfr_ms} --fps-median ${out.fps_median} --fps-p5 ${p5} --client-mem-mb ${out.client_mem_mb} ` +
  `--server-rss-mb ${out.server_rss_mb} --ws-bytes ${bytes} --triangles ${out.triangles} --geometry-kb ${out.geometry_kb} ` +
  `--browser "${out.browser}" --gpu-renderer "<fill>" --machine-id "<fill>" --notes "auto_b.mjs"`);
await browser.close();
