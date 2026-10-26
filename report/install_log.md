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
| 2026-10-26 | Download ParaView 6.2.0 Linux tarball (901 MB) to `~/opt/dl` | see M0 entry below | none | background `curl -C -`, ~3.5 MB/s | Linux |
| 2026-10-26 | Fetch `https://klacansky.com/open-scivis-datasets/...` | - | `Connection refused` on port 443 (IPv4 and NAT64 IPv6) | Plain `http://` on port 80 works; manifest URLs use http. Files are 16 MB each, SHA-256 recorded | Linux |
| 2026-10-26 | `headsq.vti` from `kitware.github.io/vtk-js/data/volume/headsq.vti` | - | URL 301-redirects to `.../headsq.vti/`, which is vtk.js's JSON directory format (`vtkHttpDataSetReader`), not an XML `.vti` | Design doc assumption was wrong. Replaced by generated `wavelet_smoke.vti` (vtkRTAnalyticSource 64³) as the smoke-test volume | Linux |
| 2026-10-26 | `raw_to_vti.py --all --smoke` | ~5 s | none | ZLib binary `.vti` written by vtkXMLImageDataWriter; no fallback encoding needed | Linux |
| 2026-10-26 | `npm run verify-data` (vtk.js 37.4.6 `parseAsArrayBuffer` on all 8 files) | 1 s | Node ESM needs `.js` extension in the import path | fixed in `verify_vti.mjs`; all 8 files parse, dims and range match | Linux |
