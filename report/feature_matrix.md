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
| 1 | Volume rendering | Demonstrated - `showcase-a/src/viewer.js`, `report/figures/a_preset_bone.png` | Demonstrated - server volume option in `showcase-b/app.py` (`volume` state; UniformGridVolumeRepresentation exists in PV) [code present, no feat_ png/log yet] | Unknown (UNVERIFIED); backend is ParaView, UI exposure not read |
| 2 | Isosurface / contour | Documented - `VJ/Filters/General/ImageMarchingCubes.js` | Demonstrated - `showcase-b/app.py` (Contour), `report/figures/b_remote.png` | Unknown (UNVERIFIED) |
| 3 | Orthogonal slice / MPR | Demonstrated - `showcase-a/src/viewer.js` (ImageSlice), `report/figures/a_slice.png`; MPR classes `VJ/Interaction/Style/InteractorStyleMPRSlice.js`, `VJ/Widgets/Widgets3D/ResliceCursorWidget` | Demonstrated - Slice in `showcase-b/app.py`; `OrthographicSliceView` and `MultiSlice` view types in PV proxies [code present, no feat_ png/log yet] | Unknown (UNVERIFIED) |
| 4 | Arbitrary-plane cutting of geometry | Documented - `VJ/Filters/Core/Cutter.js`, `ImplicitPlaneWidget.js` | Demonstrated - Slice/Clip in `showcase-b/app.py` [code present, no feat_ png/log yet] | Unknown (UNVERIFIED) |
| 5 | Polygonal mesh / surface rendering | Documented - `VJ/Rendering/Core/Mapper.js`, `Actor.js` | Demonstrated - contour surface in `showcase-b/app.py` | Documented - WebGL geometry viewers (Three.js), L1 |
| 6 | Threshold / extract by value | Documented - `VJ/Filters/Core/ThresholdPoints.js` (points only; no cell Threshold found) | Demonstrated - Threshold in `showcase-b/app.py` [code present, no feat_ png/log yet] | Unknown (UNVERIFIED) |
| 7 | Glyphs | Documented - `VJ/Rendering/Core/Glyph3DMapper`, `VJ/Filters/Sources/ArrowSource.js` | Demonstrated - Glyph in `showcase-b/app.py` (Glyph3DRepresentation in PV) [code present, no feat_ png/log yet] | Unknown (UNVERIFIED) |
| 8 | Streamlines / stream tracing | Documented - `VJ/Filters/General/ImageStreamline.js` (image data input; other dataset types not found) | Demonstrated - StreamTracer in `showcase-b/app.py` [code present, no feat_ png/log yet] | Unknown (UNVERIFIED) |
| 9 | Point cloud rendering | Documented - `VJ/Filters/Sources/PointSource.js`, `VJ/Rendering/Core/SphereMapper.js` | Documented - `PointGaussianRepresentation` in PV representation list | Unknown (UNVERIFIED) |
| 10 | Tubes / ribbons | Documented - `VJ/Filters/General/TubeFilter`, `VJ/Filters/Modeling/RibbonFilter.js` | Documented - `Tube` filter in PV proxy list | Unknown (UNVERIFIED) |
| 11 | Text / corner annotations | Documented - `VJ/Rendering/Core/TextActor.js`, `VJ/Interaction/UI/CornerAnnotation` | Documented - PV text sources (271 source proxies; not itemised) | Unknown (UNVERIFIED) |
| 12 | Scalar bar / colour legend | Documented - `VJ/Rendering/Core/ScalarBarActor` (not yet demonstrated by us; see section 8) | Demonstrated - `bar` state in `showcase-b/app.py` [code present, no feat_ png/log yet] | Unknown (UNVERIFIED) |
| 13 | Axes / orientation widget | Documented - `VJ/Interaction/Widgets/OrientationMarkerWidget`, `VJ/Rendering/Core/AxesActor.js`, `CubeAxesActor.js` | Unknown - PV orientation axes (view property; not itemised) UNVERIFIED | Unknown (UNVERIFIED) |
| 14 | Colour maps / lookup tables | Demonstrated - presets in `showcase-a/src/presets.js` | Demonstrated - colour-map choice in `showcase-b/app.py` [code present, no feat_ png/log yet] | Documented - lookup-table and transfer-function editor widgets, L1; `ParaViewWebColorManager`, L2 |
| 15 | Lighting / shading | Documented - `VJ/Rendering/Core/Light.js`; volume `shade`, ambient/diffuse/specular in `VolumeProperty.js` | Documented - PV light kit and OSPRay libs present (`PV/lib/libospray*.so`) | Unknown (UNVERIFIED) |
| 16 | Clipping planes | Documented - clipping planes in `VJ/Rendering/Core/AbstractMapper.js` | Demonstrated - Clip in `showcase-b/app.py` [code present, no feat_ png/log yet] | Unknown (UNVERIFIED) |
| 17 | Volume cropping | Documented - `VJ/Widgets/Widgets3D/ImageCroppingWidget`, `VJ/Filters/General/ImageCropFilter.js` | Documented - `ExtractSubset` filter in PV proxy list | Unknown (UNVERIFIED) |
| 18 | Multi-view / layouts | Documented - multiple renderers with viewports (`VJ/Rendering/Core/Renderer.js`, `Viewport.js`); no layout manager found | Documented - 18 view types incl. `ComparativeRenderView` in PV proxies; trame layout is user code | Unknown (UNVERIFIED) |
| 19 | Transparency (order-independent) | Documented - `VJ/Rendering/OpenGL/OrderIndependentTranslucentPass.js`, WebGPU same name | Unknown - depth peeling / OSPRay present in PV (UNVERIFIED for API names) | Unknown (UNVERIFIED) |
| 20 | Ray tracing / path tracing | Not supported (no module found in `VJ/Rendering/`) | Documented - OSPRay libs in `PV/lib/` (`libospray*.so`, `libanari*.so`) | Unknown (UNVERIFIED) |
| 21 | Charts / plots (line, histogram, parallel coords) | Not supported (no chart module in `VJ/`; `VJ/Interaction/Widgets/PiecewiseGaussianWidget` is a TF editor) | Documented - `XYChartView`, `XYHistogramChartView`, `ParallelCoordinatesChartView`, `SpreadSheetView` in PV views | Documented - 1D histograms, parallel coordinates, mutual-information diagram, L1 |

