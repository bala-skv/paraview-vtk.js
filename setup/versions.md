# Versions actually installed

| Component | Version | Notes |
| --- | --- | --- |
| OS | Pop!_OS (Linux 7.0.11, x86_64), native, not WSL | |
| CPU / RAM | i7-1185G7, 8 logical cores, 31 GB | |
| GPU | Intel Iris Xe (TGL GT2, integrated), no discrete GPU | Chrome 151 via ANGLE/OpenGL on Mesa 25.2.8; WebGL and WebGPU hardware accelerated (from chromeGpuInfo.txt, 2026-10-26) |
| Node.js / npm | 24.13.0 / 11.6.2 | design target was 22 LTS; 24 works |
| Vite | 8.3.5 | pinned exact |
| @kitware/vtk.js | 37.4.6 | pinned exact (latest 37.x on 2026-10-26) |
| Python | 3.12.3 (system) | |
| trame | 4.0.0 | |
| trame-vtk | 2.11.17 | |
| trame-vuetify | 3.3.0 | |
| psutil | 7.2.2 | |
| vtk (pip, .venv only) | 9.7.1 | |
| numpy / pandas / matplotlib (.venv only) | 2.5.4 / 3.1.0 / 3.11.2 | |
| ParaView | 6.2.0 (MPI Linux tarball) | bundled Python 3.12.14, numpy 2.4.3; at `~/opt/ParaView-6.2.0-MPI-Linux-Python3.12-x86_64` |
| events (npm polyfill) | 3.3.0 | needed by vtk.js -> xmlbuilder2 in Vite |
| Browser | Google Chrome (headless used for M0 check), Firefox present | |
