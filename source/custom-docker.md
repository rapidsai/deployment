---
review_priority: "p1"
html_theme.sidebar_secondary.remove: true
---

# Custom RAPIDS Docker Guide

This guide provides instructions for building custom RAPIDS Docker containers. This approach allows you to select only the RAPIDS libraries you need, which is ideal for creating minimal, customizable images that can be tuned to your requirements.

```{note}
 For quick setup with pre-built containers that include the full RAPIDS suite,  please see the [Official RAPIDS Docker Installation Guide](https://docs.rapids.ai/install#docker).
```

## Overview

Building a custom RAPIDS container offers several advantages:

- **Minimal Image Sizes**: By including only the libraries you need, you can reduce the final image size.
- **Flexible Configuration**: You have full control over library versions and dependencies.

## Getting Started

To begin, you will need to create a few local files for your custom build: a `Dockerfile` and a configuration file (`env.yaml` for conda or `requirements.txt` for pip). The templates for these files is provided in the Docker Templates section below for you to copy.

1. **Create a Project Directory**: It's best practice to create a dedicated folder for your custom build.

   ```bash
   mkdir rapids-custom-build && cd rapids-custom-build
   ```

2. **Prepare Your Project Files**: Based on your chosen approach (conda or pip), create the necessary files in your project directory from the corresponding tab in the Docker Templates section below.

3. **Customize Your Build**:
   - When using **conda**, edit your local `env.yaml` file to add the desired RAPIDS libraries.
   - When using **pip**, edit your local `requirements.txt` file with your desired RAPIDS libraries.

4. **Build the Image**: Use the commands provided in the Build and Run section to create and start your custom container.

---

## Package Manager Differences

The choice of base image depends on how your package manager handles CuPy (a dependency for most RAPIDS libraries) and CUDA library dependencies:

### Conda → Uses `cuda-base`

```dockerfile
FROM nvidia/cuda:12.9.1-base-ubuntu24.04
```

This approach works because conda can install both Python and non-Python dependencies, including system-level CUDA libraries like `libcudart` and `libnvrtc`. When installing RAPIDS libraries via conda, the package manager automatically pulls the required CUDA runtime libraries alongside CuPy and other dependencies, providing complete dependency management in a single installation step.

### Pip → Uses `cuda-runtime`

```dockerfile
FROM nvidia/cuda:12.9.1-runtime-ubuntu24.04
```

This approach is necessary because CuPy wheels distributed via PyPI do not currently bundle CUDA runtime libraries (`libcudart`, `libnvrtc`) within the wheel packages themselves. Since pip cannot install system-level CUDA libraries, CuPy expects these libraries to already be present in the system environment. The `cuda-runtime` image provides the necessary CUDA runtime libraries that CuPy requires, eliminating the need for manual library installation.

## Docker Templates

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

This approach uses Python virtual environments and is ideal for workflows that are already based on `pip`.

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

## Build and Run

### Conda

After copying the source files into your local directory:

```bash
# Build the image
docker build -f rapids-conda.Dockerfile -t rapids-conda-base .

# Start a container with an interactive shell
docker run --gpus all -it rapids-conda-base
```

### Pip

After copying the source files into your local directory:

```bash
# Build the image
docker build -f rapids-pip.Dockerfile -t rapids-pip-base .

# Start a container with an interactive shell
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

Custom builds are smaller in size when you only need specific RAPIDS libraries like cuDF. These size reductions result in faster container pulls and deployments, reduced storage costs in container registries, lower bandwidth usage in distributed environments, and quicker startup times for containerized applications.

## Extending the Container

One of the benefits of building custom RAPIDS containers is the ability to easily add your own packages to the environment. You can add any combination of RAPIDS and non-RAPIDS libraries to create a fully featured container for your workloads.

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

## Build Configuration

You can customize the build by modifying the version variables at the top of each Dockerfile. These variables control the CUDA version, Python version, and Linux distribution used in your container.

### Available Configuration Variables

The following variables can be modified at the top of each Dockerfile to customize your build:

| Variable                | Default Value | Description                                            | Example Values       |
| ----------------------- | ------------- | ------------------------------------------------------ | -------------------- |
| `CUDA_VER`              | `12.9.1`      | Sets the CUDA version for the base image and packages. | `12.0`               |
| `PYTHON_VER` (pip only) | `3.12`        | Defines the Python version to install and use.         | `3.11`, `3.10`       |
| `LINUX_DISTRO`          | `ubuntu`      | The Linux distribution being used                      | `rockylinux9`, `cm2` |
| `LINUX_DISTRO_VER`      | `24.04`       | The version of the Linux distribution.                 | `20.04`              |

```{note}
For conda installations, you can choose the required python version in the `env.yaml` file
```

## Verifying Your Installation

After starting your container, you can quickly test that RAPIDS is installed and running correctly. The container launches directly into a `bash` shell where you can install the [RAPIDS CLI](https://github.com/rapidsai/rapids-cli) command line utility to verify your installation.

1. **Run the Container Interactively**

   This command starts your container and drops you directly into a bash shell.

   ```bash
   # For Conda builds
   docker run --gpus all -it rapids-conda-base

   # For Pip builds
   docker run --gpus all -it rapids-pip-base
   ```

2. **Install RAPIDS CLI**

   Inside the containers, install the RAPIDS CLI:

   ```bash
   pip install rapids-cli
   ```

3. **Test the installation using the Doctor subcommand**

   Once RAPIDS CLI is installed, you can use the `rapids doctor` subcommand to perform health checks.

   ```bash
   rapids doctor
   ```

4. **Expected Output**

   If your installation is successful, you will see output similar to this:

   ```bash
   🧑‍⚕️ Performing REQUIRED health check for RAPIDS
   Running checks
   All checks passed!
   ```
