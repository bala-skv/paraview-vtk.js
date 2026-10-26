#!/usr/bin/env bash
# One-shot, idempotent setup. Flags: --skip-data (skip step 8), --no-paraview (skip steps 3-5).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
SKIP_DATA=0; NO_PV=0
for a in "$@"; do case "$a" in --skip-data) SKIP_DATA=1;; --no-paraview) NO_PV=1;; *) echo "unknown flag $a"; exit 2;; esac; done
step() { echo; echo "== $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

case "$ROOT" in *" "*) echo "WARNING: path contains spaces; Vite's file watcher and some tools can misbehave. Consider moving the repo." ;; esac

step "1/9 Node + npm"
command -v node >/dev/null || die "node not found. Install Node 22+ (https://nodejs.org)"
NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
[ "$NODE_MAJOR" -ge 22 ] || die "Node $NODE_MAJOR found, need 22+"
NPM_MAJOR="$(npm --version | cut -d. -f1)"
[ "$NPM_MAJOR" -ge 10 ] || die "npm $NPM_MAJOR found, need 10+"
echo "node $(node --version), npm $(npm --version)"

step "2/9 Python 3.12"
PY=""
for c in python3.12 python3 python; do
  if command -v "$c" >/dev/null && [ "$("$c" -c 'import sys;print("%d.%d"%sys.version_info[:2])')" = "3.12" ]; then PY="$c"; break; fi
done
[ -n "$PY" ] || die "Python 3.12 not found (needed: it must match ParaView's bundled Python). Install python3.12 (+ python3.12-venv)."
echo "using $($PY --version) at $(command -v $PY)"

PV=""
if [ "$NO_PV" -eq 0 ]; then
  step "3/9 pvpython"
  PV="${PVPYTHON:-}"
  [ -n "$PV" ] || PV="$(command -v pvpython || true)"
  [ -n "$PV" ] || PV="$(ls -d "$HOME"/opt/ParaView-6.2.0-*/bin/pvpython 2>/dev/null | head -n1 || true)"
  if [ -z "$PV" ] || [ ! -x "$PV" ]; then
    echo "pvpython not found. Install ParaView 6.2.0 (https://www.paraview.org/download/), then:"
    echo "  export PVPYTHON=/path/to/ParaView-6.2.0-.../bin/pvpython"
    echo "or re-run with --no-paraview for a fallback-only setup."
    exit 1
  fi
  echo "pvpython: $PV"

  step "4/9 Python minor version match"
  PVV="$("$PV" -c 'import sys;print("%d.%d"%sys.version_info[:2])' | tail -n1)"
  [ "$PVV" = "3.12" ] || die "pvpython uses Python $PVV but the venv would use 3.12. Install a Python $PVV and edit this script."
  echo "pvpython Python $PVV == 3.12"

  step "5/9 .pvenv (setup/requirements-pv.txt)"
  [ -x .pvenv/bin/python ] || "$PY" -m venv .pvenv
  .pvenv/bin/python -m pip install -q -r setup/requirements-pv.txt
  echo ".pvenv ready"
fi

step "6/9 .venv (setup/requirements-tools.txt)"
[ -x .venv/bin/python ] || "$PY" -m venv .venv
.venv/bin/python -m pip install -q -r setup/requirements-tools.txt
echo ".venv ready"

step "7/9 npm ci (showcase-a)"
( cd showcase-a && npm ci --no-audit --no-fund )

if [ "$SKIP_DATA" -eq 0 ]; then
  step "8/9 data: fetch + convert"
  .venv/bin/python data/fetch_data.py
  .venv/bin/python data/raw_to_vti.py --smoke --all
else
  step "8/9 data skipped (--skip-data)"
fi

step "9/9 check_env"
.venv/bin/python scripts/check_env.py --tools
if [ "$NO_PV" -eq 0 ]; then "$PV" --venv .pvenv scripts/check_env.py --pv; fi

echo
echo "Setup done. Run:"
echo "  scripts/run_a.sh            # Showcase A  http://localhost:5173"
[ "$NO_PV" -eq 0 ] && echo "  scripts/run_b.sh            # Showcase B  http://localhost:8080"
echo "  scripts/run_b_fallback.sh   # Showcase B without ParaView  http://localhost:8081"
