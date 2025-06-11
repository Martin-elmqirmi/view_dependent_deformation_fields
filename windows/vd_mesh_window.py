import pickle

from utils.mesh_utils import render_mesh_image
from windows.abstract_model_window import AbstractModelWindow
from windows.rendering_window import RenderingWindow


class VDMeshWindow(AbstractModelWindow):
    def __init__(self, parent, model_dir):
        super().__init__(parent, model_dir, "models/vd_meshes/images", ".pkl", "Mesh")

    def render_model(self, model_path, image_path):
        # Get the data path to the initial 3DGS
        if model_path.lower().endswith('.pkl'):
            with open(model_path, "rb") as file:
                data = pickle.load(file)
            data_path = data["data_path"]
        else:
            raise ValueError(f"Unknown data_path type")

        render_mesh_image(data_path, image_path)

    def select_model(self, path):
        if path.lower().endswith('.pkl'):
            with open(path, "rb") as file:
                data = pickle.load(file)
            data_path = data["data_path"]
            data = data["view_deformations"]
        else:
            raise ValueError(f"Unknown data_path type")

        RenderingWindow(self.master, data_path, self.render_type, data)
