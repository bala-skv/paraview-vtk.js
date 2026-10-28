# Showcase A feature log (Stream A, 2026-10-28)

Scope: vtk.js 37.4.6 (pinned, unchanged; no new npm dependencies). All new UI sits in a collapsible "Tools" section
of the control panel (`showcase-a/src/ui.js` creates the `<details id="tools">`; the fieldsets are built in
`showcase-a/src/tools/`). The dev screenshots in `report/figures/feat_a_*.png` were taken with headless Chrome
(puppeteer-core) on software GL (SwiftShader) with the `foot_64` dataset, so they show correctness only, not speed.
Minutes are approximate wall-clock including testing. Every API was checked against
`showcase-a/node_modules/@kitware/vtk.js` before use.

Files added: `src/tools/index.js`, `src/tools/mesh.js`, `src/tools/webgpu.js`, `gen_sample_mesh.mjs`,
`public/mesh/sample_torus.obj` (125 KB generated torus, 2304 triangles). Files changed: `src/viewer.js` (exports
`volume, volMapper, slice, ctf, ofun`; optional `api` argument), `src/ui.js` (Tools container), `src/main.js` (wiring,
mesh drop routing, `?api=webgpu`), `index.html` (CSS for Tools). `src/bench.js` is untouched and calls
`createViewer(container)` with the same arguments as before.

| # | Feature | Status | Min |
|---|---|---|---|
| 1 | Isosurface | works | 15 |
| 2 | Three orthogonal slices | works | 8 |
| 3 | Probe (IJK + value) | works | 8 |
| 4 | Clipping | works | 8 |
| 5 | Scalar bar + orientation axes | works | 6 |
| 6 | Transfer-function editor | works | 8 |
| 7 | Mesh loading | works (.obj tested; .vtp/.stl not tested) | 8 |
| 8 | Distance line + screenshot export | works | 15 |
| 9 | WebGPU probe | partial | 20 |

## 1. Isosurface
- Status: works.
- Modules: `Filters/General/ImageMarchingCubes` (`contourValue`, `computeNormals`, `mergePoints`), `Rendering/Core/Mapper`, `Rendering/Core/Actor`.
- Use: Tools > Isosurface > "Show isosurface"; the slider range follows the dataset scalar range; the surface is recomputed on slider release (`change`). The result line shows triangle count and compute time.
- Observed: foot_64 at value 102 gave 26,032 triangles in 63 ms; value 60 gave 40,296 triangles in 37 ms. The filter runs on the main thread (a JS triple loop over all voxels), so 256^3 volumes block the page while it runs; not timed on 256^3. The mapper is connected to the filter on first use, because an input-less mapper logs "No input" errors under the WebGPU view.
- Screenshot: `report/figures/feat_a_isosurface.png` (volume hidden, surface only; software GL dev shot).

## 2. Three orthogonal slices
- Status: works.
- Modules: `Rendering/Core/ImageSlice`, `Rendering/Core/ImageMapper` (slicing modes I/J/K), shared `vtkColorTransferFunction`.
- Use: Tools > Orthogonal slices > "Show I / J / K slices"; three sliders. Enabling it rotates the camera (azimuth 35, elevation 25) so the planes can be told apart.
- Observed: the slices use the preset colour function without opacity, so a black background value is opaque and hides the volume behind the planes (same behaviour as the existing single slice). The existing "Slice" fieldset is unchanged.
- Screenshot: `report/figures/feat_a_mpr.png`.

## 3. Probe
- Status: works.
- Modules: `Rendering/Core/CellPicker` (`pickFromList`, `getPickedPositions`), `Filters/Sources/SphereSource` for the marker, `image.worldToIndex`.
- Use: Tools > Probe > "Click to probe", then click the 3D view; the panel shows world position, IJK and the voxel value. A click that moves more than 3 px is treated as a camera drag and ignored.
- Observed: picks the visible slices, isosurface, meshes and the volume (the volume is picked through its opacity function, `opacityThreshold` 0.2). Test on foot_64 returned world (127.5, 127.5, 147.7), IJK (32, 32, 37), value 198. The value is the nearest voxel (rounded IJK), not interpolated. Picks outside the image report "outside image".
- Screenshot: `report/figures/feat_a_probe.png`.

## 4. Clipping
- Status: works.
- Modules: `Common/DataModel/Plane`, `addClippingPlane` / `removeAllClippingPlanes` (`Rendering/Core/AbstractMapper`) on the volume mapper and the isosurface mapper.
- Use: Tools > Clipping > "Clip volume and isosurface"; min/max sliders per axis in percent of the image bounds. Six planes are always used; the shader keeps the half-space the normal points to.
- Observed: the OpenGL volume shader supports at most 6 clipping planes (`vClipPlaneNormals[6]`), which is exactly what is used. Not using `vtkImageCroppingWidget`; plain planes were simpler. Mesh actors and slices are not clipped.
- Screenshot: `report/figures/feat_a_clip.png` (I min 45 %, K max 60 %).

