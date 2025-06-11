import numpy as np

from camera.abstract_camera import AbstractCamera
from utils.utils import rotate_azimuth, rotate_polar


class MeshCamera(AbstractCamera):
    def __init__(self, width: int, height: int, f=60, z_near=0.1, z_far=100.0, azimuth=0.0, polar=0.0, radius=1.5):
        super().__init__(width, height, f, z_near, z_far, azimuth, polar, radius)
        self.up_vector = np.array([0, 1, 0], dtype=np.float32)

    """ Get the projection matrix of the camera """
    def get_k(self):
        k = np.array([[- self.fx / self.aspect_ratio, 0, self.cx],
                      [0, - self.fx / self.aspect_ratio, self.cy],
                      [0, 0, 1]], dtype=np.float32)
        return k

    """ Transform the means and covariance matrices from camera space to world space """
    def cam_to_world(self, vertices, jacobians):
        rot, trans = self.get_rotation_translation()

        # Compute the world means
        new_vertices = (rot.T @ (vertices - trans).T).T

        return new_vertices

    """ Get the camera to world matrix for openGL convention """
    def get_c2w_opengl(self):
        forward = self.look_at - self.eye
        forward /= np.linalg.norm(forward)

        right = np.cross(forward, self.up_vector)
        right /= np.linalg.norm(right)

        up = np.cross(right, forward)

        rot = np.column_stack([right, up, -forward])

        c2w = np.eye(4)
        c2w[:3, :3] = rot
        c2w[:3, 3] = self.eye

        return c2w

    """ Move the camera to new position following a 2d displacement of the mouse """
    def move_camera(self, event, last_mouse_position):
        sensitivity = 0.2
        dx = (event.x - last_mouse_position[0]) * sensitivity
        dy = (event.y - last_mouse_position[1]) * sensitivity

        self.azimuth = rotate_azimuth(self.azimuth, dx)
        self.polar = rotate_polar(self.polar, dy)

        self.eye = self.get_camera_position()
