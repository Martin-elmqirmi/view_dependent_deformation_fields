from abc import ABC, abstractmethod

import tkinter as tk

from camera.abstract_camera import AbstractCamera
from deformation.abstract_view_deformation import AbstractViewDeformation
from deformation.abstract_view_deformer import AbstractViewDeformer


class AbstractRenderer(ABC):
    def __init__(self):
        self.image1 = None
        self.image1_data = None

        self.nb_data = 0

    """ Returns the number of primitives """
    def get_nb_data(self):
        return self.nb_data

    """ Renders the view-dependent model """
    @abstractmethod
    def render(self, camera: AbstractCamera, view_deformer: AbstractViewDeformer,
                     view_deformation: AbstractViewDeformation = None):
        pass

    """ Renders the image based on the configuration and parameters defined in the provided model """
    @abstractmethod
    def render_image(self, *args, **kwargs):
        pass

    """ Deform the model based on the camera viewpoint """
    @abstractmethod
    def deform_model(self, camera: AbstractCamera, view_deformation: AbstractViewDeformation,
                     view_deformer: AbstractViewDeformer):
        pass

    """ Get the deformation for a specific viewpoint (View-Deformation) """
    @abstractmethod
    def get_view_deform(self, *args, **kwargs):
        pass

    """ Update the rendering size of the renderer (if needed) """
    def update_renderer_size(self, *args, **kwargs):
        pass

    """ Get the 2D projected points of the actual view-dependent model """
    @abstractmethod
    def get_points2d(self, *args, **kwargs):
        pass

    """ Show the rendered image in the selected canva """
    def show_rendering(self, canva, image=None):
        canva.delete("all")
        if image is None:
            canva.create_image(0, 0, anchor=tk.NW, image=self.image1)
        else:
            canva.create_image(0, 0, anchor=tk.NW, image=image)