"""Showcase B: ParaView + trame. Run with pvpython, venv flag BEFORE the script:

  pvpython --venv .pvenv showcase-b/app.py --port 8080 --server [--size 128] [--mode remote|local]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from paraview import simple  # noqa: E402
from trame.app import get_server  # noqa: E402
from trame.widgets import paraview as pv_widgets  # noqa: E402

from trame_vtk.modules.vtk.serializers.data import merge_to_polydata_serializer  # noqa: E402
from trame_vtk.modules.vtk.serializers.registry import register_instance_serializer  # noqa: E402

from ui import ShowcaseApp  # noqa: E402

# FINDING (see report/install_log.md): ParaView 6.2 mappers take a vtkPartitionedDataSetCollection,
# which trame-vtk 2.11.17 has no serializer for. Without this line every actor is silently
# dropped and *local* rendering shows an empty scene (remote rendering is unaffected).
register_instance_serializer("vtkPartitionedDataSetCollection", merge_to_polydata_serializer)


VTI_DIR = Path(__file__).resolve().parent.parent / "data" / "vti"
OUT_DIR = Path(__file__).resolve().parent / "out"
COLORMAPS = ["Cool to Warm", "Viridis", "Inferno", "Turbo", "Jet", "Grayscale", "X Ray",
             "Rainbow Uniform", "Black-Body Radiation"]
KINDS = ["Contour", "Slice", "Clip", "Threshold", "Streamlines", "Glyph"]
# defaults for the feature controls (ui.py mirrors these in trame state)
DEFAULTS = {"kind": "Contour", "source": "Wavelet", "vti": "", "axis": "Z", "offset": 0.0,
            "thr_lo": 0.3, "thr_hi": 0.7, "color_by": "Solid Color", "cmap": "Cool to Warm",
            "auto_range": True, "rmin": 0.0, "rmax": 1.0, "bar": False, "volume": False}


class ParaViewPipeline:
    """Source (Wavelet or .vti) -> one of Contour/Slice/Clip/Threshold/Streamlines/Glyph -> Show -> Render.

    Filters are created lazily and only the active one is shown. Streamlines/Glyph need a vector, so
    they read Gradient(source) (Wavelet has no vector array). Everything runs on the server.
    """
    features = True

    def __init__(self, size, iso=157.0):
        self.size, self.iso, self.representation = size, iso, "Surface"
        self.params = dict(DEFAULTS)
        self.wavelet = simple.Wavelet()
        self.source = self.wavelet
        self._set_extent()
        self.view = simple.GetActiveViewOrCreate("RenderView")
        self.view.OrientationAxesVisibility = 1
        self.filters, self.displays, self.vol_display = {}, {}, None
        self.grad = None
        self.contour = self._filter("Contour")  # existing attribute used by stats()/set_iso()
        self.active = "Contour"
        self.display = self.displays["Contour"] = simple.Show(self.contour, self.view)
        simple.ColorBy(self.display, None)
        self.display.Representation = self.representation
        self.reset_camera()

    # ---- source -------------------------------------------------------
    def _set_extent(self):
        h = self.size // 2
        self.wavelet.WholeExtent = [-h, h - 1, -h, h - 1, -h, h - 1]

    def vti_files(self):
        return sorted(p.name for p in VTI_DIR.glob("*.vti"))

    def _scalar(self):
        """Name and (lo, hi) range of the first point array of the source."""
        self.source.UpdatePipeline()
        for a in self.source.PointData:
            return a.GetName(), tuple(a.GetRange())
        return "RTData", (0.0, 1.0)

    def _use_source(self, kind, vti):
        want = self.wavelet if kind == "Wavelet" else None
        if kind != "Wavelet":
            if getattr(self, "_vti_name", None) != vti:
                self._vti_name = vti
                self._vti = simple.XMLImageDataReader(FileName=str(VTI_DIR / vti))
            want = self._vti
        if want is self.source:
            return False
        self.source = want
        for f in reversed(list(self.filters.values())):
            simple.Delete(f)
        if self.grad is not None:
            simple.Delete(self.grad)
        self.filters, self.displays, self.grad = {}, {}, None
        if self.vol_display is not None:
            self.vol_display.Visibility = 0
            self.vol_display = None
        return True

    # ---- filters ------------------------------------------------------
    def _gradient(self):
        if self.grad is None:
            name, _ = self._scalar()
            self.grad = simple.Gradient(Input=self.source, ScalarArray=["POINTS", name])
        return self.grad

    def _filter(self, kind):
        if kind in self.filters:
            return self.filters[kind]
        name, (lo, hi) = self._scalar()
        src = self.source
        if kind == "Contour":
            f = simple.Contour(Input=src, ContourBy=["POINTS", name], Isosurfaces=[self.iso])
        elif kind == "Slice":
            f = simple.Slice(Input=src, SliceType="Plane")
        elif kind == "Clip":
            f = simple.Clip(Input=src, ClipType="Plane")
        elif kind == "Threshold":
            f = simple.Threshold(Input=src, Scalars=["POINTS", name],
                                 LowerThreshold=lo, UpperThreshold=hi)
        elif kind == "Streamlines":
            g = self._gradient()
            f = simple.StreamTracer(Input=g, Vectors=["POINTS", "Gradient"], SeedType="Point Cloud")
        elif kind == "Glyph":
            g = self._gradient()
            f = simple.Glyph(Input=g, GlyphType="Arrow", OrientationArray=["POINTS", "Gradient"],
                             ScaleArray=["POINTS", "No scale array"])
        self.filters[kind] = f
        return f

    def _configure(self, kind, p):
        f = self._filter(kind)
        name, (lo, hi) = self._scalar()
        b = self.source.GetDataInformation().GetBounds()
        ctr = [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2]
        ax = "XYZ".index(p["axis"])
        normal = [0.0, 0.0, 0.0]
        normal[ax] = 1.0
        span = b[2 * ax + 1] - b[2 * ax]
        origin = list(ctr)
        origin[ax] = ctr[ax] + p["offset"] * span / 2  # offset in [-1, 1] of half-extent
        if kind == "Contour":
            f.ContourBy = ["POINTS", name]
            f.Isosurfaces = [self.iso]
        elif kind in ("Slice", "Clip"):
            plane = f.SliceType if kind == "Slice" else f.ClipType
            plane.Origin, plane.Normal = origin, normal
        elif kind == "Threshold":
            f.Scalars = ["POINTS", name]
            f.LowerThreshold = lo + p["thr_lo"] * (hi - lo)
            f.UpperThreshold = lo + p["thr_hi"] * (hi - lo)
        elif kind == "Streamlines":
            f.SeedType.Center = ctr
            f.SeedType.Radius = (b[1] - b[0]) / 2
            f.SeedType.NumberOfPoints = 150
            f.MaximumStreamlineLength = b[1] - b[0]
            f.IntegrationDirection = "BOTH"
        elif kind == "Glyph":
            f.ScaleFactor = (b[1] - b[0]) / 12
            f.GlyphMode = "Uniform Spatial Distribution (Bounds Based)"
            f.MaximumNumberOfSamplePoints = 400
        return f

    # ---- apply (called by ui.py with the full feature-parameter dict) ----
    def apply(self, p):
        """Idempotent: make the scene match dict p. Returns {arrays, range, source_array, iso_range}."""
        changed_src = self._use_source(p["source"], p["vti"])
        kind = p["kind"]
        f = self._configure(kind, p)
        key = kind
        if kind == "Contour":
            # the isosurface only carries the contoured array (constant on the surface), so add an
            # Elevation array to give colour-by something to show; the bench path never gets here
            if "Elevation" not in self.filters:
                self.filters["Elevation"] = simple.Elevation(Input=f)
            b = self.source.GetDataInformation().GetBounds()
            self.filters["Elevation"].LowPoint = [0, 0, b[4]]
            self.filters["Elevation"].HighPoint = [0, 0, b[5]]
            f, key = self.filters["Elevation"], "ContourE"
        for k, d in list(self.displays.items()):
            if k != key:
                d.Visibility = 0
                d.SetScalarBarVisibility(self.view, False)
        self.contour = f
        self.active = kind
        disp = self.displays.get(key)
        if disp is None:
            disp = self.displays[key] = simple.Show(f, self.view)
        disp.Visibility = 1
        self.display = disp
        disp.Representation = self.representation
        f.UpdatePipeline()
        # colour
        arrays = ["Solid Color"] + [a.GetName() for a in f.PointData]
        cb = p["color_by"] if p["color_by"] in arrays else "Solid Color"
        if cb == "Solid Color":
            simple.ColorBy(disp, None)
        else:
            ncomp = f.PointData[cb].GetNumberOfComponents()
            simple.ColorBy(disp, ("POINTS", cb, "Magnitude") if ncomp > 1 else ("POINTS", cb))
            lut = simple.GetColorTransferFunction(cb)
            lut.ApplyPreset(p["cmap"], True)
            if p["auto_range"]:
                lut.AutomaticRescaleRangeMode = "Grow and update on 'Apply'"
                disp.RescaleTransferFunctionToDataRange(False, True)
            else:
                lut.AutomaticRescaleRangeMode = "Never"
                lut.RescaleTransferFunction(p["rmin"], p["rmax"])
        disp.SetScalarBarVisibility(self.view, bool(p["bar"]) and cb != "Solid Color")
        # server-side volume rendering of the source (additive to the filter output)
        self._volume(bool(p["volume"]))
        self.params = dict(p)
        self._render()
        name, (lo, hi) = self._scalar()
        rng = [lo, hi] if cb == "Solid Color" else list(f.PointData[cb].GetRange(-1 if f.PointData[cb].GetNumberOfComponents() > 1 else 0))
        return {"arrays": arrays, "color_by": cb, "range": rng, "iso_range": [lo, hi],
                "source_array": name, "changed_source": changed_src}

    def _volume(self, on):
        if self.vol_display is None and not on:
            return
        if self.vol_display is None:
            self.vol_display = simple.Show(self.source, self.view)
            name, _ = self._scalar()
            simple.ColorBy(self.vol_display, ("POINTS", name))
        self.vol_display.Representation = "Volume" if on else "Outline"
        self.vol_display.Visibility = 1 if on else 0

    # ---- screenshot / state ----------------------------------------------
    def screenshot(self, path, size=(1000, 700)):
        simple.SaveScreenshot(str(path), self.view, ImageResolution=list(size))

    def save_pvsm(self, path):
        simple.SaveState(str(path))

    # ---- original interface -----------------------------------------------
    def set_iso(self, value):
        self.iso = value
        if "Contour" in self.filters:
            self.filters["Contour"].Isosurfaces = [value]
        self._render()

    def set_size(self, size):
        self.size = size
        self._set_extent()
        self._render()

    def set_representation(self, name):
        self.representation = name
        self.display.Representation = name
        self._render()

    def _render(self):
        self.contour.UpdatePipeline()
        simple.Render(self.view)

    def stats(self):
        info = self.contour.GetDataInformation()
        return int(info.GetNumberOfCells()), int(info.GetMemorySize())

    def azimuth(self, deg):
        self.view.GetActiveCamera().Azimuth(deg)
        simple.Render(self.view)

    def reset_camera(self):
        simple.ResetCamera(self.view)
        simple.Render(self.view)


def main():
    server = get_server(client_type="vue3")
    server.cli.add_argument("--size", type=int, default=128, choices=[64, 128, 256, 384])
    server.cli.add_argument("--mode", default="remote", choices=["remote", "local"])
    args, _ = server.cli.parse_known_args()
    pipeline = ParaViewPipeline(args.size)
    ShowcaseApp(server, pipeline, pv_widgets, source="wavelet",
                title="Showcase B: trame + ParaView", initial_mode=args.mode)
    server.start()


if __name__ == "__main__":
    main()
