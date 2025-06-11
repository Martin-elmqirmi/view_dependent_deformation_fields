import torch
from utils.gsplat_utils import render_gsplat_image
from windows.abstract_model_window import AbstractModelWindow


class GsplatWindow(AbstractModelWindow):
    def __init__(self, parent, model_dir):
        self.device = torch.device("cuda", 0)
        super().__init__(parent, model_dir, "models/gsplat/images", ".ply", "Gaussian")

    def render_model(self, model_path, image_path):
        render_gsplat_image(model_path, self.device, image_path)
