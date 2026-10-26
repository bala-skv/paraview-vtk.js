// Benchmark mode: ?bench=1&data=foot_128.vti&frames=360&reps=3[&machine=laptop][&restart=1]
// One repetition per page load (cold start), results accumulate in localStorage 'bench_rows'.
import { createViewer, parseVti } from './viewer';

export const CSV_HEADER = 'timestamp,machine_id,browser,gpu_renderer,showcase,condition,dataset,size,rep,ttfr_ms,fps_median,fps_p5,client_mem_mb,server_rss_mb,ws_bytes,triangles,geometry_kb,network_profile,notes';
const ROWS_KEY = 'bench_rows';
const RUN_KEY = 'bench_run';

const nextFrame = () => new Promise((r) => requestAnimationFrame(r));
const read = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
const write = (k, v) => localStorage.setItem(k, JSON.stringify(v));

function percentile(sortedAsc, p) {
  const i = Math.min(sortedAsc.length - 1, Math.max(0, Math.floor(p * (sortedAsc.length - 1))));
  return sortedAsc[i];
}

function browserName() {
  const ua = navigator.userAgent;
  const m = ua.match(/(Edg|Chrome|Firefox)\/([\d.]+)/);
  return m ? `${m[1] === 'Edg' ? 'Edge' : m[1]} ${m[2].split('.')[0]}` : 'unknown';
}

const csvCell = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));

export function rowsToCsv(rows) {
  return [CSV_HEADER, ...rows.map((r) => CSV_HEADER.split(',').map((c) => csvCell(r[c] ?? '')).join(','))].join('\n') + '\n';
}

export async function runBench(container, params, t0) {
  const dataFile = params.get('data') || 'foot_128.vti';
  const frames = Number(params.get('frames') || 360);
  const reps = Number(params.get('reps') || 3);
  const machine = params.get('machine') || 'laptop';

  let run = read(RUN_KEY, null);
  if (!run || run.data !== dataFile || run.reps !== reps || run.frames !== frames || params.get('restart') === '1') {
    run = { data: dataFile, reps, frames, done: 0 };
    write(RUN_KEY, run);
    // drop the restart flag so the reload loop does not reset itself
    const u = new URL(location.href); u.searchParams.delete('restart'); history.replaceState(null, '', u);
  }

  const status = document.createElement('pre');
  status.id = 'bench-status';
  status.style.cssText = 'position:absolute;left:8px;top:8px;margin:0;padding:8px;background:#000a;color:#9f9;font:12px monospace;z-index:5;';
  container.appendChild(status);
  const say = (s) => { status.textContent = s; };

  if (run.done >= reps) { finish(status, container); return; }

  const rep = run.done + 1;
  say(`bench ${dataFile}: rep ${rep}/${reps} loading...`);
  const resp = await fetch(`${import.meta.env.BASE_URL}data/${dataFile}`, { cache: 'no-store' });
  const image = parseVti(await resp.arrayBuffer());

  const viewer = createViewer(container);
  viewer.setImage(image);
  viewer.renderWindow.render();
  await nextFrame();
  const ttfr = performance.now() - t0;

  say(`bench ${dataFile}: rep ${rep}/${reps} orbiting ${frames} frames...`);
  const camera = viewer.renderer.getActiveCamera();
  const dts = [];
  let last = await nextFrame();
  for (let i = 0; i < frames; i++) {
    camera.azimuth(1);
    viewer.renderer.resetCameraClippingRange();
    viewer.renderWindow.render();
    const now = await nextFrame();
    dts.push(now - last);
    last = now;
  }
  const fpsSorted = dts.map((d) => 1000 / d).sort((a, b) => a - b);
  const dims = image.getDimensions();
  const mem = performance.memory ? performance.memory.usedJSHeapSize / 2 ** 20 : '';
  const row = {
    timestamp: new Date().toISOString(),
    machine_id: machine,
    browser: browserName(),
    gpu_renderer: viewer.glRenderer(),
    showcase: 'A',
    condition: 'A-local',
    dataset: dataFile.replace(/\.vti$/, ''),
    size: dims[0],
    rep,
    ttfr_ms: ttfr.toFixed(1),
    fps_median: percentile(fpsSorted, 0.5).toFixed(2),
    fps_p5: percentile(fpsSorted, 0.05).toFixed(2),
    client_mem_mb: mem === '' ? '' : mem.toFixed(1),
    network_profile: 'none',
    notes: `rAF-paced (display refresh caps fps); frames=${frames}`,
  };
  const rows = read(ROWS_KEY, []);
  rows.push(row);
  write(ROWS_KEY, rows);
  write(RUN_KEY, { ...run, done: rep });
  say(`rep ${rep}/${reps} done: median ${row.fps_median} fps, p5 ${row.fps_p5}, TTFR ${row.ttfr_ms} ms`);

  if (rep < reps) {
    setTimeout(() => location.reload(), 500);
  } else {
    finish(status, container);
  }
}

function finish(status, container) {
  const rows = read(ROWS_KEY, []);
  console.table(rows);
  status.textContent = `bench complete: ${rows.length} rows in localStorage "${ROWS_KEY}"`;
  const btn = document.createElement('button');
  btn.textContent = 'Download CSV';
  btn.id = 'bench-download';
  btn.style.cssText = 'position:absolute;left:8px;top:48px;z-index:5;padding:6px 10px;';
  btn.onclick = () => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([rowsToCsv(read(ROWS_KEY, []))], { type: 'text/csv' }));
    a.download = 'bench_rows.csv';
    a.click();
  };
  container.appendChild(btn);
}
