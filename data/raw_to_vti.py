"""Convert raw volumes to .vti for vtk.js. Run in .venv.

  python data/raw_to_vti.py --name foot [--resize 64 128 384] [--compress zlib|none|raw]
  python data/raw_to_vti.py --all
  python data/raw_to_vti.py --smoke        # generated wavelet, no download needed

Writes data/vti/*.vti, copies them to showcase-a/public/data/ and rewrites index.json there.
"""
import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import vtk
from vtk.util import numpy_support as ns

HERE = Path(__file__).parent
VTI = HERE / "vti"
PUBLIC = HERE.parent / "showcase-a" / "public" / "data"
DTYPES = {"uint8": np.uint8, "uint16": np.uint16, "int16": np.int16, "float32": np.float32}


def load_manifest():
    return {d["name"]: d for d in json.loads((HERE / "manifest.json").read_text())["datasets"]}


def make_image(arr_zyx, spacing):
    z, y, x = arr_zyx.shape
    img = vtk.vtkImageData()
    img.SetDimensions(x, y, z)
    img.SetSpacing(*spacing)
    vt = ns.numpy_to_vtk(arr_zyx.ravel(order="C"), deep=True)
    vt.SetName("scalars")
    img.GetPointData().SetScalars(vt)
    return img


def resized(img, n):
    dims = img.GetDimensions()
    sp = img.GetSpacing()
    r = vtk.vtkImageResize()
    r.SetInputData(img)
    r.SetOutputDimensions(n, n, n)
    r.InterpolateOn()
    r.Update()
    out = vtk.vtkImageData()
    out.DeepCopy(r.GetOutput())
    # keep the physical extent of the source
    out.SetSpacing(*[sp[i] * (dims[i] - 1) / (n - 1) for i in range(3)])
    out.GetPointData().GetScalars().SetName("scalars")
    return out


def write(img, name, compress):
    VTI.mkdir(exist_ok=True)
    path = VTI / f"{name}.vti"
    w = vtk.vtkXMLImageDataWriter()
    w.SetFileName(str(path))
    w.SetInputData(img)
    if compress == "zlib":
        w.SetDataModeToBinary()
        w.SetCompressorTypeToZLib()
    elif compress == "none":
        w.SetDataModeToBinary()
        w.SetCompressorTypeToNone()
    else:  # raw appended
        w.SetDataModeToAppended()
        w.EncodeAppendedDataOff()
        w.SetCompressorTypeToNone()
    if w.Write() != 1:
        raise SystemExit(f"FAIL: could not write {path}")
    print(f"wrote {path.relative_to(HERE.parent)} ({path.stat().st_size / 1e6:.2f} MB)")
    return path


def rebuild_index():
    entries = []
    for p in sorted(VTI.glob("*.vti")):
        r = vtk.vtkXMLImageDataReader()
        r.SetFileName(str(p))
        r.Update()
        img = r.GetOutput()
        d = img.GetDimensions()
        lo, hi = img.GetPointData().GetScalars().GetRange()
        entries.append({"name": p.stem, "file": p.name, "dims": list(d),
                        "voxels": d[0] * d[1] * d[2], "range": [lo, hi],
                        "spacing": list(img.GetSpacing())})
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for p in VTI.glob("*.vti"):
        shutil.copy2(p, PUBLIC / p.name)
    (PUBLIC / "index.json").write_text(json.dumps(entries, indent=2) + "\n")
    print(f"index.json: {[e['name'] for e in entries]}")


def convert(ds, sizes, compress):
    raw = HERE / "raw" / ds["url"].rsplit("/", 1)[1]
    x, y, z = ds["dims"]
    arr = np.fromfile(raw, dtype=np.dtype(DTYPES[ds["dtype"]]).newbyteorder("<")).reshape(z, y, x)
    img = make_image(arr.astype(DTYPES[ds["dtype"]], copy=False), ds["spacing"])
    write(img, ds["name"], compress)
    for n in sizes:
        if n == x == y == z:
            write(img, f"{ds['name']}_{n}", compress)
        else:
            write(resized(img, n), f"{ds['name']}_{n}", compress)


def smoke(compress):
    src = vtk.vtkRTAnalyticSource()
    src.SetWholeExtent(0, 63, 0, 63, 0, 63)
    src.Update()
    img = vtk.vtkImageData()
    img.DeepCopy(src.GetOutput())
    img.GetPointData().GetScalars().SetName("scalars")
    write(img, "wavelet_smoke", compress)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name")
    ap.add_argument("--all", action="store_true", help="every dataset; foot gets --resize 64 128 256")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--resize", type=int, nargs="*", default=[])
    ap.add_argument("--compress", choices=["zlib", "none", "raw"], default="zlib")
    a = ap.parse_args()
    m = load_manifest()
    if a.smoke:
        smoke(a.compress)
    if a.all:
        for name, ds in m.items():
            convert(ds, [64, 128, 256] if name == "foot" else [], a.compress)
    elif a.name:
        convert(m[a.name], a.resize, a.compress)
    rebuild_index()


if __name__ == "__main__":
    main()
