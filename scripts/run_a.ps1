# Start Showcase A (Vite dev server) at http://localhost:5173
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root 'showcase-a')
if (-not (Test-Path 'node_modules')) { Write-Host "node_modules missing: run scripts\setup.ps1 (or 'npm ci' in showcase-a)"; exit 1 }
if (-not (Test-Path 'public/data/index.json')) { Write-Host 'WARNING: no datasets in showcase-a/public/data. Run scripts\setup.ps1 first.' }
Write-Host 'Showcase A: http://localhost:5173'
npm run dev -- --port 5173 @args
