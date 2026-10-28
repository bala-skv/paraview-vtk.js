// Build Showcase A for GitHub Pages (extra E1) into showcase-a/dist-pages.
// Usage: node scripts/pages_build.mjs   (VITE_BASE defaults to /paraview-vtk.js/; set it for other repo names)
// Ships only tooth and foot_128 from the tracked pages-data/ folder; local public/data is never touched.
import { spawnSync } from 'node:child_process';
import { cpSync, rmSync, mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'dist-pages');
const base = process.env.VITE_BASE || '/paraview-vtk.js/';
const KEEP = ['tooth.vti', 'foot_128.vti', 'index.json', 'LICENSE-DATA.txt'];

const vite = join(root, 'node_modules', 'vite', 'bin', 'vite.js');
const r = spawnSync(process.execPath, [vite, 'build', '--outDir', 'dist-pages', '--emptyOutDir'],
  { cwd: root, stdio: 'inherit', env: { ...process.env, VITE_BASE: base } });
if (r.status !== 0) process.exit(r.status ?? 1);

// replace whatever Vite copied from public/data with the trimmed, tracked set
rmSync(join(out, 'data'), { recursive: true, force: true });
mkdirSync(join(out, 'data'), { recursive: true });
for (const f of KEEP) cpSync(join(root, 'pages-data', f), join(out, 'data', f));
writeFileSync(join(out, '.nojekyll'), '');

// credits / licence footer, injected only into the Pages build (local dev and ?bench=1 are untouched)
const footer = `<div id="credits" style="position:fixed;right:0;bottom:0;z-index:9;max-width:520px;padding:4px 8px;background:#000a;color:#bbc;font:11px system-ui,sans-serif">
Datasets: <a style="color:#8cf" href="https://klacansky.com/open-scivis-datasets/">Open SciVis Datasets</a> (P. Klacansky), CC BY-NC-SA 4.0:
tooth &ndash; GE Aircraft Engines; foot &ndash; volvis.org and Philips Research. Converted to .vti (foot downsampled to 128&sup3;).
Code: BSD-3-Clause, <a style="color:#8cf" href="https://github.com/bala-skv/paraview-vtk.js">source</a>. <a style="color:#8cf" href="${base}data/LICENSE-DATA.txt">Data licence</a>.</div>
`;
const idx = join(out, 'index.html');
if (!existsSync(idx)) throw new Error('index.html missing in dist-pages');
const html = readFileSync(idx, 'utf8');
if (!html.includes('</body>')) throw new Error('no </body> in index.html');
writeFileSync(idx, html.replace('</body>', footer + '</body>'));
console.log(`pages build ready: ${out} (base ${base})`);
