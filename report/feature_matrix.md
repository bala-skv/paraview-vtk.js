# Feature matrix

[DRAFT - student to review]

Facts only. Opinions and scoring are the student's and are marked `[STUDENT]`. Checked 2026-10-28.

Columns: **vtk.js 37.4.6** (Showcase A) | **ParaView 6.2.0 + trame 4.0.0** via pvpython (Showcase B) | **legacy ParaViewWeb** (Visualizer, Lite, Divvy, ParaViewWeb JS library; see `report/legacy_desk_note.md`).

Cell values: **Demonstrated** (we built it; file linked), **Documented** (supported per a source I checked; path or URL given), **Not supported** (checked and absent), **Unknown** (not verified; marked UNVERIFIED). Counts at the bottom treat Not supported and Unknown as one class.

Path shorthand:
- `VJ/` = `showcase-a/node_modules/@kitware/vtk.js/` (installed 37.4.6; presence of a module is evidence the code ships, not that it is feature-complete).
- `PV/` = `/home/bala/opt/ParaView-6.2.0-MPI-Linux-Python3.12-x86_64/` (checked by listing `lib/`, `plugins/`, and by querying proxy definitions with `bin/pvpython`: 288 filters, 78 representations, 18 view types).
- `TR/` = `.pvenv/lib/python3.12/site-packages/` (trame 4.0.0, trame-client 4.1.4, trame-server 4.1.0, trame-vtk 2.11.17, trame-vuetify 3.3.0, wslink 2.6.0).
- `PVW/` = `PV/lib/python3.12/site-packages/paraview/web/` (Python side of ParaViewWeb, still shipped in 6.2.0).

Legacy column: the Visualizer, Lite and Divvy landing pages (kitware.github.io/visualizer, /paraview-lite, /divvy) list no features, only a tagline and a launch command. The `/docs/` subpages were not read. So legacy UI-level cells are Unknown unless a source below says otherwise. Sources used for the legacy column: L1 = https://kitware.github.io/paraviewweb/docs/ (Overview, read); L2 = `PVW/protocols.py` (class list, read); L3 = https://github.com/Kitware/paraviewweb README (read).

