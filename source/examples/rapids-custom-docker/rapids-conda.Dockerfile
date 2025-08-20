# syntax=docker/dockerfile:1
# Copyright (c) 2024-2025, NVIDIA CORPORATION.

ARG CUDA_VER=12.9.1
ARG LINUX_DISTRO=ubuntu
ARG LINUX_DISTRO_VER=24.04

FROM nvidia/cuda:${CUDA_VER}-base-${LINUX_DISTRO}${LINUX_DISTRO_VER}

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

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

# Add conda to PATH
ENV PATH="/opt/conda/bin:${PATH}"

# Create conda group and rapids user
RUN groupadd -g 1001 conda && \
    useradd -rm -d /home/rapids -s /bin/bash -g conda -u 1001 rapids && \
    chown -R rapids:conda /opt/conda

USER rapids
WORKDIR /home/rapids

# Copy the environment file template
COPY env.yaml /home/rapids/env.yaml

# Update the base environment with user's packages from env.yaml
RUN conda env update -n base -f env.yaml && \
    conda clean --all --yes

CMD ["bash"]
