# Showcase B without ParaView (plain VTK + trame, .venv Python) at http://localhost:8081
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$py = '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { Write-Host '.venv missing: run scripts\setup.ps1 -NoParaview'; exit 1 }
Write-Host 'Showcase B fallback: http://localhost:8081'
& $py showcase-b/app_vtk.py --port 8081 --server @args
