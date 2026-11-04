---
short_title: "molab"
review_priority: "p1"
---

# marimo notebooks on molab

[molab](https://molab.marimo.io) is a hosted service for running
[marimo](https://marimo.io) notebooks in the cloud. A molab notebook can use an
NVIDIA RTX Pro 6000 (Blackwell) GPU, which you can turn on from the notebook
editor. See the [molab documentation](https://docs.marimo.io/guides/molab/)
for current usage limits.

## Create a GPU notebook

1. Sign in to [molab](https://molab.marimo.io) and select **Create a notebook**.
1. Select the resources button in the notebook header, which shows
   **4 CPU · 32 GiB**. Under **GPUs**, select **RTX Pro 6000 (Blackwell)**,
   then select **Save and restart**.

   ```{figure} /_static/images/platforms/molab/enable-gpu.png
   ---
   alt: molab Configure Resources menu with RTX Pro 6000 (Blackwell) selected under GPUs
   ---
   ```

## Install the libraries

marimo notebooks don't support `%pip` magics. Install the libraries from the
**Packages** panel instead.

1. Select the cube icon in the sidebar to open the **Packages** panel.
1. Paste the following line into the package input and select **Add**.

   ```text
   --extra-index-url={{ rapids_pip_index }} cudf-cu{{ rapids_cuda_major }}=={{ rapids_pip_version }} cuml-cu{{ rapids_cuda_major }}=={{ rapids_pip_version }}
   ```

   ```{figure} /_static/images/platforms/molab/packages-panel.png
   ---
   alt: molab Packages panel with cuDF and cuML pasted into the package input
   width: 400px
   align: center
   ---
   ```

1. molab shows the installation logs in an **Installing packages** dialog. Wait
   for the installation to finish.

   ```{figure} /_static/images/platforms/molab/install-logs.png
   ---
   alt: molab Installing packages dialog showing uv resolving and downloading the CUDA-X libraries
   width: 550px
   align: center
   ---
   ```

1. Restart the kernel so that Python picks up the new libraries. Select the
   menu icon in the top right of the notebook, then select **Restart kernel**.
   Without a restart, `import cudf` fails with
   `ModuleNotFoundError: No module named 'numba.cuda.core'`.

   ```{figure} /_static/images/platforms/molab/restart-kernel.png
   ---
   alt: marimo notebook menu with the Restart kernel option
   width: 320px
   align: center
   ---
   ```

This installs cuDF and cuML. To install other NVIDIA CUDA-X libraries for data
science, find their package names in the
[release selector](https://docs.nvidia.com/datascience/install/#selector) and
add them to the line without the quotes, separated by spaces.

## Verify the installation

Enter the following code in a notebook cell and run it:

```python
import cudf

gdf = cudf.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
gdf
```

The cell displays the DataFrame:

```{figure} /_static/images/platforms/molab/verify-output.png
---
alt: molab notebook cell displaying a cuDF DataFrame with columns a and b
width: 520px
align: center
---
```

This confirms that cuDF can use the GPU. cuML is ready to import in the same
notebook. If the cell fails,
check that the GPU is turned on and that you restarted the kernel after
installing.

To get started with cuDF, work through
[10 Minutes to cuDF](https://docs.nvidia.com/cudf/latest/cudf/10min/).
