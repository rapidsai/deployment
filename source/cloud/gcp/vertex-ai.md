# Vertex AI

RAPIDS can be deployed on [Vertex AI Workbench](https://cloud.google.com/vertex-ai-workbench).

## Create a new user-managed Notebook

1. From the Google Cloud UI, navigate to [**Vertex AI**](https://console.cloud.google.com/vertex-ai/workbench/user-managed) -> **Workbench**
2. Make sure you select **User-Managed Notebooks** (**Managed Notebooks** are currently not supported) and select **+ CREATE NEW**.
3. In the **Details** section give the instance a name.
4. Under the **Environment** section choose "Python 3 with CUDA 11.8".
5. Check the "Attach 1 NVIDIA T4 GPU" option.
6. After customizing any other aspects of the machine you wish, click **CREATE**.

```{tip}
If you want to select a different GPU or select other hardware options you can select "Advanced Options" at the bottom and then make changes in the "Machine type" seciton.
```

## Install RAPIDS

Once the instance has started select **OPEN JUPYTER LAB** and at the top of a notebook install the RAPIDS libraries you wish to use.

```bash
!pip install cudf-cu11 dask-cudf-cu11 --extra-index-url=https://pypi.nvidia.com
!pip install cuml-cu11 --extra-index-url=https://pypi.nvidia.com
!pip install cugraph-cu11 --extra-index-url=https://pypi.nvidia.com
```

## Test RAPIDS

You should now be able to open a notebook and use RAPIDS.

For example we could import and use RAPIDS libraries like `cudf`.

```ipython
In [1]: import cudf
In [2]: df = cudf.datasets.timeseries()
In [3]: df.head()
Out[3]:
                       id     name         x         y
timestamp
2000-01-01 00:00:00  1020    Kevin  0.091536  0.664482
2000-01-01 00:00:01   974    Frank  0.683788 -0.467281
2000-01-01 00:00:02  1000  Charlie  0.419740 -0.796866
2000-01-01 00:00:03  1019    Edith  0.488411  0.731661
2000-01-01 00:00:04   998    Quinn  0.651381 -0.525398
```

```{relatedexamples}

```
