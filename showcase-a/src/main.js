const t0 = performance.now();

import { createViewer, parseVti } from './viewer';
import { buildPanel, showInfo } from './ui';
import { runBench } from './bench';
import { initTools } from './tools';
import { MESH_EXT, extOf } from './tools/mesh';

const root = document.getElementById('app');
const params = new URLSearchParams(location.search);
const BASE = import.meta.env.BASE_URL;

async function main() {
  if (params.get('bench') === '1') {
    root.className = 'bench';
    await runBench(root, params, t0);
    return;
  }

  const datasets = await (await fetch(`${BASE}data/index.json`)).json();
  const ui = buildPanel(root, datasets);
  const view = document.createElement('div');
  view.id = 'view';
  root.appendChild(view);
  const viewer = createViewer(view, { fps: true });
  ui.preset.value = viewer.getState().preset;
  const glr = viewer.glRenderer();
  const tools = initTools(viewer, ui.tools, ui);

  function syncSlice() {
    const n = viewer.sliceCount(ui.axis.value);
    ui.sliceIdx.max = n - 1;
    ui.sliceIdx.value = Math.floor(n / 2);
    ui.sliceOut.textContent = ui.sliceIdx.value;
  }

  function show(image, label, loadMs) {
    viewer.setImage(image);
    tools.setImage(image);
    syncSlice();
    const d = image.getDimensions();
    showInfo(ui, [
      ['Dataset', label],
      ['Dimensions', d.join(' × ')],
      ['Voxels', (d[0] * d[1] * d[2]).toLocaleString()],
      ['Load time', `${loadMs.toFixed(0)} ms`],
      ['WebGL renderer', glr],
    ]);
  }

  async function loadUrl(file, label) {
    const start = performance.now();
    const buf = await (await fetch(`${BASE}data/${file}`, { cache: 'no-store' })).arrayBuffer();
    const image = parseVti(buf);
    show(image, label, performance.now() - start);
  }

  ui.dataset.onchange = () => loadUrl(ui.dataset.value, ui.dataset.selectedOptions[0].text);
  ui.preset.onchange = () => { viewer.applyPreset(ui.preset.value); tools.presetChanged(); };
  ui.opacity.oninput = () => { ui.opacityOut.textContent = (+ui.opacity.value).toFixed(1); viewer.applyPreset(ui.preset.value, +ui.opacity.value); tools.presetChanged(); };
  ui.sample.oninput = () => { ui.sampleOut.textContent = (+ui.sample.value).toFixed(1); viewer.setSampleFactor(+ui.sample.value); };
  ui.shade.onchange = () => viewer.setShade(ui.shade.checked);
  ui.volVis.onchange = () => viewer.setVolumeVisible(ui.volVis.checked);
  ui.sliceVis.onchange = () => viewer.setSliceVisible(ui.sliceVis.checked);
  ui.axis.onchange = () => { viewer.setSliceAxis(ui.axis.value); syncSlice(); viewer.setSliceIndex(+ui.sliceIdx.value); };
  ui.sliceIdx.oninput = () => {
    ui.sliceOut.textContent = ui.sliceIdx.value;
    if (!ui.sliceVis.checked) { ui.sliceVis.checked = true; viewer.setSliceVisible(true); }
    viewer.setSliceIndex(+ui.sliceIdx.value);
  };
  ui.reset.onclick = () => viewer.resetCamera();

  // drag-and-drop a local .vti
  for (const ev of ['dragover', 'dragenter']) {
    window.addEventListener(ev, (e) => { e.preventDefault(); ui.drop.classList.add('over'); });
  }
  window.addEventListener('dragleave', () => ui.drop.classList.remove('over'));
  window.addEventListener('drop', async (e) => {
    e.preventDefault();
    ui.drop.classList.remove('over');
    const f = e.dataTransfer.files[0];
    if (!f) return;
    if (MESH_EXT.includes(extOf(f.name))) { tools.loadMesh(f); return; }
    try {
      const start = performance.now();
      show(parseVti(await f.arrayBuffer()), f.name, performance.now() - start);
    } catch (err) {
      ui.drop.textContent = `could not parse ${f.name}: ${err.message}`;
    }
  });

  const initial = datasets.find((d) => d.name === 'foot') || datasets[0];
  ui.dataset.value = initial.file;
  await loadUrl(initial.file, initial.name);
}

main().catch((e) => {
  console.error(e);
  root.insertAdjacentHTML('beforeend', `<pre style="color:#f66;padding:1em">${e.stack || e}</pre>`);
});
