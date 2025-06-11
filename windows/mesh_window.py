from utils.mesh_utils import render_mesh_image
from windows.abstract_model_window import AbstractModelWindow


class MeshWindow(AbstractModelWindow):
    def __init__(self, parent, model_dir):
        super().__init__(parent, model_dir, "models/meshes/images", ".glb", "Mesh")

    def render_model(self, model_path, image_path):
        render_mesh_image(model_path, image_path)
