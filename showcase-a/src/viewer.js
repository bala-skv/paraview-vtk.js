import '@kitware/vtk.js/Rendering/Profiles/Volume';
import vtkFullScreenRenderWindow from '@kitware/vtk.js/Rendering/Misc/FullScreenRenderWindow';
import vtkVolume from '@kitware/vtk.js/Rendering/Core/Volume';
import vtkVolumeMapper from '@kitware/vtk.js/Rendering/Core/VolumeMapper';
import vtkImageSlice from '@kitware/vtk.js/Rendering/Core/ImageSlice';
import vtkImageMapper from '@kitware/vtk.js/Rendering/Core/ImageMapper';
import vtkColorTransferFunction from '@kitware/vtk.js/Rendering/Core/ColorTransferFunction';
import vtkPiecewiseFunction from '@kitware/vtk.js/Common/DataModel/PiecewiseFunction';
import vtkXMLImageDataReader from '@kitware/vtk.js/IO/XML/XMLImageDataReader';
import vtkFPSMonitor from '@kitware/vtk.js/Interaction/UI/FPSMonitor';
import { PRESETS } from './presets';

// ImageMapper slicing modes: I = 0 (x), J = 1 (y), K = 2 (z)
const AXES = { I: 0, J: 1, K: 2 };

export function parseVti(arrayBuffer) {
  const reader = vtkXMLImageDataReader.newInstance();
  reader.parseAsArrayBuffer(arrayBuffer);
  return reader.getOutputData(0);
}

// api: undefined = default WebGL2 view, 'WebGPU' = experimental WebGPU view (see tools/webgpu.js)
export function createViewer(container, { fps = false, api } = {}) {
  const fsrw = vtkFullScreenRenderWindow.newInstance({
    ...(api ? { defaultViewAPI: api } : {}),
    rootContainer: container,
    containerStyle: { position: 'absolute', inset: '0' },
    background: [0.08, 0.08, 0.12],
  });
  const renderer = fsrw.getRenderer();
  const renderWindow = fsrw.getRenderWindow();

  const ctf = vtkColorTransferFunction.newInstance();
  const ofun = vtkPiecewiseFunction.newInstance();

  const volMapper = vtkVolumeMapper.newInstance();
  volMapper.setAutoAdjustSampleDistances(false);
  const volume = vtkVolume.newInstance();
  volume.setMapper(volMapper);
  const prop = volume.getProperty();
  prop.setRGBTransferFunction(0, ctf);
  prop.setScalarOpacity(0, ofun);
  prop.setInterpolationTypeToLinear();
  prop.setShade(true);
  prop.setAmbient(0.2);
  prop.setDiffuse(0.7);
  prop.setSpecular(0.3);

  const sliceMapper = vtkImageMapper.newInstance();
  const slice = vtkImageSlice.newInstance();
  slice.setMapper(sliceMapper);
  slice.getProperty().setRGBTransferFunction(0, ctf);
  slice.getProperty().setInterpolationTypeToLinear();
  slice.setVisibility(false);

  renderer.addVolume(volume);
  renderer.addActor(slice);

  let fpsMonitor = null;
  if (fps) {
    fpsMonitor = vtkFPSMonitor.newInstance();
    fpsMonitor.setContainer(container);
    fpsMonitor.setRenderWindow(renderWindow);
  }

  const state = { image: null, range: [0, 1], spacingMean: 1, preset: 'Bone', opacityScale: 1, sampleFactor: 1 };

  function applyPreset(name = state.preset, opacityScale = state.opacityScale) {
    const p = PRESETS[name];
    if (!p) throw new Error(`unknown preset ${name}`);
    state.preset = name;
    state.opacityScale = opacityScale;
    const [lo, hi] = state.range;
    const at = (x) => lo + x * (hi - lo);
    ctf.removeAllPoints();
    p.color.forEach(([x, r, g, b]) => ctf.addRGBPoint(at(x), r, g, b));
    ofun.removeAllPoints();
    p.opacity.forEach(([x, a]) => ofun.addPoint(at(x), Math.min(1, a * opacityScale)));
    renderWindow.render();
  }

  function setSampleFactor(f) {
    state.sampleFactor = f;
    volMapper.setSampleDistance(state.spacingMean * f);
    renderWindow.render();
  }

  function setImage(image) {
    state.image = image;
    state.range = image.getPointData().getScalars().getRange();
    const sp = image.getSpacing();
    state.spacingMean = (sp[0] + sp[1] + sp[2]) / 3;
    volMapper.setInputData(image);
    sliceMapper.setInputData(image);
    prop.setScalarOpacityUnitDistance(0, state.spacingMean);
    volMapper.setSampleDistance(state.spacingMean * state.sampleFactor);
    applyPreset();
    setSliceAxis('K');
    renderer.resetCamera();
    renderWindow.render();
  }

  function sliceCount(axis) {
    return state.image ? state.image.getDimensions()[AXES[axis]] : 1;
  }

  function setSliceAxis(axis) {
    sliceMapper.setSlicingMode(AXES[axis]);
    sliceMapper.setSlice(Math.floor(sliceCount(axis) / 2));
    renderWindow.render();
  }

  function setSliceIndex(i) {
    sliceMapper.setSlice(i);
    renderWindow.render();
  }

  function setShade(on) { prop.setShade(on); renderWindow.render(); }
  function setVolumeVisible(on) { volume.setVisibility(on); renderWindow.render(); }
  function setSliceVisible(on) { slice.setVisibility(on); renderWindow.render(); }
  function resetCamera() { renderer.resetCamera(); renderWindow.render(); }

  function glRenderer() {
    try {
      const info = fsrw.getApiSpecificRenderWindow().getGLInformations();
      return info.UNMASKED_RENDERER?.value || info.RENDERER?.value || 'unknown';
    } catch {
      return 'unknown';
    }
  }

  return {
    fsrw, renderer, renderWindow, fpsMonitor, volume, volMapper, slice, ctf, ofun,
    getState: () => state,
    setImage, applyPreset, setSampleFactor, setShade, setVolumeVisible, setSliceVisible,
    setSliceAxis, setSliceIndex, sliceCount, resetCamera, glRenderer,
  };
}
