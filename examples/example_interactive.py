""" Example to show how to use TubeClipper
"""

from tubeclipper import TubeClipper
import pyvista as pv 

if __name__ == "__main__":
    # Input a surface file or a mesh file
    meshfile = '/Users/danmacdonald/Dropbox/malek_pairs_project/pairs_project_mesh_prep/03_meshed/Pair8a.vtu'
    mesh = pv.read(meshfile)

    # Toggle use_mesh if you want to clip a volume mesh
    t = TubeClipper(mesh)
    t.interact(use_mesh=False)
