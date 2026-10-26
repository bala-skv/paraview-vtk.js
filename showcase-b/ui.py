"""Shared trame layout, state handlers and instrumentation for Showcase B.

app.py (ParaView) and app_vtk.py (plain VTK fallback) each provide a `pipeline`
object and this module does the rest, so both apps behave identically.

Pipeline interface:
    size, iso, representation        current values
    view                             object handed to VtkRemoteLocalView
    set_size(n), set_iso(v), set_representation(name)
    stats() -> (triangles, geometry_kb)
    azimuth(deg), reset_camera()
"""
import asyncio
import csv
import os
import time
from pathlib import Path

import psutil
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import html, vuetify3 as v3

T_START = time.perf_counter()
EVENTS_CSV = Path(__file__).resolve().parent.parent / "bench" / "results" / "server_events.csv"
EVENTS_HEADER = ["timestamp", "event", "source", "size", "mode", "duration_ms",
                 "triangles", "geometry_kb", "rss_mb"]
ORBIT_STEPS, ORBIT_DEG = 180, 2


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
        })
        self._initial_mode = initial_mode
        self._build_ui()
        self.state.change("iso")(self.on_iso)
        self.state.change("size")(self.on_size)
        self.state.change("representation")(self.on_representation)
        self.state.change("local_rendering")(self.on_mode)
        self.ctrl.on_client_connected.add(self.on_client_connected)
        self.ctrl.on_server_ready.add(self.on_server_ready)
        self.ctrl.run_orbit = self.run_orbit
        self.ctrl.reset_camera = self.reset_camera
        EVENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
        if not EVENTS_CSV.exists():
            EVENTS_CSV.write_text(",".join(EVENTS_HEADER) + "\n")

    # ---- layout -------------------------------------------------------
    def _build_ui(self):
        with SinglePageLayout(self.server) as layout:
            layout.title.set_text(self.title)
            with layout.toolbar:
                v3.VSpacer()
                v3.VSlider(v_model=("iso", self.pipeline.iso), min=40, max=270, step=1,
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

    def on_representation(self, representation, **_):
        if self.ready and representation != self.pipeline.representation:
            self.timed("representation_change",
                       lambda: self.pipeline.set_representation(representation))

    def on_mode(self, local_rendering, **_):
        if not self.ready:
            return
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
    def on_client_connected(self, **_):
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
