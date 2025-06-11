import numpy as np

from camera.abstract_camera import AbstractCamera
from utils.utils import rotate_azimuth, rotate_polar


class GsplatCamera(AbstractCamera):
    def __init__(self, width: int, height: int, f=60, z_near=0.1, z_far=100.0, azimuth=0.0, polar=0.0, radius=1.5):
        super().__init__(width, height, f, z_near, z_far, azimuth, polar, radius)
        self.up_vector = np.array([0, 1, 0], dtype=np.float32)

    """ Transform the means and covariance matrices from camera space to world space """
    def cam_to_world(self, means, jacobians):
        rot, trans = self.get_rotation_translation()

        # Compute the world means
        new_means = (rot.T @ (means - trans).T).T

        # Compute the world covariance matrices
        world_covars = None
        if jacobians is not None:
            world_covars = rot.T @ jacobians @ rot

        return new_means, world_covars

    """ Move the camera to new position following a 2d displacement of the mouse """
    def move_camera(self, event, last_mouse_position):
        sensitivity = 0.2
        dx = - (event.x - last_mouse_position[0]) * sensitivity
        dy = - (event.y - last_mouse_position[1]) * sensitivity

        self.azimuth = rotate_azimuth(self.azimuth, dx)
        self.polar = rotate_polar(self.polar, dy)

        self.eye = self.get_camera_position()