## 1. Rendering

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 1 | Volume rendering | Demonstrated - `showcase-a/src/viewer.js`, `report/figures/a_preset_bone.png` | Demonstrated - server volume option in `showcase-b/app.py` (`Representation = "Volume"`), `report/figures/feat_b_volume.png` (software GL, 64^3 wavelet; `features_b_log.md` section 3) | Unknown (UNVERIFIED); backend is ParaView, UI exposure not read |
| 2 | Isosurface / contour | Demonstrated - `VJ/Filters/General/ImageMarchingCubes.js` in Tools > Isosurface, `report/figures/feat_a_isosurface.png` (foot_64: 26,032 triangles at value 102 in 63 ms; runs on the main thread) | Demonstrated - `showcase-b/app.py` (Contour), `report/figures/b_remote.png` | Unknown (UNVERIFIED) |
| 3 | Orthogonal slice / MPR | Demonstrated - `showcase-a/src/viewer.js` (ImageSlice), `report/figures/a_slice.png`; three slices together (ImageMapper I/J/K), `report/figures/feat_a_mpr.png`; MPR classes `VJ/Interaction/Style/InteractorStyleMPRSlice.js`, `VJ/Widgets/Widgets3D/ResliceCursorWidget` not used | Demonstrated (Slice filter only) - Slice in `showcase-b/app.py`, `report/figures/feat_b_pipeline_selector.png`; `OrthographicSliceView` and `MultiSlice` view types exist in PV proxies, not demonstrated | Unknown (UNVERIFIED) |
| 4 | Arbitrary-plane cutting of geometry | Documented - `VJ/Filters/Core/Cutter.js`, `ImplicitPlaneWidget.js` (not demonstrated; clipping planes are row 16) | Demonstrated - Slice and Clip in the Pipeline drawer of `showcase-b/ui.py`, `report/figures/feat_b_pipeline_selector.png` | Unknown (UNVERIFIED) |
| 5 | Polygonal mesh / surface rendering | Demonstrated - OBJ torus and isosurface drawn with Mapper/Actor, `report/figures/feat_a_mesh.png`, `report/figures/feat_a_isosurface.png` | Demonstrated - contour surface in `showcase-b/app.py` | Documented - WebGL geometry viewers (Three.js), L1 |
| 6 | Threshold / extract by value | Documented - `VJ/Filters/Core/ThresholdPoints.js` (points only; no cell Threshold found) | Demonstrated - Threshold in the Pipeline drawer, `report/figures/feat_b_pipeline_selector.png` | Unknown (UNVERIFIED) |
| 7 | Glyphs | Documented - `VJ/Rendering/Core/Glyph3DMapper`, `VJ/Filters/Sources/ArrowSource.js` | Demonstrated - Glyph (arrow glyphs on a Gradient vector array) in the Pipeline drawer, `report/figures/feat_b_pipeline_selector.png` | Unknown (UNVERIFIED) |
| 8 | Streamlines / stream tracing | Documented - `VJ/Filters/General/ImageStreamline.js` (image data input; other dataset types not found) | Demonstrated - StreamTracer (150 point-cloud seeds) in the Pipeline drawer, `report/figures/feat_b_streamlines.png` | Unknown (UNVERIFIED) |
| 9 | Point cloud rendering | Documented - `VJ/Filters/Sources/PointSource.js`, `VJ/Rendering/Core/SphereMapper.js` | Documented - `PointGaussianRepresentation` in PV representation list | Unknown (UNVERIFIED) |
| 10 | Tubes / ribbons | Documented - `VJ/Filters/General/TubeFilter`, `VJ/Filters/Modeling/RibbonFilter.js` | Documented - `Tube` filter in PV proxy list | Unknown (UNVERIFIED) |
| 11 | Text / corner annotations | Documented - `VJ/Rendering/Core/TextActor.js`, `VJ/Interaction/UI/CornerAnnotation` | Documented - PV text sources (271 source proxies; not itemised) | Unknown (UNVERIFIED) |
| 12 | Scalar bar / colour legend | Demonstrated - `VJ/Rendering/Core/ScalarBarActor` bound to the colour function, `report/figures/feat_a_legend_axes.png` | Demonstrated - `display.SetScalarBarVisibility`, `report/figures/feat_b_colour.png`; server-side widget: shown in remote mode, absent in local (vtk.js) mode | Unknown (UNVERIFIED) |
| 13 | Axes / orientation widget | Demonstrated - `VJ/Interaction/Widgets/OrientationMarkerWidget` with `AxesActor`, `report/figures/feat_a_legend_axes.png` | Unknown - PV orientation axes (view property; not itemised) UNVERIFIED | Unknown (UNVERIFIED) |
| 14 | Colour maps / lookup tables | Demonstrated - presets in `showcase-a/src/presets.js` | Demonstrated - 9 colour-map presets, auto or manual range in the Colouring section of the drawer, `report/figures/feat_b_colour.png` | Documented - lookup-table and transfer-function editor widgets, L1; `ParaViewWebColorManager`, L2 |
| 15 | Lighting / shading | Documented - `VJ/Rendering/Core/Light.js`; volume `shade`, ambient/diffuse/specular in `VolumeProperty.js` | Documented - PV light kit and OSPRay libs present (`PV/lib/libospray*.so`) | Unknown (UNVERIFIED) |
| 16 | Clipping planes | Demonstrated - six clipping planes on the volume and isosurface mappers (`AbstractMapper.addClippingPlane`), `report/figures/feat_a_clip.png`; meshes and slices are not clipped | Demonstrated - Clip in the Pipeline drawer, `report/figures/feat_b_pipeline_selector.png` | Unknown (UNVERIFIED) |
| 17 | Volume cropping | Documented - `VJ/Widgets/Widgets3D/ImageCroppingWidget`, `VJ/Filters/General/ImageCropFilter.js` | Documented - `ExtractSubset` filter in PV proxy list | Unknown (UNVERIFIED) |
| 18 | Multi-view / layouts | Documented - multiple renderers with viewports (`VJ/Rendering/Core/Renderer.js`, `Viewport.js`); no layout manager found | Documented - 18 view types incl. `ComparativeRenderView` in PV proxies; trame layout is user code | Unknown (UNVERIFIED) |
| 19 | Transparency (order-independent) | Documented - `VJ/Rendering/OpenGL/OrderIndependentTranslucentPass.js`, WebGPU same name | Unknown - depth peeling / OSPRay present in PV (UNVERIFIED for API names) | Unknown (UNVERIFIED) |
| 20 | Ray tracing / path tracing | Not supported (no module found in `VJ/Rendering/`) | Documented - OSPRay libs in `PV/lib/` (`libospray*.so`, `libanari*.so`) | Unknown (UNVERIFIED) |
| 21 | Charts / plots (line, histogram, parallel coords) | Not supported (no chart module in `VJ/`; `VJ/Interaction/Widgets/PiecewiseGaussianWidget` is a TF editor) | Documented - `XYChartView`, `XYHistogramChartView`, `ParallelCoordinatesChartView`, `SpreadSheetView` in PV views | Documented - 1D histograms, parallel coordinates, mutual-information diagram, L1 |

