"""Write bench/results/sysinfo.json (OS, CPU, RAM, GPU, versions). Run in .venv."""
import json
import os
import platform
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import psutil

OUT = Path(__file__).parent / "results" / "sysinfo.json"


def ver(pkg):
    try:
        return metadata.version(pkg)
    except metadata.PackageNotFoundError:
        return None


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return ""


def gpu():
    if sys.platform.startswith("linux") and shutil.which("lspci"):
        lines = [l for l in run(["lspci"]).splitlines() if "VGA" in l or "3D controller" in l]
        return lines or ["unknown"]
    if sys.platform == "win32":
        out = run(["powershell", "-NoProfile", "-Command",
                   "(Get-CimInstance Win32_VideoController).Name"])
        return out.splitlines() or ["unknown"]
    return ["unknown"]


def cpu():
    if sys.platform.startswith("linux"):
        for l in Path("/proc/cpuinfo").read_text().splitlines():
            if l.startswith("model name"):
                return l.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def paraview_version():
    pv = os.environ.get("PVPYTHON") or shutil.which("pvpython")
    if not pv:
        return None
    return run([pv, "-c", "import paraview; print(paraview.__version__)"]) or None


info = {
    "os": platform.platform(),
    "wsl": "microsoft" in platform.release().lower(),
    "cpu": cpu(),
    "cores_logical": psutil.cpu_count(),
    "ram_gb": round(psutil.virtual_memory().total / 2**30, 1),
    "gpu": gpu(),
    "python": sys.version.split()[0],
    "node": run(["node", "--version"]),
    "npm": run(["npm", "--version"]),
    "paraview": paraview_version(),
    "packages": {p: ver(p) for p in ["vtk", "numpy", "pandas", "matplotlib", "trame",
                                     "trame-vtk", "trame-vuetify", "psutil"]},
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(info, indent=2) + "\n")
print(json.dumps(info, indent=2))
print(f"wrote {OUT}")
