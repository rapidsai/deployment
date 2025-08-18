# syntax=docker/dockerfile:1
# Copyright (c) 2024-2025, NVIDIA CORPORATION.

ARG CUDA_VER=12.9.1
ARG PYTHON_VER=3.12
ARG LINUX_DISTRO=ubuntu
ARG LINUX_DISTRO_VER=24.04

# Use CUDA runtime image for pip
FROM nvidia/cuda:${CUDA_VER}-runtime-${LINUX_DISTRO}${LINUX_DISTRO_VER}

ARG PYTHON_VER

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

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

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy the requirements file
COPY requirements.txt /home/rapids/requirements.txt

# Install all packages
RUN pip install --no-cache-dir -r requirements.txt

CMD ["ipython"]