## 2. Interaction

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 22 | Picking / probing a value | Demonstrated - `VJ/Rendering/Core/CellPicker.js` (IJK and nearest-voxel value), `report/figures/feat_a_probe.png` | Unknown - `ParaViewWebSelectionHandler`-style selection exists server side; trame pick events via trame-vtk (UNVERIFIED for API) | Documented - `ParaViewWebSelectionHandler`, L2 |
| 23 | Distance / angle measurement | Demonstrated - `VJ/Widgets/Widgets3D/LineWidget` (distance in world units on a camera-facing plane), `report/figures/feat_a_measure.png`; `AngleWidget` not demonstrated | Documented - `GeodesicMeasurement` plugin in `PV/plugins/` | Unknown (UNVERIFIED) |
| 24 | 3D interactive widgets | Documented - `VJ/Widgets/Widgets3D/` (angle, ellipse, image cropping, implicit plane, line, polyline, rectangle, reslice cursor, seed, shape, sphere, spline, transform controls); `LineWidget` demonstrated (row 23) | Documented - `ParaViewWebWidgetManager`, L2; widget proxies in PV | Documented - `ParaViewWebWidgetManager`, L2 |
| 25 | Camera controls (rotate/pan/zoom) | Demonstrated - `showcase-a/src/viewer.js` (default trackball style) | Demonstrated - trame view in `showcase-b/ui.py` | Documented - `ParaViewWebMouseHandler`, L2 |
| 26 | Alternative camera styles | Documented - `VJ/Interaction/Manipulators/` (trackball, first person, unicam, multi-rotate, keyboard, gesture) | Unknown - PV interaction modes (UNVERIFIED which) | Unknown (UNVERIFIED) |
| 27 | Transfer-function editing (interactive) | Demonstrated - `VJ/Interaction/Widgets/PiecewiseGaussianWidget` (opacity only; colour stays on the preset), `report/figures/feat_a_tf_editor_dragged.png`; `VolumeController` not used | Documented - `VtkPiecewiseEditor` class in `TR/trame_vtk/widgets/vtk/common.py` | Documented - transfer-function editors and colour map editor, L1 |
| 28 | Animation / time-series playback | Documented - `VJ/IO/Core/HttpDataSetSeriesReader.js`, `VJ/Common/Core/AnimationScene` (no timeline UI shipped) | Documented - `TemporalInterpolator`, `ForceTime` filters in PV proxies; `ParaViewWebTimeHandler`, L2 | Documented - `ParaViewWebTimeHandler`, L2 |
| 29 | Screenshot / image export | Demonstrated - `getApiSpecificRenderWindow().captureNextImage('image/png')` behind Tools > Measure and export; log run output: PNG data URL of about 1.2 MB (the downloaded file was not opened; no feat_ png of the export itself) | Demonstrated - `simple.SaveScreenshot` in the Session section of the drawer, `report/figures/feat_b_screenshot.png`; `SaveStateAndScreenshot` plugin also in `PV/plugins/` | Documented - `ParaViewWebSaveData`, `ParaViewWebExportData`, L2 |
| 30 | Save / load pipeline state | Unknown - Not supported (no state serializer found; `VJ/IO/Core/Serializer` is scene serialization UNVERIFIED) | Demonstrated (app state only) - `simple.SaveState` writes `out/state.pvsm`; Load state restores only the app's own `out/state.json`, the `.pvsm` is not reloaded; round trip Slice/Viridis -> Glyph/Jet -> Slice/Viridis, `report/figures/feat_b_save_load_state.png` | Documented - `ParaViewWebStateLoader`, L2 |

