#!/usr/bin/env bash
# Showcase B without ParaView (plain VTK + trame, .venv Python) at http://localhost:8081
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[ -x .venv/bin/python ] || { echo ".venv missing: run scripts/setup.sh --no-paraview"; exit 1; }
echo "Showcase B fallback: http://localhost:8081"
exec .venv/bin/python showcase-b/app_vtk.py --port 8081 --server "$@"
