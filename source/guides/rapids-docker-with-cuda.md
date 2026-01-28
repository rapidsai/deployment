# Building RAPIDS containers from a custom base image

This guide provides instructions to add RAPIDS and CUDA to your existing Docker images. This approach allows you to integrate RAPIDS libraries into containers that must start from a specific base image, such as application-specific containers.

The CUDA installation steps are sourced from the official [NVIDIA CUDA Container Images Repository](https://gitlab.com/nvidia/container-images/cuda).

```{warning}
We strongly recommend that you use the official CUDA container images published by NVIDIA. This guide is intended for those extreme situations where you cannot use the CUDA images as the base and need to manually install CUDA components on your containers. This approach introduces significant complexity and potential issues that can be difficult to debug. We cannot provide support for users beyond what is on this page.

If you have the flexibility to choose your base image, see the {doc}`Custom RAPIDS Docker Guide <../custom-docker>` which starts from NVIDIA's official CUDA images for a simpler setup.
```

## Overview

If you cannot use NVIDIA's CUDA container images, you will need to manually install CUDA components in your existing Docker image. The components you need depends on the package manager used to install RAPIDS:

- **For conda installations**: You need the components from the NVIDIA `base` CUDA images
- **For pip installations**: You need the components from the NVIDIA `runtime` CUDA images

## Understanding CUDA Image Components

NVIDIA provides three tiers of CUDA container images, each building on the previous:

### Base Components (Required for RAPIDS on conda)

The **base** images provide the minimal CUDA runtime environment:

| Component          | Package Name  | Purpose                                           |
| ------------------ | ------------- | ------------------------------------------------- |
| CUDA Runtime       | `cuda-cudart` | Core CUDA runtime library (`libcudart.so`)        |
| CUDA Compatibility | `cuda-compat` | Forward compatibility libraries for older drivers |

### Runtime Components (Required for RAPIDS on pip)

The **runtime** images include all the base components plus additional CUDA packages such as:

| Component                     | Package Name     | Purpose                                            |
| ----------------------------- | ---------------- | -------------------------------------------------- |
| **All Base Components**       | (see above)      | Core CUDA runtime                                  |
| CUDA Libraries                | `cuda-libraries` | Comprehensive CUDA library collection              |
| CUDA Math Libraries           | `libcublas`      | Basic Linear Algebra Subprograms (BLAS)            |
| NVIDIA Performance Primitives | `libnpp`         | Image, signal and video processing primitives      |
| Sparse Matrix Library         | `libcusparse`    | Sparse matrix operations                           |
| Profiling Tools               | `cuda-nvtx`      | NVIDIA Tools Extension for profiling               |
| Communication Library         | `libnccl2`       | Multi-GPU and multi-node collective communications |

### Development Components (Optional)

The **devel** images add development tools to runtime images such as:

- CUDA development headers and static libraries
- CUDA compiler (`nvcc`)
- Debugger and profiler tools
- Additional development utilities

```{note}
Development components are typically not needed for RAPIDS usage unless you plan to compile CUDA code within your container. For the complete and up to date list of runtime and devel components, see the respective Dockerfiles in the [NVIDIA CUDA Container Images Repository](https://gitlab.com/nvidia/container-images/cuda/-/tree/master/dist).
```

## Getting the Right Components for Your Setup

The [NVIDIA CUDA Container Images repository](https://gitlab.com/nvidia/container-images/cuda) contains a `dist/` directory with pre-built Dockerfiles organized by CUDA version, Linux distribution, and container type (base, runtime, devel).

### Supported Distributions

CUDA components are available for most popular Linux distributions. For the complete and current list of supported distributions for your desired version, check the repository linked above.

### Key Differences by Distribution Type

**Ubuntu/Debian distributions:**

- Use `apt-get install` commands
- Repository setup uses GPG keys and `.list` files

**RHEL/CentOS/Rocky Linux distributions:**

- Use `yum install` or `dnf install` commands
- Repository setup uses `.repo` configuration files
- Include repository files: `cuda.repo-x86_64`, `cuda.repo-arm64`

### Installing CUDA components on your container

1. Navigate to `dist/{cuda_version}/{your_os}/base/` or `runtime/` in the [repository](https://gitlab.com/nvidia/container-images/cuda)
2. Open the `Dockerfile` for your target distribution
3. Copy all `ENV` variables for package versioning and NVIDIA Container Toolkit support (see the Essential Environment Variables section below)
4. Copy the `RUN` commands for installing the packages
5. If you are using the `runtime` components, make sure to copy the `ENV` and `RUN` commands from the `base` Dockerfile as well
6. For RHEL-based systems, also copy any `.repo` configuration files needed

```{note}
Package versions change between CUDA releases. Always check the specific Dockerfile for your desired CUDA version and distribution to get the correct versions.
```

### Installing RAPIDS libraries on your container

Refer to the Docker Templates in the [Custom RAPIDS Docker Guide](../custom-docker.md) to configure your RAPIDS installation, adding the conda or pip installation commands after the CUDA components are installed.

## Essential Environment Variables

These environment variables are **required** when building CUDA containers, as they control GPU access and CUDA functionality through the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html)

| Variable                     | Purpose                          |
| ---------------------------- | -------------------------------- |
| `NVIDIA_VISIBLE_DEVICES`     | Specifies which GPUs are visible |
| `NVIDIA_DRIVER_CAPABILITIES` | Required driver capabilities     |
| `NVIDIA_REQUIRE_CUDA`        | Driver version constraints       |
| `PATH`                       | Include CUDA binaries            |
| `LD_LIBRARY_PATH`            | Include CUDA libraries           |

## Complete Integration Examples

Here are complete examples showing how to build a RAPIDS container with CUDA 13.1.1 components on an Ubuntu 24.04 base image:

```{tip}
These examples must be built with Docker v28+.
```

`````{tab-set}

````{tab-item} conda
:sync: conda

### RAPIDS with conda (Base Components)

Create an `env.yaml` file alongside your Dockerfile with your desired RAPIDS packages following the configuration described in the [Custom RAPIDS Docker Guide](../custom-docker.md). Set the `TARGETARCH` build argument to match your target architecture (`amd64` for x86_64 or `arm64` for ARM processors).

```dockerfile
FROM ubuntu:24.04

# Build arguments
ARG TARGETARCH=amd64

# Architecture detection and setup
ENV NVARCH=${TARGETARCH/amd64/x86_64}
ENV NVARCH=${NVARCH/arm64/sbsa}

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

# NVIDIA Repository Setup (Ubuntu 24.04)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 curl ca-certificates && \
    curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/${NVARCH}/3bf863cc.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/${NVARCH} /" > /etc/apt/sources.list.d/cuda.list && \
    apt-get purge --autoremove -y curl && \
    rm -rf /var/lib/apt/lists/*

# CUDA Base Package Versions (from CUDA 13.1.1 base image)
ENV NV_CUDA_CUDART_VERSION=13.1.80-1
ENV CUDA_VERSION=13.1.1

# NVIDIA driver constraints
ENV NVIDIA_REQUIRE_CUDA="cuda>=13.1 brand=unknown,driver>=535,driver<536 brand=grid,driver>=535,driver<536 brand=tesla,driver>=535,driver<536 brand=nvidia,driver>=535,driver<536 brand=quadro,driver>=535,driver<536 brand=quadrortx,driver>=535,driver<536 brand=nvidiartx,driver>=535,driver<536 brand=vapps,driver>=535,driver<536 brand=vpc,driver>=535,driver<536 brand=vcs,driver>=535,driver<536 brand=vws,driver>=535,driver<536 brand=cloudgaming,driver>=535,driver<536 brand=unknown,driver>=550,driver<551 brand=grid,driver>=550,driver<551 brand=tesla,driver>=550,driver<551 brand=nvidia,driver>=550,driver<551 brand=quadro,driver>=550,driver<551 brand=quadrortx,driver>=550,driver<551 brand=nvidiartx,driver>=550,driver<551 brand=vapps,driver>=550,driver<551 brand=vpc,driver>=550,driver<551 brand=vcs,driver>=550,driver<551 brand=vws,driver>=550,driver<551 brand=cloudgaming,driver>=550,driver<551 brand=unknown,driver>=570,driver<571 brand=grid,driver>=570,driver<571 brand=tesla,driver>=570,driver<571 brand=nvidia,driver>=570,driver<571 brand=quadro,driver>=570,driver<571 brand=quadrortx,driver>=570,driver<571 brand=nvidiartx,driver>=570,driver<571 brand=vapps,driver>=570,driver<571 brand=vpc,driver>=570,driver<571 brand=vcs,driver>=570,driver<571 brand=vws,driver>=570,driver<571 brand=cloudgaming,driver>=570,driver<571 brand=unknown,driver>=575,driver<576 brand=grid,driver>=575,driver<576 brand=tesla,driver>=575,driver<576 brand=nvidia,driver>=575,driver<576 brand=quadro,driver>=575,driver<576 brand=quadrortx,driver>=575,driver<576 brand=nvidiartx,driver>=575,driver<576 brand=vapps,driver>=575,driver<576 brand=vpc,driver>=575,driver<576 brand=vcs,driver>=575,driver<576 brand=vws,driver>=575,driver<576 brand=cloudgaming,driver>=575,driver<576 brand=unknown,driver>=580,driver<581 brand=grid,driver>=580,driver<581 brand=tesla,driver>=580,driver<581 brand=nvidia,driver>=580,driver<581 brand=quadro,driver>=580,driver<581 brand=quadrortx,driver>=580,driver<581 brand=nvidiartx,driver>=580,driver<581 brand=vapps,driver>=580,driver<581 brand=vpc,driver>=580,driver<581 brand=vcs,driver>=580,driver<581 brand=vws,driver>=580,driver<581 brand=cloudgaming,driver>=580,driver<581"

# Install Base CUDA Components (from base image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-cudart-13-1=${NV_CUDA_CUDART_VERSION} \
    cuda-compat-13-1 && \
    rm -rf /var/lib/apt/lists/*

# CUDA Environment Configuration
ENV PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/cuda/lib64

# NVIDIA Container Runtime Configuration
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Required for nvidia-docker v1
RUN echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf && \
    echo "/usr/local/cuda/lib64" >> /etc/ld.so.conf.d/nvidia.conf

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Miniforge
RUN wget -qO /tmp/miniforge.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh" && \
    bash /tmp/miniforge.sh -b -p /opt/conda && \
    rm /tmp/miniforge.sh && \
    /opt/conda/bin/conda clean --all --yes

# Add conda to PATH and activate base environment
ENV PATH="/opt/conda/bin:${PATH}"
ENV CONDA_DEFAULT_ENV=base
ENV CONDA_PREFIX=/opt/conda

# Create conda group and rapids user
RUN groupadd -g 1001 conda && \
    useradd -rm -d /home/rapids -s /bin/bash -g conda -u 1001 rapids && \
    chown -R rapids:conda /opt/conda

USER rapids
WORKDIR /home/rapids

# Copy the environment file template
COPY --chmod=644 env.yaml /home/rapids/env.yaml

# Update the base environment with user's packages from env.yaml
# Note: The -n base flag ensures packages are installed to the base environment
# overriding any 'name:' specified in the env.yaml file
RUN /opt/conda/bin/conda env update -n base -f env.yaml && \
    /opt/conda/bin/conda clean --all --yes

CMD ["bash"]
```

````

````{tab-item} pip
:sync: pip

### RAPIDS with pip (Runtime Components)

Create a `requirements.txt` file alongside your Dockerfile with your desired RAPIDS packages following the configuration described in the [Custom RAPIDS Docker Guide](../custom-docker.md). Set the `TARGETARCH` build argument to match your target architecture (`amd64` for x86_64 or `arm64` for ARM processors). You can also customize the Python version by changing the `PYTHON_VER` build argument.

```dockerfile
FROM ubuntu:24.04

# Build arguments
ARG PYTHON_VER=3.12
ARG TARGETARCH=amd64

# Architecture detection and setup
ENV NVARCH=${TARGETARCH/amd64/x86_64}
ENV NVARCH=${NVARCH/arm64/sbsa}

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

# NVIDIA Repository Setup (Ubuntu 24.04)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 curl ca-certificates && \
    curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/${NVARCH}/3bf863cc.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/${NVARCH} /" > /etc/apt/sources.list.d/cuda.list && \
    apt-get purge --autoremove -y curl && \
    rm -rf /var/lib/apt/lists/*

# CUDA Package Versions (from CUDA 13.1.1 base and runtime images)
ENV NV_CUDA_CUDART_VERSION=13.1.80-1
ENV CUDA_VERSION=13.1.1
ENV NV_CUDA_LIB_VERSION=13.1.1-1
ENV NV_NVTX_VERSION=13.1.115-1
ENV NV_LIBNPP_VERSION=13.0.3.3-1
ENV NV_LIBNPP_PACKAGE=libnpp-13-1=${NV_LIBNPP_VERSION}
ENV NV_LIBCUSPARSE_VERSION=12.7.3.1-1
ENV NV_LIBCUBLAS_PACKAGE_NAME=libcublas-13-1
ENV NV_LIBCUBLAS_VERSION=13.2.1.1-1
ENV NV_LIBCUBLAS_PACKAGE=${NV_LIBCUBLAS_PACKAGE_NAME}=${NV_LIBCUBLAS_VERSION}

# NVIDIA driver constraints
ENV NVIDIA_REQUIRE_CUDA="cuda>=13.1 brand=unknown,driver>=535,driver<536 brand=grid,driver>=535,driver<536 brand=tesla,driver>=535,driver<536 brand=nvidia,driver>=535,driver<536 brand=quadro,driver>=535,driver<536 brand=quadrortx,driver>=535,driver<536 brand=nvidiartx,driver>=535,driver<536 brand=vapps,driver>=535,driver<536 brand=vpc,driver>=535,driver<536 brand=vcs,driver>=535,driver<536 brand=vws,driver>=535,driver<536 brand=cloudgaming,driver>=535,driver<536 brand=unknown,driver>=550,driver<551 brand=grid,driver>=550,driver<551 brand=tesla,driver>=550,driver<551 brand=nvidia,driver>=550,driver<551 brand=quadro,driver>=550,driver<551 brand=quadrortx,driver>=550,driver<551 brand=nvidiartx,driver>=550,driver<551 brand=vapps,driver>=550,driver<551 brand=vpc,driver>=550,driver<551 brand=vcs,driver>=550,driver<551 brand=vws,driver>=550,driver<551 brand=cloudgaming,driver>=550,driver<551 brand=unknown,driver>=570,driver<571 brand=grid,driver>=570,driver<571 brand=tesla,driver>=570,driver<571 brand=nvidia,driver>=570,driver<571 brand=quadro,driver>=570,driver<571 brand=quadrortx,driver>=570,driver<571 brand=nvidiartx,driver>=570,driver<571 brand=vapps,driver>=570,driver<571 brand=vpc,driver>=570,driver<571 brand=vcs,driver>=570,driver<571 brand=vws,driver>=570,driver<571 brand=cloudgaming,driver>=570,driver<571 brand=unknown,driver>=575,driver<576 brand=grid,driver>=575,driver<576 brand=tesla,driver>=575,driver<576 brand=nvidia,driver>=575,driver<576 brand=quadro,driver>=575,driver<576 brand=quadrortx,driver>=575,driver<576 brand=nvidiartx,driver>=575,driver<576 brand=vapps,driver>=575,driver<576 brand=vpc,driver>=575,driver<576 brand=vcs,driver>=575,driver<576 brand=vws,driver>=575,driver<576 brand=cloudgaming,driver>=575,driver<576 brand=unknown,driver>=580,driver<581 brand=grid,driver>=580,driver<581 brand=tesla,driver>=580,driver<581 brand=nvidia,driver>=580,driver<581 brand=quadro,driver>=580,driver<581 brand=quadrortx,driver>=580,driver<581 brand=nvidiartx,driver>=580,driver<581 brand=vapps,driver>=580,driver<581 brand=vpc,driver>=580,driver<581 brand=vcs,driver>=580,driver<581 brand=vws,driver>=580,driver<581 brand=cloudgaming,driver>=580,driver<581"

# Install Base CUDA Components
RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-cudart-13-1=${NV_CUDA_CUDART_VERSION} \
    cuda-compat-13-1 && \
    rm -rf /var/lib/apt/lists/*

# Install Runtime CUDA Components
RUN apt-get update && apt-get install -y --no-install-recommends \
    cuda-libraries-13-1=${NV_CUDA_LIB_VERSION} \
    ${NV_LIBNPP_PACKAGE} \
    cuda-nvtx-13-1=${NV_NVTX_VERSION} \
    libcusparse-13-1=${NV_LIBCUSPARSE_VERSION} \
    ${NV_LIBCUBLAS_PACKAGE} \
    && rm -rf /var/lib/apt/lists/*

# Keep apt from auto upgrading the cublas and nccl packages
RUN apt-mark hold ${NV_LIBCUBLAS_PACKAGE_NAME}

# CUDA Environment Configuration
ENV PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/cuda/lib64

# NVIDIA Container Runtime Configuration
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Required for nvidia-docker v1
RUN echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf && \
    echo "/usr/local/cuda/lib64" >> /etc/ld.so.conf.d/nvidia.conf

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python${PYTHON_VER} \
    python${PYTHON_VER}-venv \
    python3-pip \
    wget \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic links for python and pip
RUN ln -sf /usr/bin/python${PYTHON_VER} /usr/bin/python && \
    ln -sf /usr/bin/python${PYTHON_VER} /usr/bin/python3

# Create rapids user
RUN groupadd -g 1001 rapids && \
    useradd -rm -d /home/rapids -s /bin/bash -g rapids -u 1001 rapids

USER rapids
WORKDIR /home/rapids

# Create and activate virtual environment
RUN python -m venv /home/rapids/venv
ENV PATH="/home/rapids/venv/bin:$PATH"
ENV VIRTUAL_ENV="/home/rapids/venv"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy the requirements file
COPY --chmod=644 requirements.txt /home/rapids/requirements.txt

# Install all packages
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT []

CMD ["bash"]
```

````

`````

## Verifying Your Installation

After starting your container, you can quickly test that RAPIDS is installed and running correctly. The container launches directly into a `bash` shell where you can install the [RAPIDS CLI](https://github.com/rapidsai/rapids-cli) command line utility to verify your installation.

1. **Run the Container Interactively**

   This command starts your container and drops you directly into a bash shell.

   ```bash
   # Build the conda-based container (requires env.yaml in build context)
   docker build -f conda-rapids.Dockerfile -t rapids-conda-cuda .

   # Build the pip-based container (requires requirements.txt in build context)
   docker build -f pip-rapids.Dockerfile -t rapids-pip-cuda .

   # Run conda container with GPU access
   docker run --gpus all -it rapids-conda-cuda

   # Run pip container with GPU access
   docker run --gpus all -it rapids-pip-cuda
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

   ```console
   🧑‍⚕️ Performing REQUIRED health check for RAPIDS
   Running checks
   All checks passed!
   ```

For more RAPIDS on Docker, see the [Custom RAPIDS Docker Guide](../custom-docker.md) and the [RAPIDS installation guide](https://docs.rapids.ai/install/).
