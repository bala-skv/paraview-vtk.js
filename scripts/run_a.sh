#!/usr/bin/env bash
# Start Showcase A (Vite dev server) at http://localhost:5173
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/showcase-a"
[ -d node_modules ] || { echo "node_modules missing: run scripts/setup.sh (or 'npm ci' in showcase-a)"; exit 1; }
[ -f public/data/index.json ] || echo "WARNING: no datasets in showcase-a/public/data. Run scripts/setup.sh first."
echo "Showcase A: http://localhost:5173"
exec npm run dev -- --port 5173 "$@"
