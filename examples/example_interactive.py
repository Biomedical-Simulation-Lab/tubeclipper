""" Example to show how to use TubeClipper
"""

from tubeclipper import TubeClipper
import pyvista as pv 
from pyvista import examples
from pyvista import themes
pv.set_plot_theme(themes.DocumentTheme())

if __name__ == "__main__":
    # Input a surface file or a mesh file
    mesh = examples.download_dragon()

    # Toggle use_mesh if you want to clip a volume mesh
    t = TubeClipper(mesh)
    t.interact()
