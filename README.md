# view Dependent Deformation Fields for 2D Editing of 3D Models

[Project Page](https://martin-elmqirmi.github.io/view_dependent_deformation_fields_project_page/)

## Installation
### Prerequisites

- **CUDA:**  
  Before creating the Conda environment, ensure that CUDA is installed on your system.  
  We recommend using **CUDA 12.1**, as it has been thoroughly tested with this project.  
  However, CUDA versions from **11.8 up to 12.4** should also work, but you may need to adjust PyTorch versions accordingly.

- **Conda:**  
  Make sure you have [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.

### Step 1: Adjust PyTorch version in `environment.yaml`

- Depending on your installed CUDA version, update the PyTorch version in `environment.yaml` to ensure compatibility.  
- You can find the appropriate PyTorch version and installation command for your CUDA version at the [PyTorch Get Started page](https://pytorch.org/get-started/locally/).

### Step 2: Create the Conda environment

- Run the following command to create the Conda environment from the `environment.yaml` file:  
  ```bash
  conda env create -f environment.yaml
  
- Activate the environment
  ```bash
    conda activate vddf

### Step 3: Install the GSplat library

- Clone or download the GSplat library from its official repository:  
  [https://github.com/PRIP-VCLab/gsplat](https://github.com/PRIP-VCLab/gsplat)

- **Important:** This project is compatible with GSplat **version 1.5.2**. Please make sure to use this version to avoid compatibility issues.

- Follow the platform-specific build instructions provided in the GSplat repository documentation:

  - **Windows:** Follow the Windows build guide to build and install GSplat correctly.  
  - **Linux:** Follow the Linux build guide for installation.

- After building the library, install it in your Conda environment according to the instructions in the GSplat repo.

## Generation of the 2D mesh
To generate a 2D mesh from a rendered image of a 3D model, we begin by detecting the object's contour using OpenCV. This detection relies on a known background color, which can be adjusted in the rendering settings. When the background color changes, the threshold used in the contour detection must be updated accordingly to maintain accurate segmentation. Once the contour is extracted, we apply a triangulation algorithm using the triangle library. This triangulation is configurable: we can set constraints such as the maximum area of the triangles and the minimum angle allowed between their edges. In our configuration, we use a maximum triangle area of 60 pixels and enforce a minimum internal angle of 32.5 degrees to ensure a well-shaped and uniform triangulation of the detected region.

## Rendering

Our system supports two types of rendering backends: one for triangle meshes and another for 3D Gaussian splats. For mesh rendering, we use the `pyrender` library, chosen for its ease of use and quick setup for rendering 3D geometry. For Gaussian splats, we use the `gsplat` library, a high-performance renderer specifically designed for real-time visualization of Gaussian point-based models. While both libraries provide a solid starting point, each comes with trade-offs in terms of flexibility and performance, which are discussed below.

### Meshes

We use the [pyrender](https://pyrender.readthedocs.io/en/latest/api/index.html#) library to render triangle meshes. It offers a simple and efficient API for visualizing 3D models using OpenGL, including camera control and background color customization. However, `pyrender` is not well-suited for dynamic updates to mesh geometry, such as frequent vertex displacement, which limits its performance in scenarios involving real-time deformation. Replacing it with a lower-level, GPU-accelerated rendering backend could significantly improve responsiveness and rendering speed in our deformation pipeline.

### Gaussian Splats

For rendering Gaussian splats, we use the [gsplat](https://docs.gsplat.studio/main/) library. This tool enables fast and high-quality rendering of 3D Gaussian point clouds, where each point is represented as a view-dependent anisotropic Gaussian. `gsplat` provides efficient GPU-based rendering and is well-adapted for neural representations and real-time visualization. Its design makes it a natural fit for projects that involve rendering large numbers of splats with complex appearance models. More implementation details and capabilities can be found in the official documentation.


## Information

If you encounter any bugs, have questions, or simply want to discuss the project, please feel free to reach out to me at [martin.elmqirmi@umontreal.ca](mailto:martin.elmqirmi@umontreal.ca). I’m happy to help and would love to hear your feedback!