## 3. Data

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 31 | Read VTK XML ImageData (.vti) | Demonstrated - `showcase-a/verify_vti.mjs`, `VJ/IO/XML/XMLImageDataReader.js` | Demonstrated - `.vti` source option (`XMLImageDataReader`, `data/vti/`), `report/figures/feat_b_vti_source.png` (foot_64, Contour iso 90: 29,027 triangles; 256^3 files not tried) | Documented - ParaView reader (any PV reader through `ParaViewWebFileListing`), L2 |
| 32 | Read PolyData (.vtp, legacy .vtk) | Documented - `VJ/IO/XML/XMLPolyDataReader.js`, `VJ/IO/Legacy/PolyDataReader.js` | Documented - `PV/lib/libvtkIOXML-pv6.2.so`, `libvtkIOLegacy-pv6.2.so` | Documented - via ParaView readers, L2 |
| 33 | Mesh formats (STL, OBJ, PLY, glTF, Draco) | Documented - `VJ/IO/Geometry/` (STL, PLY, Draco, glTF, IFC), `VJ/IO/Misc/OBJReader.js`; OBJ demonstrated (row 73), STL and VTP code paths not exercised | Documented - `PV/lib/libvtkIOPLY`, `libvtkIOGeometry`, `libvtkIOImport` | Unknown (UNVERIFIED) |
| 34 | Scientific formats (Exodus, CGNS, NetCDF, HDF5, Xdmf, ADIOS2, EnSight) | Not supported (none in `VJ/IO/`; ITK reader wrappers `VJ/IO/Misc/ITKImageReader.js` need ITK) | Documented - `PV/lib/libvtkIOExodus`, `IOCGNSReader`, `IONetCDF`, `IOHDF`, `IOXdmf3`, `IOADIOS2`, `IOEnSight` | Documented - via ParaView readers (6.2 list is current ParaView, not 5.x era) |
| 35 | Image stacks / medical (TIFF, DICOM, NIfTI) | Unknown - `VJ/IO/Image/TIFFReader`; DICOM via external ITK helpers UNVERIFIED | Unknown - `AnalyzeNIfTIReaderWriter` plugin in `PV/plugins/`; DICOM reader UNVERIFIED | Unknown (UNVERIFIED) |
| 36 | Large data / out-of-core / LOD | Documented - `VJ/IO/Misc/HttpDataSetLODsLoader.js`; limited by browser memory (see `report/figures/results_table.md`) | Documented - MPI-enabled build (`PV/bin/pvserver`, `pvdataserver`, `pvrenderserver`) | Documented - ParaView server back end (L3: uses VTK/ParaView to generate data) |
| 37 | Distributed (MPI) processing | Not supported (client-side JS) | Documented - `PV/bin/mpiexec`, `libvtkParallelMPI-pv6.2.so`, `pvserver` | Unknown - ParaView server back end (UNVERIFIED for MPI in Visualizer launch) |
| 38 | In-situ (Catalyst) | Not supported | Documented - `PV/lib/libcatalyst.so`, `paraview/catalyst`, `paraview/demos/*miniapp*.py` | Unknown (UNVERIFIED) |
| 39 | Remote file browsing | Documented - HTTP loading via `VJ/IO/Core/DataAccessHelper`; no file browser | Documented - server filesystem via ParaView readers; trame UI is user code | Documented - `ParaViewWebFileListing`, L2 |
| 40 | Time-varying data | Documented - `VJ/IO/Core/HttpDataSetSeriesReader.js` | Documented - temporal readers and `TemporalInterpolator` | Documented - `ParaViewWebTimeHandler`, L2 |
| 41 | Unstructured grids / AMR | Not supported (no UnstructuredGrid or AMR class in `VJ/Common/DataModel/`; PolyData and ImageData only) | Documented - `UnstructuredGridVolumeRepresentation`, `libvtkIOAMR`, `libvtkRenderingVolumeAMR` | Unknown (UNVERIFIED) |
| 42 | Data export / write | Documented - `VJ/IO/XML/XMLImageDataWriter.js`, `XMLPolyDataWriter.js`, STL/PLY/OBJ writers | Documented - 47 writer proxies in PV | Documented - `ParaViewWebExportData`, `ParaViewWebSaveData`, L2 |

