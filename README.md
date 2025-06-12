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
TODO

## Rendering
TODO

### Meshes
TODO

### Gaussian Splats
TODO

## Information

If you encounter any bugs, have questions, or simply want to discuss the project, please feel free to reach out to me at [martin.elmqirmi@umontreal.ca](mailto:martin.elmqirmi@umontreal.ca). I’m happy to help and would love to hear your feedback!

