# Extra E1: GitHub Pages deploy of Showcase A (optional, not part of the initial report)

Status: built and verified locally on 2026-10-28. The GitHub Actions run itself was NOT executed. Nothing was committed, pushed or enabled.

## What was checked
* `showcase-a/vite.config.js` already has `base: process.env.VITE_BASE || '/'`. No change needed.
* Absolute URLs in `showcase-a/src`: none hardcoded. `src/main.js` (lines 12, 21, 57), `src/bench.js` (line 54) and `src/tools/mesh.js` (lines 8, 56) already use `import.meta.env.BASE_URL`. `index.html` uses `/src/main.js`, which Vite rewrites at build time. **No `src/*.js` line was edited.**
* Repo default branch is `master` (the workflow triggers on `master` and `main`). Remote: `git@github.com:bala-skv/paraview-vtk.js.git`.

## Decisions
* Data strategy: commit the two small converted files, no download at build time (klacansky.com is slow and http-only). `showcase-a/pages-data/` holds `tooth.vti` (1,294,196 B), `foot_128.vti` (838,709 B), a trimmed `index.json` (2 entries) and `LICENSE-DATA.txt`; total about 2.1 MB. The folder is not matched by `.gitignore`, so it is committable. `showcase-a/public/data` (git-ignored, local) is untouched.
* Licence: the data is CC BY-NC-SA 4.0 (klacansky.com). Redistribution is allowed with attribution, non-commercial use and the same licence. `LICENSE-DATA.txt` states this, says the files are converted (foot downsampled to 128^3) and credits the sources. The repo code stays BSD-3-Clause. The student should decide whether committing the two files is acceptable; the alternative is to drop `pages-data` and have the workflow download and convert (not implemented, depends on the slow host).
* Footer: injected by `pages_build.mjs` into the built `index.html` only (credits, CC BY-NC-SA 4.0, link to data licence and source). Local dev and the normal `npm run build` are unchanged. The footer also appears in `?bench=1` on the Pages site (bench results there are not intended for measurement).

## Files
Created:
* `showcase-a/scripts/pages_build.mjs` (runs `vite build --outDir dist-pages` with `VITE_BASE` default `/paraview-vtk.js/`, replaces `dist-pages/data` with the tracked set, writes `.nojekyll`, injects the footer; uses `process.execPath`, so it works on Windows and Linux)
* `showcase-a/pages-data/{tooth.vti,foot_128.vti,index.json,LICENSE-DATA.txt}`
* `.github/workflows/pages.yml`
* `report/figures/extra_e1_pages_preview.png`, this log
Changed:
* `showcase-a/package.json`: added script `"build:pages": "node scripts/pages_build.mjs"` (no new dependencies)
* `.gitignore`: added line `showcase-a/dist-pages/` (outside the stated edit list; `dist/` did not match `dist-pages`)
* Not changed: vite.config.js, index.html, src/*.js, any report/docs file.

## Verification (production build under /paraview-vtk.js/, `vite preview --base /paraview-vtk.js/ --port 5191`)
* `npm run build:pages`: OK; `dist-pages` is 3.9 MB (JS bundle 1.69 MB, Vite chunk-size warning only).
* curl, all 200: `/paraview-vtk.js/`, `index.html`, `assets/index-*.js` (1,693,348 B), `data/index.json` (501 B), `data/tooth.vti` (1,294,196 B), `data/foot_128.vti` (838,709 B), `mesh/sample_torus.obj`, `data/LICENSE-DATA.txt`. `data/bonsai.vti` returns the SPA index.html fallback (200, 2361 B), i.e. the file is not shipped.
* Headless Chrome (puppeteer-core, software GL SwiftShader): the page loads, dataset select lists only `foot_128, tooth`, foot_128 rendered (load 104 ms), requests go to `/paraview-vtk.js/data/...`, footer present; only error is `favicon.ico` 404. Screenshot: `report/figures/extra_e1_pages_preview.png`.
* `?bench=1&data=tooth.vti&frames=20&reps=1` on the Pages build: completed ("bench complete: 1 rows"), data fetched from the sub-path.
* Local dev server (base `/`, port 5191): normal page loads the full 8-dataset list and renders foot (1817 ms load); `?bench=1&data=foot_128.vti&frames=20&reps=1` fetched the data and started orbiting; the 60 s capture ended before completion under software GL (not waited to the end). Same only-error: favicon 404.
* YAML: `python3 yaml.safe_load` parses `.github/workflows/pages.yml`.
* Not verified: the real Actions run, `configure-pages` behaviour, the live URL, Windows execution of the script.
* Port 5191 was freed afterwards.

## Workflow (.github/workflows/pages.yml)
Triggers: push to `master`/`main` and manual `workflow_dispatch`. Permissions: `contents: read`, `pages: write`, `id-token: write`. Node 24, `npm ci` in `showcase-a`, `VITE_BASE=/<repo name>/` from `github.event.repository.name`. Action majors checked via the GitHub API (latest releases / existing major tags): `actions/checkout@v7` (v7.0.1), `actions/setup-node@v7` (v7.1.0), `actions/configure-pages@v6` (v6.0.0), `actions/upload-pages-artifact@v5` (v5.0.0), `actions/deploy-pages@v5` (v5.0.1). Note: a push to master will trigger a deploy as soon as Pages is enabled; remove the `push` trigger to keep it manual only.

## Student steps
1. Local check (any OS): `cd showcase-a && npm ci && npm run build:pages`; then `npx vite preview --outDir dist-pages --base /paraview-vtk.js/ --port 5191` and open `http://localhost:5191/paraview-vtk.js/`. For another repo name: `VITE_BASE=/name/` (PowerShell: `$env:VITE_BASE='/name/'`).
2. Review and commit: `.github/workflows/pages.yml`, `showcase-a/scripts/`, `showcase-a/pages-data/`, `showcase-a/package.json`, `.gitignore`. Push.
3. GitHub repo > Settings > Pages > Build and deployment > Source: "GitHub Actions". (Private repos need a plan that supports Pages.)
4. Actions tab > "Deploy Showcase A to GitHub Pages" > Run workflow (or push to master).
5. URL (project site): `https://bala-skv.github.io/paraview-vtk.js/`, also shown in the deploy job output.

## README snippet (not applied)
```
## Live demo (GitHub Pages)

Showcase A (vtk.js) is published at https://bala-skv.github.io/paraview-vtk.js/ with two small
datasets (tooth, foot_128). Build locally with `cd showcase-a && npm run build:pages` (output in
`showcase-a/dist-pages`). The datasets in `showcase-a/pages-data` are converted copies from
Klacansky's Open SciVis Datasets, CC BY-NC-SA 4.0 (see `LICENSE-DATA.txt`); the code is BSD-3-Clause.
```

## Limitations
* Showcase B (ParaView/trame) needs a Python server with a render process and cannot run on Pages (static hosting only); the local-versus-remote comparison needs a server.
* Only tooth and foot_128 are available online; the other datasets and the drop-a-local-.vti feature work only as far as the user's own files.
* Pages is HTTPS with no special headers; WebGPU/XR features depend on the visitor's browser, not tested on Pages.
