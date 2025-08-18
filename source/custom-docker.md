---
review_priority: "normal"
html_theme.sidebar_secondary.remove: true
---

# Custom RAPIDS Docker Guide

This guide provides instructions for building custom RAPIDS Docker containers. This approach allows you to select only the RAPIDS libraries you need, which is ideal for creating minimal, customizable images that can be tuned to your requirements.

```{note}
 For quick setup with pre-built containers that include the full RAPIDS suite,  please see the [Official RAPIDS Docker Installation Guide](https://docs.rapids.ai/install#docker).
```

## Overview

Building a custom RAPIDS container offers several advantages over using the official pre-built images:

- **Minimal Image Sizes**: By including only the libraries you need, you can reduce the final image size.
- **Flexible Configuration**: You have full control over library versions and dependencies.

## Getting Started

To begin, you will need to create a few local files for your custom build: a `Dockerfile` and a configuration file (`env.yaml` for `conda` or `requirements.txt` for `pip`). The complete source for these files is provided in the "Source Files" section below for you to copy.

1. **Create a Project Directory**: It's best practice to create a dedicated folder for your custom build.

   ```bash
   mkdir rapids-custom-build && cd rapids-custom-build
   ```

2. **Prepare Your Project Files**: Based on your chosen approach (Conda or Pip), create the necessary files in your project directory by copying the code from the corresponding "Source Files" dropdown below.

3. **Customize Your Build**:
   - If using the **conda** approach, edit your local `env.yaml` file to add the desired RAPIDS libraries.
   - If using the **pip** approach, edit your local `requirements.txt` file with your desired RAPIDS libraries.

4. **Build the Image**: Use the `docker build` commands provided in the installation sections to create your custom container.

---

## Package Manager Differences

The choice of base image depends on how your package manager handles CuPy (a dependency for most RAPIDS libraries) and CUDA library dependencies:

### Conda → Uses `cuda-base`

```dockerfile
FROM nvidia/cuda:12.9.1-base-ubuntu24.04  # Minimal image
```

This approach works because conda can install both Python and non-Python dependencies, including system-level CUDA libraries like `libcudart` and `libnvrtc`. When installing RAPIDS libraries via conda, the package manager automatically pulls the required CUDA runtime libraries alongside CuPy and other dependencies, providing complete dependency management in a single installation step.

### Pip → Uses `cuda-runtime`

```dockerfile
FROM nvidia/cuda:12.9.1-runtime-ubuntu24.04  # Includes CUDA libraries
```

This approach is necessary because CuPy wheels distributed via PyPI do not currently bundle CUDA runtime libraries (`libcudart`, `libnvrtc`) within the wheel packages themselves. Since pip cannot install system-level CUDA libraries, CuPy expects these libraries to already be present in the system environment. The `cuda-runtime` image provides the necessary CUDA runtime libraries that CuPy requires, eliminating the need for manual library installation.

## Source Code

The complete source code for the Dockerfiles and their configurations are included here. Choose your preferred package manager.

`````{tab-set}

````{tab-item} conda
:sync: conda

This method uses conda and is ideal for workflows that are based on `conda`.

**`rapids-conda.Dockerfile`**

```{literalinclude} /examples/rapids-custom-docker/rapids-conda.Dockerfile
:language: dockerfile
```

**`env.yaml`** (Conda environment configuration)

```{literalinclude} /examples/rapids-custom-docker/env.yaml
:language: yaml
```

````

````{tab-item} pip
:sync: pip

This approach uses standard Python virtual environments and is ideal for workflows that are already based on `pip`.

**`rapids-pip.Dockerfile`**

```{literalinclude} /examples/rapids-custom-docker/rapids-pip.Dockerfile
:language: dockerfile
```

**`requirements.txt`** (Pip package requirements)

```{literalinclude} /examples/rapids-custom-docker/requirements.txt
:language: text
```

````

`````

---

## Installation Methods

### Conda (Recommended)

The Conda approach uses the `nvidia/cuda:*-base-*` images as the base image, which are the minimal in size. This is possible because the `conda` package manager can pull and install the CUDA runtime libraries required by RAPIDS libraries in your configuration.

#### Quick Start (Conda)

After copying the source files into your local directory:

```bash
# Build the minimal base image
docker build -f rapids-conda.Dockerfile -t rapids-conda-base .

# Run an interactive session
docker run --gpus all -it rapids-conda-base
```

### Pip

The Pip approach requires the `nvidia/cuda:*-runtime-*` images to be used as base images. Unlike `conda`, `pip` currently does not pull in all the CUDA runtime dependencies (such as libnvrtc and libcudart), so the base image must provide the necessary CUDA runtime libraries that the RAPIDS pip wheels depend on.

#### Quick Start (Pip)

After copying the source files into your local directory:

```bash
# Build the minimal base image
docker build -f rapids-pip.Dockerfile -t rapids-pip-base .

# Run an interactive session
docker run --gpus all -it rapids-pip-base
```

:::{important}
When using `pip`, you must specify the CUDA version in the package name (e.g., `cudf-cu12`, `cuml-cu12`). This ensures you install the version of the library that is compatible with the CUDA toolkit.
:::

