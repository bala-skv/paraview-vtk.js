// "Tools" section of the control panel: extra vtk.js features layered on the base viewer.
// Each init* function builds one fieldset and returns { setImage(image) }; setImage is
// called by main.js whenever a new dataset is shown.
import '@kitware/vtk.js/Rendering/Profiles/Geometry';
import '@kitware/vtk.js/Rendering/Profiles/Glyph';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkImageSlice from '@kitware/vtk.js/Rendering/Core/ImageSlice';
import vtkImageMapper from '@kitware/vtk.js/Rendering/Core/ImageMapper';
import vtkCellPicker from '@kitware/vtk.js/Rendering/Core/CellPicker';
import vtkScalarBarActor from '@kitware/vtk.js/Rendering/Core/ScalarBarActor';
import vtkAxesActor from '@kitware/vtk.js/Rendering/Core/AxesActor';
import vtkSphereSource from '@kitware/vtk.js/Filters/Sources/SphereSource';
import vtkOrientationMarkerWidget from '@kitware/vtk.js/Interaction/Widgets/OrientationMarkerWidget';
import vtkPiecewiseGaussianWidget from '@kitware/vtk.js/Interaction/Widgets/PiecewiseGaussianWidget';
import vtkImageMarchingCubes from '@kitware/vtk.js/Filters/General/ImageMarchingCubes';
import vtkPlane from '@kitware/vtk.js/Common/DataModel/Plane';
import vtkWidgetManager from '@kitware/vtk.js/Widgets/Core/WidgetManager';
import vtkLineWidget from '@kitware/vtk.js/Widgets/Widgets3D/LineWidget';
import vtkPlaneManipulator from '@kitware/vtk.js/Widgets/Manipulators/PlaneManipulator';
import { ViewTypes } from '@kitware/vtk.js/Widgets/Core/WidgetManager/Constants';
import { initMesh } from './mesh';

const h = (html) => {
  const t = document.createElement('template');
  t.innerHTML = html.trim();
  return t.content.firstChild;
};

function fieldset(body, title, html) {
  const el = h(`<fieldset><legend>${title}</legend>${html}</fieldset>`);
  body.appendChild(el);
  return { el, $: (sel) => el.querySelector(sel) };
}

const FULL = { I: 0, J: 1, K: 2 };

