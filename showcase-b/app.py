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


class ParaViewPipeline:
    """Wavelet -> Contour(RTData) -> Show -> Render, all on the server."""

    def __init__(self, size, iso=157.0):
        self.size, self.iso, self.representation = size, iso, "Surface"
        self.source = simple.Wavelet()
        self._set_extent()
        self.contour = simple.Contour(Input=self.source, ContourBy=["POINTS", "RTData"],
                                      Isosurfaces=[iso])
        self.view = simple.GetActiveViewOrCreate("RenderView")
        self.view.OrientationAxesVisibility = 1
        self.display = simple.Show(self.contour, self.view)
        simple.ColorBy(self.display, None)
        self.display.Representation = self.representation
        self.reset_camera()

    def _set_extent(self):
        h = self.size // 2
        self.source.WholeExtent = [-h, h - 1, -h, h - 1, -h, h - 1]

    def set_iso(self, value):
        self.iso = value
        self.contour.Isosurfaces = [value]
        self._render()

    def set_size(self, size):
        self.size = size
        self._set_extent()
        self.contour.UpdatePipeline()
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
