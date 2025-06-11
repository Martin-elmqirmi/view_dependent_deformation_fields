import numpy as np
import pyrender
import torch
from PIL import Image, ImageTk

from typing_extensions import override

from camera.mesh_camera import MeshCamera
from deformation.mesh_view_deformation import MeshViewDeformation
from deformation.mesh_view_deformer import MeshViewDeformer
from rendering.abstract_renderer import AbstractRenderer
from utils.mesh_utils import load_scene


class MeshRenderer(AbstractRenderer):
    def __init__(self, data_path, camera: MeshCamera):
        super().__init__()
        self.device = torch.device("cuda")

        self.width = camera.width
        self.height = camera.height

        # Load and normalize the scene with descriptive naming
        scene = load_scene(data_path)

        # Convert to pyrender scene
        self.scene = pyrender.Scene.from_trimesh_scene(scene)
        self.scene.bg_color = (255, 255, 255)
        self.renderer = pyrender.OffscreenRenderer(self.width, self.height)

        # Add camera
        self.camera = pyrender.PerspectiveCamera(yfov=camera.f_rad)
        camera_pose = camera.get_c2w_opengl()
        self.cam_node = self.scene.add(self.camera, pose=camera_pose)

        # Add the lightning of the scene
        self.add_lightning()

        # Get ordered mesh nodes based on geometry metadata
        ordered_geom_names = list(scene.geometry.keys())
        self.mesh_nodes = self.get_ordered_mesh_nodes(ordered_geom_names)

        # Extract vertices
        self.vertices_list = []
        for node in self.mesh_nodes:
            for prim in node.mesh.primitives:
                self.vertices_list.append(torch.tensor(prim.positions, dtype=torch.float32, device=self.device))

        self.all_vertices = torch.cat(self.vertices_list, dim=0)
        self.nb_data = len(self.all_vertices)
        self.mesh_shapes = [v.shape[0] for v in self.vertices_list]
        print(self.mesh_shapes)

    """ Renders the view-dependent mesh """
    def render(self, deformation_camera: MeshCamera, view_deformer: MeshViewDeformer,
               view_deformation: MeshViewDeformation = None):
        deformed_vertices = self.deform_model(deformation_camera, view_deformation, view_deformer)
        self.update_all_mesh_vertices(deformed_vertices)

        # This is time-consuming and could be much better with another mesh rendering library
        # This is done to update the vertex positions in the gpu
        self.renderer.delete()
        self.renderer = pyrender.OffscreenRenderer(self.width, self.height)

        self.set_camera_pose(self.cam_node, deformation_camera)
        self.render_image('image1_data', 'image1')

    """ Renders the image based on the configuration and parameters defined in the provided model """
    def render_image(self, image_attr, photo_image_attr):
        # Set camera position
        color, _ = self.renderer.render(self.scene)
        setattr(self, image_attr, color)
        image = Image.fromarray(color)
        setattr(self, photo_image_attr, ImageTk.PhotoImage(image))

    """ Deform the Mesh based on the camera viewpoint """
    def deform_model(self, camera: MeshCamera, view_deformation: MeshViewDeformation, view_deformer: MeshViewDeformer):
        nb_deformations = len(view_deformer.view_deformations)
        nb_deformations -= 1 if view_deformation else 0

        displacements = view_deformer.get_interpolated_values(camera, nb_deformations, self.nb_data)
        interpolated_vertices = self.all_vertices + displacements

        if view_deformation:
            return self.get_view_deform(camera, view_deformation, interpolated_vertices)

        return interpolated_vertices

    """ Get the deformation for a specific viewpoint (View-Deformation) """
    def get_view_deform(self, camera: MeshCamera, view_deformation: MeshViewDeformation, interpolated_vertices):
        # Project the means and covariance matrices onto the image plane of the camera
        cam_vertices = camera.world_to_cam(interpolated_vertices)  # Camera space
        proj_vertices, depths = camera.proj(cam_vertices)  # Image space

        deform_proj_vertices = view_deformation.deform(proj_vertices)

        un_proj_vertices = camera.un_proj(deform_proj_vertices, depths)

        deformed_vertices = camera.cam_to_world(un_proj_vertices, None)

        if view_deformation.need_update:
            view_deformation.save_view_deformation(deformed_vertices - interpolated_vertices)
            view_deformation.need_update = False

        return deformed_vertices

    """ Update the rendering size of the renderer """
    @override
    def update_renderer_size(self, camera: MeshCamera):
        self.renderer.delete()
        self.width = camera.width
        self.height = camera.height
        self.renderer = pyrender.OffscreenRenderer(self.width, self.height)

    """ Get the 2D projected points of the actual view-dependent mesh """
    def get_points2d(self, view_deformer: MeshViewDeformer, camera: MeshCamera):
        displacements = view_deformer.get_interpolated_values(camera,
                                                                 len(view_deformer.view_deformations) - 1,
                                                                 self.nb_data)
        interpolated_vertices = self.all_vertices + displacements

        # Project the means and covariance matrices onto the image plane of the camera
        cam_vertices = camera.world_to_cam(interpolated_vertices)  # Camera space
        proj_vertices, depths = camera.proj(cam_vertices)  # Image space

        return proj_vertices, - depths

    """ Set the camera pose in the pyrender scene """
    def set_camera_pose(self, camera_node, camera):
        updated_pose = camera.get_c2w_opengl()
        self.scene.set_pose(camera_node, pose=updated_pose)
        return updated_pose

    """ update the mesh vertices of the pyrender scene """
    def update_all_mesh_vertices(self, deformed_vertices):
        deformed_vertices_list = torch.split(deformed_vertices, self.mesh_shapes)
        for i, node in enumerate(self.mesh_nodes):
            for prim in node.mesh.primitives:
                prim.positions = deformed_vertices_list[i].cpu().numpy()

    """ Order the meshes of the model during the loading """
    def get_ordered_mesh_nodes(self, ordered_geom_names):
        mesh_nodes = []
        used_nodes = set()

        # Create a map of vertex counts from geometry names
        geom_vertex_counts = {
            name: int(name.split('_v')[1].split('_')[0]) for name in ordered_geom_names
        }

        for geom_name in ordered_geom_names:
            target_vcount = geom_vertex_counts[geom_name]
            matched = False
            for node in self.scene.mesh_nodes:
                if node in used_nodes:
                    continue
                total_verts = sum(len(prim.positions) for prim in node.mesh.primitives)
                if total_verts == target_vcount:
                    mesh_nodes.append(node)
                    used_nodes.add(node)
                    matched = True
                    break
            if not matched:
                print(
                    f"⚠️ Warning: Could not match mesh node for geometry '{geom_name}' with vertex count {target_vcount}")
        return mesh_nodes

    """ Add lightning to the scene """
    def add_lightning(self):
        # Add ambient light (already present)
        self.scene.ambient_light = np.array([0.4, 0.4, 0.4])  # Slightly reduced to emphasize directional lights

        # Define 3-point directional lighting
        directional_light = pyrender.DirectionalLight(color=np.ones(3), intensity=1.0)

        # Key light (front-right-top)
        light_pose_1 = np.array([
            [1., 0., 0., 2.0],
            [0., 1., 0., 2.0],
            [0., 0., 1., 2.0],
            [0., 0., 0., 1.]
        ])
        self.scene.add(directional_light, pose=light_pose_1)

        # Fill light (front-left-top)
        light_pose_2 = np.array([
            [1., 0., 0., -2.0],
            [0., 1., 0., 2.0],
            [0., 0., 1., 2.0],
            [0., 0., 0., 1.]
        ])
        self.scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=1.0), pose=light_pose_2)

        # Back light (back-top)
        light_pose_3 = np.array([
            [1., 0., 0., 0.0],
            [0., 1., 0., 2.0],
            [0., 0., 1., -2.5],
            [0., 0., 0., 1.]
        ])
        self.scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=1.0), pose=light_pose_3)


