# Verify your environment

When a GPU workload fails or behaves unexpectedly, check the environment before you debug the code. A GPU environment has three layers, and each one depends on the layer below it:

1. **Host:** the GPU hardware and the NVIDIA driver.
2. **Python CUDA runtime:** the CUDA libraries that your Python environment loads to talk to the driver.
3. **CUDA-X libraries:** cuDF, cuML, CuPy, and the other packages that you actually use.

Debug from the bottom up. If a lower layer fails, stop and fix it first. A broken driver makes every check above it fail, so there is nothing to gain from debugging the Python environment until the host is healthy.

```{note}
For a hands-on walkthrough of this material, see the [RAPIDS CLI](https://github.com/rapidsai-community/gpu-deployment-tutorial/blob/main/3-rapids-cli-verify-env.md) and [Monitoring and Debugging](https://github.com/rapidsai-community/gpu-deployment-tutorial/blob/main/5-monitoring-and-debugging.md) modules of the GPU deployment tutorial.
```

## Host: `nvidia-smi`

`nvidia-smi` ships with the NVIDIA driver. Run it on the GPU machine:

```console
$ nvidia-smi
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.159.03             Driver Version: 580.159.03     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA L4                      On  |   00000000:00:03.0 Off |                    0 |
| N/A   40C    P8             13W /   72W |       0MiB /  23034MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```

The table shows the GPU name, the driver version, the newest CUDA version that the driver supports, memory usage, utilization, and the processes that are using the GPU.

For a short list of GPUs, run:

```bash
nvidia-smi -L
```

For a detailed dump that is useful in a support request, run:

```bash
nvidia-smi -q
```

If `nvidia-smi` prints this information, the host driver can see the GPU. It does **not** show that your Python environment is healthy: the host can have a working driver while the active Python environment is missing CUDA runtime libraries or contains incompatible packages.

If `nvidia-smi` fails, fix the driver, the virtual machine, or the container runtime before you go further.

## Python: `cuda.core`

