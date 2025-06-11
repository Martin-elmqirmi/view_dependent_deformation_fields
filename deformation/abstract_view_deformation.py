import copy
from abc import ABC, abstractmethod
import numpy as np

from camera.abstract_camera import AbstractCamera
from deformation.tools import BbwMeshTool


class AbstractViewDeformation(ABC):
    def __init__(self,
                 camera: AbstractCamera,
                 nb_data
                 ):

        self.camera = copy.deepcopy(camera)
        self.nb_data = nb_data
        self.mean_azimuth = camera.azimuth
        self.mean_polar = camera.polar
        self.variance_azimuth = 15
        self.variance_polar = 15
        self.need_update = False

        self.bbw_mesh_tool = None

    """ Change the azimuth variance of the gaussian """
    def change_variance_azimuth(self, variance_azimuth):
        self.variance_azimuth = variance_azimuth

    """ Change the polar variance of the gaussian """
    def change_variance_polar(self, variance_polar):
        self.variance_polar = variance_polar

    """ Save the view deformation in 3D """
    @abstractmethod
    def save_view_deformation(self, displacement_vectors, jacobians=None):
        pass

    """ Select the 2D mesh tool to deform the 3D model """
    def select_bbw_mesh_tool(self, image, points2d):
        if self.bbw_mesh_tool is None:
            vertices2d = points2d.cpu().numpy().astype(np.float32)
            self.bbw_mesh_tool = BbwMeshTool()
            self.bbw_mesh_tool.initialize_bbw_mesh(vertices2d, image)
        else:
            self.delete_bbw_mesh_tool()

    """ Delete the 2D mesh tool """
    def delete_bbw_mesh_tool(self):
        del self.bbw_mesh_tool
        self.bbw_mesh_tool = None

    """ Select a handle to move """
    def select_handle(self, event):
        if self.bbw_mesh_tool is not None:
            self.bbw_mesh_tool.bbw_mesh.select_handle(event)

    """ Add or Remove a handle on the 2D mesh """
    def add_or_remove_handle(self, event):
        if self.bbw_mesh_tool is not None:
            self.bbw_mesh_tool.bbw_mesh.add_or_remove_handle(event)

    """ Check if a handle can be selected """
    def check_handle(self, event):
        if self.bbw_mesh_tool is not None:
            self.bbw_mesh_tool.bbw_mesh.check_handle(event)

    """ Get the deformation of the 2D mesh.
        Here it is possible to add more tools to deform the 2D mesh """
    def get_deformation(self, event, last_mouse_position, type):
        if self.bbw_mesh_tool is not None:
            self.bbw_mesh_tool.bbw_mesh.get_deformation(event, last_mouse_position, type)

    """ Check if a handle can be removed """
    def check_handle_remove(self, event):
        if self.bbw_mesh_tool is not None:
            self.bbw_mesh_tool.bbw_mesh.check_handle_remove(event)

    """ computer weight matrix of the 2D mesh based on the controllers (handles) """
    def compute_weight_matrix(self):
        if self.bbw_mesh_tool is not None:
            self.bbw_mesh_tool.bbw_mesh.compute_weight_matrix()

    """ Get the deformation of the projected 2D points of the 3D model using the 2D mesh tool.
        Here it is possible to add more tools to deform the 3D model """
    @abstractmethod
    def deform(self, points2d):
       pass

    """ Save the view deformation as a dict to save the view-dependent model """
    @abstractmethod
    def to_dict(self):
        pass
