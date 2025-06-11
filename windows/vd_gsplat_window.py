import pickle
import torch
from utils.gsplat_utils import render_gsplat_image
from windows.abstract_model_window import AbstractModelWindow
from windows.rendering_window import RenderingWindow


class VDGsplatWindow(AbstractModelWindow):
    def __init__(self, parent, model_dir):
        self.device = torch.device("cuda", 0)
        super().__init__(parent, model_dir, "models/vd_gsplat/images", ".pkl", "Gaussian")

    def render_model(self, model_path, image_path):
        # Get the data path to the initial 3DGS
        if model_path.lower().endswith('.pkl'):
            with open(model_path, "rb") as file:
                data = pickle.load(file)
            data_path = data["data_path"]
        else:
            raise ValueError(f"Unknown data_path type")

        print(data_path)

        render_gsplat_image(data_path, self.device, image_path)

    def select_model(self, path):
        if path.lower().endswith('.pkl'):
            with open(path, "rb") as file:
                data = pickle.load(file)
            data_path = data["data_path"]
            data = data["view_deformations"]
        else:
            raise ValueError(f"Unknown data_path type")

        RenderingWindow(self.master, data_path, self.render_type, data)
