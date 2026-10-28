# Feature-coverage plan (added 2026-10-28)

Why: "evaluation of visualization systems" should cover what the systems can do, not only benchmarks. Goal: widen
the demonstrated feature set, and record the rest in a feature matrix (`report/feature_matrix.md`) as
Demonstrated / Documented / Not supported. Three parallel streams, each owned by one agent; the main agent merges,
tests and commits. Priorities are in order; stop an item that exceeds its time box and log it.

## Stream A: vtk.js features (Showcase A, `showcase-a/`) ~60-90 min
Add a "Tools" section to the existing viewer (do not break the existing UI or `?bench=1` mode).
1. Isosurface in the browser (vtkImageMarchingCubes, iso slider, triangle count shown) alongside the volume. 20 min
2. Orthogonal 3-slice view (I, J, K together with the volume). 15 min
3. Picking/probe: click shows voxel value and IJK position. 15 min
4. Clipping/cropping of the volume (mapper clipping planes or cropping widget). 15 min
5. Scalar bar / colour legend and orientation axes widget. 10 min
6. Interactive transfer-function editor (vtkPiecewiseGaussianWidget or similar). 20 min
7. Mesh loading (drag-and-drop .vtp/.stl/.obj; ship one small generated sample). 15 min
8. Distance measurement (line widget) and screenshot export. 15 min
9. WebGPU probe (`?api=webgpu`) with side-by-side notes of what is missing (E7). 20 min
Log: `report/features_a_log.md` (what works, what failed, which vtk.js API, how long).

## Stream B: trame/ParaView features (Showcase B, `showcase-b/`) ~60-90 min
Keep existing remote/local modes and the benchmark orbit working (`bench/auto_b.mjs` must still run).
1. Pipeline selector: Contour (existing), Slice, Clip, Threshold, Streamlines/Glyph on a vector field. 25 min
2. Colour-by array, colour-map choice, range, scalar bar. 15 min
3. Server-side volume rendering (GPU volume mapper) in remote mode. 15 min
4. `.vti` source option (load the Showcase A datasets) (E0). 15 min
5. Screenshot / save-state / load-state. 10 min
6. Multi-client demo: two browsers share one session (shared trame state); document behaviour. 10 min
7. Jupyter notebook embedding the app (E8) if trame-jupyter is installable. 20 min
Log: `report/features_b_log.md`.

## Stream C: feature matrix and desk research ~40 min
Create `report/feature_matrix.md`: rows = capabilities; columns = vtk.js, ParaView+trame, legacy ParaViewWeb;
cell = Demonstrated (link to file/screenshot), Documented (link to official doc URL, checked), Not supported/unknown.
Also draft a one-page desk note on the legacy apps (Visualizer, Lite, Divvy, LightViz): what each did, why removed,
trame equivalent. Mark every unverified claim. Facts only; opinions are `[STUDENT]`.

## Merge and exit criteria (main agent)
- Existing benchmark path still works (smoke: `scripts/cleanroom_test.sh`, one `auto_b.mjs` cell).
- Screenshots of each new feature saved to `report/figures/feat_*.png` (software GL is fine; say so).
- README feature list, report sections 4/5 and the matrix updated; commit prefix `M7:`.
