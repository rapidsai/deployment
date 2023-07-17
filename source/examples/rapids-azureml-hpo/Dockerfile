# Use rapids base image v23.02 with the necessary dependencies
FROM rapidsai/rapidsai:23.02-cuda11.8-runtime-ubuntu22.04-py3.10

# Update package information and install required packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential fuse && \
    rm -rf /var/lib/apt/lists/*

# Activate rapids conda environment
RUN /bin/bash -c "source activate rapids && pip install azureml-mlflow azureml-dataprep"
