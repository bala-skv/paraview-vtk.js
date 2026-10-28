# Evaluation of vtk.js and ParaView/trame for Web-Based Scientific Visualization

Balasubramanian (2025121002) · Scientific Visualization · October 2026

> **How to read this draft.** `[DRAFT - student to review]` marks factual text written by the agent from the repo's logs and results; check each claim against the cited file. `[STUDENT]` marks analysis, opinion and conclusions that only the student writes. Nothing in a `[STUDENT]` slot has been written for you; the bullet prompts under it are suggestions only. Figures are in `report/figures/`. Convert to PDF/Word when complete (suggested length 12–15 pages; see `outline.md`).

---

## 1. Introduction and scope

**[DRAFT - student to review]**
This report evaluates web-based scientific visualization with the Kitware stack as it exists in October 2026. The original project target was "ParaViewWeb + vtk.js". During setup it became clear that the `Kitware/paraviewweb` JavaScript repository is in maintenance mode and points developers to trame, which runs on the same stack (wslink, vtk.js, pvpython) (references #1). The scope, agreed with the course instructor by email, is therefore:

1. **vtk.js** for client-side rendering (Showcase A: a volume viewer served as static files).
2. **ParaView 6.2.0 with trame/wslink** for server-side and hybrid rendering (Showcase B: an isosurface app with a switch between server-rendered images and client-rendered geometry).
3. A benchmark comparing local (browser) and remote (server) rendering on one machine.

The deliverables are the two showcases, scripts and instructions that reproduce them (`README.md`, `scripts/`), and this report.

**[STUDENT]** Motivation and research questions. Suggested prompts: What decision should a reader be able to make after this report (when to render in the browser vs on a server)? Which questions did you set out to answer (installation effort, interactive performance, data transfer, maintainability)?

## 2. Background and architecture

**[DRAFT - student to review]**
*Showcase A* is a static web application. Vite serves the files, and vtk.js renders a volume in the browser with WebGL2. No server code runs; datasets are `.vti` files downloaded by the browser.

*Showcase B* is a trame application started with ParaView's `pvpython`. ParaView builds the pipeline on the server (Wavelet source, Contour filter on `RTData`, Show). In **remote** mode the server renders and streams compressed images to the browser over a wslink WebSocket. In **local** mode the server serialises the isosurface geometry once and vtk.js renders it in the browser; rotating the view then needs no server round-trip. Switching mode triggers a full update.

Figure 1 (`figures/architecture.svg`) shows the components.

Software versions are pinned (`setup/versions.md`): vtk.js 37.4.6, Vite 8.3.5, ParaView 6.2.0, trame 4.0.0, trame-vtk 2.11.17, trame-vuetify 3.3.0, Node.js 24.13.0, Python 3.12.

**[STUDENT]** Compare with the original 2010 ParaViewWeb architecture (references #7; image streaming from a ParaView server to a thin JavaScript client) and with the survey of remote-rendering systems (references #9). What is the same, what changed?

## 3. Installation and reproducibility

**[DRAFT - student to review]**
All installation steps, durations and failures were logged as they happened in `report/install_log.md`. A one-shot setup script (`scripts/setup.sh`, `scripts/setup.ps1`) creates two Python virtual environments (`.pvenv` for ParaView/trame and `.venv` for tooling), runs `npm ci`, downloads and converts the datasets, and runs an environment check. Notable events:

| Event | Effect | Resolution |
| --- | --- | --- |
| ParaView 6.2.0 tarball is 901 MB | 4 min 10 s download at ~3.6 MB/s | background download, resumable |
| HTTPS to the dataset host (klacansky.com) refused on port 443 | download failed | plain HTTP URLs in the manifest, SHA-256 checksums recorded |
| Dataset host very slow at times (about 5 kB/s observed during a clean-room run) | `setup.sh` appeared to hang on step 8 | downloader rewritten to resume (HTTP Range), abort trickling connections and retry; manual copy as fallback |
| The design document's `headsq.vti` URL redirects to vtk.js's JSON directory format, not an XML `.vti` | smoke-test file unusable | replaced by a generated wavelet volume |
| vtk.js in Vite: "Module `events` externalized / Class extends value undefined", blank page | Showcase A did not render | install `events@3.3.0` and alias it in `vite.config.js` |
| ParaView local mode showed an empty scene | Showcase B local mode unusable | see Section 5 |
| `pkill -f` matched its own shell | killed the command shell | use `fuser -k PORT/tcp` |

A scripted clean-room test (`scripts/cleanroom_test.sh`: fresh clone, setup, environment check, start both showcases and the fallback, HTTP checks) passed all 8 checks in 34 s on the development laptop with datasets pre-copied. An earlier manual clean-room run completed all 9 setup steps in 2 min 10 s. Windows scripts (`.ps1`) were written but not tested; Firefox was not verified (headless check inconclusive).

**[STUDENT]** Your assessment of reproducibility effort. Prompts: how many manual steps did a newcomer need? Which failures were the tools' fault and which were environment or documentation? Would you recommend this install path to another student?

## 4. Showcase A: client-side volume rendering with vtk.js

**[DRAFT - student to review]**
Features: dataset dropdown and drag-and-drop loading of local `.vti` files; three transfer-function presets (Grayscale, Bone, Vessel; `src/presets.js`); opacity-scale and sample-distance sliders; shading and volume toggles; an I/J/K slice view with an index slider; an info panel (dataset, dimensions, voxels, load time, WebGL renderer); vtk.js's FPS monitor overlay ("Mean / Current" over a rolling frame buffer); and a URL-driven benchmark mode (`?bench=1&data=…&frames=…&reps=…`).

Datasets are the Open SciVis datasets (references #10), converted to `.vti`: foot (256³), aneurism (256³), bonsai (256³) and tooth (103×94×161), plus resized foot copies (64³, 128³) for the benchmark. Observed on the development laptop (Intel Iris Xe, Chrome, 1593×934 view; screenshots below): load times 97–289 ms; the vtk.js overlay showed mean 39–46 fps on the 256³ volumes and 60 fps on the tooth; GPU memory reported by the overlay was 16.8 MB for 256³ and 1.6 MB for the tooth.

Figures: `figures/a_preset_grayscale.png`, `a_preset_bone.png`, `a_preset_vessel.png`, `a_slice.png` (and `a_slice_with_volume.png`), `a_fps_overlay.png`.

**[STUDENT]** Observed image quality, usability and limits. Prompts: Do the presets bring out the anatomy? Is interaction smooth at 256³? What could not be done (no server-side data processing, data must fit browser/GPU memory)?

## 5. Showcase B: trame + ParaView, remote and local rendering

**[DRAFT - student to review]**
The UI (Vuetify single-page layout) has an iso-value slider, a size selector (64³, 128³, 256³), Surface/Wireframe, a "Local rendering" switch, Reset camera, and a "Benchmark orbit" button that rotates the camera 180 steps × 2° and reports the server-side time. A "Server stats" card shows mode, triangle count, geometry size, last-update time and server resident memory. Server events (start, first client, orbit) are logged to `bench/results/server_events.csv`. A fallback using plain VTK (`showcase-b/app_vtk.py`) runs without ParaView and produced identical triangle counts in a software-GL check.

At 128³ and iso 160 the isosurface has 271,408 triangles and about 12.2 MB of geometry (Figures `b_remote.png`, `b_local.png`). Geometry sizes by volume size: 64³ → 66,260 triangles, 3.0 MB; 128³ → 272,634 triangles, 12.3 MB; 256³ → 1,103,026 triangles, 49.6 MB (median rows in `results.csv`).

**Finding: local mode was blank with ParaView 6.2.0 + trame-vtk 2.11.17.** Remote mode and the plain-VTK fallback worked, with no error in the server log or browser console. About 40 minutes of debugging located the cause: ParaView 6.2 mappers take a `vtkPartitionedDataSetCollection`, and trame-vtk 2.11.17 has no serializer for that class, so every actor is silently dropped from the vtk.js scene. The workaround in `showcase-b/app.py` registers an existing serializer for the class (`register_instance_serializer("vtkPartitionedDataSetCollection", merge_to_polydata_serializer)`).

**[STUDENT]** Interpretation. Prompts: What does the silent failure say about the maturity of the hybrid path? What does the local/remote switch feel like to use? Which mode would you pick for this scene and why (use the data in Section 6)?

## 6. Benchmark

### 6.1 Method **[DRAFT - student to review]**

Machine `laptop-a`: Intel i7-1185G7 (8 logical cores), 31 GB RAM, Intel Iris Xe integrated GPU (WebGL renderer `ANGLE (Intel, Mesa Intel(R) Iris(R) Xe Graphics (TGL GT2), OpenGL ES 3.2)`), Pop!_OS Linux, Chrome 151, 60 Hz display (`bench/results/sysinfo.json`, `chromeGpuInfo.txt`).

Conditions: **A-local** (volume in browser), **B-local** (isosurface geometry rendered in browser), **B-remote** (images streamed from the server). Sizes 64, 128, 256 (cube edge length); 3 repetitions each, cold start per repetition. Metrics: time to first render (TTFR), median FPS, minimum 1-second FPS bin (a coarse stand-in for the 5th percentile), client JS heap, server resident memory, WebSocket bytes during the run, triangles and geometry size. A-local FPS comes from `requestAnimationFrame` over 360 frames. B runs use a scripted 10-second mouse orbit (`bench/auto_b.mjs`) with the same path every time: remote FPS is binary image frames received per second, local FPS is page animation frames per second. `ws_bytes_setup`, the cost of the one-time geometry push on a mode or size switch, is recorded separately in the row notes. Full protocol: `bench/protocol.md`.

### 6.2 Validity limits **[DRAFT - student to review]**
- Localhost has almost no network latency, which flatters remote rendering.
- A (volume) and B (isosurface) are different workloads; their FPS values must not be compared with each other.
- FPS is capped by the 60 Hz display, so values at 60 cannot rank conditions.
- Remote FPS in the scripted orbit is limited by trame's client mouse throttle (`throttleDelay` 33.3 ms, about 30 events/s at best, about 20 observed with the scripting overhead), not by render cost.
- Three repetitions per cell; TTFR is noisy (remote repetition 3 had first renders of 2.7–2.9 s against about 0.37 s for repetitions 1–2 at all three sizes; cause not found).
- One machine, integrated GPU, Linux only.
- Development screenshots and early tests used software GL and are not results.

### 6.3 Results **[DRAFT - student to review]** (medians over 3 repetitions; `results_table.md`, Figures `fig_fps_by_size.png`, `fig_ttfr_bytes.png`)

| condition | size | ttfr_ms | fps_median | fps_p5 | client_mem_mb | server_rss_mb | ws_bytes | triangles | geometry_kb |
|---|---|---|---|---|---|---|---|---|---|
| A-local | 64 | 215.5 | 59.9 | 59.5 | 19.6 | | | | |
| A-local | 128 | 107.2 | 59.9 | 59.5 | 21.3 | | | | |
| A-local | 256 | 434.5 | 30.0 | 25.6 | 41.0 | | | | |
| B-local | 64 | 376.0 | 60.0 | 60.0 | 10.4 | 709.3 | 0 | 66,260 | 2,991 |
| B-local | 128 | 357.0 | 60.0 | 60.0 | 11.7 | 757.4 | 0 | 272,634 | 12,279 |
| B-local | 256 | 356.0 | 60.0 | 60.0 | 11.7 | 958.4 | 0 | 1,103,026 | 49,615 |
| B-remote | 64 | 400.0 | 20.0 | 20.0 | 10.5 | 732.0 | 3,920,535 | 66,260 | 2,991 |
| B-remote | 128 | 366.0 | 20.0 | 19.0 | 9.9 | 777.8 | 3,977,234 | 272,634 | 12,279 |
| B-remote | 256 | 374.0 | 21.0 | 20.0 | 11.2 | 979.5 | 4,034,738 | 1,103,026 | 49,615 |

Observations stated as facts only: B-local holds the 60 Hz cap at all sizes and sends 0 bytes during the orbit (the geometry push happened at setup: 3.0, 12.3 and 49.6 MB). B-remote sends about 4 MB per 10-second orbit at every size and shows about 20 fps at every size. A-local holds the cap at 64 and 128 and drops to a median of 30 fps (minimum bin 25.6) at 256. Server resident memory rises with size (709 → 958 MB local, 732 → 980 MB remote). The server-side orbit (180 steps) took 2.90–2.93 s at all sizes in the scripted headless-style runs (about 16 ms/step); **one interactive run in the student's own browser logged 867 ms/step (156 s total)**, which is unexplained and is under re-test (`install_log.md`, 2026-10-28). Do not cite the 16 ms/step figure until that is resolved.

**[STUDENT]** Results discussion. Prompts: what does the flat remote FPS say (input throttle, not rendering)? What is the trade-off between a one-time 3–50 MB geometry push and a steady ~4 MB/10 s image stream, and where would it break (larger data, real network)? Why does A-local fall to 30 fps only at 256³? What would change on a discrete GPU or a remote server? Include `figures/b_devtools_ws.png` when taken.

## 7. ISO/IEC 25010 evaluation

**[STUDENT]** Score each characteristic for each showcase and justify it in one or two sentences. Evidence is tabulated per characteristic in `report/iso25010_evidence.md` (functional suitability, performance efficiency, compatibility, usability, reliability, security, maintainability, portability). Facts you can use: Firefox and Windows were not verified; wslink has no authentication or TLS by design here; versions are pinned with lock files; the trame-vtk serializer gap needed a workaround.

## 8. Munzner nested-model analysis

**[STUDENT]** For each showcase give the four levels: domain situation (who, what data), data/task abstraction (3D scalar volume; explore structure; compare iso-levels), visual encoding and interaction idiom (direct volume rendering with transfer function; isosurface; slice; orbit/zoom), and algorithm (GPU ray casting in WebGL2; marching-cubes contour on the server; image compression and streaming). Discuss where each level's choices constrain the next.

## 9. Advantages and disadvantages

**[STUDENT]** All content. Draw on Sections 3–7 for evidence. A starting checklist: install effort; interactivity; data transfer; server and client requirements; scalability to large data; maintenance status; security; documentation quality.

## 10. Legacy ParaViewWeb (background note)

**[DRAFT - student to review]** The instructor-approved scope covers vtk.js and ParaView/trame; the legacy ParaViewWeb applications are mentioned only for context and were **not built or run** (details: `legacy_desk_note.md`). The `Kitware/paraviewweb` README states that the repository is in maintenance mode, not adding features, and points to trame (references #1, verified). The ParaView 5.13.0 release notes (kitware.com, announcement dated 2024-08-23) state that the web applications divvy, lite and visualizer were removed and are "not bundled with ParaView anymore" (references #2, verified); the same release added the `--venv` option to the executables. The earlier ParaView Discourse thread (2024-05-07, by a Kitware developer) was a *proposal* ("strongly considering removal"), not an announcement of a decision, so cite the release notes for the removal. LightViz's own README says it "has been deprecated and is no longer supported" (no date). In the installed ParaView 6.2.0, `paraview/apps/` contains only `trame.py`, a `glance.py` stub and `packages.py`. No source read names a drop-in trame replacement for Visualizer, Lite or Divvy.

**[STUDENT]** One paragraph on what this means for a project that starts today.

## 11. Research gaps and future work

**[STUDENT]** All content. Material from this project: trame-vtk lagging ParaView's data model (silent failure); no hybrid decision aid (which mode is faster for a given data size and network?); WebGPU in vtk.js still tracking WebGL parity (references #4, #5); VTK.wasm local rendering via trame-vtklocal (references #6); benchmarking only on localhost; large-data and multi-user (launcher) deployments were not tested.

## 12. Conclusion and recommendations

**[STUDENT]** All content.

## References

See `report/references.md` (11 entries, each marked with how it was verified; #2 and #3 are only partly verified or unverified).

## Appendix

**[DRAFT - student to review]** A. Software versions: `setup/versions.md`. B. System information: `bench/results/sysinfo.json`. C. Installation log: `report/install_log.md`. D. Raw benchmark data: `bench/results/results.csv` (27 rows). E. Progress log: `docs/progress.md`. F. Dataset credits and licence (CC BY-NC-SA 4.0): README acknowledgements and the Open SciVis Datasets site.
