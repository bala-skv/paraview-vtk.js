// Mesh loading: .vtp / .stl / .obj via file picker, drag-and-drop (routed from main.js) or the bundled sample.
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkXMLPolyDataReader from '@kitware/vtk.js/IO/XML/XMLPolyDataReader';
import vtkSTLReader from '@kitware/vtk.js/IO/Geometry/STLReader';
import vtkOBJReader from '@kitware/vtk.js/IO/Misc/OBJReader';

const BASE = import.meta.env.BASE_URL;
export const MESH_EXT = ['vtp', 'stl', 'obj'];
export const extOf = (name) => name.split('.').pop().toLowerCase();

// Returns vtkPolyData parsed from an ArrayBuffer according to the file extension.
export function parseMesh(name, buf) {
  const ext = extOf(name);
  if (ext === 'obj') {
    const r = vtkOBJReader.newInstance();
    r.parseAsText(new TextDecoder().decode(buf));
    return r.getOutputData(0);
  }
  const r = ext === 'stl' ? vtkSTLReader.newInstance() : vtkXMLPolyDataReader.newInstance();
  r.parseAsArrayBuffer(buf);
  return r.getOutputData(0);
}

export function initMesh(body, viewer, ui, getImage) {
  const f = document.createElement('fieldset');
  f.innerHTML = `<legend>Mesh</legend>
    <button class="sample">Load sample torus (.obj)</button>
    <label>Open .vtp / .stl / .obj <input class="file" type="file" accept=".vtp,.stl,.obj" /></label>
    <label class="row"><input class="vis" type="checkbox" checked /> Show meshes</label>
    <small>or drop a mesh file anywhere on the page</small>
    <output class="res">-</output>`;
  body.appendChild(f);
  const $ = (s) => f.querySelector(s);
  const actors = [];

  function addMesh(name, poly) {
    const mapper = vtkMapper.newInstance({ scalarVisibility: false });
    mapper.setInputData(poly);
    const actor = vtkActor.newInstance();
    actor.setMapper(mapper);
    actor.getProperty().setColor(0.3, 0.7, 1);
    actor.setVisibility($('.vis').checked);
    viewer.renderer.addActor(actor);
    actors.push(actor);
    const b = poly.getBounds().map((x) => x.toFixed(0));
    $('.res').textContent = `${name}: ${poly.getNumberOfPoints().toLocaleString()} points, ${poly.getPolys().getNumberOfCells().toLocaleString()} polys\nbounds ${b.join(' ')}`;
    viewer.renderWindow.render();
  }

  async function loadFile(file) {
    try { addMesh(file.name, parseMesh(file.name, await file.arrayBuffer())); } catch (e) { $('.res').textContent = `could not parse ${file.name}: ${e.message}`; }
  }

  $('.sample').onclick = async () => {
    const buf = await (await fetch(`${BASE}mesh/sample_torus.obj`)).arrayBuffer();
    addMesh('sample_torus.obj', parseMesh('sample_torus.obj', buf));
  };
  $('.file').onchange = (e) => { if (e.target.files[0]) loadFile(e.target.files[0]); };
  $('.vis').onchange = (e) => { actors.forEach((a) => a.setVisibility(e.target.checked)); viewer.renderWindow.render(); };
  return { actors: () => actors, loadFile, setImage() {} };
}
