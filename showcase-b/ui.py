"""Shared trame layout, state handlers and instrumentation for Showcase B.

app.py (ParaView) and app_vtk.py (plain VTK fallback) each provide a `pipeline`
object and this module does the rest, so both apps behave identically.

Pipeline interface:
    size, iso, representation        current values
    view                             object handed to VtkRemoteLocalView
    set_size(n), set_iso(v), set_representation(name)
    stats() -> (triangles, geometry_kb)
    azimuth(deg), reset_camera()

Optional (ParaView app only): if `pipeline.features` is true the UI adds the "Pipeline" drawer
(filter selector, colouring, volume rendering, .vti source, screenshot, save/load state) and calls
    apply(params: dict) -> info dict, screenshot(path), save_pvsm(path), vti_files()
Without it (app_vtk.py) the drawer is not built and the toolbar is unchanged.
"""
import asyncio
import base64
import csv
import json
import os
import time
from pathlib import Path

import psutil
from trame.ui.vuetify3 import SinglePageLayout, SinglePageWithDrawerLayout
from trame.widgets import html, vuetify3 as v3

T_START = time.perf_counter()
EVENTS_CSV = Path(__file__).resolve().parent.parent / "bench" / "results" / "server_events.csv"
EVENTS_HEADER = ["timestamp", "event", "source", "size", "mode", "duration_ms",
                 "triangles", "geometry_kb", "rss_mb"]
ORBIT_STEPS, ORBIT_DEG = 180, 2
OUT_DIR = Path(__file__).resolve().parent / "out"
# trame state keys that make up the Pipeline drawer (same names as app.DEFAULTS)
FEATURE_KEYS = ["kind", "source", "vti", "axis", "offset", "thr_lo", "thr_hi", "color_by", "cmap",
                "auto_range", "rmin", "rmax", "bar", "volume"]
KINDS = ["Contour", "Slice", "Clip", "Threshold", "Streamlines", "Glyph"]
COLORMAPS = ["Cool to Warm", "Viridis", "Inferno", "Turbo", "Jet", "Grayscale", "X Ray",
             "Rainbow Uniform", "Black-Body Radiation"]


def rss_mb():
    return psutil.Process(os.getpid()).memory_info().rss / 2**20


