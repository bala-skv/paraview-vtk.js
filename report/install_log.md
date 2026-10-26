# Install log

Evidence for the report. Failures are recorded as they happened.

| Date | Step | Duration | Error | Fix / outcome | OS |
| --- | --- | --- | --- | --- | --- |
| 2026-10-26 | Probe tools (node, npm, python3.12, git, uv, pvpython) | <1 min | `pvpython` and `uv` not on PATH, no `~/opt/ParaView*` | ParaView must be installed by the student; logged as blocker. uv is optional | Linux |
| 2026-10-26 | Create `.pvenv` and `.venv` with system `python3 -m venv` | <1 min | none | ok | Linux |
| 2026-10-26 | `pip install -r setup/requirements-pv.txt` into `.pvenv` | 10 s | none | trame 4.0.0, trame-vtk 2.11.17, trame-vuetify 3.3.0 installed with no conflict | Linux |
| 2026-10-26 | `pip install` tools (vtk, numpy, pandas, matplotlib) into `.venv` | 40 s | none | vtk 9.7.1 wheel installed | Linux |
| 2026-10-26 | `npm install @kitware/vtk.js@37.4.6 vite@8.3.5` | ~11 s | none | 0 vulnerabilities. npm 11.6.2 on Node 24 | Linux |
| 2026-10-26 | `npm run build` (cone smoke test) | 0.4 s | warning: chunk >500 kB (vtk.js bundle) | harmless, expected for vtk.js | Linux |
| 2026-10-26 | Render cone in headless Chrome (SwiftShader software GL) | ~5 s | none | renders, see `report/figures/m0_cone_check.png` | Linux |
| 2026-10-26 | `check_env.py --pv` with plain python (no pvpython) | n/a | "not running under pvpython" | expected; guard works. Real check pending ParaView | Linux |
| 2026-10-26 | Download ParaView 6.2.0 Linux tarball (901 MB) to `~/opt/dl` | 4 min 10 s | none | background `curl -L -C -`, ~3.6 MB/s; URL `https://www.paraview.org/files/v6.2/ParaView-6.2.0-MPI-Linux-Python3.12-x86_64.tar.gz` | Linux |
| 2026-10-26 | Fetch `https://klacansky.com/open-scivis-datasets/...` | - | `Connection refused` on port 443 (IPv4 and NAT64 IPv6) | Plain `http://` on port 80 works; manifest URLs use http. Files are 16 MB each, SHA-256 recorded | Linux |
| 2026-10-26 | `headsq.vti` from `kitware.github.io/vtk-js/data/volume/headsq.vti` | - | URL 301-redirects to `.../headsq.vti/`, which is vtk.js's JSON directory format (`vtkHttpDataSetReader`), not an XML `.vti` | Design doc assumption was wrong. Replaced by generated `wavelet_smoke.vti` (vtkRTAnalyticSource 64³) as the smoke-test volume | Linux |
| 2026-10-26 | `raw_to_vti.py --all --smoke` | ~5 s | none | ZLib binary `.vti` written by vtkXMLImageDataWriter; no fallback encoding needed | Linux |
| 2026-10-26 | `npm run verify-data` (vtk.js 37.4.6 `parseAsArrayBuffer` on all 8 files) | 1 s | Node ESM needs `.js` extension in the import path | fixed in `verify_vti.mjs`; all 8 files parse, dims and range match | Linux |
| 2026-10-26 | Extract ParaView tarball to `~/opt/` | 13 s | none | `~/opt/ParaView-6.2.0-MPI-Linux-Python3.12-x86_64/bin/pvpython` (set `PVPYTHON`) | Linux |
| 2026-10-26 | `pvpython -c "import sys, paraview"` | <1 s | none | Python 3.12.14, ParaView 6.2.0. Matches system Python 3.12.3 minor version | Linux |
| 2026-10-26 | Rebuild `.pvenv` with system Python and install requirements-pv.txt | 15 s | none | `pvpython --venv .pvenv scripts/check_env.py --pv` -> OK. numpy 2.4.3 is ParaView's bundled copy, pip did not touch it; no pip `vtk` | Linux |
| 2026-10-26 | `pvpython --venv .pvenv -m paraview.simple.example.trame --server --port 8090` | <15 s | none | serves on :8090 (HTTP 302 to app). Passes the M0 check without opening a browser | Linux |
| 2026-10-26 | `npm run dev` then open page | - | Page blank: `Module "events" has been externalized`, `Class extends value undefined` (vtk.js -> xmlbuilder2 needs Node `events`) | `npm i events@3.3.0` and `resolve.alias: {events: 'events/'}` in vite.config.js. Same issue affects `vite build`, which only warns | Linux |
| 2026-10-26 | Showcase B (ParaView) in **local** rendering mode | ~40 min debugging | View is blank in local mode; remote mode and the plain-VTK fallback are fine. No error in server log or browser console | Root cause: ParaView 6.2 mappers take a `vtkPartitionedDataSetCollection`, and trame-vtk 2.11.17 has no serializer for that class, so every actor is silently dropped from the vtk.js scene. Workaround in `showcase-b/app.py`: `register_instance_serializer("vtkPartitionedDataSetCollection", merge_to_polydata_serializer)`. Evaluation finding: trame-vtk lags ParaView data-model changes | Linux |
| 2026-10-26 | `npm ci && npm run build` from scratch (node_modules deleted) | 1.6 s | none | ok | Linux |
| 2026-10-26 | Showcase A in headless Firefox (`firefox --headless --screenshot`) | - | screenshot is taken at page load, before the bundle renders: blank, inconclusive | NOT verified. Student to open http://localhost:5173 in Firefox once and log the result | Linux |
| 2026-10-26 | Showcase A benchmark mode, 3 reps foot_128 (8 frames) in headless Chrome + SwiftShader | ~1.5 min | 40 frames x 3 reps exceeded a 4-min wait under software GL | Logic verified (3 CSV rows, correct schema). Real FPS numbers need a GPU browser (student run) | Linux |
| 2026-10-26 | `pkill -f` used while shell command line contained the pattern | - | killed my own shell twice | use `fuser -k PORT/tcp` | Linux |
| 2026-10-26 | **Clean-room test**: `git clone` into a new folder, no venvs or node_modules, `scripts/setup.sh` with `PVPYTHON` set | 2 min 10 s | none | all 9 steps passed (venvs, `npm ci`, 4 downloads + conversion, `check_env` OK in both). Then started `run_a`, `run_b`, `run_b_fallback` (HTTP 200/302/302) and ran Showcase A bench mode with 1 rep (1 CSV row, imported by `add_row.py`, plotted by `plot_results.py`). Done on this Linux laptop with headless Chrome + software GL; Windows scripts untested | Linux |

