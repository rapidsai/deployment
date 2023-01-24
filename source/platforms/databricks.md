# RAPIDS on Databricks

## Prerequisites

Your Databricks workspace must have Databricks Container Services [enabled](https://docs.databricks.com/administration-guide/clusters/container-services.html).

Your machine must be running a recent Docker daemon (one that is tested and works with Version 18.03.0-ce) and the docker command must be available on your PATH:

```console
$ docker version
```

Databricks recommends that you build from a Docker base that Databricks has built and tested, but it is also possible to work with your custome Follow the instructions below to get started:

## Configure and create a cluster

- Create your cluster:

  1. Name your cluster, and select either `Multi` or `Single` Node

  2. Select a Standard Databricks runtime. For example 12.1(Scala 2.12, Spark 3.3.1)

     - This needs to be a Databricks runtime version that supports Databricks Container Services.- **Note** Databricks Runtime for Machine Learning does not support Databricks Container Services.

  3. For Node type, Select a GPU enabled worker and driver type.

     - **Note** Selected GPU must be Pascal generation or greater.

  4. Under **Advanced Options**, in the the **Docker** tab select "Use your own Docker container".

  5. In the Docker Image URL field, enter the Rapids image name, in this case:`rapidsai/rapidsai-core:22.12-cuda11.5-runtime-ubuntu18.04-py3.9`

  6. Select the authentication type, you can use default or manually input username and password for your DockerHub account

  7. Create and launch your cluster

## Test Rapids

## More on Integrating Databricks Jobs with MLFlow and RAPIDS

You can find more detail in [this blog post on MLFlow + RAPIDS](https://medium.com/rapids-ai/managing-and-deploying-high-performance-machine-learning-models-on-gpus-with-rapids-and-mlflow-753b6fcaf75a).
