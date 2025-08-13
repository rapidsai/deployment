# syntax=docker/dockerfile:1
# Copyright (c) 2024-2025, NVIDIA CORPORATION.

ARG CUDA_VER=12.9.1
ARG PYTHON_VER=3.12
ARG LINUX_DISTRO=ubuntu
ARG LINUX_DISTRO_VER=24.04

# Use CUDA base image for minimal size
FROM nvidia/cuda:${CUDA_VER}-base-${LINUX_DISTRO}${LINUX_DISTRO_VER} AS base

ARG CUDA_VER
ARG PYTHON_VER

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

# Install minimal system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Miniforge (conda-forge focused conda distribution)
RUN wget -qO /tmp/miniforge.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh" && \
    bash /tmp/miniforge.sh -b -p /opt/conda && \
    rm /tmp/miniforge.sh && \
    /opt/conda/bin/conda clean --all --yes

# Add conda to PATH
ENV PATH="/opt/conda/bin:${PATH}"

# Create conda group and rapids user
RUN groupadd -g 1001 conda && \
    useradd -rm -d /home/rapids -s /bin/bash -g conda -u 1001 rapids && \
    chown -R rapids:conda /opt/conda

USER rapids
WORKDIR /home/rapids

# Create rapids-env with Python and IPython first
RUN conda create -y -n rapids-env -c rapidsai-nightly -c conda-forge -c nvidia \
    python=${PYTHON_VER} \
    ipython \
    && conda clean --all --yes

# Copy the environment file template
COPY env.yaml /home/rapids/env.yaml

# Update the rapids-env environment with user's packages from env.yaml
RUN conda env update -n rapids-env -f env.yaml && \
    conda clean --all --yes

# Set up conda activation in bashrc and make it the default environment
RUN echo ". /opt/conda/etc/profile.d/conda.sh; conda activate rapids-env" >> ~/.bashrc
ENV CONDA_DEFAULT_ENV=rapids-env

# Set PATH to use the conda environment directly
ENV PATH="/opt/conda/envs/rapids-env/bin:${PATH}"

# ARM-specific CUDA 12.9 configuration
RUN if [ "$(uname -m)" = "aarch64" ]; then \
        echo 'if [[ "$CUDA_VERSION" = 12.9* ]]; then export NCCL_CUMEM_HOST_ENABLE=0; fi' >> ~/.bashrc; \
    fi

# Direct command execution - no entrypoint needed
CMD ["ipython"]

# Notebooks image - extends base with Jupyter
FROM base AS notebooks

USER rapids
WORKDIR /home/rapids

# Install Jupyter packages directly in the existing environment
RUN conda install -y -n rapids-env -c rapidsai-nightly -c conda-forge -c nvidia \
    "jupyterlab=4" \
    dask-labextension \
    jupyterlab-nvdashboard && \
    conda clean --all --yes

# Disable the JupyterLab announcements
RUN /opt/conda/envs/rapids-env/bin/jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# Set up Dask configuration for CUDA clusters
ENV DASK_LABEXTENSION__FACTORY__MODULE="dask_cuda"
ENV DASK_LABEXTENSION__FACTORY__CLASS="LocalCUDACluster"

# Create notebooks directory
RUN mkdir -p /home/rapids/notebooks

EXPOSE 8888

# Direct Jupyter command - no entrypoint needed
CMD ["jupyter", "lab", "--notebook-dir=/home/rapids/notebooks", "--ip=0.0.0.0", "--no-browser", "--NotebookApp.token=", "--NotebookApp.allow_origin=*"]

# Metadata
LABEL com.nvidia.cuda.version="${CUDA_VER}"
LABEL org.opencontainers.image.description="Minimal customizable RAPIDS container from CUDA base"
