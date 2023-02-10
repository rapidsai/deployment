# Databricks

To use RAPIDS on Databricks we can create and launch a compute cluster with the RAPIDS libraries.

## Pre-requisites

1. Your Databricks workspace must have [Databricks Container Services enabled](https://docs.databricks.com/administration-guide/clusters/container-services.html).

2. You'll need [Docker](https://docs.docker.com/engine/reference/commandline/cli/) and a container registry such as [DockerHub](https://hub.docker.com/) or [Amazon ECR](https://aws.amazon.com/ecr/) where you can publish images.

## Build custom RAPIDS container

To start we need to build a container image that is compatible with Databricks and has the RAPIDS libraries installed. It is recommended to build from a [Databricks base image](https://hub.docker.com/u/databricksruntime) so we will use a multi-stage build to combine the Databricks container with the RAPIDS container

```{note}
You can also build your Docker base from scratch if you prefer. The Docker image must meet these [requirements](https://docs.databricks.com/clusters/custom-containers.html#option-2-build-your-own-docker-base)
```

Let's create a new `Dockerfile` with the following contents.

```dockerfile
# First stage will use the RAPIDS image to export the RAPIDS conda environment
FROM rapidsai/rapidsai-core:22.12-cuda11.5-runtime-ubuntu18.04-py3.9 as rapids
RUN conda list -n rapids --explicit > /rapids/rapids-spec.txt

# Second stage will take the Databricks image and install the exported conda environment
FROM databricksruntime/gpu-conda:cuda11
COPY --from=rapids /rapids/rapids-spec.txt /tmp/spec.txt
RUN conda create --name rapids --file /tmp/spec.txt && rm -f /tmp/spec.txt
```

Now we can build the image. Be sure to use the registry/username where you will be publishing your image.

```console
$ docker build --tag <registry>/<username>/rapids_databricks:latest .
```

Then push the image to your registry.

```console
$ docker push <registry>/<username>/rapids_databricks:latest
```

## Configure and create GPU-enabled cluster

Next we can create a compute cluster on Databricks and use our RAPIDS powered container image.

1. Open the [Databricks control panel](https://accounts.cloud.databricks.com).
2. Navigate to Compute > Create compute.
3. Name your cluster.
4. Select `Multi node` or `Single node` depending on the type of cluster you want to launch.
5. Select a Standard Databricks runtime.
   - **Note** Databricks ML Runtime does not support Databricks Container Services.
   - You may also need to uncheck "Use Photon Acceleration".
6. Under **Advanced Options**, in the the **Docker** tab select **Use your own Docker container**.
   - In the Docker Image URL field, enter the image that you created above.
   - Select the authentication type.
7. Also under **Advanced Options**, in the **Spark** tab add the following configuration line.
   - `spark.databricks.driverNfs.enabled false`
8. Scroll back up to **Performance** and select a GPU enabled node type.
   - Selected GPU must be Pascal generation or greater (eg: `g4dn.xlarge`).
   - You will need to have checked **Use your own Docker container** in the previous step in order for GPU nodes to be available.
9. Create and launch your cluster.

## Test Rapids

For more details on Integrating Databricks Jobs with MLFlow and RAPIDS, check out this [blog post](https://medium.com/rapids-ai/managing-and-deploying-high-performance-machine-learning-models-on-gpus-with-rapids-and-mlflow-753b6fcaf75a).
