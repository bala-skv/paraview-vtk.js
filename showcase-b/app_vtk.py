"""Showcase B fallback: plain VTK + trame, no ParaView needed. Run with the .venv Python:

  .venv/bin/python showcase-b/app_vtk.py --port 8081 --server [--size 128] [--mode remote|local]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Without these imports remote rendering fails (no OpenGL factory / interaction style registered).
import vtkmodules.vtkRenderingOpenGL2  # noqa: F401, E402
import vtkmodules.vtkInteractionStyle  # noqa: F401, E402
import vtkmodules.vtkRenderingFreeType  # noqa: F401, E402
from vtkmodules.vtkFiltersCore import vtkContourFilter  # noqa: E402
from vtkmodules.vtkImagingCore import vtkRTAnalyticSource  # noqa: E402
from vtkmodules.vtkRenderingCore import (  # noqa: E402
    vtkActor, vtkPolyDataMapper, vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor,
)

from trame.app import get_server  # noqa: E402
from trame.widgets import vtk as vtk_widgets  # noqa: E402

from ui import ShowcaseApp  # noqa: E402


class VtkPipeline:
    """vtkRTAnalyticSource -> vtkContourFilter -> mapper/actor in an offscreen window."""

    def __init__(self, size, iso=157.0):
        self.size, self.iso, self.representation = size, iso, "Surface"
        self.source = vtkRTAnalyticSource()
        self._set_extent()
        self.contour = vtkContourFilter()
        self.contour.SetInputConnection(self.source.GetOutputPort())
        self.contour.SetValue(0, iso)
        self.contour.ComputeNormalsOn()
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(self.contour.GetOutputPort())
        mapper.ScalarVisibilityOff()
        self.actor = vtkActor()
        self.actor.SetMapper(mapper)
        self.renderer = vtkRenderer()
        self.renderer.AddActor(self.actor)
        self.renderer.SetBackground(0.32, 0.34, 0.43)
        self.view = vtkRenderWindow()
        self.view.SetOffScreenRendering(1)
        self.view.AddRenderer(self.renderer)
        inter = vtkRenderWindowInteractor()
        inter.SetRenderWindow(self.view)
        inter.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
        self.contour.Update()
        self.reset_camera()

    def _set_extent(self):
        h = self.size // 2
        self.source.SetWholeExtent(-h, h - 1, -h, h - 1, -h, h - 1)

    def set_iso(self, value):
        self.iso = value
        self.contour.SetValue(0, value)
        self._render()

    def set_size(self, size):
        self.size = size
        self._set_extent()
        self._render()

    def set_representation(self, name):
        self.representation = name
        prop = self.actor.GetProperty()
        prop.SetRepresentationToWireframe() if name == "Wireframe" else prop.SetRepresentationToSurface()
        self._render()

    def _render(self):
        self.contour.Update()
        self.view.Render()

    def stats(self):
        out = self.contour.GetOutput()
        return int(out.GetNumberOfCells()), int(out.GetActualMemorySize())

    def azimuth(self, deg):
        self.renderer.GetActiveCamera().Azimuth(deg)
        self.view.Render()

    def reset_camera(self):
        self.renderer.ResetCamera()
        self.view.Render()


def main():
    server = get_server(client_type="vue3")
    server.cli.add_argument("--size", type=int, default=128, choices=[64, 128, 256, 384])
    server.cli.add_argument("--mode", default="remote", choices=["remote", "local"])
    args, _ = server.cli.parse_known_args()
    pipeline = VtkPipeline(args.size)
    ShowcaseApp(server, pipeline, vtk_widgets, source="wavelet-vtk",
                title="Showcase B (fallback): trame + plain VTK", initial_mode=args.mode)
    server.start()


if __name__ == "__main__":
    main()
