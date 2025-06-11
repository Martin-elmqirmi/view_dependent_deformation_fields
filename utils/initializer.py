import torch

from camera.abstract_camera import AbstractCamera
from camera.gsplat_camera import GsplatCamera
from camera.mesh_camera import MeshCamera
from deformation.gsplat_view_deformation import GsplatViewDeformation
from deformation.gsplat_view_deformer import GsplatViewDeformer
from deformation.mesh_view_deformation import MeshViewDeformation
from deformation.mesh_view_deformer import MeshViewDeformer
from rendering.gs_renderer import GaussianSplattingRenderer
from rendering.mesh_renderer import MeshRenderer


""" Initialize the camera based on the model type """
def initialize_camera(renderer_type, width, height, azimuth=0.0, polar=0.0):
    if renderer_type == "Gaussian":
        return GsplatCamera(width, height, azimuth=azimuth, polar=polar)
    elif renderer_type == "Mesh":
        return MeshCamera(width, height, azimuth=azimuth, polar=polar)
    else:
        raise ValueError(f"Unknown renderer type: {renderer_type}")


""" Initialize the renderer based on the model type """
def initialize_renderer(renderer_type, local_rank, world_rank, world_size, data_path, camera):
    if renderer_type == "Gaussian":
        return GaussianSplattingRenderer(data_path, local_rank, world_rank, world_size)
    elif renderer_type == "Mesh":
        return MeshRenderer(data_path, camera)
    else:
        raise ValueError(f"Unknown renderer type: {renderer_type}")


""" Initialize the view deformer based on the model type """
def initialize_view_deformer(renderer_type):
    if renderer_type == "Gaussian":
        return GsplatViewDeformer()
    elif renderer_type == "Mesh":
        return MeshViewDeformer()
    else:
        raise ValueError(f"Unknown renderer type: {renderer_type}")


""" Initialize a view deformation based on the model type """
def initialize_vd(camera: AbstractCamera, vd_data):
    displacements = torch.tensor(vd_data["displacements"], device="cuda")

    # Gaussian Splatting Case
    if vd_data.get("jacobians") is not None:
        jacobians = torch.tensor(vd_data["jacobians"], device="cuda")
        view_deformation = GsplatViewDeformation(camera, vd_data["nb_data"], displacements, jacobians)
    # Mesh Case
    else:
        view_deformation = MeshViewDeformation(camera, vd_data["nb_data"], displacements)

    # Update the azimuth and polar variance
    view_deformation.change_variance_azimuth(vd_data["variance_azimuth"])
    view_deformation.change_variance_polar(vd_data["variance_polar"])

    return view_deformation