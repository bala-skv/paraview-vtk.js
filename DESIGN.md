# Design Doc: VTK.js + ParaViewWeb Evaluation Project

Oct 26, 2026 · @Bala

## How the agent should use this doc

Build the project milestone by milestone (M0 to M6), and start no extra until the phase gate in Goals passes.

Operating rules:

1. Work in milestone order. Pass a milestone's acceptance checks before starting the next one.
2. After each milestone, commit with the prefix `M<n>:` and append one line to `docs/progress.md` (date, milestone, status, blockers).
3. Log every install error, workaround and duration in `report/install_log.md`. The student cites this log as evaluation evidence, so record failures honestly.
4. Verify APIs before using them. Check the installed source (`node_modules/@kitware/vtk.js`, `site-packages/trame*`) or the official examples. Never guess import paths.
5. Pin versions as soon as something works, and record them in `setup/versions.md`.
6. Never commit datasets, `node_modules`, virtual environments or build output. Keep the repo under 20 MB.
7. Timebox every task. At 150% of its estimate, revert to the last good commit, log the blocker and move on.
8. Ask the human instead of guessing when a GUI installer is needed, the ParaView path is unknown, a download fails twice, a timebox expires, or a choice changes scope.
9. The student owns the report's analysis and opinions. The agent produces evidence (figures, tables, logs, screenshot list) and drafts factual sections only, marked `[DRAFT - student to review]`.

Hard constraints, never to be broken:

- Never `pip install vtk` into the ParaView venv, and never upgrade numpy there. Both conflict with ParaView's bundled copies.
- Always create trame servers with `client_type="vue3"`.
- `pvpython --venv <dir>` goes before the script path, never after it.
- Everything must run on Windows (PowerShell) and on Linux or WSL2.

## Context and scope

The project evaluates "VTK.js + ParaViewWeb" as it exists in October 2026: vtk.js for client-side rendering, plus ParaView 6.2 with trame/wslink for server-side and hybrid rendering.

The assignment is worth 15% of a Scientific Visualization course grade. The brief asks the student to:

1. Install the tool.
2. Explore and showcase use cases as visualizations or other outputs.
3. Provide scripts and instructions to install and reproduce them.
4. Write a comprehensive report on advantages, disadvantages and a thorough evaluation.
5. Suggest research gaps and future improvements.

Items 3 and 4 are submitted, then presented with a Q&A. The deadline is 3 days from now

**Why the scope is reframed.** Kitware has put the `Kitware/paraviewweb` JS repo into maintenance mode and recommends trame. Visualizer, Lite and Divvy were unbundled from ParaView in 5.13, and LightViz is deprecated. trame runs on the same stack (wslink + vtk.js + pvpython). So the project builds on vtk.js and trame, and the report covers the legacy apps as a short desk study. The agent does not build or run the legacy apps unless extra E6 is reached.

The system has two independent showcases that share datasets and a benchmark harness:

- **Showcase A** is a static web app. Vite serves files, and vtk.js renders a volume in the browser with WebGL2. No server code runs.
- **Showcase B** is a trame app run by `pvpython`. ParaView builds the pipeline on the server. In remote mode the server renders and streams compressed images over a wslink WebSocket. In local mode it sends geometry, and vtk.js renders it in the browser.

&#91;embedded content: system architecture · 2 showcases, remote and local paths\]

In remote mode the server sends only images, so the browser needs little GPU power. In local mode it sends geometry once per change, and the browser renders every frame.

## Goals, non-goals and the phase gate

Phase 1 delivers seven must-have milestones (M0 to M6, about 30 hours over three days, buffer included). Phase 2 extras start only after the gate passes. To fit three days, three lower-value items moved to extra E0.

Goals (phase 1, must-have):

- Two working showcases that demonstrate client-side rendering (A) and server-side plus hybrid rendering (B).
- A benchmark comparing local and remote rendering at 3 or 4 dataset sizes, with a CSV and 2 charts.
- A repo that a stranger can clone and run on Windows or Linux by following the README literally.
- Evidence for the report: install log, version table, screenshots list, figures and results tables.

Non-goals (do not build in phase 1):

- Rebuilding or reviving legacy ParaViewWeb apps (Visualizer, LightViz, ArcticViewer).
- Production deployment, authentication, TLS or multi-user hosting.
- Datasets larger than 384³ voxels, or any download above 100 MB.
- Custom shaders, a custom UI framework, or React/Vue rewrites of Showcase A.
- Writing the report's analysis, conclusions or opinions.

**Phase gate.** The agent starts an extra only when all of these are true:

- [ ] M0 to M5 pass their acceptance checks.
- [ ] M6 scaffolding exists (report outline, figures, results tables).
- [ ] The clean-room reproduction test in M5 passed on the student's machine.
- [ ] The student confirms the report draft has every section.

