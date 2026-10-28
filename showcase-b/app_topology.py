"""Extra E9: topology analysis on the server with the Topology ToolKit (TTK) bundled in ParaView 6.2.

  pvpython --venv .pvenv showcase-b/app_topology.py --port 8120 --server [--res 48]

TTK filters used (real TTK 1.3.0, plugin "TopologyToolKit" shipped in the ParaView 6.2.0 binary):
  TTKPersistenceDiagram (EmbedinDomain=1) -> persistence pairs: chart (right) and, embedded in the domain,
                                             the critical points (min/saddle/max) of every pair
Critical points shown = end points of the pairs whose persistence >= slider * scalar range (selection done
with numpy on the server).  validate_topology.py also runs TTKTopologicalSimplificationByPersistence +
TTKScalarFieldCriticalPoints for comparison.
Everything is computed in the ParaView server process; the browser gets rendered images (VtkRemoteView)
and a small SVG string for the diagram.  Standalone: does not import app.py / ui.py.
"""
import sys
import time
from pathlib import Path

import numpy as np
from paraview import simple
from paraview import servermanager as sm
from vtkmodules.numpy_interface import dataset_adapter as dsa

VTI_DIR = Path(__file__).resolve().parent.parent / "data" / "vti"
# CriticalType in 3D: 0 minimum, 1 1-saddle, 2 2-saddle, 3 maximum
TYPES = [(0, "minimum", (0.20, 0.40, 1.00)), (1, "1-saddle", (0.10, 0.75, 0.30)),
         (2, "2-saddle", (1.00, 0.80, 0.10)), (3, "maximum", (1.00, 0.15, 0.15))]
GAUSS_CENTRES = [(0.2, 0.25, 0.3, 1.0, 0.10), (0.75, 0.2, 0.7, 0.8, 0.09), (0.5, 0.55, 0.5, 0.9, 0.08),
                 (0.25, 0.8, 0.75, 0.7, 0.10), (0.8, 0.78, 0.25, 0.6, 0.09)]  # x, y, z, height, sigma (unit cube)
GAUSS_N_MAX = len(GAUSS_CENTRES)


def load_ttk():
    simple.LoadPlugin("TopologyToolKit", remote=False, ns=globals())
    return globals()["TTKPersistenceDiagram"], globals()["TTKTopologicalSimplificationByPersistence"], \
        globals()["TTKScalarFieldCriticalPoints"]


