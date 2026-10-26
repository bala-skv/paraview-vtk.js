2026-10-26 | M0 | PASS (ParaView 6.2.0 installed, check_env OK in both venvs, cone + trame example OK) | none
2026-10-26 | M1 | PASS (headsq replaced by wavelet_smoke, see install_log) | none
2026-10-26 | M2 | PASS except: Firefox check not done (headless inconclusive), FPS-overlay live update and drag-drop only verified by code/screenshot, not by real mouse in a GPU browser. Nothing cut | student to eyeball in real Chrome/Edge
2026-10-26 | M3 | PASS (remote+local, sizes 64/128/256, server_events.csv rows, orbit, fallback). Needed trame-vtk PDC serializer workaround, see install_log | none
2026-10-26 | M4 tools | DONE (protocol.md, add_row.py, plot_results.py, auto_b.mjs); M4 itself WAITING for student's GPU runs | results.csv empty
2026-10-26 | M5 | PASS on Linux (clean-room 2m10s). setup.ps1/run_*.ps1 written but untested (no PowerShell here) | student: run README literally once, ideally also on Windows
2026-10-26 | M6 | scaffolding DONE (all files in report table exist); figures from benchmark pending M4; references 2 and 3 only partly verified, see references.md | student to review
2026-10-26 | M4 (A-local) | 9 rows imported (laptop-a, hardware Iris Xe, Chrome 151); 3 stale rows from an earlier test (machine_id=laptop) excluded | B-local and B-remote runs still to do