After the gate, take the highest-ranked extra that fits before the next fixed commitment. Start no new extra after 14:00 on submission day.

## Tech stack and version pins

Use the versions below as targets, re-check each one on Day 1, and pin whatever installs cleanly in `setup/versions.md`.

| Component | Target version | Used by | Notes |
| --- | --- | --- | --- |
| Node.js + npm | 22 LTS, npm 10+ | Showcase A | vtk.js requires Node 22+ |
| Vite (`create-vite`) | latest | Showcase A | Needs Node 20.19+ or 22.12+ |
| `@kitware/vtk.js` | 37.x, pin exact (37.4.1 seen 2026-10-03) | Showcase A, trame local mode | v37.0.0 made `setModelTransformMatrix` column-major |
| ParaView | 6.2.0 (released 2026-10-01) | Showcase B | Bundled Python should be 3.12; confirm with `pvpython -c "import sys; print(sys.version)"` |
| Python | 3.12, separate install | Both venvs | Must match ParaView's bundled Python minor version |
| `trame` | 4.0.0 | Showcase B | Fall back to `trame<4` if examples break; log it |
| `trame-vtk` | 2.11.x | Showcase B | Provides `VtkRemoteView`, `VtkLocalView`, `VtkRemoteLocalView` |
| `trame-vuetify` | 3.3.x | Showcase B | Use `vuetify3` imports only |
| `psutil` | latest | Server metrics | Safe in both venvs |
| `vtk` (pip wheel) | latest 9.x | Data tools, fallback app | `.venv` only, never `.pvenv` |
| `numpy`, `pandas`, `matplotlib` | latest | Data tools, plots | `.venv` only |
| `uv` | latest | Optional `paraview.envs` route | Only if the `--venv` route fails |
| Browser | Chrome or Edge, current | Benchmarks | DevTools metrics and `performance.memory` are Chromium-only |

The project uses two Python environments, both created from a separate Python 3.12:

- **`.pvenv`** is loaded into ParaView with `pvpython --venv .pvenv`. It installs `setup/requirements-pv.txt`: `trame`, `trame-vtk`, `trame-vuetify`, `psutil`. Nothing else.
- **`.venv`** is a normal venv for data conversion, plotting and the no-ParaView fallback. It installs `setup/requirements-tools.txt`: the four packages above plus `vtk`, `numpy`, `pandas`, `matplotlib`.

The alternative ParaView route is `pvpython -m paraview.envs create trame setup/requirements-pv.txt`, new in 6.2 and based on uv. Support it in the README, but default all scripts to `--venv`.

## Repository layout

Create this tree in M0 with empty placeholders, so every later milestone only fills files in.

```
vtkjs-pvweb-eval/
├── README.md                  # quickstart (Windows + Linux), run, reproduce, troubleshoot
├── DESIGN.md                  # this doc, exported as Markdown
├── LICENSE                    # BSD-3-Clause
├── .gitignore                 # data/raw, data/vti, .venv, .pvenv, node_modules, dist
├── setup/
│   ├── requirements-pv.txt    # trame, trame-vtk, trame-vuetify, psutil (pinned)
│   ├── requirements-tools.txt # + vtk, numpy, pandas, matplotlib (pinned)
│   └── versions.md            # versions actually installed, OS, GPU
├── scripts/
│   ├── setup.ps1 / setup.sh   # create venvs, npm ci, fetch + convert data
│   ├── run_a.ps1 / run_a.sh   # start Showcase A
│   ├── run_b.ps1 / run_b.sh   # start Showcase B under pvpython
│   ├── run_b_fallback.*       # start Showcase B without ParaView
│   └── check_env.py           # prints versions, fails loudly on mismatch
├── data/
│   ├── manifest.json          # datasets: url, dims, dtype, spacing, sha256
│   ├── fetch_data.py
│   ├── raw_to_vti.py
│   ├── raw/                   # downloads (gitignored)
│   └── vti/                   # converted volumes (gitignored)
├── showcase-a/                # Vite + vtk.js
│   ├── package.json, package-lock.json, vite.config.js, index.html
│   ├── src/main.js            # wiring and app state
│   ├── src/viewer.js          # render window, volume, slice
│   ├── src/presets.js         # transfer-function presets
│   ├── src/ui.js              # control panel
│   ├── src/bench.js           # benchmark mode
│   └── public/data/           # copied .vti files (gitignored)
├── showcase-b/
│   ├── app.py                 # ParaView + trame (main)
│   ├── app_vtk.py             # plain VTK + trame (fallback)
│   └── ui.py                  # shared layout builder
├── bench/
│   ├── protocol.md            # step-by-step manual procedure
│   ├── sysinfo.py             # writes results/sysinfo.json
│   ├── add_row.py             # appends one validated CSV row
│   ├── server_monitor.py      # psutil sampler (extra E0)
│   ├── plot_results.py        # CSV to figures and tables
│   └── results/               # results.csv, sysinfo.json, figures/
├── report/
│   ├── outline.md
│   ├── install_log.md
│   ├── iso25010_evidence.md
│   ├── screenshots.md         # shot list with file names
│   └── figures/
└── docs/
    └── progress.md            # one line per milestone
```

