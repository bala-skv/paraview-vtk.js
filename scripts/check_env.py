"""Print environment versions and fail loudly on mismatch.

  pvpython --venv .pvenv scripts/check_env.py --pv
  .venv/bin/python scripts/check_env.py --tools
"""
import argparse
import sys
from importlib import metadata


def ver(pkg):
    try:
        return metadata.version(pkg)
    except metadata.PackageNotFoundError:
        return None


def show(pkgs):
    for p in pkgs:
        print(f"  {p:<14} {ver(p) or 'not installed'}")


def check_pv():
    print(f"Python {sys.version.split()[0]}")
    try:
        import paraview
        print(f"  paraview       {paraview.__version__}")
    except ImportError:
        print("FAIL: not running under pvpython (paraview not importable)")
        return 1
    show(["trame", "trame-vtk", "trame-vuetify", "psutil", "numpy"])
    if ver("vtk") is not None:
        print("FAIL: pip 'vtk' is installed in .pvenv; it conflicts with ParaView's bundled VTK."
              " Delete .pvenv and rebuild it from setup/requirements-pv.txt.")
        return 1
    missing = [p for p in ("trame", "trame-vtk", "trame-vuetify") if ver(p) is None]
    if missing:
        print(f"FAIL: missing in .pvenv: {missing}. Is --venv placed BEFORE the script path?")
        return 1
    print("OK")
    return 0


def check_tools():
    print(f"Python {sys.version.split()[0]}")
    if sys.version_info[:2] != (3, 12):
        print("WARN: project targets Python 3.12")
    show(["vtk", "numpy", "pandas", "matplotlib", "trame", "trame-vtk", "trame-vuetify", "psutil"])
    missing = [p for p in ("vtk", "numpy", "trame") if ver(p) is None]
    if missing:
        print(f"FAIL: missing in .venv: {missing}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pv", action="store_true")
    g.add_argument("--tools", action="store_true")
    a = ap.parse_args()
    sys.exit(check_pv() if a.pv else check_tools())
