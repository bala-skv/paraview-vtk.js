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

## Status (student's real-GPU shots, taken 2026-10-26 on Intel Iris Xe, Chrome, 1593x934 view)

Originals are in `screenshots/` (timestamped names); copies with final names are in `report/figures/`.

| Shot | Status | Note |
| --- | --- | --- |
| `a_preset_grayscale.png`, `a_preset_bone.png`, `a_preset_vessel.png` | done | foot (Grayscale, Bone) and aneurism (Vessel); WebGL renderer string visible in the panel |
| `a_slice.png` | done | tooth, slice axis J index 47, volume hidden; `a_slice_with_volume.png` is the same with volume shown |
| `a_fps_overlay.png` | done | aneurism, Mean 39 / Current 43 after interaction |
| `b_remote.png`, `b_local.png` | done | wavelet 128, iso 160; stats card shows mode and "Last update" |
| `b_stats_panel.png` | **missing** | `b_orbit_terminal.png` shows only the terminal orbit line, not the card after an orbit |
| `b_devtools_ws.png` | **missing** | DevTools Network > WS during a 10 s orbit |

Facts visible in the shots that the report can cite: Showcase A on 256^3 foot/aneurism holds 39-46 fps mean at 1593x934 (tooth 1.5 M voxels: 60); load times 142-289 ms; GPU memory 16.8 MB (256^3) vs 1.6 MB (tooth).