## Data pipeline

Three small scripts turn public raw volumes into `.vti` files that vtk.js can read. Showcase B generates its benchmark data with ParaView's Wavelet source, so it downloads nothing.

| Name | Dims (x × y × z) | Type | Approx. size | Source | Role |
| --- | --- | --- | --- | --- | --- |
| headsq | as shipped | .vti | small | `https://kitware.github.io/vtk-js/data/volume/headsq.vti` | Day-1 smoke test, no conversion |
| foot | 256 × 256 × 256 | uint8 | 16 MB | Open SciVis Datasets | Main demo; resized copies for the benchmark |
| aneurism | 256 × 256 × 256 | uint8 | 16 MB | Open SciVis Datasets | Vessel preset demo |
| bonsai | 256 × 256 × 256 | uint8 | 16 MB | Open SciVis Datasets | Opacity preset demo |
| tooth | 103 × 94 × 161 | uint8 | \~1.5 MB | Open SciVis Datasets | Fast-loading demo |
| Wavelet | 64³ to 384³ | float32 | generated | ParaView / VTK source | Showcase B benchmark sizes |

The Open SciVis URL pattern is expected to be `https://klacansky.com/open-scivis-datasets/<name>/<name>_<X>x<Y>x<Z>_<dtype>.raw`. Confirm it on the site before writing the manifest. Copy each dataset's spacing from its listing, and credit every dataset in the README.

**`data/manifest.json`** holds one entry per dataset with these fields: `name`, `url`, `dims` `[x, y, z]`, `dtype`, `spacing` `[sx, sy, sz]`, `sha256`, `role`. Leave `sha256` empty until the first successful download, then record it and commit.

**`data/fetch_data.py`** (standard library only):

- CLI: `python data/fetch_data.py [--only foot,tooth]`.
- Downloads into `data/raw/`, retrying 3 times with backoff.
- Skips a file that exists and matches its checksum.
- Fills an empty `sha256` on first download, and fails loudly on a mismatch.

**`data/raw_to_vti.py`** (runs in `.venv`):

- CLI: `python data/raw_to_vti.py --name foot [--resize 64 128 384]`.
- Reads little-endian raw data and reshapes it to `(z, y, x)`, so x varies fastest.
- Builds `vtkImageData` with the manifest spacing, and names the scalar array `scalars`.
- With `--resize N`, writes extra cubic copies via `vtkImageResize` named `foot_N.vti`. Sizes 64, 128 and 256 are must-have; 384 is optional.
- Writes with `vtkXMLImageDataWriter`: binary data mode and ZLib compression.
- Writes to `data/vti/`, then copies to `showcase-a/public/data/`.

If vtk.js fails to parse the output, rewrite it with compression off, then try appended raw encoding. Record whichever variant works in `install_log.md`.

## Showcase A: vtk.js volume viewer

Showcase A is a single-page Vite app that loads a `.vti` volume and renders it entirely in the browser. Its job is to demonstrate client-side rendering and to produce the client half of the benchmark.

**Layout.** A fixed 280 px control panel on the left and one 3D view filling the rest. Use plain HTML, CSS and ES modules, with no UI framework.

Must-have features:

1. **Loading.** A dataset dropdown fed by `public/data/index.json`, which `raw_to_vti.py` writes. Also accept a dragged-and-dropped local `.vti`. Parse with `vtkXMLImageDataReader.parseAsArrayBuffer`. Do not use `vtkHttpDataSetReader`, which expects a different directory format.
2. **Volume rendering.** `vtkVolume` with `vtkVolumeMapper`, linear interpolation, a color transfer function and a piecewise opacity function.
3. **Presets** (`presets.js`). Four presets stored as data: Grayscale, Bone, Soft tissue, Vessel. Define control points on a 0 to 1 scale and map them to the dataset's scalar range when applied.
4. **Controls.** Preset select, opacity scale slider, sample-distance slider (0.5 to 2.0, quality vs speed), shading toggle, volume visibility toggle, reset camera.
5. **Slice.** A `vtkImageMapper` + `vtkImageSlice` in the same renderer. Add an I/J/K axis select and a slice-index slider.
6. **Info panel.** Dataset dimensions, voxel count, load time, and the WebGL renderer string. Use `vtkFPSMonitor` for the FPS overlay.

**Cut order.** If M2 runs past 5 hours, drop these in order: drag-and-drop loading, the shading toggle, then the Firefox check.

**Benchmark mode** (`bench.js`). It is triggered by URL parameters, for example `?bench=1&data=foot_128.vti&frames=360&reps=3`.

