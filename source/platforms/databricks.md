---
review_priority: "p0"
---

# Databricks

You can install RAPIDS on Databricks in a few different ways:

1. Accelerate machine learning workflows in a single-node GPU notebook environment
2. Spark users can install [RAPIDS Accelerator for Apache Spark 3.x on Databricks](https://docs.nvidia.com/spark-rapids/user-guide/latest/getting-started/databricks.html)
3. Install Dask alongside Spark and then use libraries like `dask-cudf` for multi-node workloads

## Single-node GPU Notebook environment

(create-init-script)=

### Create init-script

To get started, you must first configure an [initialization script](https://docs.databricks.com/en/init-scripts/index.html) to install RAPIDS libraries and all other dependencies for your project.

Databricks recommends using [cluster-scoped](https://docs.databricks.com/en/init-scripts/cluster-scoped.html) init scripts stored in the workspace files.

Navigate to the top-left **Workspace** tab and click on your **Home** directory then select **Add** > **File** from the menu. Create an `init.sh` script with contents:

```bash
#!/bin/bash
set -e

# Install RAPIDS libraries
pip install \
    --extra-index-url={{rapids_pip_index}} \
    "cudf-cu12>={{rapids_pip_version}}" "cuml-cu12>={{rapids_pip_version}}" \
    "dask-cuda>={{rapids_pip_version}}"

```

(launch-databricks-cluster)=

### Launch cluster

To get started, navigate to the **All Purpose Compute** tab of the **Compute** section in Databricks and select **Create Compute**. Name your cluster and choose **"Single node"**.

![Screenshot of the Databricks compute page](../images/databricks-create-compute.png)

In order to launch a GPU node uncheck **Use Photon Acceleration** and select any `15.x`, `16.x` or `17.x` ML LTS runtime with GPU support.
For example for long-term support releases you could select the `15.4 LTS ML (includes Apache Spark 3.5.0, GPU, Scala 2.12)` runtime version.

The "GPU accelerated" nodes should now be available in the **Node type** dropdown.

![Screenshot of selecting a g4dn.xlarge node type](../images/databricks-choose-gpu-node.png)

Then expand the **Advanced Options** section, open the **Init Scripts** tab and enter the file path to the init-script in your Workspace directory starting with `/Users/<user-name>/<script-name>.sh` and click **"Add"**.

![Screenshot of init script path](../images/databricks-dask-init-script.png)

Select **Create Compute**

### Test RAPIDS

Once your cluster has started, you can create a new notebook or open an existing one from the `/Workspace` directory then attach it to your running cluster.

```python
import cudf

gdf = cudf.DataFrame({"a":[1,2,3],"b":[4,5,6]})
gdf
    a   b
0   1   4
1   2   5
2   3   6
```

#### Quickstart with cuDF Pandas

RAPIDS recently introduced cuDF’s [pandas accelerator mode](https://rapids.ai/cudf-pandas/) to accelerate existing pandas workflows with zero changes to code.

Using `cudf.pandas` in Databricks on a single-node can offer significant performance improvements over traditional pandas when dealing with large datasets; operations are optimized to run on the GPU (cuDF) whenever possible, seamlessly falling back to the CPU (pandas) when necessary, with synchronization happening in the background.

Below is a quick example how to load the `cudf.pandas` extension in a Jupyter notebook:

```python

%load_ext cudf.pandas

%%time

import pandas as pd

df = pd.read_parquet(
    "nyc_parking_violations_2022.parquet",
    columns=["Registration State", "Violation Description", "Vehicle Body Type", "Issue Date", "Summons Number"]
)

(df[["Registration State", "Violation Description"]]
 .value_counts()
 .groupby("Registration State")
 .head(1)
 .sort_index()
 .reset_index()
)
```

Upload the [10 Minutes to RAPIDS cuDF Pandas notebook](https://colab.research.google.com/drive/12tCzP94zFG2BRduACucn5Q_OcX1TUKY3) in your single-node Databricks cluster and run through the cells.

**NOTE**: cuDF pandas is open beta and under active development. You can [learn more through the documentation](https://docs.rapids.ai/api/cudf/~~~rapids_api_docs_version~~~/?_gl=1*1oyfbsi*_ga*MTc5NDYzNzYyNC4xNjgzMDc2ODc2*_ga_RKXFW6CM42*MTcwNTU4NDUyNS4yMC4wLjE3MDU1ODQ1MjUuNjAuMC4w) and the [release blog](https://developer.nvidia.com/blog/rapids-cudf-accelerates-pandas-nearly-150x-with-zero-code-changes/).

## Multi-node Dask cluster

Dask now has a [dask-databricks](https://github.com/jacobtomlinson/dask-databricks) CLI tool (via [`conda`](https://github.com/conda-forge/dask-databricks-feedstock) and [`pip`](https://pypi.org/project/dask-databricks/)) to simplify the Dask cluster startup process within Databricks.

### Install RAPIDS and Dask

[Create the init script](create-init-script) below to install `dask`, `dask-databricks` RAPIDS libraries and all other dependencies for your project.

```bash
#!/bin/bash
set -e

# Install RAPIDS libraries
pip install \
    --extra-index-url={{rapids_pip_index}} \
    "cudf-cu12>={{rapids_pip_version}}" "cuml-cu12>={{rapids_pip_version}}" \
    "dask-cuda>={{rapids_pip_version}}" "dask-cudf-cu11>={{rapids_pip_version}} \
    "dask[complete]" dask-databricks

# Start the Dask cluster with CUDA workers
dask databricks run --cuda

```

**Note**: By default, the `dask databricks run` command will launch a dask scheduler in the driver node and standard workers on remaining nodes.

To launch a dask cluster with GPU workers, you must parse in `--cuda` flag option.

### Launch Dask cluster

Once your script is ready, follow the [instructions](launch-databricks-cluster) to launch a **Multi-node** cluster.

Be sure to select `16.4 LTS ML (includes Apache Spark 3.5.2, GPU, Scala 2.13)` ML Runtime as shown below.

Configure the path to your init script in the **Init Scripts** tab. Optionally, you can also configure cluster log delivery in the **Logging** tab, which will write the [init script logs](https://docs.databricks.com/en/init-scripts/logs.html) to DBFS in a subdirectory called `dbfs:/cluster-logs/<cluster-id>/init_scripts/`.

![Screenshot of log delivery](../images/databricks-dask-logging.png)

Once you have completed, you should be able to select a "GPU-Accelerated" instance for both **Worker** and **Driver** nodes.

![Screenshot of driver worker node](../images/databricks-worker-driver-node.png)

Select **Create Compute**

### Connect to Client

```python
import dask_databricks


client = dask_databricks.get_client()
client
```

#### Dashboard

The **[Dask dashboard](https://docs.dask.org/en/latest/dashboard.html)** provides a web-based UI with visualizations and real-time information about the Dask cluster status i.e task progress, resource utilization, etc.

The dashboard server will start up automatically when the scheduler is created, and is hosted on port `8087` by default. To access follow the URL to the dashboard status endpoint within Databricks.

![Screenshot of dask-client.png](../images/databricks-mnmg-dask-client.png)

#### Submit tasks

```python
import cudf
import dask


df = dask.datasets.timeseries().map_partitions(cudf.from_pandas)
df.x.mean().compute()
```

![Screenshot of dask-cudf-example.png](../images/databricks-dask-cudf-example.png)

#### Dask-Databricks example

In your multi-node cluster, upload the [Training XGBoost with Dask RAPIDS in Databricks](https://github.com/rapidsai/deployment/blob/main/source/examples/xgboost-dask-databricks/notebook.ipynb) example in Jupyter notebook and run through the cells.

### Clean up

```python
client.close()
```
