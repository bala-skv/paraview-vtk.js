# Screenshot shot list

Final screenshots must be taken on the student's machine with a real GPU browser (Chrome or Edge, window 1280 x 720). Files named `swgl_*` in `report/figures/` are development evidence rendered with software GL (headless Chrome + SwiftShader) on 2026-10-26. They show the apps work but are not final shots and carry no performance meaning.

| File (save to `report/figures/`) | What to capture | How |
| --- | --- | --- |
| `a_preset_grayscale.png` | Showcase A, foot, preset Grayscale | `scripts/run_a`; open http://localhost:5173; choose foot + Grayscale; wait for render |
| `a_preset_bone.png` | foot, preset Bone | same, preset Bone |
| `a_preset_vessel.png` | aneurism, preset Vessel | dataset aneurism, preset Vessel |
| `a_slice.png` | tooth or foot with slice shown, axis K, mid index | tick "Show slice", move slider |
| `a_fps_overlay.png` | FPS overlay visible after dragging the volume | rotate with the mouse, capture while/just after dragging; overlay is top-left of the view |
| `b_remote.png` | Showcase B, remote mode, 128 | `scripts/run_b`; http://localhost:8080; Local rendering off |
| `b_local.png` | Showcase B, local mode, same iso and size | switch Local rendering on; confirm card says "local (vtk.js)" |
| `b_stats_panel.png` | Close-up of the Server stats card after a size change and one Benchmark orbit | remote mode, press Benchmark orbit, wait for the orbit line |
| `b_devtools_ws.png` | Chrome DevTools, Network > WS > Messages during a 10 s orbit | open DevTools before loading; filter WS; orbit 10 s; capture message sizes/totals |

Existing dev shots: `swgl_a_bone.png`, `swgl_a_vessel.png`, `swgl_a_slice.png`, `swgl_pv_remote.png`, `swgl_pv_local.png`, `m0_cone_check.png`.
