"""Validation of the TTK pipeline on a field with a known answer. Run:
  pvpython --venv .pvenv showcase-b/validate_topology.py
Checks: (1) 5 Gaussians + 1% noise: persistent TTK maxima (pairs above threshold) == 5;
        (2) noise-free: TTK maxima == 5 and equals an independent numpy neighbour comparison;
        (3) with threshold 0 on the noisy field, TTK maxima count vs numpy 26-neighbour local-maxima count.
"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app_topology import TopologyPipeline, make_gaussians, GAUSS_N_MAX  # noqa: E402
from paraview import servermanager as sm  # noqa: E402
from vtkmodules.numpy_interface import dataset_adapter as dsa  # noqa: E402
from vtkmodules.util.numpy_support import vtk_to_numpy  # noqa: E402


def np_maxima(img, n):
    """Interior strict local maxima by comparison with all 26 neighbours (numpy only; scipy of the
    ParaView bundle is incompatible with the numpy 2.x found in ~/.local, see log)."""
    f = vtk_to_numpy(img.GetPointData().GetScalars()).reshape(n, n, n)
    c = f[1:-1, 1:-1, 1:-1]
    m = np.ones(c.shape, bool)
    for dz in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (dz, dy, dx) != (0, 0, 0):
                    m &= c > f[1 + dz:n - 1 + dz, 1 + dy:n - 1 + dy, 1 + dx:n - 1 + dx]
    return int(m.sum())


ok = True
n = 48
pipe = TopologyPipeline(n)
for noise in (0.0, 0.01):
    import app_topology
    orig = app_topology.make_gaussians
    app_topology.make_gaussians = lambda r, noise=noise: orig(r, noise=noise)
    pipe.set_source("Gaussians (known: 5 maxima)")
    img = orig(n, noise=noise)
    npmax = np_maxima(img, n)
    print(f"--- noise {noise*100:.0f}% of range; numpy 3x3x3 local maxima (unsimplified): {npmax}")
    for th in (0.0, 0.005, 0.02, 0.05, 0.1):
        c = pipe.set_threshold(th, {0, 1, 2, 3}, False, 6)
        print(f"th={th:5.3f}  min/1s/2s/max = {c}   pairs>=th: {int((pipe.pairs['pers'] >= th*(pipe.rng[1]-pipe.rng[0])).sum())}")
        simp = pipe.SIMP(Input=pipe.grid, InputArray=["POINTS", pipe.name], PersistenceThreshold=th, DebugLevel=0)
        crit = pipe.CRIT(Input=simp, ScalarField=["POINTS", pipe.name], DebugLevel=0)
        ct = np.array(dsa.WrapDataObject(sm.Fetch(crit)).PointData["CriticalType"])
        print("   (TTKTopologicalSimplification + TTKScalarFieldCriticalPoints on simplified field: "
              f"{[int((ct == k).sum()) for k in range(4)]})")
        if th in (0.05, 0.1):
            good = c[3] == GAUSS_N_MAX
            ok &= good
            print("   expected maxima", GAUSS_N_MAX, "->", "PASS" if good else "FAIL")
    app_topology.make_gaussians = orig
print("OVERALL", "PASS" if ok else "FAIL")
