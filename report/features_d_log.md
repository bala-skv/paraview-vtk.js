# Feature stream D: E9, TTK topology on the server (log)

Date 2026-10-28, started 14:07 IST, build and test finished about 14:21 IST (system clock). Outcome: **real TTK is usable**.
No fallback implementation was needed.

## 1. Feasibility (time used: about 10 min of the 25 min box)

| Check | Result | Evidence |
| --- | --- | --- |
| TTK in the installed ParaView 6.2.0 binary | **Present.** `lib/paraview-6.2/plugins/TopologyToolKit/` has 173 files (about 77 MB, e.g. `libttkPersistenceDiagram.so`, `libttkTopologicalSimplificationByPersistence.so`, `libttkScalarFieldCriticalPoints.so`, `libttkMorseSmaleComplex.so`, `libttkContourTree.so`). Listed in `plugins/paraview.plugins.xml` as `<Plugin name="TopologyToolKit" auto_load="0" />`. | `find`, `ls` |
| TTK version | 1.3.0 (`share/paraview-6.2/spdx/ttk.spdx`: `PackageDownloadLocation: https://www.paraview.org/files/dependencies/ttk-1.3.0-trimmed.zip`; licence in `share/licenses/ttk`). "Trimmed" = the ParaView-bundled subset of TTK. | spdx file |
| Loads in pvpython | **Yes.** `simple.LoadPlugin("TopologyToolKit", remote=False, ns=globals())` took 6.6 s (first load) and returned without error. `ldd` on `libttkPersistenceDiagram.so` reports no missing libraries. Python proxies exist: `TTKPersistenceDiagram`, `TTKScalarFieldCriticalPoints`, `TTKTopologicalSimplificationByPersistence`, `TTKPersistenceCurve`, `TTKMorseSmaleComplex`, `TTKMergeTreeClustering`. | `/tmp/.../scratchpad/t1.py` |
| Runs | **Yes.** `TTKPersistenceDiagram` on a 64^3 Wavelet: 2.7 s, 1192 pairs. The filters report 8 threads. | `t2.py` |
| conda-forge `topologytoolkit` | Exists, latest 1.3.0 (`api.anaconda.org/package/conda-forge/topologytoolkit`, queried during this session). `with_paraview` Linux builds (py312: `topologytoolkit-1.3.0-with_paraview_py312hc02410a_8.conda`, 17 MB) depend on `paraview >=5.13.2,<5.14.0a0`; `no_paraview` builds depend on `vtk-base >=9.4.2,<9.4.3.0a0`. Neither matches ParaView 6.2.0 / VTK 9.7. Not installed, not downloaded. | API JSON |
| PyPI | `https://pypi.org/pypi/topologytoolkit/json` returns 404, `simple/topologytoolkit/` returns 404. No PyPI package. | curl |
| TTK GitHub releases | GitHub API rate-limited (HTTP 403 from this IP); not checked. Not needed because TTK is bundled. | curl |
| Windows | Not tested. The ParaView 6.2.0 Windows binary was not inspected here; whether it bundles the TTK plugin (`TopologyToolKit.dll`) is unverified. |  |

Conclusion of step 1: no download or install was needed. Nothing was installed (no new venv, no pip, no conda); `.pvenv` was not modified.

Failures and surprises logged during the feasibility/prototype phase:

1. `TTKPersistenceDiagram(Input=wavelet)` without `ScalarField` printed "Unable to retrieve input scalar array for idx 0" and **segfaulted pvpython** (exit with "Segmentation fault"). Fix: always pass `ScalarField=["POINTS", "<array>"]` (same for `InputArray` of the simplification filter).
2. `pvpython --venv .pvenv` still imports **numpy 2.4.3 from `~/.local/lib/python3.12/site-packages`** (user site), not the bundled numpy 1.26.4. The bundled scipy (compiled for numpy 1.x) then fails with "A module that was compiled using NumPy 1.x cannot be run in NumPy 2.4.3". The app uses only numpy and vtk (works with both), and the validation script avoids scipy. Setting `PYTHONNOUSERSITE=1` was not tested.
3. `simple.ColorBy(display, None)` raised `RuntimeError: invalid association string 'NONE'` on a Threshold output; replaced with `display.ColorArrayName = ["POINTS", ""]`.
4. Chrome console shows one `405 Method Not Allowed` resource error on page load (not investigated; the app works).
5. `TTKTopologicalSimplificationByPersistence` followed by `TTKScalarFieldCriticalPoints` on the simplified field keeps thousands of saddles (see validation table, e.g. 10918 1-saddles on the 1% noise field at any threshold >= 2%) while minima and maxima drop to the expected numbers. The simplification only removes extremum-saddle pairs; the flattened regions produce saddles in the critical point filter. Because of this the app selects critical points from the persistence diagram instead (section 2).

