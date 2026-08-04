# RAPIDS Deployment Documentation

This repository contains the source for the
[RAPIDS Deployment Documentation](https://docs.rapids.ai/deployment/stable/).
It explains how to install, configure, and operate RAPIDS across local systems,
GPU clusters, and managed compute services.

The documentation includes:

- Installation paths for local workstations, custom containers, and
  Slurm-managed HPC clusters.
- Infrastructure-specific deployment instructions for major cloud providers,
  including virtual machines, managed Kubernetes, and machine learning
  services.
- Integration guidance for compute and application platforms such as
  Kubernetes, Kubeflow, Databricks, Snowflake, and Google Colab.
- Practical guides and end-to-end notebook examples covering distributed data
  processing, machine learning, optimization, and MLOps workflows.

## Repository Layout

- `source/cloud/` contains provider-specific infrastructure instructions for
  deploying NVIDIA RAPIDS on cloud platforms like AWS, Azure, Google Cloud, and IBM
  Cloud. These pages cover services such as virtual machines, managed
  Kubernetes, and hosted machine learning environments.
- `source/platforms/` explains how to run NVIDIA RAPIDS on cloud platforms such as
  Kubernetes, Kubeflow, KServe, Databricks, Snowflake,
  Google Colab, Coiled, Modal, and NVIDIA AI Workbench.
- `source/guides/` contains focused, cross-platform guidance for deployment
  topics such as custom CUDA containers, Multi-Instance GPU, InfiniBand, Dask
  scheduler sizing, Kubernetes worker placement, and image caching.
- `source/examples/` contains end-to-end Jupyter notebook workflows and the
  supporting Python scripts, Dockerfiles, environment files, and Kubernetes
  manifests needed to run them.
- `source/hpc.md` covers running NVIDIA RAPIDS on Slurm-managed HPC clusters,
  including interactive and batch jobs, environment modules, and distributed
  workloads.
- `source/local.md` is the entry point for running NVIDIA RAPIDS on a workstation or
  server using conda, pip, Docker, or WSL2.
- `source/custom-docker.md` describes how to build smaller, tailored NVIDIA RAPIDS
  container images with only the required libraries using conda or pip.

## Build Locally

The site is built with Sphinx and requires Python 3.12 or newer. Dependencies
are managed with [uv](https://docs.astral.sh/uv/).

```bash
uv venv
uv sync --locked
uv run make dirhtml
```

The generated site is written to `build/dirhtml`. For live previews while
editing, run:

```bash
uv run sphinx-autobuild -b dirhtml source build/html
```

## Published Documentation

- [Stable documentation](https://docs.rapids.ai/deployment/stable/) is published
  from release tags.
- [Nightly documentation](https://docs.rapids.ai/deployment/nightly/) is
  published from the `main` branch.

See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on building, writing, linting, and releasing.
