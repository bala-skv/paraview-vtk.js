#!/usr/bin/env bash
# Register a Jupyter kernel that runs ParaView's pvpython with the .jvenv packages (extra E8).
# Usage: scripts/install_jupyter_kernel.sh   (PVPYTHON may point to pvpython; run from anywhere)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PV="${PVPYTHON:-$(command -v pvpython || true)}"
if [ -z "$PV" ]; then PV="$(ls -d "$HOME"/opt/ParaView-6.2.0-*/bin/pvpython 2>/dev/null | head -n1 || true)"; fi
[ -x "$PV" ] || { echo "pvpython not found; set PVPYTHON"; exit 1; }
D="$ROOT/.jvenv/share/jupyter/kernels/pvpython"
mkdir -p "$D"
cat > "$D/kernel.json" <<JSON
{"argv": ["$PV", "--venv", "$ROOT/.jvenv", "-m", "ipykernel_launcher", "--IPKernelApp.capture_fd_output=False", "-f", "{connection_file}"],
 "display_name": "ParaView 6.2 pvpython", "language": "python",
 "env": {"TRAME_BACKEND": "jupyter", "TRAME_IFRAME_BUILDER": "jupyter-extension"}}
JSON
echo "kernel written to $D"