def make_gaussians(n, noise=0.01, seed=1):
    """vtkImageData with a sum of GAUSS_N_MAX Gaussians (+ optional uniform noise, fraction of range)."""
    from vtkmodules.vtkCommonDataModel import vtkImageData
    from vtkmodules.util.numpy_support import numpy_to_vtk
    ax = np.linspace(0, 1, n)
    z, y, x = np.meshgrid(ax, ax, ax, indexing="ij")
    f = np.zeros((n, n, n))
    for cx, cy, cz, h, s in GAUSS_CENTRES:
        f += h * np.exp(-((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2) / (2 * s * s))
    f = f / f.max() * 100.0
    if noise > 0:
        f += np.random.default_rng(seed).uniform(-noise, noise, f.shape) * 100.0
    img = vtkImageData()
    img.SetDimensions(n, n, n)
    img.SetSpacing(1.0 / (n - 1), 1.0 / (n - 1), 1.0 / (n - 1))
    arr = numpy_to_vtk(f.astype(np.float32).ravel(), deep=True)  # x fastest = VTK order
    arr.SetName("field")
    img.GetPointData().SetScalars(arr)
    return img


class TopologyPipeline:
    def __init__(self, res=48):
        self.PD, self.SIMP, self.CRIT = load_ttk()  # SIMP/CRIT only used by validate_topology.py
        self.res = res
        self.view = simple.CreateView("RenderView")
        self.view.OrientationAxesVisibility = 1
        self.view.Background = [0.12, 0.12, 0.15]
        self.src_kind = None
        self.src = self.grid = self.pd = None
        self.type_filters, self.type_disp = {}, {}
        self.slice = self.slice_disp = self.outline_disp = None
        self.name, self.rng = None, (0.0, 1.0)
        self.timings = {}
        self.pairs = None  # numpy dict of the diagram, for the chart

    # ---- source ---------------------------------------------------------
    def vti_files(self):
        return sorted(p.name for p in VTI_DIR.glob("*.vti"))

    def set_source(self, kind):
        """kind: 'Wavelet', 'Gaussians (known: 5 maxima)', or a .vti file name. Rebuilds the TTK pipeline."""
        t0 = time.perf_counter()
        for f in list(self.type_filters.values()) + [self.pd, self.slice, self.grid, self.src]:
            if f is not None:
                simple.Delete(f)
        self.type_filters, self.type_disp, self.slice, self.slice_disp, self.outline_disp = {}, {}, None, None, None
        r = self.res
        if kind == "Wavelet":
            h = r // 2
            self.src = simple.Wavelet(WholeExtent=[-h, h - 1, -h, h - 1, -h, h - 1])
            self.grid = self.src
            self.name = "RTData"
        elif kind.startswith("Gaussians"):
            self.src = simple.TrivialProducer()
            self.src.GetClientSideObject().SetOutput(make_gaussians(r))
            self.grid = self.src
            self.name = "field"
        else:
            reader = simple.XMLImageDataReader(FileName=str(VTI_DIR / kind))
            reader.UpdatePipeline()
            self.src = reader
            self.name = reader.PointData[0].GetName()
            # resample large volumes to r^3 so that TTK stays interactive
            self.grid = simple.ResampleToImage(Input=reader, UseInputBounds=1, SamplingDimensions=[r, r, r])
            self.grid.UpdatePipeline()
        self.src_kind = kind
        self.grid.UpdatePipeline()
        a = self.grid.PointData[self.name]
        self.rng = tuple(float(v) for v in a.GetRange())
        t1 = time.perf_counter()
        self.pd = self.PD(Input=self.grid, ScalarField=["POINTS", self.name], EmbedinDomain=1, DebugLevel=0)
        self.pd.UpdatePipeline()
        self.timings["pd_s"] = time.perf_counter() - t1
        self._read_pairs()
        # context: field slice + outline
        self.slice = simple.Slice(Input=self.grid, SliceType="Plane")
        b = self.grid.GetDataInformation().GetBounds()
        self.slice.SliceType.Origin = [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2]
        self.slice.SliceType.Normal = [0, 0, 1]
        self.slice_disp = simple.Show(self.slice, self.view)
        simple.ColorBy(self.slice_disp, ("POINTS", self.name))
        simple.GetColorTransferFunction(self.name).ApplyPreset("Grayscale", True)
        simple.GetColorTransferFunction(self.name).RescaleTransferFunction(*self.rng)
        self.slice_disp.Opacity = 0.55
        self.slice_disp.SetScalarBarVisibility(self.view, False)
        self.outline_disp = simple.Show(self.grid, self.view)
        self.outline_disp.Representation = "Outline"
        self.outline_disp.ColorArrayName = ["POINTS", ""]
        self.timings["source_s"] = time.perf_counter() - t0
        self.reset_camera()

    def _read_pairs(self):
        g = sm.Fetch(self.pd)  # EmbedinDomain: pair i = cell i = points (2i, 2i+1) located at the critical vertices
        o = dsa.WrapDataObject(g)
        cd = o.CellData
        self.pairs = {"birth": np.array(cd["Birth"]), "pers": np.array(cd["Persistence"]),
                      "type": np.array(cd["PairType"]), "finite": np.array(cd["IsFinite"])}
        self.pair_pts = np.array(o.Points)
        self.pair_ctype = np.array(o.PointData["CriticalType"])
        self.pair_cells = np.array([[g.GetCell(i).GetPointId(0), g.GetCell(i).GetPointId(1)]
                                    for i in range(g.GetNumberOfCells())])

    # ---- parameters -------------------------------------------------------
    def persistent_points(self, frac):
        """Critical points that belong to a persistence pair with persistence >= frac * range."""
        thr = frac * (self.rng[1] - self.rng[0])
        ids = np.unique(self.pair_cells[self.pairs["pers"] >= thr].ravel())
        pts, ct = self.pair_pts[ids], self.pair_ctype[ids]
        # a saddle can appear in two pairs; also merge coincident points
        key = np.round(pts, 6)
        _, first = np.unique(np.column_stack([key, ct]), axis=0, return_index=True)
        return pts[first], ct[first]

    def set_threshold(self, frac, shown, show_slice, point_size):
        """frac: persistence threshold as fraction of the scalar range. shown: set of CriticalType ints."""
        from vtkmodules.vtkCommonDataModel import vtkPolyData
        from vtkmodules.vtkCommonCore import vtkPoints
        from vtkmodules.util.numpy_support import numpy_to_vtk
        t0 = time.perf_counter()
        pts, ct = self.persistent_points(frac)
        counts = [int((ct == t).sum()) for t, _, _ in TYPES]
        for t, label, col in TYPES:
            sel = pts[ct == t].astype(np.float32)
            poly = vtkPolyData()
            vp = vtkPoints()
            vp.SetData(numpy_to_vtk(np.ascontiguousarray(sel.reshape(-1, 3)), deep=True))
            poly.SetPoints(vp)
            from vtkmodules.vtkCommonDataModel import vtkCellArray
            ca = vtkCellArray()
            for i in range(len(sel)):
                ca.InsertNextCell(1)
                ca.InsertCellPoint(i)
            poly.SetVerts(ca)
            if t not in self.type_filters:
                prod = simple.TrivialProducer()
                self.type_filters[t] = prod
                prod.GetClientSideObject().SetOutput(poly)
                d = simple.Show(prod, self.view)
                d.ColorArrayName = ["POINTS", ""]
                d.AmbientColor = d.DiffuseColor = list(col)
                d.Representation = "Points"
                d.RenderPointsAsSpheres = 1
                self.type_disp[t] = d
            else:
                self.type_filters[t].GetClientSideObject().SetOutput(poly)
                self.type_filters[t].MarkModified(self.type_filters[t])
            self.type_disp[t].PointSize = float(point_size)
            self.type_disp[t].Visibility = 1 if (t in shown and len(sel)) else 0
        self.slice_disp.Visibility = 1 if show_slice else 0
        self.timings["select_s"] = time.perf_counter() - t0
        simple.Render(self.view)
        return counts

    def reset_camera(self):
        b = self.grid.GetDataInformation().GetBounds()
        c = [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2]
        self.view.CameraFocalPoint = c
        self.view.CameraViewUp = [0, 0, 1]
        self.view.CameraPosition = [c[0] + 1.0, c[1] - 1.4, c[2] + 0.9]
        self.view.ResetCamera()
        simple.Render(self.view)

    # ---- chart (SVG string) ---------------------------------------------
    def diagram_svg(self, frac, w=400, h=360):
        p = self.pairs
        lo, hi = self.rng
        span = max(hi - lo, 1e-9)
        pad = 38
        death = p["birth"] + p["pers"]
        d_all = np.concatenate([p["birth"], death])
        vmin, vmax = float(min(d_all.min(), lo)), float(max(d_all.max(), hi))
        sc = (w - 2 * pad) / max(vmax - vmin, 1e-9)
        X = lambda v: pad + (v - vmin) * sc  # noqa: E731
        Y = lambda v: h - pad - (v - vmin) * sc  # noqa: E731
        cols = {0: "#3366ff", 1: "#1cbf4d", 2: "#ff2626", -1: "#aaaaaa"}
        out = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{w}px;'
               f'background:#1e1e26;border-radius:6px;font:11px sans-serif">']
        out.append(f'<line x1="{X(vmin):.1f}" y1="{Y(vmin):.1f}" x2="{X(vmax):.1f}" y2="{Y(vmax):.1f}" stroke="#777"/>')
        thr = frac * span
        out.append(f'<line x1="{X(vmin):.1f}" y1="{Y(vmin + thr):.1f}" x2="{X(vmax - thr):.1f}" y2="{Y(vmax):.1f}" '
                   f'stroke="#ffd54a" stroke-dasharray="5 4"/>')
        keep = 0
        for b, pe, ty in zip(p["birth"], p["pers"], p["type"]):
            ok = pe >= thr
            keep += int(ok)
            out.append(f'<circle cx="{X(b):.1f}" cy="{Y(b + pe):.1f}" r="{3.2 if ok else 1.8}" '
                       f'fill="{cols.get(int(ty), "#aaa")}" opacity="{0.95 if ok else 0.35}"/>')
        out.append(f'<text x="{w / 2}" y="{h - 8}" fill="#ccc" text-anchor="middle">birth (scalar value)</text>')
        out.append(f'<text x="12" y="{h / 2}" fill="#ccc" text-anchor="middle" transform="rotate(-90 12 {h / 2})">'
                   f'death</text>')
        out.append(f'<text x="{w - 6}" y="16" fill="#ffd54a" text-anchor="end">threshold {frac * 100:.1f}% of range'
                   f' = {thr:.2f}; {keep} of {len(p["pers"])} pairs kept</text>')
        out.append("</svg>")
        return "".join(out), keep


