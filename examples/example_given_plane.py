""" Example to show how to use TubeClipper
"""

from tubeclipper import TubeClipper
import pyvista as pv 
import numpy as np 

if __name__ == "__main__":
    # Input a surface file or a mesh file
    meshfile = '/Users/danmacdonald/Dropbox/malek_pairs_project/pairs_project_mesh_prep/03_meshed/Pair8a.vtu'
    mesh = pv.read(meshfile)

    # Try running the interactive example to get a normal and origin,
    # a normal and origin will print on completion.
    origin = np.array([23.65, 9.43, 28.13])
    normal = np.array([-0.15, -0.36, 0.92])

    t = TubeClipper(mesh)
    t.clip(origin, normal)
    t.clipped.plot(scalars='Side')
