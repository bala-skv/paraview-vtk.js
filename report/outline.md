# Report outline

Marking: `[DRAFT - student to review]` = factual text drafted by the agent. `[STUDENT]` = analysis, opinion or conclusion to be written by the student.

## 1. Introduction and scope
- [DRAFT - student to review] The project evaluates vtk.js (client-side rendering) and ParaView 6.2.0 with trame/wslink (server-side and hybrid rendering) as of October 2026. Legacy ParaViewWeb apps are covered as a desk study only (section 10).
- [STUDENT] Motivation and research questions.
- Evidence: `DESIGN.md` (Context and scope), `references.md` #1-#2.

## 2. Background and architecture
- [DRAFT - student to review] Showcase A is a static Vite app: vtk.js renders a volume in the browser with WebGL2. Showcase B is a trame app under pvpython: in remote mode the server renders and streams images over a wslink WebSocket; in local mode it sends geometry and vtk.js renders it.
- [STUDENT] Comparison with the 2010 ParaViewWeb architecture.
- Evidence: `figures/architecture.svg`, `figures/architecture.mmd`, `references.md` #7-#9.

## 3. Installation and reproducibility
- [DRAFT - student to review] Install steps, durations and errors are logged in `install_log.md`. Notable events: HTTPS to klacansky.com refused (plain HTTP used); the design doc's `headsq.vti` URL serves vtk.js's JSON directory format, not XML `.vti`; Vite needed an `events` alias for vtk.js; ParaView 6.2.0 tarball is 901 MB (4 min 10 s download).
- [STUDENT] Assessment of reproducibility effort.
- Evidence: `install_log.md`, `../setup/versions.md`, `../README.md`, clean-room test result (M5).

## 4. Showcase A
- [DRAFT - student to review] Features: dataset dropdown and drag-and-drop, four transfer-function presets, opacity and sample-distance sliders, shading toggle, I/J/K slice, info panel, FPS overlay, URL-driven benchmark mode.
- [STUDENT] Observed quality, limits, usability.
- Evidence: `figures/a_preset_*.png`, `a_slice.png`, `a_fps_overlay.png` (final shots pending; see `screenshots.md`), `swgl_a_*.png` (dev only).

## 5. Showcase B
- [DRAFT - student to review] Pipeline: Wavelet -> Contour on RTData -> Show. State: iso, size (64/128/256), representation, local/remote mode. Instrumentation writes `bench/results/server_events.csv`. A plain-VTK fallback runs without ParaView and gave identical triangle counts in a software-GL check (e.g. 114,560 at iso 100, size 128). Finding: with trame-vtk 2.11.17, ParaView 6.2 local mode showed an empty scene because mapper input is `vtkPartitionedDataSetCollection`, which had no serializer; fixed by registering one in `showcase-b/app.py`.
- [STUDENT] Interpretation of the finding and of mode behavior.
- Evidence: `figures/b_*.png`, `swgl_pv_*.png`, `install_log.md`, `../bench/results/server_events.csv`.

## 6. Benchmark method and results
- [DRAFT - student to review] Method follows `bench/protocol.md`: conditions A-local, B-local, B-remote; sizes 64/128/256; 3 repetitions; metrics TTFR, median and 5th-percentile FPS, memory, WebSocket bytes, triangles. Validity limits: localhost has almost no latency; A (volume) and B (isosurface) are different workloads; Showcase A FPS is paced by requestAnimationFrame (display refresh caps it). Development runs used software GL and are not results.
- [STUDENT] Results discussion.
- Evidence: `../bench/results/results.csv`, `sysinfo.json`, `figures/fig_fps_by_size.png`, `fig_ttfr_bytes.png`, `results_table.md`, `figures/b_devtools_ws.png`.

## 7. ISO/IEC 25010 evaluation
- [STUDENT] Scores and justification.
- Evidence: `iso25010_evidence.md`.

## 8. Munzner nested-model analysis
- [STUDENT] Domain, abstraction, idiom and algorithm levels for each showcase.
- Evidence: sections 4-5 of this report; `../showcase-a/src/`, `../showcase-b/app.py`.

## 9. Advantages and disadvantages
- [STUDENT] All content.
- Evidence: sections 3-7, `install_log.md`.

## 10. Legacy ParaViewWeb case study
- [DRAFT - student to review] The `Kitware/paraviewweb` README states maintenance mode and points to trame. A ParaView Discourse thread (2024-05-07) is titled "Removal of web applications Visualizer, Lite, and Divvy from ParaView 5.13.0". The apps were not built or run (extra E6 not done).
- [STUDENT] Implications.
- Evidence: `references.md` #1-#2 (note which parts are only partly verified).

## 11. Research gaps and future work
- [STUDENT] All content.
- Evidence: `references.md` #4-#6 (WebGPU parity issue, WebGPU roadmap, trame-vtklocal), section 5 finding.

## 12. Conclusion and recommendations
- [STUDENT] All content.

## References
- [DRAFT - student to review] See `references.md`.

## Appendix
- [DRAFT - student to review] `setup/versions.md`, `bench/results/sysinfo.json`, `install_log.md`, `docs/progress.md`, data credits from the README.