## 4. Architecture

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 43 | Client-only rendering (no server compute) | Demonstrated - `showcase-a/` (static `dist/`) | Demonstrated - local mode in `showcase-b/` (`report/figures/b_local.png`; geometry rendered in browser by vtk.js) | Documented - `ParaViewWebLocalRendering`, `ParaViewWebViewPortGeometryDelivery`, L2 |
| 44 | Server-side rendering (image stream) | Documented - client for remote streams only (`VJ/IO/Core/ImageStream`, `WSLinkClient.js`) | Demonstrated - remote mode in `showcase-b/` (`report/figures/b_remote.png`) | Documented - `ParaViewWebViewPortImageDelivery`, `ParaViewWebPublishImageDelivery`, L2 |
| 45 | Hybrid (switch local/remote) | Not supported (client library only) | Demonstrated - `VtkRemoteLocalView` in `showcase-b/ui.py` (class in `TR/trame_vtk/widgets/vtk/common.py`) | Documented - both delivery protocols exist, L2 |
| 46 | WebGL2 | Demonstrated - Showcase A runs on it; `VJ/Rendering/OpenGL/RenderWindow.js` uses `WebGL2RenderingContext` | Demonstrated - local mode uses vtk.js in browser via trame-vtk | Unknown (UNVERIFIED; L1 says WebGL geometry viewers are Three.js) |
| 47 | WebGPU | Documented - `VJ/Rendering/WebGPU/` (Volume, ImageMapper, PolyDataMapper, ...); parity incomplete per issue https://github.com/Kitware/vtk-js/issues/3473 (references.md #4). Our `?api=webgpu` probe is partial: headless Chrome adapter was software (swiftshader), "No input!" console errors, tab closed, no WebGPU render obtained, no screenshot; real GPU not tested (`features_a_log.md` section 9) | Not supported in trame-vtk 2.11.17 (no WebGPU view class in `TR/trame_vtk/widgets/vtk/common.py`); VTK WebGPU roadmap https://discourse.vtk.org/t/vtk-webgpu-roadmap/13749 | Unknown - Not supported (UNVERIFIED; predates WebGPU) |
| 48 | WebXR / VR | Documented - `VJ/Rendering/WebXR/RenderWindowHelper`, `VJ/Interaction/Manipulators/CompositeVRManipulator.js` | Documented - `VtkWebXRHelper`, `XrSessionTypes` in `TR/trame_vtk/widgets/vtk/common.py`; desktop OpenXR libs `PV/lib/libopenxr_loader.so` | Unknown (UNVERIFIED) |
| 49 | WebAssembly | Unknown - Not supported (pure JS; no wasm in `VJ/` except optional deps UNVERIFIED) | Documented - `trame-vtklocal` (VTK.wasm) https://github.com/Kitware/trame-vtklocal, not installed in `.pvenv` | Unknown - Not supported (UNVERIFIED) |
| 50 | Offscreen / headless server rendering | Not supported (browser API) | Documented - pvpython with Mesa/EGL; see `report/install_log.md` (software GL used in `report/figures/swgl_pv_*.png`) | Documented - Docker/EGL advice in https://discourse.paraview.org/t/way-forward-with-paraview-web/11900 (Jourdain, 2023-04) |

