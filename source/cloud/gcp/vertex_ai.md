# Vertex AI

RAPIDS can be deployed on Vertex AI.

## Managed Notebooks

While Vertex AI does provide a `RAPIDS 0.18` environment for new, user-managed notebooks, it is recommended to a RAPIDS docker image to access the latest RAPIDS software.

**0. Prepare RAPIDS Docker Image.** Before configuring a new notebook, your preferred version of the [RAPIDS Docker image](#rapids-docker) will need to be made available in [Google Container Registry](https://cloud.google.com/container-registry/docs/pushing-and-pulling).

**1. Create a New Notebook.** From the Google Cloud UI, nagivate to `Vertex AI` -> `Dashboard` and select `+ CREATE NOTEBOOK INSTANCE`

**2. Configure.** Under the `Environment` section, specity `Custom container`, and in the section below, select the `gcr.io` path to your pushed RAPIDS Docker image. 