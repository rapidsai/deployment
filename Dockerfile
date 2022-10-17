# Maybe have to transfer from Debian
ARG RAPIDS_IMAGE
FROM $RAPIDS_IMAGE as rapids

RUN conda list -n rapids --explicit > /rapids/rapids-spec.txt

FROM gcr.io/deeplearning-platform-release/rapids-gpu.21-12

COPY --from=rapids /rapids/rapids-spec.txt /tmp/spec.txt

RUN conda create --name rapids --file /tmp/spec.txt && \
    rm -f /tmp/spec.txt

ENV CONDA_DEFAULT_ENV=rapids

#CMD python -c "import platform; print(platform.python_version())"
# 3.7.12

#CMD python -c "import platform; print(platform.platform())"
# Linux-5.10.109-0-virt-x86_64-with-debian-bullseye-sid

#CMD printenv
# GDAL_DATA=/opt/conda/share/gdal
# NV_LIBNPP_DEV_VERSION=11.1.0.245-1
# CUDA_PATH=/opt/conda
# NVIDIA_VISIBLE_DEVICES=all
# NCCL_VERSION=2.12.10-1
# CONDA_PREFIX=/opt/conda
# GSETTINGS_SCHEMA_DIR_CONDA_BACKUP=
# CONDA_EXE=/opt/conda/bin/conda
# JAVA_HOME=/opt/conda
# PWD=/
# JAVA_LD_LIBRARY_PATH_BACKUP=
# PROJ_LIB=/opt/conda/share/proj
# LC_ALL=C.UTF-8
# NV_CUDNN_VERSION=8.0.5.39
# NV_NVTX_VERSION=11.0.167-1
# NV_LIBNPP_VERSION=11.1.0.245-1
# NV_LIBNCCL_DEV_PACKAGE=libnccl-dev=2.12.10-1+cuda11.0
# CONDA_DEFAULT_ENV=base
# SHELL=/bin/bash
# NV_LIBCUBLAS_DEV_PACKAGE=libcublas-dev-11-0=11.2.0.252-1
# GSETTINGS_SCHEMA_DIR=/opt/conda/share/glib-2.0/schemas
# CONDA_PYTHON_EXE=/opt/conda/bin/python
# NV_CUDA_CUDART_DEV_VERSION=11.0.221-1
# CONTAINER_NAME=rapids-gpu/21-12+cu110
# LANG=C.UTF-8
# NV_LIBNCCL_DEV_PACKAGE_NAME=libnccl-dev
# NV_LIBCUSPARSE_DEV_VERSION=11.1.1.245-1
# NV_LIBNCCL_PACKAGE=libnccl2=2.12.10-1+cuda11.0
# DL_ANACONDA_HOME=/opt/conda
# NV_LIBCUBLAS_DEV_PACKAGE_NAME=libcublas-dev-11-0
# NV_LIBCUBLAS_PACKAGE=libcublas-11-0=11.2.0.252-1
# NVARCH=x86_64
# PROJ_NETWORK=ON
# PATH=/opt/conda/bin:/opt/conda/condabin:/opt/conda/bin:/usr/local/nvidia/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# NV_CUDA_CUDART_VERSION=11.0.221-1
# ANACONDA_PYTHON_VERSION=3.7
# _CE_CONDA=
# NV_CUDNN_PACKAGE_DEV=libcudnn8-dev=8.0.5.39-1+cuda11.0
# NV_NVML_DEV_VERSION=11.0.167-1
# NV_LIBNPP_DEV_PACKAGE=libnpp-dev-11-0=11.1.0.245-1
# CONTAINER_URL=us-docker.pkg.dev/deeplearning-platform-release/gcr.io/rapids-gpu.21-12:nightly-2022-05-26
# TERM=xterm
# NV_LIBCUSPARSE_VERSION=11.1.1.245-1
# NVIDIA_DRIVER_CAPABILITIES=compute,utility
# NV_CUDA_LIB_VERSION=11.0.3-1
# NV_LIBNCCL_PACKAGE_NAME=libnccl2
# NVIDIA_REQUIRE_CUDA=cuda>=11.0 brand=tesla,driver>=418,driver<419
# NV_LIBCUBLAS_PACKAGE_NAME=libcublas-11-0
# NV_NVPROF_VERSION=11.0.221-1
# NV_CUDNN_PACKAGE=libcudnn8=8.0.5.39-1+cuda11.0
# CUDA_VERSION=11.0.3
# _CE_M=
# NV_LIBNPP_PACKAGE=libnpp-11-0=11.1.0.245-1
# NV_LIBNCCL_DEV_PACKAGE_VERSION=2.12.10-1
# CPL_ZIP_ENCODING=UTF-8
# NV_CUDNN_PACKAGE_NAME=libcudnn8
# JAVA_LD_LIBRARY_PATH=/opt/conda/lib/server
# NV_LIBCUBLAS_DEV_VERSION=11.2.0.252-1
# HOME=/root
# CONDA_SHLVL=1
# SHLVL=0
# LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/local/cuda/lib:/usr/local/lib/x86_64-linux-gnu:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/nvidia/lib:/usr/local/nvidia/lib64
# NV_LIBNCCL_PACKAGE_VERSION=2.12.10-1
# HOSTNAME=6b8a39109ad6
# JAVA_HOME_CONDA_BACKUP=
# NV_LIBCUBLAS_VERSION=11.2.0.252-1
# NV_NVPROF_DEV_PACKAGE=cuda-nvprof-11-0=11.0.221-1
# CONDA_PROMPT_MODIFIER=(base)
# NV_CUDA_COMPAT_PACKAGE=cuda-compat-11-0
# LIBRARY_PATH=/usr/local/cuda/lib64/stubs