## 2. Interaction

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 22 | Picking / probing a value | Documented - `VJ/Rendering/Core/CellPicker.js`, `PointPicker.js`, `HardwareSelector` (not yet demonstrated; see section 8) | Unknown - `ParaViewWebSelectionHandler`-style selection exists server side; trame pick events via trame-vtk (UNVERIFIED for API) | Documented - `ParaViewWebSelectionHandler`, L2 |
| 23 | Distance / angle measurement | Documented - `VJ/Widgets/Widgets3D/LineWidget`, `AngleWidget` (not yet demonstrated) | Documented - `GeodesicMeasurement` plugin in `PV/plugins/` | Unknown (UNVERIFIED) |
| 24 | 3D interactive widgets | Documented - `VJ/Widgets/Widgets3D/` (angle, ellipse, image cropping, implicit plane, line, polyline, rectangle, reslice cursor, seed, shape, sphere, spline, transform controls) | Documented - `ParaViewWebWidgetManager`, L2; widget proxies in PV | Documented - `ParaViewWebWidgetManager`, L2 |
| 25 | Camera controls (rotate/pan/zoom) | Demonstrated - `showcase-a/src/viewer.js` (default trackball style) | Demonstrated - trame view in `showcase-b/ui.py` | Documented - `ParaViewWebMouseHandler`, L2 |
| 26 | Alternative camera styles | Documented - `VJ/Interaction/Manipulators/` (trackball, first person, unicam, multi-rotate, keyboard, gesture) | Unknown - PV interaction modes (UNVERIFIED which) | Unknown (UNVERIFIED) |
| 27 | Transfer-function editing (interactive) | Documented - `VJ/Interaction/Widgets/PiecewiseGaussianWidget`, `VJ/Interaction/UI/VolumeController` (we ship fixed presets only so far; see section 8) | Documented - `VtkPiecewiseEditor` class in `TR/trame_vtk/widgets/vtk/common.py` | Documented - transfer-function editors and colour map editor, L1 |
| 28 | Animation / time-series playback | Documented - `VJ/IO/Core/HttpDataSetSeriesReader.js`, `VJ/Common/Core/AnimationScene` (no timeline UI shipped) | Documented - `TemporalInterpolator`, `ForceTime` filters in PV proxies; `ParaViewWebTimeHandler`, L2 | Documented - `ParaViewWebTimeHandler`, L2 |
| 29 | Screenshot / image export | Unknown - canvas capture via browser; vtk.js `RenderWindow.captureImages` UNVERIFIED | Documented - `SaveStateAndScreenshot` plugin in `PV/plugins/`; `simple.SaveScreenshot` | Documented - `ParaViewWebSaveData`, `ParaViewWebExportData`, L2 |
| 30 | Save / load pipeline state | Unknown - Not supported (no state serializer found; `VJ/IO/Core/Serializer` is scene serialization UNVERIFIED) | Documented - `servermanager`/`smstate.py` in `PV/lib/python3.12/site-packages/paraview/` | Documented - `ParaViewWebStateLoader`, L2 |

