import torch

from camera.abstract_camera import AbstractCamera
from deformation.abstract_view_deformation import AbstractViewDeformation


class MeshViewDeformation(AbstractViewDeformation):
    def __init__(self,
                 camera: AbstractCamera,
                 nb_data,
                 displacements=None
                 ):
        super().__init__(camera, nb_data)

        if displacements is None:
            self.displacements = torch.zeros((nb_data, 3), device='cuda')
        else:
            self.displacements = displacements

    """ Save the 3D displacements associated with this view deformation """
    def save_view_deformation(self, displacement_vectors, jacobians=None):
        self.displacements = displacement_vectors

    """ Deform the 2D points based on the 2D mesh associated with this view deformation """
    def deform(self, points2d):
        if self.bbw_mesh_tool is not None:
            triangles = self.bbw_mesh_tool.get_triangles('cuda')

             # Compute the displacement for the 2D vertices
            displacements =  torch.sum(self.bbw_mesh_tool.barycentric_coordinates * triangles, dim=1) - points2d

            points2d += displacements

            return points2d

        return points2d

    """ Return the parameters of the view deformation """
    def to_dict(self):
        return {
            "camera": self.camera.to_dict(),
            "mean_azimuth": self.mean_azimuth,
            "mean_polar": self.mean_polar,
            "variance_azimuth": self.variance_azimuth,
            "variance_polar": self.variance_polar,
            "nb_data": self.nb_data,
            "displacements": self.displacements.cpu().numpy() if self.displacements is not None else None
        }