1. Record `t0` at module start, then fetch the file with `cache: 'no-store'`.
2. Time-to-first-render (TTFR) = time from `t0` until the first rendered frame.
3. Orbit the camera 1° per frame for `frames` frames in a `requestAnimationFrame` loop. Record each frame's duration.
4. Compute median FPS and 5th-percentile FPS. Read `performance.memory.usedJSHeapSize` when it exists.
5. Append one CSV row (schema in the benchmark section) to `localStorage` key `bench_rows`, then reload for the next repetition.
6. After the last repetition, show a Download CSV button and log the rows with `console.table`.

Hooks for extras, not to be built in phase 1: `?api=webgpu` to select the WebGPU view (E7), and a configurable Vite `base` path for GitHub Pages (E1).

Acceptance checks:

- [ ] `npm ci && npm run build` succeeds with no errors.
- [ ] `foot.vti` loads in under 5 s on localhost, and preset changes show immediately.
- [ ] The slice slider moves the slice, and the FPS overlay updates during interaction.
- [ ] Benchmark mode writes 3 CSV rows for `foot_128.vti`.
- [ ] It works in Chrome and Edge. Firefox is tried once and the result is logged.

## Showcase B: trame + ParaView app

Showcase B is one Python file run by `pvpython` that serves a ParaView pipeline to the browser and switches between remote and local rendering live. Its job is to demonstrate server-side rendering and to produce the server half of the benchmark.

**Run command.** `pvpython --venv .pvenv showcase-b/app.py --port 8080 --server [--size 128] [--mode remote|local]`. Add `--size` and `--mode` with `server.cli.add_argument`. `--server` stops a browser from opening, and `--host 0.0.0.0` allows a phone test on the LAN.

**Pipeline.** `Wavelet` (`WholeExtent` set from `--size`) → `Contour` on `RTData` (iso range 40 to 270, default 157) → `Show` → `Render`. A second source option loads a `.vti` from `data/vti/` with `XMLImageDataReader`, so the foot volume can appear in both showcases. With three days left, that option moves to extra E0 and is not built in phase 1.

| State variable | Type / values | Effect |
| --- | --- | --- |
| `iso` | float, 40 to 270 | Sets `Contour.Isosurfaces`, then calls `ctrl.view_update()` |
| `size` | 64, 128, 256 (384 optional) | Resets `WholeExtent`, updates the pipeline, resets the camera |
| `source` | `wavelet` or a `.vti` name | Swaps the contour input (extra E0, not phase 1) |
| `representation` | `Surface` or `Wireframe` | Sets the display representation |
| `viewMode` | `remote` or `local` | Created by `VtkRemoteLocalView(namespace="view")` |
| `interactive_quality` | 0 to 100 | Remote JPEG quality while interacting |
| `interactive_ratio` | 0.25 to 1 | Remote image scale while interacting |
| `stats` | dict | Triangles, geometry KB, last update ms, server RSS MB |

Check in the installed trame-vtk source whether the two quality settings can be bound to state on `VtkRemoteLocalView`. If they cannot, expose them as CLI arguments instead.

**UI** (`ui.py`, shared with the fallback). Use `SinglePageLayout` from `trame.ui.vuetify3`. The toolbar holds the iso slider, size select, representation select, Local rendering switch and Reset camera. A right-hand card shows `stats`. A Benchmark orbit button runs the auto-orbit.

Instrumentation:

- Time every state-change handler with `time.perf_counter`, then read cells and memory from `contour.GetDataInformation()`.
- Sample `psutil.Process().memory_info().rss` once per second in an async task.
- Append rows to `bench/results/server_events.csv`: `timestamp, event, source, size, mode, duration_ms, triangles, geometry_kb, rss_mb`.
- Log the time from server start to the first client connection and the first view update.
- **Benchmark orbit** (remote mode only): an async task rotates the camera 2° for 180 steps, calling `ctrl.view_update()` and yielding each step. It logs total and per-step time. Disable the button in local mode, where the client owns the camera.

**Fallback, `app_vtk.py`.** It provides the same UI and state with no ParaView, run by `.venv` Python. It uses `vtkRTAnalyticSource` → `vtkContourFilter` → mapper and actor in an offscreen `vtkRenderWindow`, shown through `trame.widgets.vtk.VtkRemoteLocalView`. Import `vtkmodules.vtkRenderingOpenGL2` and the interaction-style module, or remote rendering fails.

Acceptance checks:

- [ ] `scripts/run_b` starts the app with one command and prints the URL.
- [ ] The iso slider updates the view in both modes, and the toggle switches without a restart.
- [ ] Sizes 64, 128 and 256 switch without a crash, and `stats` shows triangles and KB.
- [ ] `server_events.csv` gains a row for every change and every benchmark orbit.
- [ ] `scripts/run_b_fallback` runs on a machine with no ParaView installed.

## Benchmark harness

