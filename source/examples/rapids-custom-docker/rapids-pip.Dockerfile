# syntax=docker/dockerfile:1
# Copyright (c) 2024-2025, NVIDIA CORPORATION.

ARG CUDA_VER=12.9.1
ARG PYTHON_VER=3.12
ARG LINUX_DISTRO=ubuntu
ARG LINUX_DISTRO_VER=24.04

# Use CUDA runtime image for pip (provides CUDA libraries that pip packages need)
FROM nvidia/cuda:${CUDA_VER}-runtime-${LINUX_DISTRO}${LINUX_DISTRO_VER} AS base

ARG CUDA_VER
ARG PYTHON_VER

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

# Install system dependencies including Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python${PYTHON_VER} \
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

# Create Python virtual environment
RUN python -m venv --system-site-packages rapids-env

# Activate virtual environment and upgrade pip
RUN . rapids-env/bin/activate && \
    pip install --no-cache-dir --upgrade pip setuptools wheel

# Install IPython first
RUN . rapids-env/bin/activate && \
    pip install --no-cache-dir ipython

# Copy the requirements file
COPY requirements.txt /home/rapids/requirements.txt

# Install packages from requirements.txt
RUN . rapids-env/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Set up activation in bashrc
RUN echo "source /home/rapids/rapids-env/bin/activate" >> ~/.bashrc

# Set PATH to use the virtual environment directly
ENV PATH="/home/rapids/rapids-env/bin:${PATH}"
ENV VIRTUAL_ENV="/home/rapids/rapids-env"

# Direct command execution - no entrypoint needed
CMD ["ipython"]

# Notebooks image - extends base with Jupyter
FROM base AS notebooks

USER rapids
WORKDIR /home/rapids

# Install Jupyter packages in the virtual environment
RUN . rapids-env/bin/activate && \
    pip install --no-cache-dir \
    "jupyterlab>=4.0" \
    jupyterlab-nvdashboard \
    dask-labextension

# Disable the JupyterLab announcements
RUN /home/rapids/rapids-env/bin/jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

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
LABEL org.opencontainers.image.description="Minimal customizable RAPIDS container with pip from CUDA runtime"