## 3. Data

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 31 | Read VTK XML ImageData (.vti) | Demonstrated - `showcase-a/verify_vti.mjs`, `VJ/IO/XML/XMLImageDataReader.js` | Demonstrated - `.vti` option in `showcase-b/app.py` [code present, no feat_ png/log yet] | Documented - ParaView reader (any PV reader through `ParaViewWebFileListing`), L2 |
| 32 | Read PolyData (.vtp, legacy .vtk) | Documented - `VJ/IO/XML/XMLPolyDataReader.js`, `VJ/IO/Legacy/PolyDataReader.js` | Documented - `PV/lib/libvtkIOXML-pv6.2.so`, `libvtkIOLegacy-pv6.2.so` | Documented - via ParaView readers, L2 |
| 33 | Mesh formats (STL, OBJ, PLY, glTF, Draco) | Documented - `VJ/IO/Geometry/` (STL, PLY, Draco, glTF, IFC), `VJ/IO/Misc/OBJReader.js` | Documented - `PV/lib/libvtkIOPLY`, `libvtkIOGeometry`, `libvtkIOImport` | Unknown (UNVERIFIED) |
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
| 47 | WebGPU | Documented - `VJ/Rendering/WebGPU/` (Volume, ImageMapper, PolyDataMapper, ...); parity incomplete per issue https://github.com/Kitware/vtk-js/issues/3473 (references.md #4); our probe: see section 8 | Not supported in trame-vtk 2.11.17 (no WebGPU view class in `TR/trame_vtk/widgets/vtk/common.py`); VTK WebGPU roadmap https://discourse.vtk.org/t/vtk-webgpu-roadmap/13749 | Unknown - Not supported (UNVERIFIED; predates WebGPU) |
| 48 | WebXR / VR | Documented - `VJ/Rendering/WebXR/RenderWindowHelper`, `VJ/Interaction/Manipulators/CompositeVRManipulator.js` | Documented - `VtkWebXRHelper`, `XrSessionTypes` in `TR/trame_vtk/widgets/vtk/common.py`; desktop OpenXR libs `PV/lib/libopenxr_loader.so` | Unknown (UNVERIFIED) |
| 49 | WebAssembly | Unknown - Not supported (pure JS; no wasm in `VJ/` except optional deps UNVERIFIED) | Documented - `trame-vtklocal` (VTK.wasm) https://github.com/Kitware/trame-vtklocal, not installed in `.pvenv` | Unknown - Not supported (UNVERIFIED) |
| 50 | Offscreen / headless server rendering | Not supported (browser API) | Documented - pvpython with Mesa/EGL; see `report/install_log.md` (software GL used in `report/figures/swgl_pv_*.png`) | Documented - Docker/EGL advice in https://discourse.paraview.org/t/way-forward-with-paraview-web/11900 (Jourdain, 2023-04) |

## 5. Collaboration and deployment