export function initTools(viewer, body, ui) {
  const { renderer, renderWindow, ctf, ofun, volume, volMapper } = viewer;
  const render = () => renderWindow.render();
  let image = null;
  const parts = [];
  const add = (p) => { parts.push(p); return p; };

  // ---- 1. isosurface (vtkImageMarchingCubes) ----
  const iso = (() => {
    const f = fieldset(body, 'Isosurface', `
      <label class="row"><input class="on" type="checkbox" /> Show isosurface</label>
      <label>Iso value <output class="val">0</output>
        <input class="v" type="range" min="0" max="255" step="1" value="100" /></label>
      <output class="res"></output>`);
    const mc = vtkImageMarchingCubes.newInstance({ contourValue: 100, computeNormals: true, mergePoints: true });
    const mapper = vtkMapper.newInstance({ scalarVisibility: false });
    let connected = false; // connected on first use: an input-less mapper logs errors under the WebGPU view
    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.getProperty().setColor(0.9, 0.75, 0.55);
    actor.setVisibility(false);
    renderer.addActor(actor);
    const v = f.$('.v'); const on = f.$('.on'); const res = f.$('.res');

    function recompute() {
      if (!image) return;
      const t = performance.now();
      mc.setContourValue(+v.value);
      mc.setInputData(image);
      if (!connected) { mapper.setInputConnection(mc.getOutputPort()); connected = true; }
      mc.update();
      const tris = mc.getOutputData().getPolys().getNumberOfCells();
      res.textContent = `${tris.toLocaleString()} triangles, ${(performance.now() - t).toFixed(0)} ms`;
      render();
    }
    v.oninput = () => { f.$('.val').textContent = v.value; };
    v.onchange = () => { if (on.checked) recompute(); };
    on.onchange = () => { actor.setVisibility(on.checked); if (on.checked) recompute(); else render(); };
    return {
      actor,
      setImage(im) {
        const [lo, hi] = im.getPointData().getScalars().getRange();
        v.min = Math.floor(lo); v.max = Math.ceil(hi);
        v.value = Math.round(lo + 0.4 * (hi - lo));
        f.$('.val').textContent = v.value;
        if (on.checked) recompute();
      },
      recompute,
    };
  })();
  add(iso);

  // ---- 2. three orthogonal slices (MPR-style) ----
  const mpr = (() => {
    const f = fieldset(body, 'Orthogonal slices', `
      <label class="row"><input class="on" type="checkbox" /> Show I / J / K slices</label>
      ${['I', 'J', 'K'].map((a) => `<label>${a} <output class="o${a}">0</output>
        <input class="s${a}" type="range" min="0" max="0" step="1" value="0" /></label>`).join('')}`);
    const slices = {};
    for (const a of ['I', 'J', 'K']) {
      const m = vtkImageMapper.newInstance();
      m.setSlicingMode(FULL[a]);
      const s = vtkImageSlice.newInstance();
      s.setMapper(m);
      s.getProperty().setRGBTransferFunction(0, ctf);
      s.setVisibility(false);
      renderer.addActor(s);
      slices[a] = { m, s };
      const r = f.$(`.s${a}`);
      r.oninput = () => { m.setSlice(+r.value); f.$(`.o${a}`).textContent = r.value; render(); };
    }
    f.$('.on').onchange = (e) => {
      for (const a in slices) slices[a].s.setVisibility(e.target.checked);
      if (e.target.checked) { // oblique view so the three planes are distinguishable
        const cam = renderer.getActiveCamera();
        cam.azimuth(35); cam.elevation(25); cam.orthogonalizeViewUp();
        renderer.resetCameraClippingRange();
      }
      render();
    };
    return {
      actors: () => Object.values(slices).map((x) => x.s),
      setImage(im) {
        const d = im.getDimensions();
        for (const a in slices) {
          const n = d[FULL[a]];
          const r = f.$(`.s${a}`);
          slices[a].m.setInputData(im);
          r.max = n - 1; r.value = Math.floor(n / 2);
          slices[a].m.setSlice(+r.value);
          f.$(`.o${a}`).textContent = r.value;
        }
      },
    };
  })();
  add(mpr);

  // ---- 3. probe: click shows world position, IJK and voxel value ----
  const probe = (() => {
    const f = fieldset(body, 'Probe', `
      <label class="row"><input class="on" type="checkbox" /> Click to probe</label>
      <small>picks slices, isosurface, meshes and the volume</small>
      <output class="res">-</output>`);
    const picker = vtkCellPicker.newInstance();
    picker.setPickFromList(true);
    picker.setTolerance(0.005);
    const marker = vtkActor.newInstance();
    const sph = vtkSphereSource.newInstance({ radius: 2, thetaResolution: 12, phiResolution: 12 });
    const mm = vtkMapper.newInstance();
    mm.setInputConnection(sph.getOutputPort());
    marker.setMapper(mm);
    marker.getProperty().setColor(1, 0.1, 0.1);
    marker.setVisibility(false);
    renderer.addActor(marker);
    const on = f.$('.on'); const res = f.$('.res');
    let down = null;
    const inter = renderWindow.getInteractor();
    inter.onLeftButtonPress((e) => { down = e.position; });
    inter.onLeftButtonRelease((e) => {
      if (!on.checked || !down || !image) return;
      const moved = Math.hypot(e.position.x - down.x, e.position.y - down.y);
      down = null;
      if (moved > 3) return; // was a camera drag
      const list = [...mpr.actors(), iso.actor, viewer.slice, volume, ...(meshActors())].filter((a) => a.getVisibility());
      picker.initializePickList();
      list.forEach((a) => picker.addPickList(a));
      picker.pick([e.position.x, e.position.y, 0], renderer);
      const pos = picker.getPickedPositions()[0];
      if (!pos) { res.textContent = 'no hit'; marker.setVisibility(false); render(); return; }
      const ijk = image.worldToIndex(pos).map(Math.round);
      const d = image.getDimensions();
      const inside = ijk.every((c, i) => c >= 0 && c < d[i]);
      const val = inside ? image.getPointData().getScalars().getData()[ijk[0] + ijk[1] * d[0] + ijk[2] * d[0] * d[1]] : null;
      res.textContent = `world ${pos.map((x) => x.toFixed(1)).join(', ')}\nIJK ${ijk.join(', ')}\nvalue ${val === null ? 'outside image' : val}`;
      marker.setPosition(...pos);
      marker.setVisibility(true);
      render();
    });
    on.onchange = () => { if (!on.checked) { marker.setVisibility(false); render(); } };
    return { setImage() { marker.setVisibility(false); } };
  })();
  add(probe);

  // ---- 4. clipping: six axis-aligned planes on the volume and isosurface mappers ----
  const clip = (() => {
    const f = fieldset(body, 'Clipping', `
      <label class="row"><input class="on" type="checkbox" /> Clip volume and isosurface</label>
      ${['I', 'J', 'K'].map((a) => `<label>${a} min / max (%)
        <span style="display:flex;gap:4px"><input class="lo${a}" type="range" min="0" max="100" value="0" style="flex:1;min-width:0" />
        <input class="hi${a}" type="range" min="0" max="100" value="100" style="flex:1;min-width:0" /></span></label>`).join('')}`);
    const planes = [];
    const on = f.$('.on');
    for (let a = 0; a < 3; a++) for (const sign of [1, -1]) planes.push(vtkPlane.newInstance({ normal: [0, 1, 2].map((i) => (i === a ? sign : 0)) }));
    const isoMapper = iso.actor.getMapper();
    function apply() {
      volMapper.removeAllClippingPlanes();
      isoMapper.removeAllClippingPlanes();
      if (on.checked && image) {
        const b = image.getBounds();
        ['I', 'J', 'K'].forEach((a, i) => {
          const lo = b[2 * i] + (b[2 * i + 1] - b[2 * i]) * (+f.$(`.lo${a}`).value / 100);
          const hi = b[2 * i] + (b[2 * i + 1] - b[2 * i]) * (+f.$(`.hi${a}`).value / 100);
          const o = [0, 0, 0];
          o[i] = lo; planes[2 * i].setOrigin(o);
          const o2 = [0, 0, 0];
          o2[i] = hi; planes[2 * i + 1].setOrigin(o2);
        });
        planes.forEach((p) => { volMapper.addClippingPlane(p); isoMapper.addClippingPlane(p); });
      }
      render();
    }
    f.el.querySelectorAll('input').forEach((i) => { i.oninput = apply; i.onchange = apply; });
    return { setImage: apply };
  })();
  add(clip);

  // ---- 5. scalar bar + orientation axes ----
  const decor = (() => {
    const f = fieldset(body, 'Legend and axes', `
      <label class="row"><input class="bar" type="checkbox" /> Scalar bar</label>
      <label class="row"><input class="axes" type="checkbox" /> Orientation axes</label>`);
    const bar = vtkScalarBarActor.newInstance();
    bar.setScalarsToColors(ctf);
    bar.setAxisLabel('Intensity');
    bar.setDrawNanAnnotation(false);
    bar.setVisibility(false);
    renderer.addActor(bar);
    const marker = vtkOrientationMarkerWidget.newInstance({
      actor: vtkAxesActor.newInstance(),
      interactor: renderWindow.getInteractor(),
    });
    marker.setViewportCorner(vtkOrientationMarkerWidget.Corners.BOTTOM_RIGHT);
    marker.setViewportSize(0.15);
    marker.setMinPixelSize(60);
    marker.setMaxPixelSize(200);
    f.$('.bar').onchange = (e) => { bar.setVisibility(e.target.checked); render(); };
    f.$('.axes').onchange = (e) => { marker.setEnabled(e.target.checked); render(); };
    return { setImage() { bar.modified(); } };
  })();
  add(decor);

  // ---- 6. transfer-function editor (vtkPiecewiseGaussianWidget) ----
  const tf = (() => {
    const f = fieldset(body, 'Transfer function editor', `
      <label class="row"><input class="on" type="checkbox" /> Edit opacity (overrides preset opacity)</label>
      <div class="host"></div>
      <small>drag to move, click the plot to add, right-click a handle to remove</small>`);
    const widget = vtkPiecewiseGaussianWidget.newInstance({ numberOfBins: 256, size: [240, 120] });
    widget.updateStyle({ backgroundColor: 'rgba(32,32,48,1)', histogramColor: 'rgba(120,120,160,0.6)', strokeColor: 'rgb(200,200,255)', activeColor: 'rgb(255,255,255)', handleColor: 'rgb(80,160,255)', buttonDisableFillColor: 'rgba(255,255,255,0.5)', buttonDisableStrokeColor: 'rgba(0,0,0,0.5)', buttonStrokeColor: 'rgba(0,0,0,1)', buttonFillColor: 'rgba(255,255,255,1)', strokeWidth: 2, activeStrokeWidth: 3, buttonStrokeWidth: 1.5, handleWidth: 3, iconSize: 0, padding: 10 });
    widget.setContainer(f.$('.host'));
    widget.setColorTransferFunction(ctf);
    widget.addGaussian(0.7, 0.8, 0.2, 0, 0);
    widget.bindMouseListeners();
    const on = f.$('.on');
    const apply = () => {
      if (!on.checked || !image) return;
      widget.applyOpacity(ofun, image.getPointData().getScalars().getRange());
      widget.setColorTransferFunction(ctf);
      render();
    };
    widget.onOpacityChange(apply);
    on.onchange = () => { apply(); };
    return {
      setImage(im) {
        widget.setDataArray(im.getPointData().getScalars().getData(), { numberOfBinsToSkip: 1 });
        widget.render();
        apply();
      },
      // a preset replaces the opacity points, so the editor hands control back
      presetChanged() { on.checked = false; widget.render(); },
    };
  })();
  add(tf);

  // ---- 7. mesh loading (.vtp / .stl / .obj) ----
  const mesh = initMesh(body, viewer, ui, () => image);
  const meshActors = () => mesh.actors();
  add(mesh);

  // ---- 8. distance measurement (vtkLineWidget) + screenshot ----
  const measure = (() => {
    const f = fieldset(body, 'Measure and export', `
      <label class="row"><input class="on" type="checkbox" /> Distance line (click two points)</label>
      <output class="res">-</output>
      <button class="shot">Save screenshot (PNG)</button>`);
    const wm = vtkWidgetManager.newInstance();
    wm.setRenderer(renderer);
    const widget = vtkLineWidget.newInstance();
    const man = vtkPlaneManipulator.newInstance({ useCameraNormal: true });
    widget.setManipulator(man);
    const res = f.$('.res');
    let handle = null;
    const show = () => { res.textContent = `${widget.getDistance().toFixed(2)} world units`; };
    const on = f.$('.on');
    on.onchange = () => {
      if (on.checked) {
        if (image) man.setWidgetOrigin(image.getCenter());
        if (!handle) {
          handle = wm.addWidget(widget, ViewTypes.VOLUME);
          handle.onInteractionEvent(show);
          handle.onEndInteractionEvent(show);
        }
        handle.reset?.();
        wm.grabFocus(widget);
        res.textContent = 'click two points';
      } else if (handle) {
        wm.releaseFocus();
        wm.removeWidget(widget);
        handle = null;
        res.textContent = '-';
      }
      render();
    };
    f.$('.shot').onclick = async () => {
      const pending = viewer.fsrw.getApiSpecificRenderWindow().captureNextImage('image/png');
      renderWindow.render();
      const data = await pending;
      const a = document.createElement('a');
      a.href = data; a.download = 'vtkjs_viewer.png';
      document.body.appendChild(a); a.click(); a.remove();
    };
    return { setImage(im) { man.setWidgetOrigin(im.getCenter()); } };
  })();
  add(measure);

  return {
    setImage(im) { image = im; parts.forEach((p) => p.setImage?.(im)); },
    presetChanged: () => tf.presetChanged(),
    loadMesh: (file) => mesh.loadFile(file),
  };
}
