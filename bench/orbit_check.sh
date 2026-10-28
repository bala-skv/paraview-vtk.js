#!/usr/bin/env bash
# Re-measure the server-side Benchmark orbit (180 steps x 2 deg, remote mode) at several browser
# viewport sizes, to find out whether render time depends on window size.
#   export PVPYTHON=...
#   bench/orbit_check.sh [--headless] [--chrome /path]        (default PORT=8099, SIZE=128)
# Also saves the Server stats card as report/figures/b_stats_panel.png (from the last run).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PORT="${PORT:-8099}"; SIZE="${SIZE:-128}"
VIEWPORTS="${VIEWPORTS:-640x480 1280x720 1593x934 1920x1080}"
if (exec 3<>"/dev/tcp/127.0.0.1/8080") 2>/dev/null; then
  echo "NOTE: something else is listening on :8080 (a stale Showcase B?). It competes for CPU and can distort timing; stop it for a clean result."
fi
[ -d bench/node_modules ] || (cd bench && npm ci --no-audit --no-fund)
LOG="$(mktemp)"
scripts/run_b.sh --size "$SIZE" --mode remote >"$LOG" 2>&1 & SRV=$!
trap 'kill $SRV 2>/dev/null; wait $SRV 2>/dev/null' EXIT
for _ in $(seq 1 60); do curl -s -o /dev/null "http://localhost:$PORT/" && break; sleep 1; done
curl -s -o /dev/null "http://localhost:$PORT/" || { echo "server did not start:"; tail -20 "$LOG"; exit 1; }
echo "load average before: $(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null)"
echo "| viewport | orbit report |"; echo "|---|---|"
for vp in $VIEWPORTS; do
  w="${vp%x*}"; h="${vp#*x}"
  line="$(cd bench && node auto_b.mjs --mode remote --size "$SIZE" --port "$PORT" --width "$w" --height "$h" \
          --shot "$ROOT/report/figures/b_stats_panel.png" --seconds 3 --emit "$@" 2>/dev/null | grep '^RESULT ' | tail -1)"
  rep="$(printf '%s' "${line#RESULT }" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("orbit_report","(none)"))' 2>/dev/null)"
  echo "| $vp | ${rep:-FAILED} |"
done
echo "server log orbit lines:"; grep "\[bench\] orbit" "$LOG"
