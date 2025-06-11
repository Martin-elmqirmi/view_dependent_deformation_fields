import trimesh
import numpy as np
import pyrender
from PIL import Image


""" Function to load the Mesh model from the .glb file """
def load_scene(data_path):
    mesh = trimesh.load(data_path)
    if not isinstance(mesh, trimesh.Scene):
        scene = trimesh.Scene(mesh)
    else:
        scene = mesh

    # Aggregate vertices from all meshes
    vertices = [geometry.vertices for geometry in scene.geometry.values()]
    all_vertices = np.vstack(vertices)  # Combine into a single array

    # Compute bounding box
    min_coords = all_vertices.min(axis=0)
    max_coords = all_vertices.max(axis=0)
    bounding_box_size = max_coords - min_coords

    # Determine scaling factor and translation
    largest_dimension = bounding_box_size.max()
    scale_factor = 1.0 / largest_dimension
    center = (min_coords + max_coords) / 2
    translation = -center

    # Create transformation matrix (scaling + translation)
    scaling_matrix = np.eye(4)
    scaling_matrix[:3, :3] *= scale_factor
    translation_matrix = np.eye(4)
    translation_matrix[:3, 3] = translation
    transform_matrix = scaling_matrix @ translation_matrix

    # Apply transformation to all meshes
    for geometry in scene.geometry.values():
        geometry.apply_transform(transform_matrix)

    # Assign consistent descriptive names to geometries
    new_scene = trimesh.Scene()
    for i, (old_name, geometry) in enumerate(scene.geometry.items()):
        num_vertices = len(geometry.vertices)
        num_faces = len(geometry.faces) if geometry.faces is not None else 0
        area = geometry.area if hasattr(geometry, "area") else 0.0

        name = f"mesh_{i}_v{num_vertices}_f{num_faces}_a{area:.4f}"
        geometry.name = name
        new_scene.add_geometry(geometry, node_name=name, geom_name=name)

    return new_scene


def render_mesh_image(data_path, image_path):
    loaded_scene = load_scene(data_path)
    scene = pyrender.Scene.from_trimesh_scene(loaded_scene)

    camera = pyrender.PerspectiveCamera(yfov=np.radians(60))
    scene.add(camera, pose=[[1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 1, 1.5],
                            [0, 0, 0, 1]])

    light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.0)
    scene.add(light)

    r = pyrender.OffscreenRenderer(256, 256)
    color, _ = r.render(scene)
    img = Image.fromarray(color)
    img.save(image_path)