## 5. Collaboration and deployment

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 51 | Multi-user sessions (isolated) | Not supported (static page; each tab independent by nature) | Documented - one process per client via launcher + Docker, https://github.com/Kitware/trame/discussions/43 (search snippet, thread not read in full) | Documented - wslink launcher `TR/wslink/launcher.py`; L1 docs sidebar lists "Launchers" (page not read) |
| 52 | Shared state across browsers (one session) | Not supported (no server) | Demonstrated - two Chrome pages on one server share filter, colour, stats and camera, `report/figures/feat_b_multiclient.png`; one trame server, no per-user isolation; `TR/trame_server/state.py` | Unknown (UNVERIFIED) |
| 53 | Session launcher | Not supported | Documented - `TR/wslink/launcher.py` (session launcher incl. password generation); `--launcher` option removed in trame v2 per maintainer, https://github.com/Kitware/trame/discussions/276 | Documented - same wslink launcher (ParaViewWeb Launchers doc page: not read) |
| 54 | Jupyter embedding | Not supported (no Jupyter integration found in `VJ/`) | Documented - trame docs list JupyterLab/Notebook as optional dependencies https://trame.readthedocs.io/en/latest/; `TR/trame/app/jupyter.py` says that module is deprecated. Not demonstrated: the package is `trame-jupyter-extension` 2.1.4, a dry run would add about 90 packages to `.pvenv`, so it was not installed (`features_b_log.md` section 7) | Unknown - Not supported (UNVERIFIED) |
| 55 | Docker deployment | Not supported (static files; any web server) | Documented - https://kitware.github.io/trame/examples/core/docker.html (URL from search result, page not fetched) | Documented - paraview-visualizer Docker files, per Jourdain in https://discourse.paraview.org/t/way-forward-with-paraview-web/11900 |
| 56 | Authentication / access control | Not supported (none in library) | Documented - wslink `authKey` secret (`TR/wslink/launcher.py`, `server.py`); no user login found | Documented - same wslink authKey |
| 57 | Static (no-server) hosting | Demonstrated - `showcase-a/dist/` | Not supported (needs Python server; trame has no static-export mode found) | Not supported (server required) |

