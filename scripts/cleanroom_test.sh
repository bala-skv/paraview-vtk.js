#!/usr/bin/env bash
# Automated clean-room test: fresh clone -> setup.sh -> start A, B, B-fallback -> HTTP smoke checks.
#   export PVPYTHON=/path/to/pvpython
#   scripts/cleanroom_test.sh [REPO]            REPO = git URL or local path (default: origin of this repo)
# Env: DATA_FROM=<dir with *.raw>  copy datasets instead of downloading (the data host can be slow)
#      PORT=8098                   port for Showcase B (A uses 5173, fallback 8081)
# Prints a PASS/FAIL table and a timing line you can paste into report/install_log.md.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${1:-$(git -C "$HERE" remote get-url origin)}"
export PORT="${PORT:-8098}"
DEST="$(mktemp -d)/cleanroom"
RES=(); PIDS=()
t_start=$SECONDS
note() { RES+=("| $1 | $2 |"); echo "[$2] $1"; }
cleanup() { for p in "${PIDS[@]:-}"; do [ -n "$p" ] && { kill -- "-$p" 2>/dev/null; pkill -P "$p" 2>/dev/null; kill "$p" 2>/dev/null; }; done; for port in 5173 "$PORT" 8081; do fuser -k "$port/tcp" >/dev/null 2>&1; done; }
trap cleanup EXIT
wait_http() { for _ in $(seq 1 90); do curl -s -o /dev/null "$1" && return 0; sleep 1; done; return 1; }
busy() { (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null || (exec 3<>"/dev/tcp/::1/$1") 2>/dev/null; }

echo "Cloning $REPO -> $DEST"
git clone -q "$REPO" "$DEST" || { echo "clone failed"; exit 1; }
cd "$DEST"
[ -n "${DATA_FROM:-}" ] && { mkdir -p data/raw && cp "$DATA_FROM"/*.raw data/raw/ && echo "copied datasets from $DATA_FROM"; }

t=$SECONDS
if scripts/setup.sh >setup.log 2>&1; then note "setup.sh ($((SECONDS - t)) s)" PASS; else note "setup.sh (see $DEST/setup.log)" FAIL; tail -15 setup.log; fi

PV="${PVPYTHON:-$(command -v pvpython || true)}"
if [ -n "$PV" ] && "$PV" --venv .pvenv scripts/check_env.py --pv >/dev/null 2>&1; then note "check_env --pv" PASS; else note "check_env --pv" FAIL; fi
if .venv/bin/python scripts/check_env.py --tools >/dev/null 2>&1; then note "check_env --tools" PASS; else note "check_env --tools" FAIL; fi

for spec in "A|5173|scripts/run_a.sh|/" "B|$PORT|scripts/run_b.sh|/" "B-fallback|8081|scripts/run_b_fallback.sh|/"; do
  IFS='|' read -r name port cmd path <<<"$spec"
  if busy "$port"; then note "start $name: port $port already in use (stop the stale server)" FAIL; continue; fi
  setsid $cmd >"run_$name.log" 2>&1 & PIDS+=($!)
  if wait_http "http://localhost:$port$path"; then note "start $name on :$port" PASS; else note "start $name on :$port (see $DEST/run_$name.log)" FAIL; fi
done

if curl -s "http://localhost:5173/data/index.json" | grep -q foot; then note "A serves dataset index (foot present)" PASS; else note "A serves dataset index" FAIL; fi
if curl -sL "http://localhost:$PORT/" | grep -qi "trame"; then note "B serves trame page" PASS; else note "B serves trame page" FAIL; fi

echo; echo "| step | result |"; echo "|---|---|"; printf '%s\n' "${RES[@]}"
echo; echo "total $((SECONDS - t_start)) s; clone kept at $DEST"
printf '%s\n' "${RES[@]}" | grep -q FAIL && exit 1 || exit 0
