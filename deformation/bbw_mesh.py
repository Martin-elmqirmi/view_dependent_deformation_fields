import math

import igl
import numpy as np
import torch

from utils.utils import get_contour_mesh


""" Class to represent a handle for the 2D mesh """
class Handle:
    def __init__(self, initial_position):
        self.angle = 0.0
        self.initial_position = initial_position
        self.rotation_matrix = np.array([[1.0, 0.0], [0.0, 1.0]])
        self.new_position = initial_position.copy()
        self.delta = np.array([0.0, 0.0])

    """ Compute the translation """
    def compute_delta(self):
        self.delta = self.new_position - np.dot(self.rotation_matrix, self.initial_position)

    """ Update the rotation matrix of the handle """
    def update_rotation_matrix(self, angle):
        self.angle += angle
        cos_theta = np.cos(self.angle)
        sin_theta = np.sin(self.angle)
        self.rotation_matrix = np.array([[cos_theta, -sin_theta],
                                         [sin_theta, cos_theta]])
        self.compute_delta()

    """ Update the position of the handle """
    def update_new_position(self, displacement):
        self.new_position += displacement
        self.compute_delta()

    """ Get the Transformation matrix of the handle """
    def get_transformation_matrix(self):
        delta_reshaped = self.delta.reshape(2, 1)
        combined_matrix = np.hstack((self.rotation_matrix, delta_reshaped))
        return combined_matrix


""" Class to represent the 2D mesh deformed using BBW """
class BbwMesh:
    def __init__(self, image):
        self.old_angle = 0

        self.bbw = igl.BBW()

        self.vertices, self.faces = get_contour_mesh(image)
        self.vertices_augmented = np.hstack((self.vertices.copy(), np.ones((self.vertices.shape[0], 1))))
        self.new_vertices = self.vertices.copy()
        self.gradients = igl.grad(np.hstack([self.vertices, np.ones((self.vertices.shape[0], 1))]), self.faces)
        self.jacobians = torch.eye(2, dtype=torch.float32).repeat(len(self.faces), 1, 1)

        self.new_vertices_tensor = torch.from_numpy(self.new_vertices).type(torch.float32)

        self.original_vertices = self.vertices.copy()
        self.original_vertices_augmented = np.hstack(
            (self.original_vertices, np.ones((self.original_vertices.shape[0], 1))))

        self.handles_index = np.array([])
        self.handles = []
        self.selected_handles_index = np.array([])

        self.points2d = None

        self.weight_matrix = None

    """ Compute the weight matrix based on the controllers (handles) """
    def compute_weight_matrix(self):
        identity_matrix = np.identity(len(self.handles))
        self.weight_matrix = self.bbw.solve(self.original_vertices, self.faces, self.handles_index, identity_matrix)

        row_sums = np.clip(self.weight_matrix.sum(axis=1, keepdims=True), a_min=1, a_max=None)
        self.weight_matrix /= row_sums

        self.vertices = self.new_vertices.copy()

    """ Check if handle is selectable """
    def check_handle(self, event):
        if len(self.selected_handles_index) < 1:
            self.select_handle(event)
            self.compute_weight_matrix()

    """ Check if  """
    def check_handle_remove(self, event):
        if len(self.selected_handles_index) == 1:
            self.select_handle(event)

    """ Get the 2D deformation based on the controllers (handles) and BBW """
    def get_deformation(self, event, mouse_position, deformation_type):
        dx, dy = event.x - mouse_position[0], event.y - mouse_position[1]

        if deformation_type == 'rotation':
            displacement = np.array([0., 0.])
            angle = dx * 0.05  # Scale dx to a small angle (in radians)
        else:
            displacement = np.array([dx, dy])
            angle = 0.0

        # Update positions of the selected handles
        for i, selected_handle in enumerate(self.selected_handles_index):
            index = int(selected_handle)
            if deformation_type == 'rotation':
                self.handles[index].update_rotation_matrix(angle)
            else:
                self.handles[index].update_new_position(displacement)

        # Get all the transformation matrices
        transformation_matrices = np.array([handle.get_transformation_matrix() for handle in self.handles])
        transformed_points = np.einsum('mij,nj->mni', transformation_matrices, self.original_vertices_augmented)

        # Calculate new vertices based on the weight matrix
        result = self.weight_matrix[:, :, np.newaxis] * transformed_points.transpose(1, 0, 2)
        self.new_vertices = np.sum(result, axis=1)
        self.new_vertices_tensor = torch.from_numpy(self.new_vertices).type(torch.float32)
        self.compute_jacobians()

    """ Find the closest vertex to the click event """
    def find_closest_vertex(self, event, vertices):
        x = event.x
        y = event.y
        distances = [math.sqrt((vx - x) ** 2 + (vy - y) ** 2) for vx, vy in vertices]
        closest_index = distances.index(min(distances))

        return closest_index

    """ Add or remove a handle based on the click event """
    def add_or_remove_handle(self, event):
        closest_index = self.find_closest_vertex(event, self.new_vertices)

        if closest_index in self.handles_index:
            index = np.where(self.handles_index == closest_index)[0]
            self.selected_handles_index = self.selected_handles_index[self.selected_handles_index != closest_index]
            self.handles_index = np.delete(self.handles_index, index)
            self.handles.pop(index[0])
        else:
            self.handles_index = np.append(self.handles_index, closest_index)
            handle = Handle(self.new_vertices[closest_index])
            self.handles.append(handle)

    """ Select a handle based on the click event """
    def select_handle(self, event):
        handles = self.new_vertices[self.handles_index.astype(int)]
        closest_index = self.find_closest_vertex(event, handles)

        # Toggle presence of closest_index
        self.selected_handles_index = np.setxor1d(self.selected_handles_index, [closest_index])

    """ Compute the jacobians of the triangle faces """
    def compute_jacobians(self):
        jacobians = self.gradients * np.hstack([self.new_vertices, np.ones((self.new_vertices.shape[0], 1))])
        rows_to_keep = 2 * jacobians.shape[0] // 3
        jacobians = jacobians[:rows_to_keep, :2].T

        n = len(self.faces)
        x_part = jacobians[:, :n]
        y_part = jacobians[:, n:]

        jacobians2d = torch.from_numpy(np.stack([x_part, y_part], axis=1)).type(torch.float32)
        self.jacobians = jacobians2d.permute(2, 0, 1)
