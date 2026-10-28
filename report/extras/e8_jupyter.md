# Extra E8: Showcase B (ParaView + trame) in Jupyter

Date: 2026-10-28. Outcome: works (JupyterLab 4.6.4 in headless Chrome, Linux, ParaView 6.2.0 MPI Python 3.12, software-independent: real X display :1 with GLX). Optional extra, not part of the initial report.

## Files
- `notebooks/trame_in_jupyter.ipynb` (6 cells, outputs cleared, 4.5 KB). Imports `ParaViewPipeline` from `showcase-b/app.py` (read-only; `main()` is guarded, so import starts no server). Builds a minimal trame layout (VtkRemoteView + iso VSlider) rather than `ShowcaseApp` from ui.py.
- `setup/requirements-jupyter.txt` (pinned subset of `pip freeze`, 108 packages in full freeze).
- `scripts/install_jupyter_kernel.sh` (writes the kernelspec into `.jvenv/share/jupyter/kernels/pvpython/kernel.json`).
- `bench/e8_shot.mjs` (puppeteer-core driver: opens the notebook on port 8888, runs all cells, moves the slider, screenshots).
- `report/figures/extra_e8_jupyter.png` (iso 157), `report/figures/extra_e8_jupyter_slider.png` (slider moved by 40 keyboard steps, iso 197).
- `.gitignore`: added `.jvenv/`. `.pvenv` and `.venv` untouched; no `vtk` installed anywhere.

## Reproduce (from repo root)
```
python3 -m venv .jvenv
.jvenv/bin/pip install -r setup/requirements-jupyter.txt
scripts/install_jupyter_kernel.sh            # PVPYTHON=... if pvpython is not on PATH / ~/opt
.jvenv/bin/jupyter lab --port 8888           # run with a real DISPLAY (see below); open notebooks/trame_in_jupyter.ipynb, kernel "ParaView 6.2 pvpython"
```
Screenshot run used: `DISPLAY=:1 .jvenv/bin/jupyter lab --no-browser --port 8888 --ServerApp.token='' --ServerApp.password='' --ServerApp.disable_check_xsrf=True --expose-app-in-browser --notebook-dir=.` then `cd bench && DISPLAY=:1 node e8_shot.mjs ../report/figures/extra_e8_jupyter.png`.
`nbconvert --execute --ExecutePreprocessor.kernel_name=pvpython` also runs the notebook without error (30 s) but shows no view because no browser frontend exists.

## Install facts
- `.jvenv` created from system python 3.12.3. `pip install jupyterlab trame-jupyter-extension trame==4.0.0 trame-vtk==2.11.17 trame-vuetify==3.3.0`: 22 s wall (pip cache warm or fast mirror), no errors. Then `psutil` (needed because `app.py` imports `ui.py`, which imports psutil). Later `ipykernel<7` (see below). Final: 108 packages, `.jvenv` 274 MB.
- trame-jupyter-extension 2.1.4 and its server extension are enabled automatically (`jupyter labextension list`: enabled OK; `jupyter server extension list`: trame_jupyter_extension 2.1.4 OK). Prebuilt labextension, no node needed.
- Earlier decision (features_b_log item 7: not installed into .pvenv because ~90 extra packages) is unchanged; this is a separate venv.

## How ParaView runs inside Jupyter: option (a), used
`pvpython --help` lists `--venv TEXT`. Kernelspec argv:
`<pvpython> --venv <repo>/.jvenv -m ipykernel_launcher --IPKernelApp.capture_fd_output=False -f {connection_file}`
with env `TRAME_BACKEND=jupyter`, `TRAME_IFRAME_BUILDER=jupyter-extension`. Check: `pvpython --venv .jvenv -c "import ipykernel, paraview"` works; Python reported is 3.12.14 (ParaView's), packages from `.jvenv` (pure Python plus pyzmq cp312 wheel).
Option (b) (standard `paraview` + trame-jupyter-extension in a normal python kernel) was not run: the ParaView binary distribution ships no pip-installable `paraview` wheel into the system python 3.12 here, and `pip install vtk` into a pvpython-used env is excluded by the scope rules. Not tested.

## Errors and workarounds (each observed)
1. Kernel dies at start under pvpython: `AttributeError: 'vtkPythonStdStreamCaptureHelper' object has no attribute 'fileno'` (ipykernel/iostream.py `_setup_stream_redirects`; pvpython replaces `sys.stdout`). Workaround: `--IPKernelApp.capture_fd_output=False` in argv. Side effect: C-level stdout/stderr (VTK warnings) goes to the terminal of the Jupyter server, not the notebook.
2. With ipykernel 7.4.0 the first browser connection crashes the kernel: `X Error of failed request: BadAccess ... Major opcode 149 (GLX) Minor opcode 5 (X_GLXMakeCurrent)`; the server then restarts the kernel and the iframe logs `trame::jupyter-comm::close -- NO COMM`. Cause not isolated; observed fact: a render happening off the thread that created the GL context. Thread check with ipykernel 7.4.0: cells and `async` cells ran in MainThread, so the offending thread is presumably the comm-message handler (not verified). Workaround: `pip install "ipykernel<7"` -> 6.31.0; same notebook then renders. Pinned in requirements-jupyter.txt.
3. Jupyter server started with empty `DISPLAY=`: ParaView prints `vtkXOpenGLRenderWindow ... bad X server connection. DISPLAY=` then falls back to EGL and fails with `vtkEGLRenderWindow: Unable to eglMakeCurrent: 12290` and `attempt to add attribute without a handleless buffer`; trame view stays black (UI and slider still work, state is synced over the comm). Workaround: start Jupyter with a real X display (`DISPLAY=:1` here). A headless server without X: untested (`pvpython --mesa` / xvfb not tried).

## Observed behaviour
- Notebook cell 4 uses `await layout.display_cell(height='480px')`; the layout is an iframe served from `/trame-jupyter-server/servers/e8_jupyter/index.html?ui=main&server=e8_jupyter&wsProxy&reconnect=auto`; websocket traffic goes over a kernel comm `wslink_comm`. No extra port is opened (only 8888).
- Run-all to first rendered frame in headless Chrome: under 55 s (15 s wait + kernel start + 40 s wait in the script; exact time not measured). 64^3 Wavelet used.
- Slider change re-contours in the kernel and a new frame arrives (screenshot 2 differs from 1).

## Not tested
Windows (kernelspec path/`--venv` handling, script is bash only), macOS, Firefox/Safari, JupyterHub / remote Jupyter, Jupyter Notebook 7 UI (only JupyterLab), headless server without X, ipykernel 7.x with a fix, local (vtk.js) rendering mode in the notebook (only remote images), the full Showcase B UI (ShowcaseApp drawer, orbit benchmark) in the notebook.