[`cuda.core`](https://nvidia.github.io/cuda-python/cuda-core/latest/) is part of CUDA Python. It answers a different question from `nvidia-smi`: can this Python environment load the CUDA libraries that it needs to talk to the driver?

The following script asks CUDA how many devices it can see, and prints the name, compute capability, and memory of each one ({download}`download gpu-probe-cuda-core.py <scripts/gpu-probe-cuda-core.py>`):

```{literalinclude} scripts/gpu-probe-cuda-core.py
:language: python
:lines: 4-
```

Run it with the Python interpreter of the environment that you want to check:

```bash
python gpu-probe-cuda-core.py
```

How to read the result:

- **Both `nvidia-smi` and the script succeed:** the host and the active Python environment both see the GPU.
- **`nvidia-smi` succeeds but the script fails:** the host is fine, but the Python environment isn't. This is an environment problem, not a hardware problem. Check that the CUDA packages in the environment match the CUDA version that the driver supports.

The same kind of error can show up later in a CUDA-X library. For example, if CuPy fails with a message about `libnvrtc.so.13`, CuPy is trying to load the NVIDIA Runtime Compiler library and can't find it. Install the matching CUDA runtime packages into the environment, or reinstall CuPy for the CUDA version that you have.

## CUDA-X libraries: `rapids doctor`

The [RAPIDS CLI](https://github.com/rapidsai/rapids-cli) bundles the checks that you would otherwise run by hand into two commands:

- `rapids doctor` tells you whether your environment is healthy.
- `rapids debug` tells you exactly what is in that environment.

Install it into the environment that you want to check, with pip:

```bash
pip install rapids-cli
```

Or with conda, from the `rapidsai` channel:

```bash
conda install -c rapidsai -c conda-forge rapids-cli
```

Then run the health checks:

```console
$ rapids doctor
🧑‍⚕️ Performing REQUIRED health check for RAPIDS
Running checks
All checks passed!
```

The core checks answer one question each:

- **GPU present:** Is there at least one GPU, and does it meet the [compute capability](https://developer.nvidia.com/cuda-gpus) that RAPIDS requires (7.0 or higher)?
- **CUDA driver:** Can the CLI read the CUDA version that the driver supports?
- **CUDA toolkit vs. driver:** Is the CUDA toolkit in the environment no newer than the driver supports?
- **Memory ratio:** Does the system have at least roughly twice as much memory as the total GPU memory? This check is advisory (useful for Dask), so it prints a warning instead of failing.
- **NVLink:** On machines with two or more GPUs, are the [NVLink](https://www.nvidia.com/en-us/data-center/nvlink/) connections active?

A failed check prints a message that tells you how to fix it. For example, when the CUDA toolkit is newer than the driver supports, the message tells you to update the driver or recreate the environment with matching CUDA packages.

CUDA-X libraries can register their own checks through the `rapids_doctor_check` entry point, so installing a library such as cuML adds small end-to-end smoke tests to `rapids doctor` automatically. Run `rapids doctor --verbose` to see which checks were discovered and the result of each one. For a walkthrough of the checks and their output, see the [RAPIDS CLI](https://github.com/rapidsai-community/gpu-deployment-tutorial/blob/main/3-rapids-cli-verify-env.md) module of the GPU deployment tutorial.

## Sharing your environment: `rapids debug`

Where `rapids doctor` gives a verdict, `rapids debug` gives a full report of the machine. It prints the full `nvidia-smi` table, OS details, every installed package, and the build tools on your `PATH`. A trimmed example:

```console
$ rapids debug
RAPIDS Debug Information
...
Driver Version
580.159.03

Cuda Version
13.0

Cuda Runtime Path
/home/ubuntu/.venv/lib/python3.13/site-packages/nvidia/cu13/include

System Ctk
[]
...
Package Versions
┌───────────────┬──────────┐
│ cuda-bindings │ 13.3.1   │
│ cuda-toolkit  │ 13.3.0   │
│ cupy-cuda13x  │ 14.1.1   │
│ numpy         │ 2.2.6    │
│ rapids-cli    │ 0.2.0    │
│ ...           │ ...      │
└───────────────┴──────────┘
...
Tools
┌───────┬─────────────────────────────────────────────────────────────────────────────────┐
│ pip   │ pip 25.2 from /home/ubuntu/.venv/lib/python3.13/site-packages/pip (python 3.13) │
│ g++   │ g++ (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0                                       │
│ nvcc  │ None                                                                            │
│ cmake │ None                                                                            │
└───────┴─────────────────────────────────────────────────────────────────────────────────┘
...
```

The fields that matter most:

- **Driver and CUDA versions:** `Driver Version` is the NVIDIA driver, the same number that `nvidia-smi` shows. `Cuda Version` is the newest CUDA that the driver supports. A CUDA toolkit newer than this is the classic broken install, and it's what the toolkit check in `rapids doctor` catches.
- **Toolkit location:** `Cuda Runtime Path` is where your environment found the CUDA runtime, and `System Ctk` lists any toolkits installed under `/usr/local/cuda*`. In the example above, `System Ctk` is empty and the runtime path points inside `site-packages`, so CUDA came from pip wheels rather than a system install. Together, these two fields tell you which CUDA you're actually using when more than one could be present.
- **Package and tool versions:** `Package Versions` lists every installed Python package, and `Tools` lists the build and packaging tools on your `PATH`. A tool that isn't installed shows as `None`.

To get the same information in a machine-readable format, run:

```bash
rapids debug --json
```

The JSON output is what you paste into a GitHub issue when you ask for help, for example in the [cuDF](https://github.com/NVIDIA/cudf/issues), [cuML](https://github.com/NVIDIA/cuml/issues), or [RAPIDS CLI](https://github.com/rapidsai/rapids-cli/issues) issue trackers.

## Summary

| Tool            | Question it answers                                                                       |
| --------------- | ----------------------------------------------------------------------------------------- |
| `nvidia-smi`    | Does the host driver see the GPU?                                                         |
| `cuda.core`     | Can this Python environment load CUDA and see the GPU?                                    |
| `rapids doctor` | Are the driver, CUDA toolkit, GPU, and installed CUDA-X libraries consistent and working? |
| `rapids debug`  | What exactly is installed, so you can share it in a bug report?                           |

Once the environment is healthy, see {doc}`monitoring` to check whether your workload keeps the GPU busy.
