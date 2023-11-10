# Databricks

You can install RAPIDS libraries into a Databricks GPU Notebook environment.

## DASK Rapids in Databricks MNMG Cluster

You can launch Dask RAPIDS cluster on a multi-node GPU Databricks cluster. To do this, you must first create an [initialization script](https://docs.databricks.com/en/init-scripts/index.html) to install Dask before launching the Databricks cluster.

Databricks recommends storing all cluster-scoped init scripts using workspace files. Each user has a Home directory configured under the `/Users` directory in the workspace. Navigate to your home directory in the UI and select **Create** > **File** from the menu, create an `init.sh` script with contents:

```bash
#!/bin/bash
set -e

# The Databricks Python directory isn't on the path in
# databricksruntime/gpu-tensorflow:cuda11.8 for some reason
export PATH="/databricks/python/bin:$PATH"

# Install RAPIDS (cudf & dask-cudf) and dask-databricks
/databricks/python/bin/pip install --extra-index-url=https://pypi.nvidia.com \
      bokeh==3.2.2 \
      cudf-cu11 \
      dask[complete] \
      dask-cudf-cu11 \
      dask-cuda==23.10.0 \
      dask-databricks

# Start the Dask cluster with CUDA workers
dask databricks run --cuda

```

```{note}
If you only need to install RAPIDS in a Databricks GPU Notebook environment, then skip this section and proceed directly to launch a Databricks cluster.
```

## Launch Databricks cluster

Navigate to the **All Purpose Compute** tab of the **Compute** section in Databricks and select **Create Compute**. Name your cluster and choose "Multi node" or "Single node".

![Screenshot of the Databricks compute page](../images/databricks-create-compute.png)

In order to launch a GPU node uncheck **Use Photon Acceleration**.

![Screenshot of Use Photon Acceleration unchecked](../images/databricks-deselect-photon.png)

Then expand the **Advanced Options** section and open the **Docker** tab. Select **Use your own Docker container** and enter the image `databricksruntime/gpu-tensorflow:cuda11.8` or `databricksruntime/gpu-pytorch:cuda11.8`.

![Screenshot of setting the custom container](../images/databricks-custom-container.png)

Once you have done this the GPU nodes should be available in the **Node type** dropdown.

![Screenshot of selecting a g4dn.xlarge node type](../images/databricks-choose-gpu-node.png)

```{warning}
It is also possible to use the Databricks ML GPU Runtime to enable GPU nodes, however at the time of writing the newest version (13.3 LTS ML Beta) contains an older version of `tensorflow` and `protobuf` which is not compatible with RAPIDS. So using a custom container with the latest Databricks GPU container images is recommended.
```

Select **Create Compute**.

## Databricks notebook

Once your cluster has started create a new notebook or open an existing one.

````{warning}
At the time of writing the `databricksruntime/gpu-pytorch:cuda11.8` image does not contain the full `cuda-toolkit` so if you selected that one you will need to install that before installing RAPIDS.

```text
!cd /etc/apt/sources.list.d && \
    mv cuda-ubuntu2204-x86_64.list.disabled cuda-ubuntu2204-x86_64.list && \
    apt-get update && apt-get --no-install-recommends -y install cuda-toolkit-11-8 && \
    mv cuda-ubuntu2204-x86_64.list cuda-ubuntu2204-x86_64.list.disabled
```

````

### Test Rapids

```python
import cudf

gdf = cudf.DataFrame({"a":[1,2,3],"b":[4,5,6]})
gdf
    a   b
0   1   4
1   2   5
2   3   6

```

You can also connect to the dask client using the scheduler address and submit tasks.

```python
from dask.distributed import Client
from dask_databricks import DatabricksCluster

cluster = DatabricksCluster()
client = Client(cluster)

def inc(x):
    return x + 1

x = client.submit(inc, 10)
x.result()
 11

```

## Databricks Spark

You can also use the RAPIDS Accelerator for Apache Spark 3.x on Databricks. See the [Spark RAPIDS documentation](https://nvidia.github.io/spark-rapids/docs/get-started/getting-started-databricks.html) for more information.