## 5. Scalar bar and orientation axes
- Status: works.
- Modules: `Rendering/Core/ScalarBarActor` (bound to the colour transfer function, NaN annotation off), `Interaction/Widgets/OrientationMarkerWidget` with `Rendering/Core/AxesActor`.
- Use: Tools > Legend and axes, two checkboxes.
- Observed: needed the `Rendering/Profiles/Geometry` import (the Volume profile alone does not register the geometry classes the scalar bar needs). The bar shows the colour function, not opacity.
- Screenshot: `report/figures/feat_a_legend_axes.png`.

## 6. Transfer-function editor
- Status: works.
- Modules: `Interaction/Widgets/PiecewiseGaussianWidget` (histogram from the scalar array, `applyOpacity` into the volume's piecewise function).
- Use: Tools > Transfer function editor > tick "Edit opacity"; drag the Gaussian handles, click the plot to add one, right-click a handle to remove it.
- Observed: while enabled it overrides the preset opacity; changing the preset or the "Opacity scale" slider unticks it (the preset code rewrites the same piecewise function). Only opacity is edited; colour still comes from the preset. The histogram is computed from the full scalar array on each dataset load. A drag via puppeteer moved the Gaussian and the volume re-rendered.
- Screenshot: `report/figures/feat_a_tf_editor_dragged.png`.

## 7. Mesh loading
- Status: works for `.obj` (tested through the sample button); `.vtp` and `.stl` code paths use `XMLPolyDataReader` and `STLReader` but were not exercised with files.
- Modules: `IO/Misc/OBJReader`, `IO/Geometry/STLReader`, `IO/XML/XMLPolyDataReader`.
- Use: Tools > Mesh > "Load sample torus (.obj)", the file input, or drop a `.vtp/.stl/.obj` file on the page (main.js routes by extension; `.vti` drops behave as before).
- Observed: meshes are shown in world coordinates and the camera is not reset, so a mesh far from the volume may be off screen. The sample is generated by `node gen_sample_mesh.mjs` and sits in the middle of the 256^3 sample volumes. The loaded mesh is not removed by loading another; the "Show meshes" checkbox hides all of them.
- Screenshot: `report/figures/feat_a_mesh.png`.

## 8. Distance measurement and screenshot export
- Status: works.
- Modules: `Widgets/Widgets3D/LineWidget` (`getDistance`), `Widgets/Core/WidgetManager` (`ViewTypes.VOLUME`, `grabFocus`), `Widgets/Manipulators/PlaneManipulator`; export uses `getApiSpecificRenderWindow().captureNextImage('image/png')`.
- Use: Tools > Measure and export > "Distance line", click two points in the 3D view; the distance is shown in world units and updates when a handle is dragged. "Save screenshot (PNG)" downloads `vtkjs_viewer.png`.
- Observed: the points are placed on a camera-facing plane through the image centre (`setWidgetOrigin`), not on a surface or voxel, so the distance is a plane measurement. Unticking removes the widget. Test distance 83.74 on foot_64. The export produced a PNG data URL of about 1.2 MB (checked by intercepting the anchor click; the file itself was not opened). The first test failed because `widget.reset` is on the view widget (`handle.reset`), fixed.
- Screenshot: `report/figures/feat_a_measure.png`.

## 9. WebGPU probe
- Status: partial.
- Modules: `Rendering/Profiles/Volume` already imports the WebGPU volume, image-slice and geometry classes; `FullScreenRenderWindow` selects the view through its `defaultViewAPI` initial value (the `viewAPI` URL parameter also works there, the `viewAPI` initial value does not).
- Use: open `?api=webgpu`. `src/tools/webgpu.js` queries `navigator.gpu` and the adapter, and adds a "WebGPU" row to the info list. The default page (no parameter) is unchanged.
- Observed: in headless Chrome with `--enable-unsafe-webgpu` the adapter reported "google / swiftshader" (software). With the WebGPU view active on the 256^3 foot, the console showed "No input!" errors and the tab then closed ("Target closed") during the test, so no WebGPU render was obtained and no screenshot is provided. Not tested on a real GPU. Not run: side-by-side check of which vtk.js classes lack a WebGPU implementation. `getGLInformations` (used for the "WebGL renderer" row) is undefined under the WebGPU view and falls back to "unknown".
- Screenshot: none.

## Not done
- `vtkImageCroppingWidget` (box cropping); plane sliders were used instead.
- `.vtp` / `.stl` sample files and a test of those readers.
- Timing of the isosurface on 256^3 volumes and the WebGPU render path on a real GPU.