```{note}
**GPU Access with `--gpus all`**: The `--gpus` flag uses the NVIDIA Container Toolkit to dynamically mount GPU device files (`/dev/nvidia*`), NVIDIA driver libraries (`libcuda.so`, `libnvidia-ml.so`), and utilities like `nvidia-smi` from the host system into your container at runtime. This is why `nvidia-smi` becomes available even though it's not installed in your Docker image. Your container only needs to provide the CUDA runtime libraries (like `libcudart`) that RAPIDS requires—the host system's NVIDIA driver handles the rest.
```

### Image Size Comparison

One of the key benefits of building custom RAPIDS containers is the significant reduction in image size compared to the pre-built RAPIDS images. Here are actual measurements from containers containing only cuDF:

| Image Type           | Contents          | Size        |
| -------------------- | ----------------- | ----------- |
| **Custom conda**     | cuDF only         | **6.83 GB** |
| **Custom pip**       | cuDF only         | **6.53 GB** |
| **Pre-built RAPIDS** | Full RAPIDS suite | **12.9 GB** |

Custom builds save approximately 6 GB when you only need specific libraries like cuDF. These size reductions result in faster container pulls and deployments, reduced storage costs in container registries, lower bandwidth usage in distributed environments, and quicker startup times for containerized applications.

## Extending the Environment

One of the benefits of this custom build process is the ability to easily add your own packages to the environment. You can add any combination of RAPIDS and non-RAPIDS libraries to create a fully featured container for your workloads.

### Using conda

To add packages to the Conda environment, add them to the `dependencies` list in your `env.yaml` file.

**Example: Adding `scikit-learn` and `xgboost` to a conda image containing `cudf`**

```yaml
name: base
channels:
  - {{ rapids_conda_channels_list[0] }}
  - conda-forge
  - nvidia
dependencies:
  - cudf={{rapids_version}}
  - scikit-learn
  - xgboost
```

### Using pip

To add packages to the Pip environment, add them to your `requirements.txt` file.

**Example: Adding `scikit-learn` and `lightgbm` to a pip image containing `cudf`**

```text
cudf-cu12=={{rapids_pip_version}}
scikit-learn
lightgbm
```

After modifying your configuration file, rebuild the Docker image. The new packages will be automatically included in your custom RAPIDS environment.

## Build Customization

You can customize the build by passing arguments to the `docker build` command. This is useful for targeting different versions of CUDA, Python, or Linux distributions.

### Available Build Arguments

| Argument           | Default Value | Description                                            | Example Values       |
| ------------------ | ------------- | ------------------------------------------------------ | -------------------- |
| `CUDA_VER`         | `12.9.1`      | Sets the CUDA version for the base image and packages. | `12.0`               |
| `PYTHON_VER` (pip only)     | `3.12`        | Defines the Python version to install and use.         | `3.11`, `3.10`       |
| `LINUX_DISTRO`     | `ubuntu`      | The base Linux distribution.                           | `rockylinux9`, `cm2` |
| `LINUX_DISTRO_VER` | `24.04`       | The version of the Linux distribution.                 | `20.04`, `24.04`     |

### Build Examples

The following examples demonstrate how to use the build arguments. These commands can be adapted for both the Conda and Pip Dockerfiles.

#### Customize Linux Distribution Version

```bash
# Build on Ubuntu 22.04
docker build -f rapids-conda.Dockerfile \
  --build-arg LINUX_DISTRO_VER=22.04 \
  -t rapids-custom:ubuntu2404
```

#### Combine Multiple Customizations

```bash
# Build for CUDA 12.9.1, Python 3.11, and Ubuntu 22.04
docker build -f rapids-pip.Dockerfile \
  --build-arg CUDA_VER=12.9.1 \
  --build-arg PYTHON_VER=3.11 \
  --build-arg LINUX_DISTRO_VER=22.04 \
  -t rapids-custom:custom-build
```

```{note}
For conda installations, you can choose the required python version in the `env.yaml` file
```


## Verifying Your Installation

After building your image, you can quickly test that RAPIDS is installed and running correctly. The base images are designed to launch directly into an interactive `ipython` shell, which is the easiest way to verify your custom environment.

1. **Run the Container Interactively**

   This command starts your container and drops you directly into an `ipython` session.

   ```bash
   # For Conda builds
   docker run --gpus all -it rapids-conda-base

   # For Pip builds
   docker run --gpus all -it rapids-pip-base
   ```

2. **Test RAPIDS within IPython**

   Once you are inside the `ipython` shell, you can import and use the RAPIDS libraries you installed.

   ```python
   # You will see an In [1]: prompt. Type the following:
   import cudf

   print(f"cuDF version: {cudf.__version__}")

   # Create a simple GPU DataFrame to confirm everything works
   gdf = cudf.DataFrame({"a": [1, 2, 3]})
   print("\nRAPIDS is working correctly!")
   print(gdf)
   ```

3. **Expected Output**

   If your installation is successful, you will see output similar to this, confirming the cuDF version and displaying a cuDF DataFrame:

   ```ipython
   In [1]: import cudf
      ...: print(f"cuDF version: {cudf.__version__}")
      ...: gdf = cudf.DataFrame({"a": [1, 2, 3]})
      ...: print("\nRAPIDS is working correctly!")
      ...: print(gdf)
      ...:
   cuDF version: 25.08.00

   RAPIDS is working correctly!
      a
   0  1
   1  2
   2  3

   In [2]:
   ```
