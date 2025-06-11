from abc import ABC, abstractmethod
from math import tan, radians

import numpy as np
import torch
from torch import Tensor

from utils.utils import get_cartesian_coordinates, rotate_azimuth, rotate_polar


class AbstractCamera(ABC):
    def __init__(self, width: int, height: int, f=60, z_near=0.1, z_far=100.0, azimuth=0.0, polar=0.0, radius=1.5):
        self.width = width
        self.height = height
        self.f_rad = radians(f)
        self.f = f
        self.aspect_ratio = width / height
        self.fx = width / (2.0 * tan(self.f_rad / 2.))
        self.cx = width / 2.0
        self.cy = height / 2.0
        self.z_near = z_near
        self.z_far = z_far
        self.azimuth = azimuth
        self.polar = polar
        self.radius = radius
        self.look_at = np.array([0., 0., 0.], dtype=np.float32)
        self.up_vector = np.array([0., 1., 0.], dtype=np.float32)
        self.eye = self.get_camera_position()

    """ Update camera window size """
    def update_camera_window_size(self, width, height):
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        self.fx = width / (2.0 * tan(self.f_rad / 2.))
        self.cx = width / 2.0
        self.cy = height / 2.0

    """ Get the camera position in the world space """
    def get_camera_position(self):
        x, y, z = get_cartesian_coordinates(self.radius, self.azimuth, self.polar)
        return np.array([x, y, z], dtype=np.float32)

    def update_position(self, azimuth, polar):
        self.azimuth = azimuth
        self.polar = polar

        self.eye = self.get_camera_position()

    def update(self, camera):
        self.azimuth = camera.azimuth
        self.polar = camera.polar
        self.look_at = camera.look_at
        self.up_vector = camera.up_vector
        self.eye = camera.eye
        self.radius = camera.radius

    """ Get the projection matrix of the camera """
    def get_k(self):
        cx = self.width / 2.0
        cy = self.height / 2.0
        return np.array([[self.fx, 0, cx],
                         [0, self.fx, cy],
                         [0, 0, 1]], dtype=np.float32)

    """ Get the camera to world matrix """
    def get_c2w(self):
        forward = self.look_at - self.eye
        forward /= np.linalg.norm(forward)

        right = np.cross(self.up_vector, forward)
        right /= np.linalg.norm(right)

        up = np.cross(forward, right)

        rot = np.array([right, up, forward])

        trans = self.eye

        c2w = np.eye(4)
        c2w[:3, :3] = rot.T
        c2w[:3, 3] = trans

        return c2w

    """ Get the world to camera matrix """
    def get_w2c(self):
        c2w = self.get_c2w()
        view_mat = np.linalg.inv(c2w)
        return view_mat

    """ Get the rotation and translation matrices of the camera """
    def get_rotation_translation(self):
        view_mat = self.get_w2c()

        rot = torch.tensor([
            [view_mat[0, 0], view_mat[0, 1], view_mat[0, 2]],
            [view_mat[1, 0], view_mat[1, 1], view_mat[1, 2]],
            [view_mat[2, 0], view_mat[2, 1], view_mat[2, 2]],
        ], device='cuda:0', dtype=torch.float32)

        trans = torch.tensor([view_mat[0, 3], view_mat[1, 3], view_mat[2, 3]], device='cuda:0', dtype=torch.float32)

        return rot, trans

    """ Transform the points from world space to camera space """
    def world_to_cam(self, points):
        rot, trans = self.get_rotation_translation()
        new_points = (rot @ points.T).T + trans

        return new_points

    """ Transform the points and covariance matrices from camera space to world space """
    @abstractmethod
    def cam_to_world(self, points, jacobians):
        pass

    """ Transform the points and covariance matrices from camera space to image space """
    def proj(self, points: Tensor):
        k = torch.tensor(self.get_k()[:2, :], device='cuda:0')

        depths = points[:, 2]

        proj_points = (k @ points.T / depths).T

        return proj_points, depths

    """ Transform the points from image space to camera space """
    def un_proj(self, points: Tensor, depths):
        inv_k = torch.tensor(np.linalg.inv(self.get_k()), dtype=torch.float32, device='cuda:0')
        depths = depths.unsqueeze(1)
        un_proj_points = torch.cat([points * depths, depths], dim=1).type(torch.float32)
        un_proj_points = un_proj_points @ inv_k.T

        return un_proj_points

    """ Move the camera to new position following a 2d displacement of the mouse """
    @abstractmethod
    def move_camera(self, event, last_mouse_position):
        pass

    """ Change the radius of the sphere where the camera is """
    def change_radius(self, event):
        if event.delta > 0:
            self.radius -= 0.2
        else:
            self.radius += 0.2
        self.eye = self.get_camera_position()

    def get_params(self):
        return self.azimuth, self.polar

    """Serialize the Camera object to a dictionary."""
    def to_dict(self):
        return {
            "width": self.width,
            "height": self.height,
            "f": self.f,
            "z_near": self.z_near,
            "z_far": self.z_far,
            "azimuth": self.azimuth,
            "polar": self.polar,
            "radius": self.radius,
        }