The benchmark's core comparison is B-local vs B-remote, because both render the same contour pipeline. Showcase A gives a separate scaling curve for browser volume rendering, and must not be ranked directly against B, which renders a different workload.

| Condition | Showcase | Data and sizes | How it runs |
| --- | --- | --- | --- |
| A-local | A | `foot_64`, `foot_128`, `foot_256` (`foot_384` optional) | Fully automated by benchmark mode |
| B-local | B | Wavelet contour, 64³ / 128³ / 256³ | Manual 10 s orbit with DevTools |
| B-remote | B | Same | Benchmark orbit button + manual orbit |
| B-remote-lowres | B | Same, `interactive_ratio = 0.5` | Extra E0 only, not phase 1 |

| Metric | Unit | Measured with |
| --- | --- | --- |
| Time to first render | ms | A: `performance.now()`. B: DevTools Network timing plus the server log |
| FPS, median and 5th percentile | frames/s | A: frame timings. B: DevTools Frame Rendering Stats while orbiting |
| Client memory | MB | `performance.memory` (A) or Chrome Task Manager (both) |
| Server memory | MB | `server_events.csv` RSS column |
| WebSocket traffic | bytes per 10 s orbit | DevTools Network → WS → Messages |
| Geometry size | triangles, KB | `stats` panel and `server_events.csv` |

All results go into one file, `bench/results/results.csv`, with this header:

```csv
timestamp,machine_id,browser,gpu_renderer,showcase,condition,dataset,size,rep,ttfr_ms,fps_median,fps_p5,client_mem_mb,server_rss_mb,ws_bytes,triangles,geometry_kb,network_profile,notes
```

Scripts to build:

- **`bench/sysinfo.py`** writes `results/sysinfo.json`: OS, CPU, RAM, GPU, Python, ParaView and package versions.
- **`bench/add_row.py`** appends one validated row from CLI arguments, so manual results never break the schema.
- **`bench/server_monitor.py`** samples CPU and RSS for a given PID at 1 Hz. It moved to extra E0, because the in-app log covers phase 1.
- **`bench/plot_results.py`** (matplotlib) reads the CSV and writes three outputs to `results/figures/`, copying them to `report/figures/`:
  - `fig_fps_by_size.png`: grouped bars of median FPS per size, one bar per condition, min–max whiskers.
  - `fig_ttfr_bytes.png`: two panels, TTFR and WebSocket bytes against triangle count, local vs remote.
  - `results_table.md`: medians per condition and size.

**`bench/protocol.md`** gives the human a step-by-step procedure:

1. Plug in the laptop, close other apps, and set the browser window to 1280 × 720.
2. Run `sysinfo.py` once.
3. Run 3 repetitions per condition and size, with a cold cache.
4. Record median values, and note anything odd in `notes`.

Extra E2 later re-runs the B conditions under DevTools Fast 4G and Slow 4G throttling, recorded in `network_profile`.

## Setup scripts, run scripts and README

A new user should need three commands: clone, `setup`, `run`. Every script exists as a PowerShell (`.ps1`) and a Bash (`.sh`) version with identical behavior.

**`scripts/setup.ps1` and `scripts/setup.sh`** run these steps in order. Each step is idempotent, so re-running skips completed work.