## 2. What was built

Files (all new; `showcase-a/`, `showcase-b/app.py`, `showcase-b/ui.py` untouched, nothing imported from them):

- `showcase-b/app_topology.py`: standalone trame app, port 8120.
- `showcase-b/validate_topology.py`: headless validation script.
- `bench/shot_topology.mjs`: puppeteer-core screenshot driver (drives state through `window.trame.state.set`).
- `setup/requirements-topology.txt`: no new packages (comment plus `-r requirements-pv.txt`).
- `report/figures/feat_d_*.png`: screenshots.

Pipeline (all in the pvpython server process):

1. Source: Wavelet (N^3 grid, default N=48), "Gaussians (known: 5 maxima)" (numpy-built vtkImageData in a `TrivialProducer`), or any `data/vti/*.vti` (reader, then `ResampleToImage` to N^3).
2. `TTKPersistenceDiagram(ScalarField=..., EmbedinDomain=1)`: persistence pairs. With `EmbedinDomain` each pair is one line cell whose two points sit on the critical vertices; point data `CriticalType` (0 minimum, 1 1-saddle, 2 2-saddle, 3 maximum), cell data `PairType` (0 min-saddle, 1 saddle-saddle, 2 saddle-max), `Persistence`, `Birth`, `IsFinite`.
3. Persistence slider (0 to 30 % of the scalar range, applied on slider release): critical points shown are the end points of the pairs with `Persistence >= slider * (max - min)`; selection is numpy code on the server, points go to one `TrivialProducer` per critical type and are drawn as coloured spheres (blue min, green 1-saddle, yellow 2-saddle, red max) over a translucent z mid-slice of the field and the outline. Checkboxes toggle each type; point-size slider.
4. Persistence diagram: an SVG string built on the server (birth on x, death on y, dashed line = threshold, kept points large, removed points small and faded) pushed to the browser as trame state and displayed with `v-html`. Not a second ParaView view.
5. Rendering: `VtkRemoteView` (remote rendering, images streamed by trame). Local (vtk.js) rendering was not tried for this app.

TTK filters actually used in the app: `TTKPersistenceDiagram`. `TTKTopologicalSimplificationByPersistence` and `TTKScalarFieldCriticalPoints` are only used in `validate_topology.py` for comparison.

## 3. How to run

```
export PVPYTHON=/home/bala/opt/ParaView-6.2.0-MPI-Linux-Python3.12-x86_64/bin/pvpython
$PVPYTHON --venv .pvenv showcase-b/app_topology.py --port 8120 --server [--res 48]
# open http://localhost:8120/   (first computation about 5 to 8 s)
$PVPYTHON --venv .pvenv showcase-b/validate_topology.py        # headless validation, prints PASS/FAIL
cd bench && node shot_topology.mjs                              # dev screenshots (app must be running)
```

Not tested on Windows. Paths in the code use `pathlib`; the Windows ParaView 6.2 binary was not checked for the TTK plugin.

## 4. Validation (`validate_topology.py`, N=48, ParaView 6.2.0, TTK 1.3.0)

Field: sum of 5 Gaussians (centres/heights in `GAUSS_CENTRES`), scaled to range 0 to 100, with 0 % or 1 % uniform noise. Known answer: 5 maxima. Columns are counts of persistent critical points (min / 1-saddle / 2-saddle / max) from the app method, then the same four counts from TTKTopologicalSimplificationByPersistence + TTKScalarFieldCriticalPoints.