## 2026-10-26 Showcase B benchmark (laptop-a, scripted puppeteer orbit, 10 s)
- 18 rows appended via bench/run_all_b.sh (~25 min wall clock incl. server restarts).
- B-local: 60 fps (display cap) at all sizes, ws_bytes 0 during orbit; geometry 3.0/12.3/49.6 MB (64/128/256).
- B-remote: ~20 fps at all sizes, ~4 MB ws traffic per 10 s. Flat across sizes => probably limited by trame's update/throttle path or the scripted mouse rate, NOT by render cost. Do not claim a size trend; investigate before reporting.
- B-remote rep 3 TTFR outliers (2.7-2.9 s) at all three sizes vs ~0.37 s for reps 1-2; cause unknown (server-side warm-up/GC?). Median hides it; mention in report.
- Server RSS grows with size (709 -> 958 MB local; 732 -> 980 MB remote).
- auto_b.mjs launches Chrome without the user's Wayland flags; renderer string in CSV is as passed via GPU= env, not verified from the launched browser.

### Follow-up: why B-remote is flat at ~20 fps (checked 2026-10-26)
- Client side: trame-vtk.js mouse handler has `throttleDelay: 33.3` ms (max ~30 mouse events/s sent to the server). With puppeteer CDP overhead per move, ~20 events/s arrive => the scripted-drag FPS is capped by the client input throttle, not by rendering.
- Server side: the built-in "Benchmark orbit" (180 steps) in server_events.csv took 2.90-2.93 s at all sizes (64: 2.90-2.91, 128: 2.92-2.93, 256: 2.91-2.93) = ~62 renders/s for 66k to 1.1M triangles. Also flat => this hardware/scene does not discriminate sizes for remote rendering either.
- Conclusion: report remote FPS as "input-throttle limited (~20-30 fps for drag)" and use the server orbit (~62 steps/s) as the render-capacity figure. No size trend claimed. Rep-3 TTFR outliers still unexplained.
