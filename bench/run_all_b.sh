#!/usr/bin/env bash
# Run every Showcase B benchmark cell (2 modes x 3 sizes x 3 reps) and append validated rows.
#   export PVPYTHON=...   (path to pvpython)
#   GPU="ANGLE (Intel, Mesa Intel(R) Iris(R) Xe Graphics (TGL GT2), OpenGL ES 3.2)" MACHINE=laptop-a \
#     bench/run_all_b.sh [--headless] [--chrome /usr/bin/google-chrome]
# Env: SIZES="64 128 256"  MODES="local remote"  REPS=3  RESULTS=<csv path>  PORT=8080
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
SIZES="${SIZES:-64 128 256}"; MODES="${MODES:-local remote}"; REPS="${REPS:-3}"; PORT="${PORT:-8080}"
MACHINE="${MACHINE:-laptop-a}"; GPU="${GPU:?set GPU to your WebGL renderer string (chrome://gpu GL_RENDERER)}"
ROW_ARGS=(); [ -n "${RESULTS:-}" ] && ROW_ARGS=(--csv "$RESULTS")
[ -d bench/node_modules ] || (cd bench && npm ci --no-audit --no-fund)
LOG="$(mktemp)"
stop_server() { [ -n "${SRV:-}" ] && kill "$SRV" 2>/dev/null; wait "$SRV" 2>/dev/null; SRV=""; }
trap stop_server EXIT
for mode in $MODES; do
  for size in $SIZES; do
    echo "=== B-$mode size=$size: starting server"
    scripts/run_b.sh --size "$size" --mode "$mode" >"$LOG" 2>&1 & SRV=$!
    for _ in $(seq 1 60); do curl -s -o /dev/null "http://localhost:$PORT/" && break; sleep 1; done
    curl -s -o /dev/null "http://localhost:$PORT/" || { echo "server did not start; log:"; tail -20 "$LOG"; exit 1; }
    for rep in $(seq 1 "$REPS"); do
      line="$(cd bench && node auto_b.mjs --mode "$mode" --size "$size" --rep "$rep" --emit "$@" 2>/dev/null | grep '^RESULT ' | tail -1)"
      [ -n "$line" ] || { echo "rep $rep failed (no RESULT)"; continue; }
      RESULT_JSON="${line#RESULT }" .venv/bin/python - "$mode" "$size" "$rep" "$MACHINE" "$GPU" "${ROW_ARGS[@]}" <<'PY'
import json, subprocess, sys
mode, size, rep, machine, gpu, *extra = sys.argv[1:]
import os
o = json.loads(os.environ["RESULT_JSON"])
note = f"auto_b.mjs; {o['fps_source']}; ws_bytes_setup={o.get('ws_bytes_setup', '')}"
if o.get("orbit_report"): note += f"; orbit: {o['orbit_report']}"
cmd = [sys.executable, "bench/add_row.py", "--showcase", "B", "--condition", f"B-{mode}", "--dataset", "wavelet",
       "--size", size, "--rep", rep, "--ttfr-ms", str(o["ttfr_ms"]), "--fps-median", str(o["fps_median"]),
       "--fps-p5", str(o["fps_p5_min_of_1s_bins"]), "--client-mem-mb", str(o["client_mem_mb"]),
       "--server-rss-mb", str(o["server_rss_mb"]), "--ws-bytes", str(o["ws_bytes"]),
       "--triangles", str(o["triangles"]), "--geometry-kb", str(o["geometry_kb"]),
       "--browser", o["browser"], "--gpu-renderer", gpu, "--machine-id", machine, "--notes", note] + extra
subprocess.run(cmd, check=True)
PY
    done
    stop_server
  done
done
echo "Done. Next: .venv/bin/python bench/plot_results.py"