| noise | threshold (% of range) | app method (pairs >= threshold) min/1s/2s/max | TTK simplification + critical points min/1s/2s/max |
| --- | --- | --- | --- |
| 0 % | 0 | 14 / 32 / 26 / 5 | 14 / 30 / 26 / 5 |
| 0 % | 5 | 1 / 1 / 6 / 5 | 1 / 17 / 26 / 5 |
| 0 % | 10 | 1 / 0 / 5 / 5 | 1 / 17 / 26 / 5 |
| 1 % | 0 | 5020 / 15778 / 14169 / 3191 | 5020 / 13792 / 13126 / 4078 |
| 1 % | 0.5 | 357 / 4999 / 4716 / 64 | 357 / 11048 / 10958 / 144 |
| 1 % | 2 | 1 / 8 / 13 / 5 | 1 / 10918 / 10916 / 5 |
| 1 % | 5 | 1 / 2 / 7 / 5 | 1 / 10918 / 10916 / 5 |
| 1 % | 10 | 1 / 0 / 5 / 5 | 1 / 10918 / 10916 / 5 |

- Check: 5 maxima at thresholds 5 % and 10 % for both noise levels with the app method: **PASS** (script prints `OVERALL PASS`). At 2 % with 1 % noise also 5 maxima.
- Independent numpy comparison (strict maximum over all 26 neighbours, interior points): 5 on the noise-free field (equals TTK), 1465 on the 1 % noise field versus 3191 TTK maxima at threshold 0. These differ because TTK uses a different neighbourhood (piecewise-linear / discrete-Morse on a tetrahedral subdivision of the grid) than the 26-neighbour cube; not investigated further.
- The 14 minima on the noise-free field at threshold 0 are in the flat, nearly constant tails of the Gaussians and at the corners; with threshold >= 0.5 % one minimum remains (not investigated in detail).
- TTK printed `#Multi-saddles: 2` for the noise-free field at threshold 0.
- Wavelet (N=48): 1162 pairs; 448 pairs >= 2 % (172 min, 386 1-saddle, 276 2-saddle, 61 max shown), 37 pairs >= 8 % (20 / 34 / 17 / 2). Wavelet has no known answer; its maxima count was not cross-checked.
- aneurism.vti resampled to 48^3: 1049 pairs, 306 >= 5 % (4 / 22 / 295 / 280). The scalar is integer-valued, so ties are likely; the many maxima/2-saddles were not analysed.

## 5. Timings (software GL, 8 threads, headless Chrome, N=48; from `[topology]` lines in the server log)

| Event | Time |
| --- | --- |
| Wavelet source + TTKPersistenceDiagram + fetch | 3.4 s (PD alone 1.0 to 1.5 s) |
| Gaussians source + PD | 2.5 to 4.7 s (PD 0.9 to 1.5 s) |
| aneurism (resample 256^3 to 48^3) + PD | 3.6 to 4.9 s (PD 1.0 s) |
| Threshold change (select points, SVG, render) | 0.03 to 0.6 s handler |
| First creation of the sphere displays after a source change | 1 to 4 s |

The PD is recomputed only when the source or N changes; the slider does not rerun TTK. Larger N was not measured (selectable 24 to 96 in the UI).

## 6. Screenshots (software-GL dev shots, 1400x800 and 1400x1000 headless Chrome, not final report figures)

All five were regenerated by the final run (oblique camera, working checkboxes):

- `report/figures/feat_d_wavelet_th002.png`, `feat_d_wavelet_th008.png`: Wavelet at 2 % and 8 %.
- `report/figures/feat_d_gaussians_th005.png`: Gaussians at 5 %.
- `report/figures/feat_d_gaussians_maxima_only.png`: only maxima checked (5 red spheres; one is behind the slice).
- `report/figures/feat_d_aneurism.png`: aneurism.vti at 5 %.

Visual notes: the SVG header text ("threshold ... pairs kept") overlaps the top-most diagram points; on the Wavelet the critical points form a regular lattice pattern from the sinusoidal terms of the field.

## 7. Limitations

- Persistence is computed on the resampled N^3 grid, not on the full-resolution volume; N=48 default.
- Critical points in the 3D view come from the diagram's embedded pair end points (a saddle that belongs to two pairs is drawn once); the TTK simplified-field route is only in the validation script (reason in section 1, item 5).
- Persistence diagram is an SVG made by own code (not a TTK or ParaView chart view); all pairs are sent (up to 21388 circles for the noisy test field).
- Slider is applied on release (`end` event), not while dragging.
- Boundary handling is TTK's default (`IgnoreBoundary` not changed).
- Morse-Smale complex, contour tree and merge trees were not tried (filters exist in the plugin).
- Not tested: Windows, Edge/Firefox, MPI with more than one rank, local (vtk.js) rendering, N above 96, `PYTHONNOUSERSITE=1`.
- No cost estimate for building TTK from source is needed since the binary bundles TTK 1.3.0.
