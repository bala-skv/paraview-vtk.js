// M0 smoke test: render a cone with vtk.js. Replaced by the real app in M2.
import '@kitware/vtk.js/Rendering/Profiles/Geometry';
import vtkFullScreenRenderWindow from '@kitware/vtk.js/Rendering/Misc/FullScreenRenderWindow';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkConeSource from '@kitware/vtk.js/Filters/Sources/ConeSource';

const fsrw = vtkFullScreenRenderWindow.newInstance({
  rootContainer: document.getElementById('app'),
  background: [0.1, 0.1, 0.15],
});
const cone = vtkConeSource.newInstance({ height: 1.0, resolution: 48 });
const mapper = vtkMapper.newInstance();
mapper.setInputConnection(cone.getOutputPort());
const actor = vtkActor.newInstance();
actor.setMapper(mapper);
fsrw.getRenderer().addActor(actor);
fsrw.getRenderer().resetCamera();
fsrw.getRenderWindow().render();
