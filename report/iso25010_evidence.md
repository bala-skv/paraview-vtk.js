# ISO/IEC 25010 evidence table

Evidence pointers only. The score column is intentionally empty: scores and justification are the student's. `[STUDENT]`

| Characteristic | vtk.js (Showcase A) | trame + ParaView (Showcase B) | Evidence pointers | Score |
| --- | --- | --- | --- | --- |
| Functional suitability | Feature list in `showcase-a/src/` (presets, slice, bench mode); `report/figures/swgl_a_*.png` | Pipeline in `showcase-b/app.py`; `report/figures/swgl_pv_*.png`; local-mode blank scene finding | `docs/progress.md` M2/M3 lines; `report/install_log.md` (PDC serializer entry) | |
| Performance efficiency | A-local rows in `bench/results/results.csv` | B-local, B-remote rows; `bench/results/server_events.csv` | `bench/results/figures/fig_fps_by_size.png`, `fig_ttfr_bytes.png`, `results_table.md`; `bench/results/sysinfo.json` | |
| Compatibility | Chrome tested; Firefox NOT verified (headless check inconclusive) | Python-minor match with ParaView; pip `vtk` conflict guard | `scripts/check_env.py`; `setup/versions.md`; `report/install_log.md` | |
| Usability (interaction capability) | Control panel, FPS overlay, drag-and-drop | Toolbar, stats card, mode switch | `report/figures/` screenshots; SUS study only if extra E3 is run | |
| Reliability | Vite `events` alias fix needed before first load | Remote vs local failure modes; fallback `app_vtk.py` | `report/install_log.md`; `scripts/run_b_fallback.*` | |
| Security | Static files only, no server code | wslink WebSocket on an open port; no auth/TLS by design (non-goal) | `DESIGN.md` non-goals; `--host 0.0.0.0` option in run scripts | |
| Maintainability | Pinned versions, `package-lock.json`, small modules | Pinned `requirements-*.txt`; dependence on trame-vtk serializer coverage | `setup/versions.md`; `showcase-b/app.py` workaround comment; ParaViewWeb maintenance-mode notice (`references.md` #1) | |
| Portability | Runs on any WebGL2 browser; tested on Linux only | Linux tested; Windows `.ps1` scripts written but untested | `scripts/*.ps1`; clean-room test result (M5) | |