1. Check Node 22+ and npm 10+.
2. Find Python 3.12: `py -3.12` on Windows, `python3.12` on Linux.
3. Find `pvpython` from the `PVPYTHON` environment variable, then `PATH`, then the default install folders (`C:\Program Files\ParaView 6.2.0\bin\`, `~/opt/ParaView-6.2.0-*/bin/`). If none is found, print how to set `PVPYTHON` and stop.
4. Compare pvpython's Python minor version with the found Python 3.12. Stop with a clear message on a mismatch.
5. Create `.pvenv` and install `setup/requirements-pv.txt`.
6. Create `.venv` and install `setup/requirements-tools.txt`.
7. Run `npm ci` in `showcase-a/`.
8. Run `fetch_data.py`, then `raw_to_vti.py` for every dataset, with `--resize 64 128` for foot.
9. Run `check_env.py` in both environments, then print the run commands.

Flags: `--skip-data` skips step 8, and `--no-paraview` skips steps 3 to 5 for a fallback-only setup.

**`scripts/check_env.py`** has two modes:

- `--pv` (run as `pvpython --venv .pvenv scripts/check_env.py --pv`): prints the ParaView and trame package versions. It fails if a pip `vtk` package is present in `.pvenv`.
- `--tools`: prints `vtk`, `numpy` and `trame` versions from `.venv`.

| Script | Command it wraps | URL |
| --- | --- | --- |
| `run_a` | `npm run dev -- --port 5173` in `showcase-a/` | `http://localhost:5173` |
| `run_b` | `"$PVPYTHON" --venv .pvenv showcase-b/app.py --port 8080 --server` plus pass-through arguments | `http://localhost:8080` |
| `run_b_fallback` | `.venv` Python `showcase-b/app_vtk.py --port 8081 --server` | `http://localhost:8081` |

Windows details to handle in the scripts and README:

- Activating a venv may need `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. Print that hint when activation fails.
- Quote every path, because ParaView installs under `Program Files`.
- Warn when the repo sits inside OneDrive or a path with spaces, which breaks Vite's file watcher.
- Expect a Firewall prompt for `pvpython.exe` on first run.

**`README.md`** contains these sections, in this order:

1. What this is: two sentences and one screenshot per showcase.
2. Tested on: a table copied from `setup/versions.md`.
3. Prerequisites.
4. Quickstart for Windows and for Linux, three commands each.
5. Running Showcase A, Showcase B and the fallback.
6. Reproducing the benchmark, linking `bench/protocol.md`.
7. The alternative `paraview.envs` route.
8. Troubleshooting: the pitfalls from Risks, each with its fix.
9. Data credits and licenses.
10. Project structure.

## Report and presentation support

The agent supplies the report's evidence and scaffolding, and the student writes the evaluation. Mark every agent-drafted paragraph `[DRAFT - student to review]` and every analysis slot `[STUDENT]`.

| File | Contents | Agent may draft prose? |
| --- | --- | --- |
| `report/outline.md` | The 12 report sections, each listing the evidence files to cite | Factual parts only: installation, showcase features, method, appendix |
| `report/install_log.md` | Date, step, duration, error, fix, OS for every install action | Yes (it is a log) |
| `report/iso25010_evidence.md` | Rows: the 8 ISO/IEC 25010 characteristics. Columns: vtk.js, trame + ParaView, evidence pointers, an empty score column | Evidence pointers only, no scores |
| `report/screenshots.md` | Shot list with exact file names and how to capture each | Yes |
| `report/figures/` | Benchmark charts, screenshots, `architecture.svg` and its Mermaid source `architecture.mmd` | Yes |
| `report/references.md` | The sources below, with URLs | Yes |
| `report/slides_outline.md` | 10 slides, each mapped to a figure or screenshot | Yes |
| `report/demo_script.md` | A timed 3 to 4 minute script for the backup video | Yes |

Report sections for `outline.md`:

1. Introduction and scope
2. Background and architecture
3. Installation and reproducibility
4. Showcase A
5. Showcase B
6. Benchmark method and results
7. ISO/IEC 25010 evaluation
8. Munzner nested-model analysis
9. Advantages and disadvantages
10. Legacy ParaViewWeb case study
11. Research gaps and future work
12. Conclusion and recommendations, followed by References and Appendix

Screenshot names: `a_preset_grayscale.png`, `a_preset_bone.png`, `a_preset_vessel.png`, `a_slice.png`, `a_fps_overlay.png`, `b_remote.png`, `b_local.png`, `b_stats_panel.png`, `b_devtools_ws.png`.

Sources for `references.md`, to be verified and linked by the agent:

- `Kitware/paraviewweb` README (maintenance-mode notice).
- ParaView 5.13.0 release notes (unbundling of Visualizer, Lite, Divvy).
- ParaView 6.2.0 release notes (`paraview.envs`).
- vtk.js issue #3473, WebGPU-WebGL feature parity.
- VTK WebGPU roadmap thread on the VTK Discourse.
- trame-vtklocal README (VTK.wasm local rendering).
- Jourdain, Ayachit, Geveci, "ParaViewWeb, a Web Framework for 3D Visualization and Data Processing", 2010.
- Usher and Pascucci, "Interactive Visualization of Terascale Data in the Browser: Fact or Fiction?", LDAV 2020.
- Shi and Hsu, "A Survey of Interactive Remote Rendering Systems", ACM Computing Surveys 47(4), 2015.
- The Open SciVis Datasets page, plus each dataset's own credit.

## Milestones and acceptance criteria

The agent's seven milestones now take about 20 hours over three 10-hour days. The student's report writing and benchmark runs overlap with the agent's work from Day 2, leaving about 3 hours of buffer.

&#91;embedded content: 3-day roadmap · 7 milestones, 1 gate\]

Each row is one working day. The agent's milestones run left to right in order, the student writes the report from Day 3, and extras start only after the gate.

| Milestone | Agent hours | Depends on | Done when |
| --- | --- | --- | --- |
| M0 Bootstrap | 2.5 | — | Repo tree exists. Both venvs created. `check_env.py` passes in both. The Vite cone renders. `pvpython --venv .pvenv -m paraview.simple.example.trame` opens in the browser. `sysinfo.json` written |
| M1 Data | 1 | M0 | Manifest has checksums. `foot_64`, `foot_128`, `foot_256`, aneurism, bonsai, tooth and headsq are in `public/data/` with `index.json`. vtk.js parses one converted file |
| M2 Showcase A | 5 | M1 | Every Showcase A acceptance check passes, after the cut order if needed |
| M3 Showcase B | 4 | M0 | Every Showcase B acceptance check passes |
| M4 Benchmark | 3, plus the student's runs | M2, M3 | `results.csv` has 3 repetitions per size for A-local, B-local and B-remote. Both figures and `results_table.md` exist |
| M5 Reproducibility | 2.5 | M2, M3 | README and all scripts done. Versions pinned. A clean-room test passes: fresh clone in a new folder, venvs deleted, setup run, both showcases started, Showcase A benchmarked with 1 repetition |
| M6 Report support | 2 | M4 | Every file in the report support table exists, and the figures are in `report/figures/` |

After each milestone, the agent posts a short summary to the student: what works, what was cut, what was logged.

## Extras backlog

Extras are ranked by impact per hour. Take them strictly in rank order after the gate, and stop each one at its kill time.

| Rank | Extra | Est. hours | What to build | Kill at |
| --- | --- | --- | --- | --- |
| E0 | Restore the 3-day cuts | 1.5 | The `.vti` source option in Showcase B, the B-remote-lowres benchmark condition (`interactive_ratio = 0.5`), and `bench/server_monitor.py` | 2 h |
| E1 | GitHub Pages deploy of Showcase A | 1 | Set the Vite `base` path. Add a GitHub Actions workflow that publishes `dist/`. Ship only `tooth` and `foot_128` to keep the site small | 1.5 h |
| E2 | Network throttling run | 1 | Re-run B-local and B-remote at 128³ under DevTools Fast 4G and Slow 4G. Add `fig_throttle.png` | 1.5 h |
| E3 | SUS mini-study | 2 to 3 | `report/sus_form.md` (the 10 standard SUS items plus 3 tasks per showcase) and `bench/sus_score.py`. The student runs 3 to 5 participants | 4 h |
| E4 | VTK.wasm local rendering | 2 to 3 | `showcase-b/app_wasm.py` in `.venv` using `trame-vtklocal`. Add a B-wasm benchmark condition. Check which VTK wheel it needs (`wheels.vtk.org`) first | 4 h |
| E5 | Docker reproducibility | 3 | A Dockerfile from a `kitware/trame` image, `setup/apps.yml` and a compose file for Showcase B, plus a README section | 4.5 h |
| E6 | Legacy Visualizer hands-on | 2 to 3 | Install the separately distributed Visualizer into its own venv and try it with ParaView 6.2. Log what works and what breaks | 3 h |
| E7 | WebGPU probe | 2 | `?api=webgpu` in Showcase A. Side-by-side screenshots against WebGL2, and a list of missing features | 3 h |
| E8 | Jupyter integration | 1 to 2 | `notebooks/trame_in_jupyter.ipynb` showing the Showcase B app inside a notebook | 3 h |
| E9 | TTK topology on the server | 5+ | Persistence diagram and critical points streamed to the browser. Attempt only if a TTK build for ParaView 6.2 exists | 7 h |
| E10 | WebXR volume | 3+ | Adapt the vtk.js WebXR volume example, tested with a browser XR emulator | 4 h |

If the deadline moves:

- **Extended by 2 days:** do E0 to E4, then two presentation rehearsals.
- **Extended by 1 week:** add E5 to E7, and repeat the benchmark on a second machine.

## Phase 3: feature coverage (added 2026-10-28)

**Decision.** On 2026-10-28 the student decided that "evaluation of visualization systems" must cover what the systems can do, not only benchmarks, and asked for as many features as possible to be added quickly. This work is therefore done **before** the phase gate opens and takes priority over extras E0 to E10, except where it absorbs them (E0 `.vti` source, E7 WebGPU probe, E8 Jupyter, E6 legacy desk note). The gate itself (clean-room pass on the student's machine, report draft confirmed) is unchanged. Source of this section: `docs/feature_plan.md`; outcomes are logged in `report/features_a_log.md`, `report/features_b_log.md` and `report/feature_matrix.md`.

Why: "evaluation of visualization systems" should cover what the systems can do, not only benchmarks. Goal: widen
the demonstrated feature set, and record the rest in a feature matrix (`report/feature_matrix.md`) as
Demonstrated / Documented / Not supported. Three parallel streams, each owned by one agent; the main agent merges,
tests and commits. Priorities are in order; stop an item that exceeds its time box and log it.

### Stream A: vtk.js features (Showcase A, `showcase-a/`) ~60-90 min
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

### Stream B: trame/ParaView features (Showcase B, `showcase-b/`) ~60-90 min
Keep existing remote/local modes and the benchmark orbit working (`bench/auto_b.mjs` must still run).
1. Pipeline selector: Contour (existing), Slice, Clip, Threshold, Streamlines/Glyph on a vector field. 25 min
2. Colour-by array, colour-map choice, range, scalar bar. 15 min
3. Server-side volume rendering (GPU volume mapper) in remote mode. 15 min
4. `.vti` source option (load the Showcase A datasets) (E0). 15 min
5. Screenshot / save-state / load-state. 10 min
6. Multi-client demo: two browsers share one session (shared trame state); document behaviour. 10 min
7. Jupyter notebook embedding the app (E8) if trame-jupyter is installable. 20 min
Log: `report/features_b_log.md`.

### Stream C: feature matrix and desk research ~40 min
Create `report/feature_matrix.md`: rows = capabilities; columns = vtk.js, ParaView+trame, legacy ParaViewWeb;
cell = Demonstrated (link to file/screenshot), Documented (link to official doc URL, checked), Not supported/unknown.
Also draft a one-page desk note on the legacy apps (Visualizer, Lite, Divvy, LightViz): what each did, why removed,
trame equivalent. Mark every unverified claim. Facts only; opinions are `[STUDENT]`.

### Merge and exit criteria (main agent)
- Existing benchmark path still works (smoke: `scripts/cleanroom_test.sh`, one `auto_b.mjs` cell).
- Screenshots of each new feature saved to `report/figures/feat_*.png` (software GL is fine; say so).
- README feature list, report sections 4/5 and the matrix updated; commit prefix `M7:`.

### Milestone M7 acceptance
M7 is done when: the benchmark path still works (`scripts/cleanroom_test.sh` passes and one `bench/auto_b.mjs` cell emits a result); every feature marked "works" in the logs has a `report/figures/feat_*.png`; `report/feature_matrix.md` cells are promoted to Demonstrated only for features with a screenshot or log entry; the README feature list and report sections 4 and 5 are updated. Commit prefix `M7:`.

## Risks, fallbacks and known pitfalls

The biggest risk is losing Day 1 to the ParaView Python environment. If the ParaView route still fails after 90 minutes in total, switch Showcase B to `app_vtk.py` and log the failure as an evaluation finding.

| Risk | Early signal | Fix or fallback |
| --- | --- | --- |
| ParaView and venv Python versions differ | `ModuleNotFoundError: trame`, or a crash importing VTK | Rebuild `.pvenv` with the matching Python. Try `paraview.envs`. Then use the fallback |
| `vtk` or a newer numpy got into `.pvenv` | Import conflicts or segfaults under pvpython | Delete and rebuild `.pvenv` from `requirements-pv.txt`. `check_env.py --pv` guards against this |
| `--venv` placed after the script path | trame not found although installed | Put `--venv .pvenv` before the script |
| Venv created with pvpython itself | `ensurepip` error on Windows | Create venvs with the separate Python 3.12 only |
| trame 4 changes break copied examples | Errors from `trame.ui.vuetify` or Vue 2 code | Use `vuetify3` imports and `client_type="vue3"`. Else pin `trame<4` and log it |
| WebGL problems on the laptop | Black canvas, or `chrome://gpu` shows software rendering | Update the GPU driver, try Edge or Firefox, raise sample distance. Demo B in remote mode |
| vtk.js cannot parse a converted `.vti` | Reader exception in the console | Rewrite without compression, then try appended raw encoding |
| `vtkHttpDataSetReader` used on a `.vti` | 404 for `index.json` | Use `vtkXMLImageDataReader` |
| Slow or failed downloads | Under 1 MB/s, or a checksum mismatch | Start downloads first thing on Day 1. Work with headsq and Wavelet meanwhile |
| A large volume freezes the tab | Tab memory above 2 GB | Cap at 256³ (384³ optional) and downsample |
| Windows Firewall or a busy port | Browser cannot connect | Allow `pvpython.exe`, or change the port |
| Repo in OneDrive or a path with spaces | Vite misses file changes | Move the repo, for example to `C:\dev\` |
| WSL2 renders with Mesa | Very low remote FPS | Record the renderer string. It is a finding, not a bug |
| vtk.js updates change behavior | Code that worked breaks after `npm install` | Pin the exact version, use `npm ci`, never run `npm update` |

Two validity limits must be stated in the report, not fixed in code:

- Localhost has almost no network latency, so remote rendering looks better than it would over a real network. E2 partly addresses this.
- Showcase A renders a volume and Showcase B renders an isosurface, so their FPS numbers are not directly comparable.

## Open questions for the student

The agent should get answers to these before or during M0. Until then, it assumes Windows, no discrete GPU and the 3-day deadline.

- [ ] Which OS will run the project: Windows, WSL2, Linux or macOS?
- [ ] Where is ParaView 6.2.0 installed, and what does `pvpython -c "import sys; print(sys.version)"` print?
- [ ] Does the laptop have a discrete GPU? What does `chrome://gpu` report?
- [ ] Has the instructor confirmed the reframed scope, and is an extension granted?
- [ ] Is there a GitHub account and an empty repo to push to?
- [ ] Is there a phone or a second machine available for one extra benchmark run?
