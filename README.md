# tubeclipper

Clips a mesh based on local connectivity.

`tubeclipper` is for clipping a mesh while avoiding undesired cuts. Say we wanted to clip the dragon below, but only at its midsection -- clipping with a plane will cut through the head and other body sections. Instead, `tubeclipper` marks the mesh based on connectivity relative to the clipping point, as in the image below.

Clipping with a plane:
![Before](https://github.com/Biomedical-Simulation-Lab/tubeclipper/blob/master/imgs/before.jpg)

Clipping with `tubeclipper`:
![After](https://github.com/Biomedical-Simulation-Lab/tubeclipper/blob/master/imgs/after.jpg)

Requirements:
- numpy 
- pyvista 
- scipy 
- networkx 