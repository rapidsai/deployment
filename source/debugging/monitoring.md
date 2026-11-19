# Monitor GPU usage

A health check tells you that the GPU is reachable. It doesn't tell you whether your workload actually uses it. The tools on this page show GPU utilization and memory while a process runs, so you can see whether the GPU is busy, idle, or busy only for part of the run.

```{note}
For a hands-on walkthrough of this material, see the [Monitoring and Debugging](https://github.com/rapidsai-community/gpu-deployment-tutorial/blob/main/5-monitoring-and-debugging.md) module of the GPU deployment tutorial.
```

## Snapshots: `watch nvidia-smi`

`nvidia-smi` prints the state of the GPU at one moment. To refresh it every second, run:

```bash
watch -n 1 nvidia-smi
```

Press `Ctrl+C` to exit. Look at these columns:

- **`GPU-Util`:** The percentage of time over the last sample period during which a kernel was running on the GPU.
- **`Memory-Usage`:** The GPU memory in use, out of the total. Memory that stays allocated after your process finishes usually means another process, such as a Jupyter kernel, still holds it.
- **Process table:** The processes that are using the GPU and how much memory each one holds. If your process doesn't appear here, it isn't using the GPU.

## Live timeline: `nvtop`

[`nvtop`](https://github.com/Syllo/nvtop) is an interactive GPU monitor, like `htop` for GPUs. It plots utilization and memory over time, which makes it easier to see how GPU usage changes during a run than a series of `nvidia-smi` snapshots.

Install it from conda-forge, which doesn't need `sudo`:

```bash
conda install -c conda-forge nvtop
```

Or, on Ubuntu or Debian, install it with the system package manager:

```bash
sudo apt install nvtop
```

Then start it and press `q` to quit:

```bash
nvtop
```

Use `watch nvidia-smi` when you want a quick look at the current GPU state. Use `nvtop` when you want to follow a running process over time and check whether it keeps the GPU busy.

### Example: a GPU that goes idle

The {doc}`profiling` page uses an example script, {download}`xarray-cupy-naive.py <scripts/xarray-cupy-naive.py>`, that moves a climate dataset to the GPU, preprocesses it there, and then copies it back to the CPU for the expensive singular value decomposition (SVD). Run it in one terminal and `nvtop` in another. The GPU utilization spikes briefly while the data moves to the GPU and the preprocessing runs, then drops back to idle and stays there while the CPU computes the SVD.

That pattern, a short burst of GPU activity followed by a long idle stretch in a run that is supposed to be GPU accelerated, means that the expensive work isn't running on the GPU. `nvtop` shows you _that_ the GPU went idle. To see _why_, capture a timeline with Nsight Systems, as described in {doc}`profiling`.

## In JupyterLab: NVDashboard

[`jupyterlab-nvdashboard`](https://github.com/rapidsai/jupyterlab-nvdashboard) is a JupyterLab extension that shows live GPU metrics, such as GPU utilization, GPU memory, and PCIe and NVLink throughput, in panels next to your notebook. After you install it, open the panels from the GPU dashboard icon in the JupyterLab sidebar.

Install it with pip or conda:

```bash
pip install jupyterlab-nvdashboard
```

```bash
conda install -c conda-forge jupyterlab-nvdashboard
```

```{warning}
Install `jupyterlab-nvdashboard` into the environment where the **JupyterLab server** runs, not the environment of your notebook kernel. These are often different environments, for example when a platform runs JupyterLab from a system environment and your kernel comes from a conda environment. If you install the extension only in the kernel environment, it's importable as a Python package, but the JupyterLab interface never loads it.

After you install the extension, restart the JupyterLab server and refresh your browser.
```

Recent versions of NVDashboard also include a **GPU Accelerators** panel that turns on `cudf.pandas` and `cuml.accel` with no code changes. See the [`jupyterlab-nvdashboard` repository](https://github.com/rapidsai/jupyterlab-nvdashboard) for details.

## Key point

GPU activity during a run doesn't prove that the expensive work ran on the GPU. Monitoring tells you when the GPU is busy and when it's idle. To find out what runs where, and in what order, see {doc}`profiling`.
