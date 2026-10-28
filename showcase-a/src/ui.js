import { PRESET_NAMES } from './presets';

const h = (html) => {
  const t = document.createElement('template');
  t.innerHTML = html.trim();
  return t.content.firstChild;
};

// Builds the 280 px control panel and returns element refs. Wiring lives in main.js.
export function buildPanel(root, datasets) {
  const panel = h(`
    <aside id="panel">
      <h1>vtk.js volume viewer</h1>
      <label>Dataset
        <select id="dataset">${datasets.map((d) => `<option value="${d.file}">${d.name}</option>`).join('')}</select>
      </label>
      <div id="drop">or drop a local .vti file here</div>
      <label>Preset
        <select id="preset">${PRESET_NAMES.map((n) => `<option>${n}</option>`).join('')}</select>
      </label>
      <label>Opacity scale <output id="opacityOut">1.0</output>
        <input id="opacity" type="range" min="0.1" max="3" step="0.1" value="1" />
      </label>
      <label>Sample distance <output id="sampleOut">1.0</output>
        <input id="sample" type="range" min="0.5" max="2" step="0.1" value="1" />
        <small>low = quality, high = speed</small>
      </label>
      <label class="row"><input id="shade" type="checkbox" checked /> Shading</label>
      <label class="row"><input id="volVis" type="checkbox" checked /> Show volume</label>
      <fieldset>
        <legend>Slice</legend>
        <label class="row"><input id="sliceVis" type="checkbox" /> Show slice</label>
        <label>Axis
          <select id="axis"><option>K</option><option>J</option><option>I</option></select>
        </label>
        <label>Index <output id="sliceOut">0</output>
          <input id="sliceIdx" type="range" min="0" max="0" step="1" value="0" />
        </label>
      </fieldset>
      <button id="reset">Reset camera</button>
      <details id="tools"><summary>Tools</summary><div id="toolsBody"></div></details>
      <dl id="info"></dl>
    </aside>`);
  root.appendChild(panel);
  const $ = (id) => panel.querySelector(`#${id}`);
  return {
    panel, dataset: $('dataset'), drop: $('drop'), preset: $('preset'),
    opacity: $('opacity'), opacityOut: $('opacityOut'), sample: $('sample'), sampleOut: $('sampleOut'),
    shade: $('shade'), volVis: $('volVis'), sliceVis: $('sliceVis'), axis: $('axis'),
    sliceIdx: $('sliceIdx'), sliceOut: $('sliceOut'), reset: $('reset'), tools: $('toolsBody'), info: $('info'),
  };
}

export function showInfo(ui, rows) {
  ui.info.innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
}
