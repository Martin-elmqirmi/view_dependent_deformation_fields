import numpy as np
import torch
from gpytoolbox import barycentric_coordinates, in_element_aabb

from deformation.bbw_mesh import BbwMesh


""" 2D Mesh tool using BBW for the deformations """
class BbwMeshTool:
    def __init__(self):
        self.bbw_mesh = None
        self.barycentric_coordinates = None
        self.indices = None

    """ Initialize the tool by generating a 2D mesh using the rendered image of the 3D model """
    def initialize_bbw_mesh(self, points2d, image):
        self.bbw_mesh = BbwMesh(image)
        indices = in_element_aabb(points2d, self.bbw_mesh.vertices, self.bbw_mesh.faces)
        triangles = self.bbw_mesh.vertices[self.bbw_mesh.faces[indices]].astype(np.float32)
        bary_coordinates = barycentric_coordinates(points2d,
                                                   np.ascontiguousarray(triangles[:, 0]),
                                                   np.ascontiguousarray(triangles[:, 1]),
                                                   np.ascontiguousarray(triangles[:, 2]))

        self.barycentric_coordinates = torch.from_numpy(bary_coordinates[:, :, np.newaxis]).to('cuda')
        self.indices = indices
        self.bbw_mesh.points2d = points2d

    """ get the new triangle's positions to compute the barycentric coordinates """
    def get_triangles(self, device):
        new_triangles = self.bbw_mesh.new_vertices_tensor[self.bbw_mesh.faces[self.indices]].to(device)
        return new_triangles