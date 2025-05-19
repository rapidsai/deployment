FROM nvidia/cuda:12.8.1-runtime-ubuntu24.04

# Install curl (needed to fetch miniforge installer)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Download and install Miniforge from GitHub
RUN curl -L  "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh" -o miniforge.sh && \
    bash miniforge.sh -b -p /opt/conda && \
    rm miniforge.sh

# Set up miniforge environment
ENV PATH=/opt/conda/bin:$PATH

RUN <<EOF
# ensure conda environment is always activated
ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh
echo ". /opt/conda/etc/profile.d/conda.sh; conda activate base" >> /etc/skel/.bashrc
echo ". /opt/conda/etc/profile.d/conda.sh; conda activate base" >> ~/.bashrc
EOF

# Copy the environment YAML file into the container
COPY morpheus-nightly-env.yaml /tmp/env.yaml

ARG CUDA_VERSION=12.8

# Install dependencies from the YAML file using mamba
RUN CONDA_OVERRIDE_CUDA=$CUDA_VERSION conda env create -n morpheus_env -f /tmp/env.yaml && \
    conda clean --all --yes && \
    echo ". /opt/conda/etc/profile.d/conda.sh; conda activate morpheus_env" >> ~/.bashrc

# Copy pipeline script
COPY run_pipeline_kafka.py /workspace/run_pipeline_kafka.py
COPY network_traffic_analyzer_stage.py /workspace/network_traffic_analyzer_stage.py
COPY message_filter_stage.py /workspace/message_filter_stage.py
WORKDIR /workspace

# Set entrypoint to run the script in the morpheus environment
ENTRYPOINT ["/bin/bash", "-c", "\
  source /opt/conda/etc/profile.d/conda.sh && \
  conda activate morpheus_env && \
  python run_pipeline_kafka.py"]