""" Example to show how to use TubeClipper
"""

from tubeclipper import TubeClipper
import pyvista as pv 
import numpy as np 
from pyvista import examples
from pyvista import themes
pv.set_plot_theme(themes.DocumentTheme())

if __name__ == "__main__":
    # Input a surface file or a mesh file
    mesh = examples.download_dragon()

    # Try running the interactive example to get a normal and origin,
    # a normal and origin will print on completion.
    origin = np.array([-0.0059, 0.12, -0.0046])
    normal = np.array([0.48, 0.87, -0.085])

    t = TubeClipper(mesh)
    t.clip(origin, -normal)

    cpos = [(-0.0069, 0.070, -0.39),
            (-0.0091, 0.12, -0.0038),
            (0.0, 1.0, 0.0)]

    p = pv.Plotter()
    p.camera_position = cpos
    p.add_mesh(t.clipped, scalars='Side')
    p.set_focus(t.clipped.outline().center)
    p.show()


