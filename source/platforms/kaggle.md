---
review_priority: "p1"
---

# RAPIDS on Kaggle

[Kaggle Notebooks](https://www.kaggle.com/code) provide hosted Jupyter notebooks
with GPU accelerators. The latest Kaggle notebook environment includes RAPIDS
libraries such as [cuDF](https://docs.nvidia.com/cudf/latest/) and
[cuML](https://docs.nvidia.com/cuml/latest/), so you can start using them
without a separate installation.

## Create a GPU notebook

1. [Log in to Kaggle](https://www.kaggle.com/account/login) or create a Kaggle
   account.
1. Select **Create** and then **Notebook**. You can also open the
   [new notebook page](https://www.kaggle.com/code/new) directly.

   ```{figure} /_static/images/platforms/kaggle/create-notebook.png
   ---
   alt: Kaggle Create menu with Notebook selected
   ---
   ```

1. In the notebook editor, select **Settings** > **Accelerator**, then choose an
   available GPU option, such as **GPU T4 x2** or **GPU P100**. Starting a GPU
   session uses your Kaggle GPU quota, so stop the session when you are done.

   ```{figure} /_static/images/platforms/kaggle/select-gpu-accelerator.png
   ---
   alt: Kaggle notebook Settings menu showing the available GPU accelerators
   ---
   ```

1. Select **Settings** > **Environment Preferences** > **Always use latest
   environment**. This makes the notebook use Kaggle's latest environment,
   which contains the preinstalled RAPIDS libraries.

   ```{figure} /_static/images/platforms/kaggle/use-latest-env.png
   ---
   alt: Kaggle notebook Environment Preferences menu with Always use latest environment selected
   ---
   ```

## Test RAPIDS

Enter the following code in a notebook cell, and select the **Run** button or
press `Shift+Enter`:

```python
import cudf

gdf = cudf.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
gdf.sum()
```

The cell should produce the following output:

```text
a     6
b    15
dtype: int64
```

This confirms that cuDF can use the prebuilt Kaggle environment. You can also
import `cuml` to run GPU-accelerated machine learning workflows.

## Next steps

Try these examples in your Kaggle notebook:

- [10 Minutes to cuDF](https://docs.nvidia.com/cudf/latest/cudf/10min/)
- [Accelerating pandas with cuDF](https://docs.nvidia.com/cudf/latest/cudf_pandas/)
- [cuML quick start](https://docs.nvidia.com/cuml/latest/#quick-start)
- [Accelerating scikit-learn with `cuml.accel`](https://docs.nvidia.com/cuml/latest/cuml-accel/examples/getting_started/)
