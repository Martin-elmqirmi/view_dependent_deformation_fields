import math

import numpy as np
from plyfile import PlyData
import torch
from gsplat import rasterization
from PIL import Image

""" Function to load the Gsplat model from the .ply file """
def load_ply(path):
    plydata = PlyData.read(path)

    xyz = np.stack((np.asarray(plydata.elements[0]["x"]),
                    np.asarray(plydata.elements[0]["y"]),
                    np.asarray(plydata.elements[0]["z"])), axis=1)
    opacities = np.asarray(plydata.elements[0]["opacity"])[..., np.newaxis]

    features_dc = np.zeros((xyz.shape[0], 3, 1))
    features_dc[:, 0, 0] = np.asarray(plydata.elements[0]["f_dc_0"])
    features_dc[:, 1, 0] = np.asarray(plydata.elements[0]["f_dc_1"])
    features_dc[:, 2, 0] = np.asarray(plydata.elements[0]["f_dc_2"])

    extra_f_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("f_rest_")]
    extra_f_names = sorted(extra_f_names, key=lambda x: int(x.split('_')[-1]))

    # Infer SH degree
    num_coeffs_per_channel = len(extra_f_names) // 3 + 1
    sh_degree = int(np.sqrt(num_coeffs_per_channel) - 1)
    assert len(extra_f_names) == 3 * ((sh_degree + 1) ** 2 - 1), "Invalid SH data length."

    features_extra = np.zeros((xyz.shape[0], len(extra_f_names)))
    for idx, attr_name in enumerate(extra_f_names):
        features_extra[:, idx] = np.asarray(plydata.elements[0][attr_name])
    features_extra = features_extra.reshape((features_extra.shape[0], 3, (sh_degree + 1) ** 2 - 1))

    scale_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("scale_")]
    scale_names = sorted(scale_names, key=lambda x: int(x.split('_')[-1]))
    scales = np.zeros((xyz.shape[0], len(scale_names)))
    for idx, attr_name in enumerate(scale_names):
        scales[:, idx] = np.asarray(plydata.elements[0][attr_name])

    rot_names = [p.name for p in plydata.elements[0].properties if p.name.startswith("rot")]
    rot_names = sorted(rot_names, key=lambda x: int(x.split('_')[-1]))
    rots = np.zeros((xyz.shape[0], len(rot_names)))
    for idx, attr_name in enumerate(rot_names):
        rots[:, idx] = np.asarray(plydata.elements[0][attr_name])

    return xyz, opacities, scales, rots, features_dc, features_extra

def render_gsplat_image(data_path, device, image_path):
    # Do the rendering of the 3DGS
    xyz, opacities, scales, rots, features_dc, features_extra = load_ply(data_path)
    means = torch.tensor(xyz, dtype=torch.float32, device=device).contiguous()
    sh0 = torch.tensor(features_dc, dtype=torch.float32, device=device).transpose(1, 2).contiguous()
    shN = torch.tensor(features_extra, dtype=torch.float32, device=device).transpose(1, 2).contiguous()
    opacities = torch.sigmoid(torch.tensor(opacities, dtype=torch.float32, device=device)).squeeze()
    scales = torch.exp(torch.tensor(scales, dtype=torch.float32, device=device)).contiguous()
    quats = torch.nn.functional.normalize(torch.tensor(rots, dtype=torch.float32, device=device)).contiguous()

    max_values_per_channel, _ = torch.max(sh0, dim=-1, keepdim=True)
    max_values_per_channel = torch.clamp(max_values_per_channel, min=1.0)
    sh0 = sh0 / max_values_per_channel
    colors = torch.cat((sh0, shN), dim=1)
    sh_degree = int(math.sqrt(colors.shape[-2]) - 1)

    viewmats = torch.tensor([[[1, 0, 0, 0],
                              [0, 1, 0, 0],
                              [0, 0, 1, 1.5],
                              [0, 0, 0, 1]]], dtype=torch.float32).to(device)
    f = 256 / (2.0 * np.tan(np.radians(60) / 2.))
    Ks = torch.tensor([[[f, 0, 128],
                        [0, f, 128],
                        [0, 0, 1]]], dtype=torch.float32).to(device)

    render_colors, _, _ = rasterization(
        means, quats, scales, opacities, colors,
        viewmats, Ks, 256, 256,
        render_mode="RGB",
        backgrounds=torch.tensor([[1., 1., 1.]], device=device),
        sh_degree=sh_degree
    )
    render_rgbs = render_colors[0, ..., 0:3].cpu().numpy()
    img = Image.fromarray((render_rgbs * 255).astype(np.uint8))
    img.save(image_path)