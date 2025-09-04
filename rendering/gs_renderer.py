import math
import tkinter as tk

import numpy as np
import torch
from PIL import ImageTk, Image
from gsplat import rasterization, quat_scale_to_covar_preci

from camera.gsplat_camera import GsplatCamera
from deformation.gsplat_view_deformation import GsplatViewDeformation
from deformation.gsplat_view_deformer import GsplatViewDeformer
from rendering.abstract_renderer import AbstractRenderer
from utils.gsplat_utils import load_ply


""" Gsplat Renderer for View-Dependent Gaussian Splatting Models """
class GaussianSplattingRenderer(AbstractRenderer):
    def __init__(self, data_path, local_rank, world_rank, world_size):
        super().__init__()
        self.device = torch.device("cuda", local_rank)

        xyz, opacities, scales, rots, features_dc, features_extra = load_ply(data_path)
        self.means = torch.tensor(xyz, dtype=torch.float32, device=self.device).contiguous()
        self.sh0 = torch.tensor(features_dc, dtype=torch.float32, device=self.device).transpose(1, 2).contiguous()
        self.shN = torch.tensor(features_extra, dtype=torch.float32, device=self.device).transpose(1, 2).contiguous()
        self.opacities = torch.sigmoid(torch.tensor(opacities, dtype=torch.float32, device=self.device)).squeeze()
        self.scales = torch.exp(torch.tensor(scales, dtype=torch.float32, device=self.device)).contiguous()
        self.quats = torch.nn.functional.normalize(torch.tensor(rots, dtype=torch.float32, device=self.device)).contiguous()

        # # Normalization of the colors
        max_values_per_channel, _ = torch.max(self.sh0, dim=-1, keepdim=True)
        max_values_per_channel = torch.clamp(max_values_per_channel, min=1.0)  # Prevent division by 0

        # Normalize each channel separately
        self.sh0 = self.sh0 / max_values_per_channel

        self.nb_data = len(self.means)

        self.covars, _ = quat_scale_to_covar_preci(self.quats, self.scales, True)
        self.colors = torch.cat((self.sh0, self.shN), dim=1)
        self.sh_degree = int(math.sqrt(self.colors.shape[-2]) - 1)

        self.world_rank = world_rank
        self.world_size = world_size

    """ Renders the view-dependent GSplat """
    def render(self, deformation_camera: GsplatCamera, view_deformer: GsplatViewDeformer,
               view_deformation: GsplatViewDeformation = None):
        # Do the deformation of the gaussian. This handles the interpolation of the deformation
        deformed_means, deformed_covars = self.deform_model(deformation_camera, view_deformation, view_deformer)

        # Render image 1
        self.render_image(deformation_camera, deformed_means, deformed_covars,
                          'image1_data', 'image1')

    """ Renders the image based on the configuration and parameters defined in the provided model """
    def render_image(self, camera, means, covars, image_attr, photo_image_attr):
        viewmats, Ks = self.get_matrices(camera)

        # Render the deformed gaussian
        render_colors, render_alphas, meta = rasterization(
            means,  # [N, 3]
            self.quats,  # [N, 4]
            self.scales,  # [N, 3]
            self.opacities,  # [N]
            self.colors,  # [N, 3]
            viewmats,  # [C, 4, 4]
            Ks,  # [C, 3, 3]
            camera.width,
            camera.height,
            render_mode="RGB",
            sh_degree=self.sh_degree,
            covars=covars,
            backgrounds=torch.ones(3, device=self.device)
        )
        render_rgbs = render_colors[0, ..., 0:3].cpu().numpy()
        color = (render_rgbs * 255).astype(np.uint8)
        setattr(self, image_attr, color)
        image = Image.fromarray(color)
        setattr(self, photo_image_attr, ImageTk.PhotoImage(image))

    """ Deform the Gsplat based on the camera viewpoint """
    def deform_model(self, camera: GsplatCamera, view_deformation: GsplatViewDeformation,
                         view_deformer: GsplatViewDeformer):
        nb_deformations = len(view_deformer.view_deformations)
        nb_deformations -= 1 if view_deformation else 0

        displacements, jacobians = view_deformer.get_interpolated_values(camera, nb_deformations, self.nb_data)
        interpolated_means = self.means + displacements
        interpolated_covars = jacobians @ self.covars @ jacobians.transpose(1, 2)

        if view_deformation:
            return self.get_view_deform(camera, view_deformation, interpolated_means, interpolated_covars)

        return interpolated_means, interpolated_covars

    """ Get the deformation for a specific viewpoint (View-Deformation) """
    def get_view_deform(self, camera: GsplatCamera, view_deformation: GsplatViewDeformation,
                             interpolated_means, interpolated_covars):
        # Project the means and covariance matrices onto the image plane of the camera
        cam_means = camera.world_to_cam(interpolated_means)
        proj_means, depths = camera.proj(cam_means)

        # Get the 2D deformation using the deformation tools activated for view_deformation
        deform_proj_means, jacobians = view_deformation.deform(proj_means)

        # Compute the jacobians for the 2D covariance matrix
        jacobians_3d = torch.zeros((jacobians.shape[0], 3, 3), device=self.device)
        jacobians_3d[:, :2, :2] = jacobians
        jacobians_3d[:, 2, 2] = 1.0

        # Unproject the means and jacobians
        un_proj_means = camera.un_proj(deform_proj_means, depths)
        deformed_means, world_jacobians = camera.cam_to_world(un_proj_means, jacobians_3d)

        # Get the 3D deformation
        deformed_covars = world_jacobians @ interpolated_covars @ world_jacobians.transpose(1, 2)

        if view_deformation.need_update:
            view_deformation.save_view_deformation(deformed_means - interpolated_means, world_jacobians)
            view_deformation.need_update = False

        return deformed_means, deformed_covars

    """ Get the 2D projected means of the actual view-dependent 3DGS model """
    def get_points2d(self, view_deformer: GsplatViewDeformer, camera: GsplatCamera):
        initial_means = self.means.clone()
        if len(view_deformer.view_deformations) > 0:
            displacements, _ = view_deformer.get_interpolated_values(camera,
                                                                     len(view_deformer.view_deformations) - 1,
                                                                     self.nb_data)
            initial_means += displacements

        # Project the means and covariance matrices onto the image plane of the camera
        cam_vertices = camera.world_to_cam(initial_means)  # Camera space
        proj_vertices = camera.proj(cam_vertices)  # Image space

        return proj_vertices

    """ Get the extrinsic and intrinsic matrices of the camera """
    def get_matrices(self, camera: GsplatCamera):
        view_mat = camera.get_w2c()
        k = camera.get_k()
        view_mats = np.array([view_mat])
        ks = np.array([k])
        viewmats = torch.tensor(view_mats, dtype=torch.float32).to(self.device).contiguous()  # View matrices
        Ks = torch.tensor(ks).to(self.device).contiguous()  # Intrinsic parameters of the cameras
        return viewmats, Ks