class ShowcaseApp:
    def __init__(self, server, pipeline, widgets, source, title, initial_mode="remote"):
        self.server, self.pipeline, self.source, self.title = server, pipeline, source, title
        self.state, self.ctrl = server.state, server.controller
        self.widgets = widgets
        self.view = None
        self.ready = False
        self.first_connect_logged = False
        self.first_update_logged = False
        self.features = bool(getattr(pipeline, "features", False))
        self._last_key = None

        self.state.update({
            "iso": pipeline.iso,
            "size": pipeline.size,
            "representation": pipeline.representation,
            "local_rendering": initial_mode == "local",
            "interactive_quality": 60,
            "interactive_ratio": 1.0,
            "stats": {"triangles": 0, "geometry_kb": 0, "last_update_ms": 0, "rss_mb": 0},
            "orbit_running": False,
            "orbit_report": "",
            "iso_min": 40, "iso_max": 270,
            "n_clients": 0,
        })
        if self.features:
            self.state.update({
                "kind": "Contour", "source": "Wavelet", "vti": "", "axis": "Z", "offset": 0.0,
                "thr_lo": 0.3, "thr_hi": 0.7, "color_by": "Solid Color", "cmap": "Cool to Warm",
                "auto_range": True, "rmin": 0.0, "rmax": 1.0, "bar": False, "volume": False,
                "kinds": KINDS, "colormaps": COLORMAPS, "sources": ["Wavelet", "VTI file"],
                "vti_files": pipeline.vti_files(), "color_arrays": ["Solid Color"],
                "data_range": "", "feature_msg": "", "shot_url": "", "shot_dialog": False,
                "state_files": [],
            })
            files = self.state.vti_files  # default to a small file: the 256^3 ones are slow under software GL
            self.state.vti = "foot_64.vti" if "foot_64.vti" in files else (files[0] if files else "")
        self._initial_mode = initial_mode
        self._build_ui()
        self.state.change("iso")(self.on_iso)
        self.state.change("size")(self.on_size)
        self.state.change("representation")(self.on_representation)
        self.state.change("local_rendering")(self.on_mode)
        if self.features:
            self.state.change(*FEATURE_KEYS)(self.on_feature)
            self.ctrl.take_screenshot = self.take_screenshot
            self.ctrl.save_state = self.save_state
            self.ctrl.load_state = self.load_state
        self.ctrl.on_client_exited.add(self.on_client_exited)
        self.ctrl.on_client_connected.add(self.on_client_connected)
        self.ctrl.on_server_ready.add(self.on_server_ready)
        self.ctrl.run_orbit = self.run_orbit
        self.ctrl.reset_camera = self.reset_camera
        EVENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
        if not EVENTS_CSV.exists():
            EVENTS_CSV.write_text(",".join(EVENTS_HEADER) + "\n")

    # ---- layout -------------------------------------------------------
    def _build_ui(self):
        Layout = SinglePageWithDrawerLayout if self.features else SinglePageLayout
        with Layout(self.server) as layout:
            layout.title.set_text(self.title)
            if self.features:
                self._build_drawer(layout)
            with layout.toolbar:
                v3.VSpacer()
                v3.VSlider(v_model=("iso", self.pipeline.iso), min=("iso_min", 40), max=("iso_max", 270), step=1,
                           label="Iso value", hide_details=True, density="compact",
                           style="max-width: 280px;")
                v3.VLabel("{{ Math.round(iso) }}", classes="mx-2")
                v3.VSelect(v_model=("size", self.pipeline.size), items=("sizes", [64, 128, 256]),
                           label="Size³", hide_details=True, density="compact",
                           style="max-width: 110px;")
                v3.VSelect(v_model=("representation", self.pipeline.representation),
                           items=("representations", ["Surface", "Wireframe"]),
                           label="Representation", hide_details=True, density="compact",
                           style="max-width: 160px;", classes="mx-2")
                v3.VSwitch(v_model=("local_rendering", self._initial_mode == "local"),
                           label="Local rendering", hide_details=True, density="compact",
                           classes="mx-2")
                v3.VBtn("Reset camera", click=self.ctrl.reset_camera, size="small", classes="mx-1")
                v3.VBtn("Benchmark orbit", click=self.ctrl.run_orbit, size="small", classes="mx-1",
                        disabled=("local_rendering || orbit_running",))
            with layout.content:
                with v3.VContainer(fluid=True, classes="pa-0 fill-height"):
                    self.view = self.widgets.VtkRemoteLocalView(
                        self.pipeline.view, namespace="view", mode=self._initial_mode,
                        interactive_quality=("interactive_quality", 60),
                        interactive_ratio=("interactive_ratio", 1.0),
                    )
                    self.ctrl.view_update = self.view.update
                    self.ctrl.view_update_image = self.view.update_image
                    self.ctrl.view_update_geometry = self.view.update_geometry
                    self.ctrl.view_reset_camera = self.view.reset_camera
                    with v3.VCard(style="position:absolute; right:12px; top:76px; width:230px; opacity:.92;"):
                        v3.VCardTitle("Server stats", classes="text-subtitle-1")
                        with v3.VCardText(classes="text-body-2"):
                            with html.Div():
                                html.Span("Mode: ")
                                html.B("{{ local_rendering ? 'local (vtk.js)' : 'remote (images)' }}")
                            with html.Div():
                                html.Span("Triangles: ")
                                html.B("{{ stats.triangles.toLocaleString() }}")
                            with html.Div():
                                html.Span("Geometry: ")
                                html.B("{{ stats.geometry_kb.toLocaleString() }} KB")
                            with html.Div():
                                html.Span("Last update: ")
                                html.B("{{ stats.last_update_ms }} ms")
                            with html.Div():
                                html.Span("Server RSS: ")
                                html.B("{{ stats.rss_mb }} MB")
                            with html.Div(v_if="orbit_report"):
                                html.Span("Orbit: ")
                                html.B("{{ orbit_report }}")

    def _build_drawer(self, layout):
        sel = dict(hide_details=True, density="compact", classes="mb-2")
        with layout.drawer:
            with v3.VContainer(classes="pa-3"):
                html.Div("Source", classes="text-subtitle-2")
                v3.VSelect(v_model=("source", "Wavelet"), items=("sources",), label="Source", **sel)
                v3.VSelect(v_model=("vti", ""), items=("vti_files",), label="VTI file (data/vti)",
                           v_if="source === 'VTI file'", **sel)
                html.Div("Pipeline", classes="text-subtitle-2 mt-2")
                v3.VSelect(v_model=("kind", "Contour"), items=("kinds",), label="Filter", **sel)
                with html.Div(v_if="kind === 'Slice' || kind === 'Clip'"):
                    v3.VSelect(v_model=("axis", "Z"), items=("['X','Y','Z']",), label="Plane normal", **sel)
                    v3.VSlider(v_model=("offset", 0.0), min=-1, max=1, step=0.02,
                               label="Offset", **sel)
                with html.Div(v_if="kind === 'Threshold'"):
                    v3.VSlider(v_model=("thr_lo", 0.3), min=0, max=1, step=0.01,
                               label="Lower (fraction of range)", **sel)
                    v3.VSlider(v_model=("thr_hi", 0.7), min=0, max=1, step=0.01,
                               label="Upper (fraction of range)", **sel)
                html.Div("Colouring", classes="text-subtitle-2 mt-2")
                v3.VSelect(v_model=("color_by", "Solid Color"), items=("color_arrays",),
                           label="Colour by", **sel)
                v3.VSelect(v_model=("cmap", "Cool to Warm"), items=("colormaps",),
                           label="Colour map", **sel)
                v3.VSwitch(v_model=("auto_range", True), label="Auto range", **sel)
                with html.Div(v_if="!auto_range", classes="d-flex"):
                    v3.VTextField(v_model_number=("rmin", 0.0), label="min", type="number", **sel)
                    v3.VTextField(v_model_number=("rmax", 1.0), label="max", type="number",
                                  classes="ml-2 mb-2", hide_details=True, density="compact")
                html.Div("Data range: {{ data_range }}", classes="text-caption mb-2")
                v3.VSwitch(v_model=("bar", False), label="Scalar bar", **sel)
                v3.VSwitch(v_model=("volume", False), label="Volume rendering (remote only)",
                           disabled=("local_rendering",), **sel)
                html.Div("Session", classes="text-subtitle-2 mt-2")
                with html.Div(classes="d-flex flex-wrap"):
                    v3.VBtn("Screenshot", click=self.ctrl.take_screenshot, size="small", classes="mr-1 mb-1")
                    v3.VBtn("Save state", click=self.ctrl.save_state, size="small", classes="mr-1 mb-1")
                    v3.VBtn("Load state", click=self.ctrl.load_state, size="small", classes="mb-1")
                html.Div("{{ feature_msg }}", classes="text-caption")
                html.Div("Clients connected so far: {{ n_clients }}", classes="text-caption mt-2")
        with v3.VDialog(v_model=("shot_dialog", False), max_width=900):
            with v3.VCard():
                v3.VImg(src=("shot_url", ""))
                with v3.VCardActions():
                    html.A("Download PNG", href=("shot_url", ""), download="showcase_b.png",
                           classes="ml-2")
                    v3.VSpacer()
                    v3.VBtn("Close", click="shot_dialog = false")

    # ---- helpers ------------------------------------------------------
    def log_event(self, event, duration_ms="", triangles="", geometry_kb=""):
        row = [time.strftime("%Y-%m-%dT%H:%M:%S"), event, self.source, self.pipeline.size,
               "local" if self.state.local_rendering else "remote",
               f"{duration_ms:.2f}" if duration_ms != "" else "", triangles, geometry_kb,
               f"{rss_mb():.1f}"]
        with open(EVENTS_CSV, "a", newline="") as f:
            csv.writer(f).writerow(row)

    def refresh(self):
        """Push only what the active mode needs."""
        if self.state.local_rendering:
            self.ctrl.view_update_geometry()
        else:
            self.ctrl.view_update_image()

    def timed(self, event, fn, reset_camera=False):
        t = time.perf_counter()
        fn()
        if reset_camera:
            self.pipeline.reset_camera()
            self.ctrl.view_update(reset_camera=True)
        else:
            self.refresh()
        ms = (time.perf_counter() - t) * 1000
        tris, kb = self.pipeline.stats()
        self.state.stats = {"triangles": tris, "geometry_kb": kb, "last_update_ms": round(ms, 1),
                            "rss_mb": round(rss_mb(), 1)}
        self.log_event(event, ms, tris, kb)
        if not self.first_update_logged and self.first_connect_logged:
            self.first_update_logged = True
            self.log_event("first_view_update_after_connect",
                           (time.perf_counter() - T_START) * 1000, tris, kb)

    # ---- state handlers ----------------------------------------------
    def on_iso(self, iso, **_):
        if self.ready and float(iso) != self.pipeline.iso:
            self.timed("iso_change", lambda: self.pipeline.set_iso(float(iso)))

    def on_size(self, size, **_):
        if self.ready and int(size) != self.pipeline.size:
            self.timed("size_change", lambda: self.pipeline.set_size(int(size)), reset_camera=True)
            if self.features and self._last_key is not None:  # only once the drawer has been used
                self._last_key = None
                self.on_feature()

    def on_representation(self, representation, **_):
        if self.ready and representation != self.pipeline.representation:
            self.timed("representation_change",
                       lambda: self.pipeline.set_representation(representation))

    def feature_params(self):
        return {k: self.state[k] for k in FEATURE_KEYS}

    def on_feature(self, **_):
        if not self.ready:
            return
        p = self.feature_params()
        key = {k: v for k, v in p.items() if not (p["auto_range"] and k in ("rmin", "rmax"))}
        if key == self._last_key:
            return
        self._last_key = key
        info = {}
        first = p["source"] != self.pipeline.params["source"] or p["vti"] != self.pipeline.params["vti"]
        first = first or p["kind"] != self.pipeline.params["kind"]

        def run():
            info.update(self.pipeline.apply(p))

        self.timed("pipeline_change", run, reset_camera=first)
        lo, hi = info["range"]
        upd = {"color_arrays": info["arrays"], "data_range": f"{lo:.4g} .. {hi:.4g}"}
        if info["color_by"] != p["color_by"]:
            upd["color_by"] = info["color_by"]
        if p["auto_range"]:
            upd["rmin"], upd["rmax"] = lo, hi
        if info["changed_source"]:
            ilo, ihi = info["iso_range"]
            upd.update(iso_min=ilo, iso_max=ihi, iso=(ilo + ihi) / 2)
        self.state.update(upd)

    # ---- screenshot / save / load -------------------------------------
    def take_screenshot(self):
        OUT_DIR.mkdir(exist_ok=True)
        path = OUT_DIR / f"shot_{time.strftime('%Y%m%d_%H%M%S')}.png"
        self.pipeline.screenshot(path)
        self.state.shot_url = "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()
        self.state.shot_dialog = True
        self.state.feature_msg = f"Saved {path.name}"
        self.log_event("screenshot")

    def save_state(self):
        OUT_DIR.mkdir(exist_ok=True)
        cam = self.pipeline.view.GetActiveCamera()
        data = {"params": self.feature_params(), "iso": self.state.iso, "size": self.state.size,
                "representation": self.state.representation,
                "local_rendering": self.state.local_rendering,
                "camera": {"position": list(cam.GetPosition()), "focal": list(cam.GetFocalPoint()),
                           "up": list(cam.GetViewUp())}}
        (OUT_DIR / "state.json").write_text(json.dumps(data, indent=1))
        self.pipeline.save_pvsm(OUT_DIR / "state.pvsm")
        self.state.feature_msg = "Saved out/state.json + out/state.pvsm"
        self.log_event("save_state")

    def load_state(self):
        f = OUT_DIR / "state.json"
        if not f.exists():
            self.state.feature_msg = "No saved state (out/state.json)"
            return
        data = json.loads(f.read_text())
        self.state.update({**data["params"], "iso": data["iso"], "size": data["size"],
                           "representation": data["representation"],
                           "local_rendering": data["local_rendering"]})
        self.state.flush()
        self._last_key = None
        self.on_feature()
        cam, c = self.pipeline.view.GetActiveCamera(), data["camera"]
        cam.SetPosition(c["position"]); cam.SetFocalPoint(c["focal"]); cam.SetViewUp(c["up"])
        self.pipeline.azimuth(0)
        self.ctrl.view_update()
        self.state.feature_msg = "Loaded out/state.json"
        self.log_event("load_state")

    def on_mode(self, local_rendering, **_):
        if not self.ready:
            return
        if self.features and local_rendering and self.state.volume:
            self.state.volume = False  # server-side volume mapper has no vtk.js equivalent here
        t = time.perf_counter()
        self.view.set_local_rendering(bool(local_rendering))
        self.ctrl.view_update()  # bring both sides up to date after a switch
        ms = (time.perf_counter() - t) * 1000
        tris, kb = self.pipeline.stats()
        self.log_event("mode_change", ms, tris, kb)

    def reset_camera(self):
        self.pipeline.reset_camera()
        self.ctrl.view_update(reset_camera=True)

    # ---- lifecycle -----------------------------------------------------
    def on_client_exited(self, **_):
        self.state.n_clients = max(0, self.state.n_clients - 1)

    def on_client_connected(self, **_):
        self.state.n_clients = self.state.n_clients + 1
        if not self.first_connect_logged:
            self.first_connect_logged = True
            ms = (time.perf_counter() - T_START) * 1000
            print(f"[bench] first client connected {ms:.0f} ms after server start", flush=True)
            self.log_event("first_client_connect", ms)

    def on_server_ready(self, **_):
        self.ready = True
        tris, kb = self.pipeline.stats()
        self.state.stats = {"triangles": tris, "geometry_kb": kb, "last_update_ms": 0,
                            "rss_mb": round(rss_mb(), 1)}
        self.log_event("server_ready", (time.perf_counter() - T_START) * 1000, tris, kb)
        asyncio.ensure_future(self._rss_sampler())

    async def _rss_sampler(self):
        while True:
            await asyncio.sleep(1)
            s = dict(self.state.stats)
            s["rss_mb"] = round(rss_mb(), 1)
            with self.state:
                self.state.stats = s

    async def run_orbit(self):
        if self.state.local_rendering or self.state.orbit_running:
            return
        self.state.orbit_running = True
        self.state.flush()
        steps = []
        t0 = time.perf_counter()
        for _ in range(ORBIT_STEPS):
            s = time.perf_counter()
            self.pipeline.azimuth(ORBIT_DEG)
            self.ctrl.view_update_image()
            await asyncio.sleep(0)
            steps.append((time.perf_counter() - s) * 1000)
        total = (time.perf_counter() - t0) * 1000
        tris, kb = self.pipeline.stats()
        report = f"{total:.0f} ms total, {total / ORBIT_STEPS:.1f} ms/step ({ORBIT_STEPS} x {ORBIT_DEG} deg)"
        print(f"[bench] orbit: {report}", flush=True)
        self.log_event("orbit", total, tris, kb)
        with self.state:
            self.state.orbit_report = report
            self.state.orbit_running = False