def build_ui(server, pipe):
    from trame.ui.vuetify3 import SinglePageLayout
    from trame.widgets import html, vuetify3 as v3
    from trame.widgets import paraview as pv_widgets

    state, ctrl = server.state, server.controller
    sources = ["Wavelet", "Gaussians (known: 5 maxima)"] + pipe.vti_files()
    state.update({"source": "Wavelet", "th_ui": 0.02, "th": 0.02, "res": pipe.res, "res_items": [24, 32, 48, 64, 96],
                  "show0": True, "show1": True, "show2": True, "show3": True, "show_slice": True, "psize": 8, "counts": [0, 0, 0, 0],
                  "pd_svg": "", "pairs_kept": 0, "pairs_total": 0, "timing": "", "busy": False})
    names = [l for _, l, _ in TYPES]
    hexes = ["#3366ff", "#1cbf4d", "#ffcc1a", "#ff2626"]

    def refresh(source_changed=False):
        state.busy = True
        t0 = time.perf_counter()
        if source_changed:
            pipe.set_source(state.source)
        counts = pipe.set_threshold(state.th, {i for i in range(4) if state[f"show{i}"]}, state.show_slice, state.psize)
        svg, keep = pipe.diagram_svg(state.th)
        state.counts, state.pd_svg = counts, svg
        state.pairs_kept, state.pairs_total = keep, int(len(pipe.pairs["pers"]))
        tm = pipe.timings
        state.timing = (f"source+PD {tm.get('source_s', 0):.2f}s (PD {tm.get('pd_s', 0):.2f}s) | select points "
                        f"{tm.get('select_s', 0):.3f}s | total handler {time.perf_counter() - t0:.2f}s")
        print("[topology]", state.source, "res", pipe.res, "th", state.th, "counts", counts, state.timing, flush=True)
        ctrl.view_update()
        state.busy = False

    @state.change("source", "res")
    def _src(source, res, **kw):
        pipe.res = int(res)
        refresh(True)

    @state.change("th", "show0", "show1", "show2", "show3", "show_slice", "psize")
    def _th(**kw):
        if pipe.pd is not None:
            refresh(False)

    ctrl.on_server_ready.add(lambda **kw: refresh(True))
    ctrl.reset_camera = lambda: (pipe.reset_camera(), ctrl.view_update())

    with SinglePageLayout(server) as layout:
        layout.title.set_text("E9: TTK topology on the server (real TTK 1.3.0 in ParaView 6.2)")
        with layout.toolbar:
            v3.VSpacer()
            v3.VSelect(v_model=("source",), items=("sources", sources), label="Scalar field", hide_details=True,
                       density="compact", style="max-width: 260px;")
            v3.VSelect(v_model=("res",), items=("res_items",), label="Grid N (N^3)", hide_details=True,
                       density="compact", style="max-width: 120px;", classes="mx-2")
            v3.VSlider(v_model=("th_ui",), min=0, max=0.3, step=0.0025, label="Persistence threshold",
                       hide_details=True, density="compact", style="max-width: 330px;",
                       end="th = th_ui")
            v3.VLabel("{{ (th_ui * 100).toFixed(2) }} % of range", classes="mx-2")
            v3.VBtn("Reset camera", click=ctrl.reset_camera, size="small", classes="mx-1")
        with layout.content:
            with v3.VContainer(fluid=True, classes="pa-0 fill-height"):
                with v3.VRow(no_gutters=True, classes="fill-height"):
                    with v3.VCol(cols=8, classes="pa-0"):
                        view = pv_widgets.VtkRemoteView(pipe.view, ref="view", interactive_ratio=1)
                        ctrl.view_update = view.update
                        ctrl.view_reset_camera = view.reset_camera
                    with v3.VCol(cols=4, classes="pa-3", style="overflow-y:auto;"):
                        html.Div("Persistence diagram (TTKPersistenceDiagram)", classes="text-subtitle-2 mb-1")
                        html.Div(v_html=("pd_svg",))
                        html.Div("blue: minimum-saddle, green: saddle-saddle, red: saddle-maximum; dashed = "
                                 "threshold; faded points are removed by the simplification",
                                 classes="text-caption mb-3")
                        html.Div("Persistent critical points (end points of the pairs above the threshold)",
                                 classes="text-subtitle-2")
                        for i, (nm, hx) in enumerate(zip(names, hexes)):
                            with html.Div(classes="d-flex align-center"):
                                v3.VCheckbox(v_model=(f"show{i}",), hide_details=True, density="compact", style="flex:none;")
                                html.Span(style=f"display:inline-block;width:12px;height:12px;border-radius:6px;"
                                                f"background:{hx};margin-right:6px;")
                                html.Span(f"{nm}: " + "{{ counts[" + str(i) + "] }}")
                        v3.VCheckbox(v_model=("show_slice",), label="Show z mid-slice of field", hide_details=True,
                                     density="compact")
                        v3.VSlider(v_model=("psize",), min=3, max=20, step=1, label="Point size",
                                   hide_details=True, density="compact")
                        html.Div("{{ pairs_kept }} of {{ pairs_total }} persistence pairs above threshold",
                                 classes="text-body-2 mt-2")
                        html.Div("{{ timing }}", classes="text-caption mt-1")
    return pipe


def main():
    from trame.app import get_server
    from trame_vtk.modules.vtk.serializers.data import merge_to_polydata_serializer
    from trame_vtk.modules.vtk.serializers.registry import register_instance_serializer
    register_instance_serializer("vtkPartitionedDataSetCollection", merge_to_polydata_serializer)
    server = get_server(client_type="vue3")
    server.cli.add_argument("--res", type=int, default=48)
    args, _ = server.cli.parse_known_args()
    pipe = TopologyPipeline(args.res)
    build_ui(server, pipe)
    server.start()


if __name__ == "__main__":
    main()