## 6. Development

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 58 | Primary language / API | Demonstrated - JavaScript, `showcase-a/src/` | Demonstrated - Python (`paraview.simple`, trame), `showcase-b/app.py` | Documented - JS library + Python (`PVW/`), L1, L3 |
| 59 | TypeScript typings | Documented - `.d.ts` files in `VJ/` (not for every module) | Not supported (Python) | Unknown (UNVERIFIED) |
| 60 | Licence | Documented - BSD-3-Clause (`VJ/package.json`) | Unknown - trame Apache-2.0 (`TR/trame-4.0.0.dist-info/METADATA`); ParaView BSD-3 per `PV/share/licenses/` (UNVERIFIED which file) | Documented - BSD-3-Clause (paraviewweb, visualizer, paraview-lite, light-viz repos; L3) |
| 61 | Maintenance status | Documented - 37.4.6 installed; commit cadence not checked | Documented - ParaView 6.2.0 and trame 4.0.0 installed; cadence not checked | Documented - paraviewweb in maintenance mode (L3); Visualizer/Lite/Divvy no longer bundled since 5.13 (see `report/legacy_desk_note.md`) |
| 62 | Install effort (this project) | Demonstrated - see `report/install_log.md` | Demonstrated - see `report/install_log.md` | Unknown - not installed |
| 63 | Docs / examples | Unknown - https://kitware.github.io/vtk-js (URL not fetched this session) UNVERIFIED | Documented - https://trame.readthedocs.io/en/latest/ (fetched, 200); https://docs.paraview.org (not fetched) | Documented - https://kitware.github.io/paraviewweb/docs/ (fetched); Jourdain called these "legacy doc" in 2023 |
| 64 | Package-manager env for extensions | Demonstrated - npm (`showcase-a/package.json`) | Documented - `paraview.envs` (uv venv manager) `PV/lib/python3.12/site-packages/paraview/envs.py`; `--venv` since 5.13 | Unknown - Not supported (UNVERIFIED) |

## 7. Server-side processing

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 65 | Catalogue of filters | Documented - ~50 filters in `VJ/Filters/` (Core, General, Modeling, Sources, Imaging, Texture) | Documented - 288 filter proxies, queried via `PV/bin/pvpython` | Documented - same ParaView back end (`ParaViewWebProxyManager`, L2) |
| 66 | Python scripting | Not supported (JS only) | Demonstrated - `showcase-b/app.py` | Documented - Python server (`PVW/`) |
| 67 | Programmable Filter / Source | Not supported | Documented - `ProgrammableFilter`, `PythonCalculator` in PV proxies | Unknown (UNVERIFIED) |
| 68 | Calculator / derived arrays | Documented - `VJ/Filters/General/Calculator.js` | Documented - `Calculator`, `PythonCalculator` in PV proxies | Unknown (UNVERIFIED) |
| 69 | Plugins | Not supported (no plugin system found) | Demonstrated - `TopologyToolKit` plugin (TTK 1.3.0) loaded with `simple.LoadPlugin` in 6.6 s, used by `showcase-b/app_topology.py`, `report/figures/feat_d_gaussians_th005.png`; ~45 plugins in `PV/lib/paraview-6.2/plugins/` | Documented - `ParaViewWebStartupPluginLoader`, L2 |
| 70 | Browser-side compute filters | Demonstrated - ImageMarchingCubes runs in the browser (Stream A), `report/figures/feat_a_isosurface.png` | Not supported (filters run on server; local mode ships geometry only) | Documented - client-side image compositing/WebGL viewers, L1 |

