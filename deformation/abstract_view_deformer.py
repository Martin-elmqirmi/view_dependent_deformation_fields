from abc import ABC, abstractmethod
from typing import List

from camera.abstract_camera import AbstractCamera
from deformation.abstract_view_deformation import AbstractViewDeformation


""" Class that handles all the view deformations to do the interpolation """
class AbstractViewDeformer(ABC):
    def __init__(self):
        self.view_deformations: List[AbstractViewDeformation] = []

    """ Create a new ViewDeformation """
    @abstractmethod
    def new_view_deformation(self, camera, nb_data, displacements, jacobians):
        pass

    """ Get the interpolation data (In our case bivariate gaussian data) for each ViewDeformation """
    @abstractmethod
    def get_gaussian_data(self):
        pass

    """ Interpolate the ViewDeformations """
    @abstractmethod
    def get_interpolated_values(self, camera: AbstractCamera, n, nb_data):
        pass