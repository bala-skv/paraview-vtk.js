# Start Showcase B (ParaView + trame) at http://localhost:8080. Extra args pass through.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$pv = $env:PVPYTHON
if (-not $pv) { $c = Get-Command pvpython -ErrorAction SilentlyContinue; if ($c) { $pv = $c.Source } }
if (-not $pv) { $d = 'C:\Program Files\ParaView 6.2.0\bin\pvpython.exe'; if (Test-Path $d) { $pv = $d } }
if (-not $pv -or -not (Test-Path $pv)) {
  Write-Host 'pvpython not found. Install ParaView 6.2.0, then set it, e.g.:'
  Write-Host '  $env:PVPYTHON = "C:\Program Files\ParaView 6.2.0\bin\pvpython.exe"'
  exit 1
}
if (-not (Test-Path '.pvenv')) { Write-Host '.pvenv missing: run scripts\setup.ps1'; exit 1 }
Write-Host 'Showcase B: http://localhost:8080'
# --venv must come BEFORE the script path
& $pv --venv .pvenv showcase-b/app.py --port 8080 --server @args