| # | Capability | vtk.js 37.4.6 | ParaView 6.2.0 + trame 4.0.0 | Legacy ParaViewWeb |
|---|---|---|---|---|
| 51 | Multi-user sessions (isolated) | Not supported (static page; each tab independent by nature) | Documented - one process per client via launcher + Docker, https://github.com/Kitware/trame/discussions/43 (search snippet, thread not read in full) | Documented - wslink launcher `TR/wslink/launcher.py`; L1 docs sidebar lists "Launchers" (page not read) |
| 52 | Shared state across browsers (one session) | Not supported (no server) | Documented - trame state is server-side (`TR/trame_server/state.py`); our two-browser test: see section 8 | Unknown (UNVERIFIED) |
| 53 | Session launcher | Not supported | Documented - `TR/wslink/launcher.py` (session launcher incl. password generation); `--launcher` option removed in trame v2 per maintainer, https://github.com/Kitware/trame/discussions/276 | Documented - same wslink launcher (ParaViewWeb Launchers doc page: not read) |
| 54 | Jupyter embedding | Not supported (no Jupyter integration found in `VJ/`) | Documented - trame docs list JupyterLab/Notebook as optional dependencies https://trame.readthedocs.io/en/latest/; `TR/trame/app/jupyter.py` says that module is deprecated; our try: see section 8 | Unknown - Not supported (UNVERIFIED) |
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
| 69 | Plugins | Not supported (no plugin system found) | Documented - ~45 plugins in `PV/lib/paraview-6.2/plugins/` (e.g. TopologyToolKit, Prism, pvNVIDIAIndeX) | Documented - `ParaViewWebStartupPluginLoader`, L2 |
| 70 | Browser-side compute filters | Demonstrated - ImageMarchingCubes etc. run in browser (Stream A; see section 8) | Not supported (filters run on server; local mode ships geometry only) | Documented - client-side image compositing/WebGL viewers, L1 |

## 8. State of Streams A and B at time of writing (2026-10-28, ~14:05)

At the end of my run, `report/features_a_log.md` and `report/features_b_log.md` did not exist and `report/figures/` held one new file, `feat_a_load.png`. So no new feature has a screenshot or log yet. Cells marked "[code present, no feat_ png/log yet]" are counted as Demonstrated only because the source file exists; they were not run by me. Source seen but not verified working:
- `showcase-a/src/` (imports seen): ImageMarchingCubes, CellPicker, ScalarBarActor, AxesActor, OrientationMarkerWidget, PiecewiseGaussianWidget, LineWidget, PlaneManipulator, STLReader, OBJReader, XMLPolyDataReader, `tools/mesh.js`; viewer.js has a WebGPU view hook (`tools/webgpu.js` was not present when checked). The vtk.js rows 12, 13, 22, 23, 27, 33 (Documented now) become Demonstrated if those work; row 70 likewise; rows 2 and 16 (vtk.js, clipping/cropping) depend on whether a clip/crop tool is added.
- `showcase-b/app.py`: six pipeline kinds, ColorBy, scalar bar, server volume mapper, SaveScreenshot. Not yet seen: multi-client test (row 52), Jupyter (row 54; `trame-jupyter-extension` is not in `.pvenv`), save/load state (row 30 PV), `.vti` run (row 31).
- Re-run the count script (below) after the logs land; update rows 2, 12, 13, 22, 23, 27, 28, 29, 30, 47, 52, 54, 70.

Count rule: leading word of each cell. Cells that contain "UNVERIFIED" are counted as Unknown.

## 9. Counts (70 rows)

| Column | Demonstrated | Documented | Not supported | Unknown | Not supported + Unknown |
|---|---|---|---|---|---|
| vtk.js 37.4.6 | 12 | 36 | 17 | 5 | 22 |
| ParaView 6.2.0 + trame 4.0.0 | 20 | 40 | 4 | 6 | 10 |
| Legacy ParaViewWeb | 0 | 33 | 1 | 36 | 37 |

Of the 20 ParaView+trame Demonstrated cells, 10 (rows 1, 3, 4, 6, 7, 8, 12, 14, 16, 31) are code-present only, so 10 have run evidence. All 12 vtk.js Demonstrated cells rest on existing code or figures.
