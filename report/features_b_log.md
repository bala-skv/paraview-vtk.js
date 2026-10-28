# Showcase B feature log (trame + ParaView 6.2.0), 2026-10-28

All screenshots are headless Chrome with software GL (Mesa/llvmpipe, ParaView server also software GL), taken with
`wavelet --size 64` unless noted; they are dev shots, not benchmark data. Port 8110 only. Code: `showcase-b/app.py`
(`ParaViewPipeline.apply`), `showcase-b/ui.py` (the "Pipeline" drawer, opened with the hamburger icon). The drawer is
built only when `pipeline.features` is true, so `app_vtk.py` is unchanged and still starts (checked on port 8111,
renders the contour). The old toolbar, size selector, remote/local switch, Benchmark orbit and `server_events.csv`
events are unchanged; new events: `pipeline_change`, `screenshot`, `save_state`, `load_state` (same CSV, same columns).
Time figures are approximate wall-clock minutes including debugging.

## 1. Pipeline selector - works (~25 min)
- API: `simple.Contour / Slice(SliceType="Plane") / Clip(ClipType="Plane") / Threshold(LowerThreshold, UpperThreshold) /
  StreamTracer(SeedType="Point Cloud") / Glyph(GlyphType="Arrow")`; vector field for Streamlines and Glyph from
  `simple.Gradient(Input=source, ScalarArray=["POINTS","RTData"])` (adds a 3-component `Gradient` array).
- Use: drawer > Filter. Slice/Clip: plane normal + offset slider. Threshold: two sliders (fraction of the array range).
  Streamlines: 150 point-cloud seeds, both directions.
- Observed: filters are created lazily, only the active one is visible. Local mode: all six pipelines render (checked
  Contour, Slice, Clip, Threshold, Streamlines, Glyph; no blank scene; the existing
  `vtkPartitionedDataSetCollection` serializer workaround covers them), with colours. Local-mode updates took 2-4 s
  per change under software GL. Clip output of a 64^3 Wavelet had 127k triangles, Threshold 169k (unstructured cells).
  The "Geometry KB" stat for Streamlines (46,607 KB with 300 triangles) is `GetMemorySize()` of the stream tracer
  output and looks inflated; left as is.
- Screenshots: `report/figures/feat_b_pipeline_selector.png` (Slice, Clip, Threshold, Glyph; remote),
  `report/figures/feat_b_streamlines.png`, `report/figures/feat_b_local_pipelines.png` (six pipelines, local mode).

## 2. Colour-by, colour map, range, scalar bar - works (~15 min)
- API: `simple.ColorBy(display, ("POINTS", name[, "Magnitude"]))`, `GetColorTransferFunction(name).ApplyPreset(preset, True)`,
  `AutomaticRescaleRangeMode`, `RescaleTransferFunction(min, max)`, `display.SetScalarBarVisibility(view, bool)`.
- Use: drawer > Colouring (array list is read from the active filter output; 9 presets; Auto range switch, else
  min/max fields; Scalar bar switch).
- Observed: the contour of RTData carries RTData as a constant (the iso value), so Contour gets an `Elevation` filter
  added once the drawer is used (colour-by Elevation). Multi-component arrays are coloured by Magnitude. The scalar bar
  is a server-side widget: it is present in remote mode and screenshots, absent in local (vtk.js) mode. Local mode
  does colour the geometry by the chosen array. Switching the filter hides the previous scalar bar explicitly (it
  otherwise stayed on screen). Server log shows harmless `vtkSMColorMapEditorHelper ... Failed to determine the
  LookupTable` warnings when the volume display is toggled.
- Screenshot: `report/figures/feat_b_colour.png` (Contour coloured by Elevation, Turbo, manual range 0.3-0.7, bar on).

## 3. Server-side volume rendering - works (~10 min)
- API: `simple.Show(source)` with `Representation = "Volume"` (ParaView GPU ray-cast volume mapper) on the source,
  additive to the active filter output; hidden by setting `Visibility = 0`.
