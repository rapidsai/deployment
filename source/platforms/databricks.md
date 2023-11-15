# Databricks

You can install RAPIDS on Databricks in a few different ways:

1. Accelerate machine learning workflows in a single-node GPU notebook environment
2. Spark users can install RAPIDS Accelerator for Apache Spark 3.x on Databricks
3. Install Dask alongside Spark and then use libraries like `dask-cudf` for multi-node workloads

## Single-node GPU Notebook environment

### Launch cluster

To get started with a single-node Databricks cluster, navigate to the **All Purpose Compute** tab of the **Compute** section in Databricks and select **Create Compute**. Name your cluster and choose "Single node".

![Screenshot of the Databricks compute page](../images/databricks-create-compute.png)

In order to launch a GPU node uncheck **Use Photon Acceleration**.

![Screenshot of Photon Acceleration unchecked](../images/databricks-runtime-deselect-photon.png)

Then expand the **Advanced Options** section and open the **Docker** tab. Select **Use your own Docker container** and enter the image `databricksruntime/gpu-tensorflow:cuda11.8` or `databricksruntime/gpu-pytorch:cuda11.8`.

![Screenshot of setting the custom container](../images/databricks-custom-container.png)

Once you have completed, the "GPU accelerated" nodes should be available in the **Worker type** and **Driver type** dropdown.

![Screenshot of worker and driver nodes](../images/databricks-worker-driver-node.png)

Select **Create Compute**

### Install RAPIDS

Once your cluster has started, you can create a new notebook or open an existing one from the `/Workspace` directory then attach it to your running cluster.

````{warning}
At the time of writing the `databricksruntime/gpu-pytorch:cuda11.8` image does not contain the full `cuda-toolkit` so if you selected that one you will need to install that before installing RAPIDS.

```text
!cd /etc/apt/sources.list.d && \
    mv cuda-ubuntu2204-x86_64.list.disabled cuda-ubuntu2204-x86_64.list && \
    apt-get update && apt-get --no-install-recommends -y install cuda-toolkit-11-8 && \
    mv cuda-ubuntu2204-x86_64.list cuda-ubuntu2204-x86_64.list.disabled
```

````

At the top of your notebook run any of the following pip install commands to install your preferred RAPIDS libraries.

```text
!pip install cudf-cu11 dask-cudf-cu11 --extra-index-url=https://pypi.nvidia.com
!pip install cuml-cu11 --extra-index-url=https://pypi.nvidia.com
!pip install cugraph-cu11 --extra-index-url=https://pypi.nvidia.com
```

### Test RAPIDS

```python
import cudf

gdf = cudf.DataFrame({"a":[1,2,3],"b":[4,5,6]})
gdf
    a   b
0   1   4
1   2   5
2   3   6
```

## Multi-node Dask cluster

We now provide a [dask-databricks](https://github.com/jacobtomlinson/dask-databricks) CLI tool (via [`conda`](https://github.com/conda-forge/dask-databricks-feedstock) and [`pip`](https://pypi.org/project/dask-databricks/)) to simplify the Dask cluster startup process within Databricks.

Running `pip install dask-databricks` should launch a dask scheduler in the driver node and workers on remaining nodes in just a few minutes.

### Create init-script

To get started, you must first configure an [initialization script](https://docs.databricks.com/en/init-scripts/index.html) to install `dask`, RAPIDS libraries and all other dependencies for your project.

Databricks recommends using [cluster-scoped](https://docs.databricks.com/en/init-scripts/cluster-scoped.html) init scripts stored in the workspace files.

Navigate to the top-left **Workspace** tab and click on your **Home** directory then select **Add** > **File** from the menu. Create an `init.sh` script with contents:

```bash
#!/bin/bash
set -e

# The Databricks Python directory isn't on the path in
# databricksruntime/gpu-tensorflow:cuda11.8 for some reason
export PATH="/databricks/python/bin:$PATH"

# Install RAPIDS (cudf & dask-cudf) and dask-databricks
/databricks/python/bin/pip install --extra-index-url=https://pypi.nvidia.com \
      cudf-cu11 \  # installs cudf
      dask[complete] \
      dask-cudf-cu11  \ #installs dask-cudf
      dask-cuda=={rapids_version} \
      dask-databricks

# Start the Dask cluster with CUDA workers
dask databricks run --cuda

```

**Note**: To launch a dask cluster with GPU workers, you must parse in `--cuda` flag option when running the command, otherwise the script will launch standard dask workers by default.

### Launch Dask cluster

Once your script is ready, follow the [instructions](#launch-cluster) to launch a Databricks cluster with **Multi node** option instead.

After docker setup in **Advanced Options**, switch to the **Init Scripts** tab and add the file path to the init-script in your Workspace directory starting with `/Users/<user-name>/<script-name>.sh`.

You can also configure cluster log delivery in the **Logging** tab, which will write the init script logs to DBFS in a subdirectory called `dbfs:/cluster-logs/<cluster-id>/init_scripts/`. Refer to [docs](https://docs.databricks.com/en/init-scripts/logs.html) for more information.

![Screenshot of init script](../images/databricks-dask-init-script.png)

### Connect to Client

To test RAPIDS, Connect to the dask client and submit tasks.

![Screenshot of dask-client](../images/databricks-mnmg-dask-client.png)

![Screenshot of dask-client](../images/databricks-mnmg-dask-example.png)

### Clean up

```python
client.close()
cluster.close()
```

## Spark-RAPIDS Cluster

You can also use the RAPIDS Accelerator for Apache Spark 3.x on Databricks. See the [Spark RAPIDS documentation](https://nvidia.github.io/spark-rapids/docs/get-started/getting-started-databricks.html) for more information.
