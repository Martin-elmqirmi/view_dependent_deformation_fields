from camera.abstract_camera import AbstractCamera
from deformation.gsplat_view_deformation import GsplatViewDeformation
from deformation.abstract_view_deformer import AbstractViewDeformer
from utils.utils import get_interpolated_displacements, get_interpolated_jacobians


class GsplatViewDeformer(AbstractViewDeformer):
    def __init__(self):
        super().__init__()

    """ Create a new GsplatViewDeformation """
    def new_view_deformation(self, camera, nb_data, displacements, jacobians):
        view_deformation = GsplatViewDeformation(camera, nb_data, displacements, jacobians)
        self.view_deformations.append(view_deformation)

    """ Get the interpolation data (In our case bivariate gaussian data) for each GsplatViewDeformation """
    def get_gaussian_data(self):
        gaussian_data = []
        displacements = []
        jacobians = []

        for view_deformation in self.view_deformations:
            gaussian_data.append([
                view_deformation.mean_azimuth,
                view_deformation.mean_polar,
                view_deformation.variance_azimuth,
                view_deformation.variance_polar
            ])

            assert isinstance(view_deformation, GsplatViewDeformation)

            displacements.append(view_deformation.displacements)
            jacobians.append(view_deformation.jacobians)

        return gaussian_data, displacements, jacobians

    """ Interpolate the GsplatViewDeformations """
    def get_interpolated_values(self, camera: AbstractCamera, n, nb_data):
        gaussian_data, displacements, jacobians = self.get_gaussian_data()

        interpolated_displacements = get_interpolated_displacements(camera.azimuth, camera.polar,
                                                                    gaussian_data, displacements,
                                                                    n, nb_data)

        interpolated_jacobians = get_interpolated_jacobians(camera.azimuth, camera.polar,
                                                            gaussian_data, jacobians,
                                                            n, nb_data)

        return interpolated_displacements, interpolated_jacobians