""" For clipping tubes while maintaining other continuity.

Given a point and a normal direction, clip the surface only
at the nearest intersection.
"""

import pyvista as pv 
import numpy as np 
from scipy.spatial import cKDTree as KDTree
import networkx as nx 

class TubeClipper():
    def __init__(self, mesh):
        self.mesh = mesh 
        self.surf = self.mesh.extract_surface()

        self.clipped = self.mesh.copy()
        self.clipped.point_arrays['Side'] = np.ones(self.mesh.n_points, dtype=bool)

    def clip(self, origin, normal):
        """ Clip mesh given origin and normal.

        Args:
            origin (array): xyz coordinate of clipping plane.
            normal (array): normal direction of clipping plane.
            use_mesh (bool): if True, use volume mesh if present,
                else use surface.
        
        Clipped mesh is stored as attribute self.clipped.
        """
        mesh = self.mesh

        naive_clip = mesh.clip(normal, origin, return_clipped=True)
        
        if naive_clip[0].n_cells > 0 and naive_clip[1].n_cells > 0:
            naive_clip = [naive_clip[idx].clean(tolerance=1e-4) for idx in [0,1]]
            naive_clip = [pv.PolyData(x.points, x.faces) for x in naive_clip]
            
            sections = naive_clip[0].split_bodies()
            id = 0
            for body in sections:
                body.plane_side = 0
                body.id = id
                id += 1

            for body in naive_clip[1].split_bodies():
                body.plane_side = 1
                body.id = id
                id += 1
                sections.append(body)

            # Get the id of the two sections nearest the origin  
            near_side_sections = [x for x in sections if x.plane_side == 0]
            min_distance_from_origin = [np.min(np.linalg.norm(x.points - origin, axis=1)) for x in near_side_sections]
            root = near_side_sections[np.argmin(min_distance_from_origin)].id

            far_side_sections = [x for x in sections if x.plane_side == 1]
            min_distance_from_origin = [np.min(np.linalg.norm(x.points - origin, axis=1)) for x in far_side_sections]
            nearest_far_side = far_side_sections[np.argmin(min_distance_from_origin)].id

            # Test adjacency
            adj = []
            for idx in range(len(sections)):
                for jdx in range(idx+1, len(sections)):
                    test = len(sections[idx].merge(sections[jdx]).split_bodies())
                    if test == 1:
                        adj.append((idx, jdx))

            # Create graph
            G = nx.Graph()
            for pair in adj:
                G.add_edge(pair[0], pair[1])
            
            # Cut graph
            G.remove_node(nearest_far_side)
            S = [G.subgraph(c).copy() for c in nx.connected_components(G)]
            
            for sdx, subgraph in enumerate(S):
                if root in subgraph.nodes:
                    near_side = sdx
            
            # Prep id lists for merging 
            near_side_ids = list(S[near_side].nodes)
            far_side_ids = [[nearest_far_side]]

            if len(S) > 1:
                far_side_ids += [list(S[sdx].nodes) for sdx in range(len(S)) if sdx != near_side]

            far_side_ids = [item for sublist in far_side_ids for item in sublist]

            # near_side = pv.MultiBlock([x for x in sections[near_side_ids]])
            # far_side = pv.MultiBlock([x for x in sections[far_side_ids]])
            near_side = [x for x in sections[near_side_ids]]
            far_side = [x for x in sections[far_side_ids]]


            if len(near_side) > 1:
                near_side = near_side[0].merge(near_side[1:])
                # near_side = near_side.combine(merge_points=True, tolerance=1e-5)
            else:
                near_side = near_side[0]

            if len(far_side) > 1:
                far_side = far_side[0].merge(far_side[1:])
                # far_side = far_side.combine(merge_points=True, tolerance=1e-5)
            else:
                far_side = far_side[0]
                
            near_side = pv.PolyData(near_side.points, near_side.cells)
            far_side = pv.PolyData(far_side.points, far_side.cells)
            print('near', near_side.n_points)
            print('far', far_side.n_points)
            near_side = near_side.clean(tolerance=1e-5)
            far_side = far_side.clean(tolerance=1e-5)

            near_side.point_arrays['Side'] = np.zeros(near_side.n_points, dtype=bool)
            far_side.point_arrays['Side'] = np.ones(far_side.n_points, dtype=bool)
            
            tree = KDTree(mesh.points) #split.points
            ndx = tree.query(near_side.points, 1)[1]
            fdx = tree.query(far_side.points, 1)[1]

            for arr in mesh.point_arrays:
                near_side.point_arrays[arr] = mesh.point_arrays[arr][ndx]
                far_side.point_arrays[arr] = mesh.point_arrays[arr][fdx]
                
            # near_side = near_side.extract_largest()
            # far_side = far_side.extract_largest()
          
            self.near_side = near_side
            self.far_side = far_side

            all_points = np.concatenate([near_side.points, far_side.points], axis=0)
            side_arr = np.concatenate([
                np.zeros(near_side.n_points, dtype=bool),
                np.ones(far_side.n_points, dtype=bool),
                ],
                axis=0)
            
            # Interpolate back onto original mesh
            tree = KDTree(all_points) #split.points
            ndx = tree.query(mesh.points, 1)[1]
            side_array = side_arr[ndx] #split.point_arrays['Side'][ndx]

        else:
            if naive_clip[0].n_cells > 0:
                side_array = np.zeros(mesh.n_points, dtype=bool)
            elif naive_clip[1].n_cells > 0:
                side_array = np.ones(mesh.n_points, dtype=bool)
            self.far_side = naive_clip[1]
            self.near_side = naive_clip[0]

            if self.far_side.n_points > 1:
                self.far_side = self.far_side.clean(tolerance=1e-4)
            if self.near_side.n_points > 1:
                self.near_side = self.near_side.clean(tolerance=1e-4)

        self.clipped.point_arrays['Side'] = np.logical_and(
            self.clipped.point_arrays['Side'], 
            side_array,
            )


        return self

    def _plane_clipping_cb(self, normal, origin):
        """ Callback for interactive method.
        """
        self.normal = normal
        self.origin = origin
        
        mesh_clip = self.surf.clip(normal, origin, invert=False)
        mesh_clip_inv = self.surf.clip(normal, origin, invert=True)
    
        if mesh_clip.n_points > 1:
            self.p.remove_actor('mesh')
        else:
            self.p.add_mesh(self.surf, name='mesh', color='white', opacity=0.1)

        if mesh_clip.n_points < 1:
            self.p.remove_actor('clip')
        else:
            self.p.add_mesh(mesh_clip, name='clip', color='green') 

        if mesh_clip_inv.n_points < 1:
            self.p.remove_actor('inv')
        else:
            self.p.add_mesh(mesh_clip_inv, name='inv', color='red') 

    def _update(self):
        """ Callback for interactive method.
        """
        self.clipped.point_arrays['Side'] = np.ones(self.clipped.n_points, dtype=bool)
        self.clip(self.origin, self.normal)

        near_mask = self.clipped.point_arrays['Side'] == 0
        near = self.clipped.extract_points(near_mask)
        far = self.clipped.extract_points(~near_mask, adjacent_cells=False)

        if self.clipped.n_points > 1:
            self.p.remove_actor('mesh')
        else:
            self.p.add_mesh(self.surf, name='mesh', color='white', opacity=0.1)

        if far.n_points < 1:
            self.p.remove_actor('clip')
        else:
            self.p.add_mesh(far, name='clip', color='green') 

        if near.n_points < 1:
            self.p.remove_actor('inv')
        else:
            self.p.add_mesh(near, name='inv', color='red', opacity=0.1) 


    def interact(self):
        """ Interactively choose a normal and origin.
        """
        self.p = pv.Plotter()
        self.p.add_text('Press space to update')
        self.p.add_mesh(self.surf, name='mesh', color='white')
        self.p.add_plane_widget(self._plane_clipping_cb)
        self.p.add_key_event(
            key='space',
            callback=self._update,
            )
        self.p.show()
        print('Origin:', self.origin)
        print('Normal:', self.normal)
        

if __name__ == "__main__":
    print('See examples directory.')