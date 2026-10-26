# Backup video script (about 3:30)

Setup before recording: `scripts/run_a` and `scripts/run_b` running, Chrome at 1280 x 720, DevTools closed.

| Time | Action | Say (student to adapt) |
| --- | --- | --- |
| 0:00-0:20 | Show repo and README quickstart | What is evaluated, two showcases |
| 0:20-1:10 | Showcase A at localhost:5173: load foot, switch presets, drag to rotate (FPS overlay) | Rendering happens entirely in the browser; no server code |
| 1:10-1:40 | Show slice slider and the info panel (renderer string) | |
| 1:40-2:10 | Showcase B at localhost:8080, remote mode: move iso slider, change size to 256 | Server renders and streams images |
| 2:10-2:40 | Toggle Local rendering, move iso slider | Server sends geometry; vtk.js renders |
| 2:40-3:00 | Back to remote, press Benchmark orbit, point at stats card | Orbit time, triangles, server RSS |
| 3:00-3:30 | Show results figures and the install log finding | One-line summary [STUDENT] |
