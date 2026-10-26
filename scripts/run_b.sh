#!/usr/bin/env bash
# Start Showcase B (ParaView + trame) at http://localhost:8080. Extra args are passed through
# (e.g. --size 256 --mode local --host 0.0.0.0).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PV="${PVPYTHON:-}"
if [ -z "$PV" ]; then PV="$(command -v pvpython || true)"; fi
if [ -z "$PV" ]; then PV="$(ls -d "$HOME"/opt/ParaView-6.2.0-*/bin/pvpython 2>/dev/null | head -n1 || true)"; fi
if [ -z "$PV" ] || [ ! -x "$PV" ]; then
  echo "pvpython not found. Install ParaView 6.2.0 and set it, e.g.:"
  echo "  export PVPYTHON=\$HOME/opt/ParaView-6.2.0-MPI-Linux-Python3.12-x86_64/bin/pvpython"
  exit 1
fi
[ -d .pvenv ] || { echo ".pvenv missing: run scripts/setup.sh"; exit 1; }
PORT="${PORT:-8080}"
if (exec 3<>"/dev/tcp/127.0.0.1/$PORT") 2>/dev/null; then
  echo "Port $PORT is already in use (an earlier Showcase B still running?)."
  echo "Stop it (Ctrl+C in its terminal, or: fuser -k $PORT/tcp) or use another port: PORT=8081 scripts/run_b.sh"
  exit 1
fi
echo "Showcase B: http://localhost:$PORT"
# --venv must come BEFORE the script path
exec "$PV" --venv .pvenv showcase-b/app.py --port "$PORT" --server "$@"
