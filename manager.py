import os.path
import pickle

import numpy as np

from camera.abstract_camera import AbstractCamera
from utils.gui_utils import ask_for_filename, draw_mesh
from utils.initializer import initialize_camera, initialize_renderer, initialize_vd, initialize_view_deformer

""" Manager class for the rendering and the deformations.
    - handles both Mesh and Gsplat renderers.
    - handles the deformations.
    - handles the interpolation of the deformations 
"""
class Manager:
    def __init__(self, data_path, renderer_type, data):
        self.data_path = data_path
        self.renderer_type = renderer_type

        self.deformation_window_width = 400
        self.deformation_window_height = 400

        self.window_width = 400
        self.window_height = 400

        self.deformation_camera = initialize_camera(renderer_type, self.window_width, self.window_height)

        self.renderer = initialize_renderer(renderer_type, 0, 0, 1, data_path, self.deformation_camera)

        self.view_deformer = initialize_view_deformer(renderer_type)
        self.initialize_view_deformer(data)

        # Some values
        self.last_mouse_position = None
        self.mouse_position = None
        self.view_deformation = None
        self.first_point = None

        # Some booleans
        self.movable = False
        self.select_zone = False
        self.show_mesh = True
        self.plane_back = True

        # Some lists
        self.view_points = []
        self.saved_images = []

    """ Save a view deformation in the view deformer """
    def save_view_deformation(self):
        self.view_deformation = None
        print("Save View Deformation!")

    """ Add a new view deformation to the view deformer """
    def new_view_deformation(self):
        index = len(self.view_deformer.view_deformations)
        self.view_deformation = index
        self.view_deformer.new_view_deformation(self.deformation_camera, self.renderer.get_nb_data(), None, None)

        return index

    """ Move handles """
    def move_handles(self):
        self.movable = not self.movable
        self.view_deformer.view_deformations[self.view_deformation].compute_weight_matrix()
        self.mouse_position = None

    """ Put the camera on the ith view deformation """
    def checkout_view_deformation(self, i):
        self.deformation_camera.update(self.view_deformer.view_deformations[i].camera)

    """ Generate the 2D mesh for the ith view deformation"""
    def mesh_generation_callback(self, i):
        (self.view_deformer.view_deformations[i]
        .select_bbw_mesh_tool(
            self.renderer.image1_data,
            self.renderer.get_points2d(
                self.view_deformer,
                self.view_deformer.view_deformations[i].camera
            )[0]
        ))
        self.movable = False

    """ Delete a view deformation from the view deformer"""
    def delete_view_deformation(self, index):
        self.view_deformer.view_deformations.pop(index)
        if self.view_deformation is not None:
            if index == self.view_deformation:
                self.view_deformation = None
            elif index < self.view_deformation:
                self.view_deformation -= 1

    """ Save the model in a pkl file. The file name is the same as the data path."""
    def save_model(self):
        data_to_save = {
            "renderer_type": self.renderer_type,
            "data_path": self.data_path,
            "view_deformations": [vd.to_dict() for vd in self.view_deformer.view_deformations],
        }

        file_name = ask_for_filename("Save Model", "Please Enter a File Name")
        _, file_extension = os.path.splitext(self.data_path)

        directory = "unknown"
        if file_extension == ".glb":
            directory = "vd_meshes"
        elif file_extension == ".ply":
            directory = "vd_gsplat"

        if not file_name.lower().endswith('.pkl'):
            file_name += '.pkl'

        save_path = os.path.join("models", directory, file_name)
        with open(save_path, "wb") as file:
            pickle.dump(data_to_save, file)

    """ Initialize the view deformer when loading a view-dependent model."""
    def initialize_view_deformer(self, data):
        if data is not None:
            for vd in data:
                camera_data = vd['camera']
                camera = initialize_camera(self.renderer_type, self.window_width, self.window_height,
                                           camera_data['azimuth'], camera_data['polar'])
                view_deformation = initialize_vd(camera, vd)
                self.view_deformer.view_deformations.append(view_deformation)

    """ Resize the camera size when resizing the deformation rendering window """
    def on_deformation_resize(self, width, height):
        self.deformation_camera.update_camera_window_size(width, height)
        self.renderer.update_renderer_size(self.deformation_camera)

    """ Mouse Press Event """
    def mouse_press_event(self, event):
        if event.state & 0x4:  # Check if Ctrl is pressed
            if self.view_deformation is not None:
                # Select the closest handle
                self.view_deformer.view_deformations[self.view_deformation].select_handle(event)
        else:
            if self.view_deformation is None:
                # Get position for camera movement
                self.last_mouse_position = np.array([event.x, event.y])
            if self.view_deformation is not None and not self.movable:
                # Add the closest vertex to the handles list
                self.view_deformer.view_deformations[self.view_deformation].add_or_remove_handle(event)
            if self.view_deformation is not None and self.movable:
                # Get position for handle movement
                self.mouse_position = np.array([event.x, event.y])
                # Get the closest handle to move it
                self.view_deformer.view_deformations[self.view_deformation].check_handle(event)

    """ Mouse move event """
    def mouse_move_event(self, event, camera: AbstractCamera):
        if self.last_mouse_position is not None:
            # Move the camera
            camera.move_camera(event, self.last_mouse_position)
            self.last_mouse_position = np.array([event.x, event.y])
        if self.view_deformation is not None and self.movable:
            # Check if the Shift key is pressed
            shift_pressed = bool(event.state & 0x0001)

            # Determine deformation type based on Shift key state
            if shift_pressed:
                deformation_type = "rotation"
            else:
                deformation_type = "displacement"

            # Move the handles
            self.view_deformer.view_deformations[self.view_deformation].get_deformation(event,
                                                                                        self.mouse_position,
                                                                                        deformation_type)
            self.mouse_position = np.array([event.x, event.y])

    """ Mouse release event """
    def mouse_release_event(self, event):
        if event.num == 1:  # Left mouse button
            self.last_mouse_position = None
        if self.view_deformation is not None and self.movable:
            # Check if a handle should be removed based on the position of the click
            self.view_deformer.view_deformations[self.view_deformation].check_handle_remove(event)

    """ Mouse wheel event """
    def mouse_wheel_event(self, event, camera: AbstractCamera):
        # Move the camera distance to the middle
        camera.change_radius(event)

    """ Update the rendering windows (Call this function every time you want an update) """
    def update(self, big_canvas):
        # Render the model to build the images in the renderer
        view_deformation = None
        if self.view_deformation is not None:
            view_deformation = self.view_deformer.view_deformations[self.view_deformation]
            self.renderer.render(self.deformation_camera, self.view_deformer, view_deformation)
        else:
            self.renderer.render(self.deformation_camera, self.view_deformer)

        # Show the rendered images on the rendering canvas
        self.renderer.show_rendering(big_canvas, self.renderer.image1)

        # Show the 2D mesh
        if view_deformation is not None and view_deformation.bbw_mesh_tool is not None:
            draw_mesh(big_canvas, view_deformation.bbw_mesh_tool.bbw_mesh, self.show_mesh)
