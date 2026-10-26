# One-shot, idempotent setup. Flags: -SkipData (skip step 8), -NoParaview (skip steps 3-5).
# If scripts are blocked:  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
param([switch]$SkipData, [switch]$NoParaview)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Step($m) { Write-Host ""; Write-Host "== $m" }
function Die($m) { Write-Host "ERROR: $m" -ForegroundColor Red; exit 1 }
function Run($exe, $argList) {
  & $exe @argList
  if ($LASTEXITCODE -ne 0) { Die "command failed: $exe $($argList -join ' ')" }
}

if ($root -match 'OneDrive' -or $root -match ' ') {
  Write-Host 'WARNING: repo is in OneDrive or a path with spaces; Vite file watching can break. Consider C:\dev\.' -ForegroundColor Yellow
}

Step '1/9 Node + npm'
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Die 'node not found. Install Node 22+ from https://nodejs.org' }
$nodeMajor = [int](node -p 'process.versions.node.split(".")[0]')
if ($nodeMajor -lt 22) { Die "Node $nodeMajor found, need 22+" }
$npmMajor = [int]((npm --version).Split('.')[0])
if ($npmMajor -lt 10) { Die "npm $npmMajor found, need 10+" }
Write-Host "node $(node --version), npm $(npm --version)"

Step '2/9 Python 3.12'
$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3.12 --version 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { $py = @('py', '-3.12') }
}
if (-not $py) { Die 'Python 3.12 not found (py -3.12). Install it from python.org; it must match ParaView''s bundled Python.' }
Write-Host "using $(& $py[0] $py[1] --version)"

$pv = $null
if (-not $NoParaview) {
  Step '3/9 pvpython'
  $pv = $env:PVPYTHON
  if (-not $pv) { $c = Get-Command pvpython -ErrorAction SilentlyContinue; if ($c) { $pv = $c.Source } }
  if (-not $pv) { $d = 'C:\Program Files\ParaView 6.2.0\bin\pvpython.exe'; if (Test-Path $d) { $pv = $d } }
  if (-not $pv -or -not (Test-Path $pv)) {
    Write-Host 'pvpython not found. Install ParaView 6.2.0 from https://www.paraview.org/download/, then:'
    Write-Host '  $env:PVPYTHON = "C:\Program Files\ParaView 6.2.0\bin\pvpython.exe"'
    Write-Host 'or re-run with -NoParaview for a fallback-only setup.'
    exit 1
  }
  Write-Host "pvpython: $pv"

  Step '4/9 Python minor version match'
  $pvv = (& $pv -c 'import sys;print("%d.%d" % sys.version_info[:2])' | Select-Object -Last 1).Trim()
  if ($pvv -ne '3.12') { Die "pvpython uses Python $pvv but the venv would use 3.12." }
  Write-Host "pvpython Python $pvv == 3.12"

  Step '5/9 .pvenv (setup\requirements-pv.txt)'
  if (-not (Test-Path '.pvenv\Scripts\python.exe')) { Run $py[0] ($py[1..($py.Length-1)] + @('-m', 'venv', '.pvenv')) }
  Run '.pvenv\Scripts\python.exe' @('-m', 'pip', 'install', '-q', '-r', 'setup\requirements-pv.txt')
  Write-Host '.pvenv ready'
}

Step '6/9 .venv (setup\requirements-tools.txt)'
if (-not (Test-Path '.venv\Scripts\python.exe')) { Run $py[0] ($py[1..($py.Length-1)] + @('-m', 'venv', '.venv')) }
Run '.venv\Scripts\python.exe' @('-m', 'pip', 'install', '-q', '-r', 'setup\requirements-tools.txt')
Write-Host '.venv ready'

Step '7/9 npm ci (showcase-a)'
Push-Location showcase-a
try { Run 'npm' @('ci', '--no-audit', '--no-fund') } finally { Pop-Location }

if (-not $SkipData) {
  Step '8/9 data: fetch + convert'
  Run '.venv\Scripts\python.exe' @('data\fetch_data.py')
  Run '.venv\Scripts\python.exe' @('data\raw_to_vti.py', '--smoke', '--all')
} else { Step '8/9 data skipped (-SkipData)' }

Step '9/9 check_env'
Run '.venv\Scripts\python.exe' @('scripts\check_env.py', '--tools')
if (-not $NoParaview) { Run $pv @('--venv', '.pvenv', 'scripts\check_env.py', '--pv') }

Write-Host ''
Write-Host 'Setup done. Run:'
Write-Host '  scripts\run_a.ps1            # Showcase A  http://localhost:5173'
if (-not $NoParaview) { Write-Host '  scripts\run_b.ps1            # Showcase B  http://localhost:8080' }
Write-Host '  scripts\run_b_fallback.ps1   # Showcase B without ParaView  http://localhost:8081'