## 7b. Rows added after the feature streams landed (2026-10-28)

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 71 | Topological analysis (persistence pairs, critical points) | Not supported (no persistence or topology module in `VJ/Filters/`) | Demonstrated - TTK 1.3.0 bundled in the ParaView 6.2.0 binary, `TTKPersistenceDiagram` in `showcase-b/app_topology.py`; `showcase-b/validate_topology.py` finds 5 maxima on a 5-Gaussian field at 5 % and 10 % thresholds (0 % and 1 % noise), `report/figures/feat_d_gaussians_th005.png`, `report/figures/feat_d_gaussians_maxima_only.png`, `report/figures/feat_d_wavelet_th002.png`, `report/figures/feat_d_aneurism.png` | Unknown (UNVERIFIED) |
| 72 | Persistence diagram display | Not supported (no chart module, see row 21) | Demonstrated - own SVG built on the server and shown with `v-html` (not a TTK or ParaView chart view), visible in the `feat_d_*.png` figures | Unknown (UNVERIFIED) |
| 73 | Mesh file loading in the page (.obj) | Demonstrated - `VJ/IO/Misc/OBJReader.js`, sample `showcase-a/public/mesh/sample_torus.obj` (2304 triangles), `report/figures/feat_a_mesh.png`; `.vtp` and `.stl` not exercised | Documented - `PV/lib/libvtkIOGeometry`; no mesh loading in the app, not demonstrated | Unknown (UNVERIFIED) |
| 74 | Three orthogonal slices shown together | Demonstrated - Tools > Orthogonal slices, `report/figures/feat_a_mpr.png` | Documented - `MultiSlice` and `OrthographicSliceView` view types in PV proxies; not demonstrated (the app shows one Slice plane) | Unknown (UNVERIFIED) |
| 75 | Runtime-selectable pipeline filters (Contour, Slice, Clip, Threshold, Streamlines, Glyph) | Documented - the corresponding filters exist (rows 2, 4, 6, 8); no selector built | Demonstrated - Pipeline drawer in `showcase-b/ui.py`, all six render in local mode, `report/figures/feat_b_pipeline_selector.png`, `report/figures/feat_b_local_pipelines.png` | Unknown (UNVERIFIED) |

## 8. State of the feature streams (updated 2026-10-28 after Streams A, B and D landed)

Sources: `report/features_a_log.md`, `report/features_b_log.md`, `report/features_d_log.md`. All feature screenshots are dev shots from headless Chrome with software GL (Showcase A: SwiftShader, foot_64; Showcase B: Mesa llvmpipe, wavelet 64); they show correctness, not speed.

Promotion rule used: a cell is Demonstrated only when a log says the feature works and a `report/figures/feat_*.png` exists or the log gives run output. The earlier tag "[code present, no feat_ png/log yet]" was removed from all ten ParaView cells (rows 1, 3, 4, 6, 7, 8, 12, 14, 16, 31); each now has a log entry and a figure. No cell was demoted.

Not demonstrated or only partly demonstrated:
- Jupyter embedding (row 54): not done. `trame-jupyter-extension` would add about 90 packages to `.pvenv`; it was not installed.
- WebGPU (row 47): partial. Headless Chrome only, software adapter, no WebGPU render obtained, no screenshot; real GPU not tested.
- Mesh loading: `.obj` only (rows 33, 73); `.vtp` and `.stl` not exercised.
- Volume cropping (row 17): clipping planes were used instead of `vtkImageCroppingWidget`, so row 17 stays Documented and row 16 is Demonstrated.
- Save/load state (row 30, ParaView): app state only; the `.pvsm` is written but not reloaded.
- Screenshot export, vtk.js (row 29): the PNG data URL was checked (about 1.2 MB); the downloaded file was not opened.
- Row 3 (ParaView) is Demonstrated for the Slice filter only; the orthographic and multi-slice view types are not.
- Not tested for any new feature: Windows, Firefox/Edge, 256^3 timing of the isosurface, 256^3 `.vti` in Showcase B, MPI.

Count rule: leading word of each cell. Cells that contain "UNVERIFIED" are counted as Unknown.

## 9. Counts (75 rows)

Computed by script from the tables above (leading word of each cell; cells containing "UNVERIFIED" counted as Unknown), not by hand.

| Column | Demonstrated | Documented | Not supported | Unknown | Not supported + Unknown |
|---|---|---|---|---|---|
| vtk.js 37.4.6 | 23 | 29 | 19 | 4 | 23 |
| ParaView 6.2.0 + trame 4.0.0 | 27 | 38 | 4 | 6 | 10 |
| Legacy ParaViewWeb | 0 | 33 | 1 | 41 | 42 |

Before the streams landed the count was 12 / 20 / 0 Demonstrated (vtk.js / ParaView / legacy). The ten ParaView cells that were code-present only are now backed by `feat_b_*.png`. The legacy column has no Demonstrated cells (nothing was built or run).
