# RAPIDS on Databricks

## Configure and create a cluster

- Create your cluster:
  1. Select a standard Databricks runtime. In this example 8.2 version, since we're using a container with CUDA 11.
     - This needs to be a Databricks runtime version that supports Databricks Container Services.
  2. Select "Use your own Docker container".
  3. In the Docker Image URL field, enter the image that you created above.
  4. Select a GPU enabled worker and driver type.
     - **Note** Selected GPU must be Pascal generation or greater.
  5. Create and launch your cluster.

## More on Integrating Databricks Jobs with MLFlow and RAPIDS

You can find more detail in [this blog post on MLFlow + RAPIDS](https://medium.com/rapids-ai/managing-and-deploying-high-performance-machine-learning-models-on-gpus-with-rapids-and-mlflow-753b6fcaf75a).
