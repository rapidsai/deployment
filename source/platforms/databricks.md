# RAPIDS on Databricks

## 0.Prerequisites

1. Your Databricks workspace must have Databricks Container Services [enabled](https://docs.databricks.com/administration-guide/clusters/container-services.html).

2. Your machine must be running a recent Docker daemon (one that is tested and works with Version 18.03.0-ce) and the `$ docker version` command must be available on your PATH:

3. It is recommended to build from a [base image](https://hub.docker.com/u/databricksruntime) that is built and tested by Databricks. But you can also build your Docker base from scratch. The Docker image must meet these [requirements](https://docs.databricks.com/clusters/custom-containers.html#option-2-build-your-own-docker-base)

## 1.Build custom RAPIDS container

```console
ARG RAPIDS_IMAGE

FROM $RAPIDS_IMAGE as rapids

RUN conda list -n rapids --explicit > /rapids/rapids-spec.txt

FROM databricksruntime/gpu-conda:cuda11

COPY --from=rapids /rapids/rapids-spec.txt /tmp/spec.txt

RUN conda create --name rapids --file /tmp/spec.txt && \
    rm -f /tmp/spec.txt
```

```console
$ docker build --tag <username>/rapids_databricks:latest --build-arg RAPIDS_IMAGE=rapidsai/rapidsai-core:22.12-cuda11.5-runtime-ubuntu18.04-py3.9 ./docker
```

## 2.Push image to Docker registry (DockerHub, Amazon ECR or Azure ACR)

## 3.Configure and create GPU-enabled cluster

1. In Databricks > Compute > Create compute > Name your cluster, and select either `Multi` or `Single` Node
2. Select a Standard Databricks runtime that supports Databricks Container Services.
   - **Note** Databricks Runtime for Machine Learning does not support Databricks Container Services.
3. Under **Advanced Options**, in the the **Docker** tab select "Use your own Docker container". In the Docker Image URL field, enter the image that you created above
4. For Node type, Select a GPU enabled worker and driver type. Selected GPU must be Pascal generation or greater (eg: `g4dn.xlarge`)
5. Select the authentication type, you can use default or manually input username and password for your DockerHub account
6. Create and launch your cluster

## 4.Test Rapids

## More on Integrating Databricks Jobs with MLFlow and RAPIDS

You can find more detail in [this blog post on MLFlow + RAPIDS](https://medium.com/rapids-ai/managing-and-deploying-high-performance-machine-learning-models-on-gpus-with-rapids-and-mlflow-753b6fcaf75a).
