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
To generate a 2D mesh from a rendered image of a 3D model, we begin by detecting the object's contour using [OpenCV](https://docs.opencv.org/4.x/). This detection relies on a known background color, which can be adjusted in the rendering settings. When the background color changes, the threshold used in the contour detection must be updated accordingly to maintain accurate segmentation. Once the contour is extracted, we apply a triangulation algorithm using the [Triangle](https://rufat.be/triangle/) library. This triangulation is configurable: we can set constraints such as the maximum area of the triangles and the minimum angle allowed between their edges. In our configuration, we use a maximum triangle area of 60 pixels and enforce a minimum internal angle of 32.5 degrees to ensure a well-shaped and uniform triangulation of the detected region.

## Rendering

Our system supports two types of rendering: triangle meshes and 3D Gaussian splats. Each uses a separate library, with different formats and rendering capabilities depending on the representation.

### Meshes

We use [pyrender](https://pyrender.readthedocs.io/en/latest/api/index.html#) to render triangle meshes. It’s a simple and quick solution for visualizing 3D models with basic camera and background control. However, it’s not ideal for frequent updates to the mesh geometry, as performance can drop when modifying vertices often.  
Currently, we only support `.glb` mesh files. To use them, place your files in the `models/meshes` directory.

### Gaussian Splats

For Gaussian splat rendering, we use the [gsplat](https://docs.gsplat.studio/main/) library. It provides fast and high-quality rendering for 3D Gaussian splats and is well-suited for neural scene representations.  
The viewer accepts `.ply` files as input for splats. To use them, place your files in the `models/gsplat` directory.

## Information

If you encounter any bugs, have questions, or simply want to discuss the project, please feel free to reach out to me at [martin.el.mqirmi@umontreal.ca](mailto:martin.el.mqirmi@umontreal.ca). I’m happy to help and would love to hear your feedback!