- Use: drawer > "Volume rendering (remote only)". Disabled in local mode, and switched off if local mode is selected.
- Observed: renders under software GL on a 64^3 grid (about 0.4-1.3 s per update in the timed events); not tried at 256^3.
  vtk.js local mode has no equivalent here, so the switch is remote-only by design.
- Screenshot: `report/figures/feat_b_volume.png` (Streamlines + volume of RTData, Turbo).

## 4. .vti source - works (~10 min)
- API: `simple.XMLImageDataReader(FileName=data/vti/<file>)`; first point array (`scalars`) used for Contour/Slice/
  Threshold and for Gradient. Source switch deletes the old filters and rebuilds; the iso slider range and value are
  reset to the array range.
- Use: drawer > Source > "VTI file", pick a file from `data/vti` (default `foot_64.vti`). The Size selector affects
  only the Wavelet.
- Observed: tested with `foot_64.vti` (Contour iso 90: 29,027 triangles). The 256^3 files were not tried under
  software GL; Gradient on them would need several hundred MB.
- Screenshot: `report/figures/feat_b_vti_source.png`.

## 5. Screenshot / save / load state - works, with a caveat (~10 min)
- API: `simple.SaveScreenshot(path, view, ImageResolution=[1000,700])` (shown in a dialog as a data-URI with a Download
  link; file also written to `showcase-b/out/shot_<time>.png`); `simple.SaveState(out/state.pvsm)`.
- Use: drawer > Session > Screenshot / Save state / Load state.
- Caveat: Load state restores the app's own `out/state.json` (all drawer parameters, iso, size, representation,
  mode, camera). The `.pvsm` is written but is not reloaded, because loading a ParaView state would replace the
  proxies the app holds. Round trip checked (Slice/Viridis saved, changed to Glyph/Jet, load returned Slice/Viridis).
  `showcase-b/out/` is created at runtime (removed after testing; consider git-ignoring it).
- Screenshots: `report/figures/feat_b_screenshot.png`, `report/figures/feat_b_save_load_state.png`.

## 6. Multi-client demo - works, behaviour documented (~8 min)
- No extra API: trame state and the ParaView view live on the server and are shared by every connected page.
- Test: two Chrome pages on one server; page A sets filter = Slice, colour-by RTData and drags the mouse.
- Observed: page B received the state change (filter, colour, stats) and the new image without any action; the camera
  drag in A moved the view in B (one server-side camera and one render, both pages show identical frames). There is
  no per-user session: a page opened later starts from the current state of the running server, and each extra
  client adds server-side image-encode work (server RSS grew by roughly 100 MB per new page in the first, repeated-page
  runs; not isolated further). This is a single trame server, as launched by `app.py`; per-user isolation would need
  the trame launcher (not tried). The "Clients connected so far" counter only increments: `on_client_exited` did not
  lower it when a page closed within 3 s, so it is labelled as a running total.
- Screenshot: `report/figures/feat_b_multiclient.png` (page A left, page B right).

## 7. Jupyter embedding - not done (~5 min)
- `pip install trame-jupyter` finds no such distribution. The package is `trame-jupyter-extension` (2.1.4). A dry run
  (`.pvenv/bin/python -m pip install trame-jupyter-extension --dry-run`) resolves without vtk but would add about
  90 packages (jupyterlab 4.6.4, jupyter_server, ipykernel, ...) to `.pvenv`, which the benchmark depends on.
  It was not installed and `setup/requirements-pv.txt` is unchanged. A working notebook would also need an ipykernel
  running inside pvpython. Dropped; no code or UI for it.

## Final checks
- Server: `$PVPYTHON --venv .pvenv showcase-b/app.py --port 8110 --server` starts.
- `bench/auto_b.mjs --mode remote --size 64 --rep 1 --seconds 3 --headless --port 8110 --emit` printed a RESULT line
  (ws_bytes 935,624, fps_median 17, triangles 66,260), no changes to bench files. `bench/results/server_events.csv`
  received rows from these tests (test rows are mixed in with real data: filter by timestamp or discard).
- Untested: `run_all_b.sh` end to end; sizes 128/256 with the drawer; 256^3 .vti files; Edge/Firefox.
