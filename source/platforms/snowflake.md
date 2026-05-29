# Snowflake

You can access `cuDF` and `cuML` in [Snowflake Notebooks in Workspaces (Jupyter compatible)](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks-in-workspaces/notebooks-in-workspaces-overview)
or in the [Snowflake Notebooks on Container Runtime for ML](https://docs.snowflake.com/en/developer-guide/snowflake-ml/notebooks-on-spcs).
You can also install RAPIDS on [Snowflake](https://www.snowflake.com) via [Snowpark Container Services](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview).

## Snowflake Notebooks in Workspaces (Jupyter compatible)

Snowflake Notebooks in Workspaces provide a Jupyter-compatible environment. The environment is pre-configured for AI/ML development with fully-managed access to GPUs, and it has cuDF and cuML
built-in.

1. In the left panel, go to **Projects** → **Workspaces**.

```{figure} /images/snowflake-workspace-nb1.png
---
alt: Screenshot of how to access workspace
---
```

2. Inside your workspace, click **+ Add new** and select **Notebook** to create a new notebook,
   or choose **Upload files** to import an existing `.ipynb` file.

```{figure} /images/snowflake-workspace-nb2.png
---
alt: Screenshot of how to access create new notebook on workspace
---
```

3. Once your notebook is open, click the **Connect** dropdown and select **Create new service**
   to attach a compute service that will run your notebook.

```{figure} /images/snowflake-workspace-nb3.png
---
alt: Screenshot of how to create a new service to connect the new notebook
---
```

4. In the **Connect your notebook** dialog, give your service a name, set the **Compute type** to **GPU**,
   select a GPU compute pool (e.g. `SYSTEM_COMPUTE_POOL_GPU (GPU_NV_S)`), and choose an
   **External access integration** (e.g. `ALLOW_ALL_INTEGRATION`) to allow package installation from PyPI and general internet access.
   Click **Create and connect** when ready.

```{figure} /images/snowflake-workspace-nb4.png
---
alt: Screenshot of how to configure service to get GPU access
---
```

5. You can import `cuDF` and or `cuML` and start using the notebook.

```{relatedexamples}

```
