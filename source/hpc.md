---
review_priority: "index"
---

# HPC

RAPIDS works extremely well in traditional HPC (High Performance Computing)
environments where GPUs are often co-located with accelerated networking
hardware. RAPIDS can be deployed on HPC clusters managed by
[Slurm](https://slurm.schedmd.com/).

## Slurm

Slurm is a job scheduler that manages access to compute nodes on HPC clusters.
Instead of logging into a GPU machine directly, you ask Slurm for resources
(CPUs, GPUs, memory, time) and it allocates a node for you when one becomes
available.

Nodes are organized into **partitions**, groups of machines with similar
hardware. For example, your cluster might have a `gpu` partition with A100 nodes
and a `cpu` partition with CPU-only nodes.

For a more comprehensive overview, see the [Slurm quickstart guide](https://slurm.schedmd.com/quickstart.html).

```{note}
Some clusters provide Slurm commands through environment modules. If commands
such as `sinfo`, `srun`, or `sbatch` are not found, load your cluster's Slurm
module first, for example `module load slurm`.
```

### Partitions

Check which partitions are available and what GPUs they have. The `-o` flag
customizes the output format: `%P` shows the partition name, `%G` the
generic resources (such as GPUs), `%D` the number of nodes, and `%T` the
node state.

```bash
sinfo -o "%P %G %D %T"
PARTITION   GRES       NODES STATE
gpu         gpu:a100:4 10    idle
gpu-dev     gpu:v100:2 4     idle
```

Your cluster admin can tell you which partition to use. Throughout this guide
we use `-p gpu`. Replace this with your partition name.

### Interactive Jobs

An interactive job gives you a shell on a compute node where you can run
commands directly. This is useful for development, debugging, and testing
before submitting longer batch jobs.

Use `srun` to request a GPU node. The `--gres=gpu:1` flag requests one GPU,
`--time` sets the maximum walltime, and `--pty bash` gives you a terminal.

```bash
srun -p gpu --gres=gpu:1 --time=01:00:00 --pty bash
```

This will queue until a node is available, then drop you into a shell on
the allocated node.

### Batch Jobs

For longer-running work, write a script and submit it with `sbatch`. Slurm
runs the script when resources become available and you don't need to stay
connected.

Run batch jobs from a filesystem that is shared between the submit host and
compute nodes. This ensures your scripts, input data, and Slurm output files
are visible wherever the job runs. Your cluster admin can tell you which paths
are shared.

```bash
sbatch my_job.sh
Submitted batch job 12345
```

Check the status of your jobs with `squeue`. The `-u` flag filters by your
username.

```bash
squeue -u $USER
```

### Keeping Sessions Alive

If your SSH connection drops while in an interactive job, the job is
terminated and you lose your work. To avoid this, start a
[tmux](https://github.com/tmux/tmux) or
[screen](https://www.gnu.org/software/screen/) session on the login node
**before** requesting your interactive job.

```bash
tmux new -s rapids
srun -p gpu --gres=gpu:1 --time=01:00:00 --pty bash
```

To detach from the tmux session without ending your job, press `Ctrl+b`
then `d`. Your interactive job continues running in the background. When
you reconnect via SSH, reattach to the session with:

```bash
tmux attach -t rapids
```

## Install RAPIDS

### Environment Modules

[Environment modules](https://modules.readthedocs.io/) are the standard way
to manage software on HPC clusters. We'll create a
[conda](https://docs.conda.io/) environment containing both CUDA and RAPIDS,
then wrap it in an [Lmod](https://lmod.readthedocs.io/) module file so it can
be loaded with a single command.

Conda installs the full RAPIDS suite alongside the CUDA toolkit in a single
command, which is convenient on shared HPC filesystems.

```{note}
Conda installs the CUDA **toolkit** (runtime libraries), but
the NVIDIA **kernel driver** must already be installed on the cluster's compute
nodes. This is typically managed by your cluster admin. You can verify the
driver is available by running `nvidia-smi` on a compute node.
```

#### Install Miniforge

If conda isn't already available on your cluster, install
[Miniforge](https://github.com/conda-forge/miniforge). Install it to a shared
filesystem so compute nodes can read the environments you create.

```bash
curl -LO "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh -b -p /path/to/miniforge3
source /path/to/miniforge3/etc/profile.d/conda.sh
```

#### Create the environment

Create the environment in a location that is available on compute nodes. On
many clusters this means installing environments on a shared filesystem rather
than on the login node's local disk.

```bash
conda create -n rapids-{{ rapids_version }} --override-channels \
    {{ rapids_conda_channels }} \
    {{ rapids_conda_packages }}
```

#### Create the module file

Replace `<path to miniforge3>` with the absolute path to your Miniforge
installation. The example below installs the modulefile to `~/modulefiles`,
which works without admin access. Cluster admins can install it to a
shared module path (e.g. `/opt/modulefiles`) instead so all users can load it.

The example below is a Lua modulefile and requires
[Lmod](https://lmod.readthedocs.io/). Verify that `module --version` reports
Lmod before using it. If your cluster uses Tcl Environment Modules, ask your
cluster admin for the equivalent Tcl modulefile.

```bash
mkdir -p ~/modulefiles/rapids
cat << 'EOF' > ~/modulefiles/rapids/{{ rapids_version }}.lua
help([[RAPIDS {{ rapids_version }} - GPU-accelerated data science libraries.]])

whatis("Name: RAPIDS")
whatis("Version: {{ rapids_version }}")
whatis("Description: GPU-accelerated data science libraries")

family("rapids")

local conda_root = "<path to miniforge3>"
local env        = "rapids-{{ rapids_version }}"
local env_prefix = pathJoin(conda_root, "envs", env)

prepend_path("PATH",            pathJoin(env_prefix, "bin"))
prepend_path("LD_LIBRARY_PATH", pathJoin(env_prefix, "lib"))

setenv("CONDA_PREFIX",     env_prefix)
setenv("CONDA_DEFAULT_ENV", env)
EOF
```

Add the modulefile directory to your module search path:

```bash
module use ~/modulefiles
```

To make this persistent across sessions, add `module use ~/modulefiles` to
your `~/.bashrc`.

#### Verify

```bash
module load rapids/{{ rapids_version }}
srun -p gpu --gres=gpu:1 python -c "import cudf; print(cudf.__version__)"
```

Run this verification on a GPU compute node. A login or head node may not have
a GPU or a compatible NVIDIA driver even when the compute nodes are configured
correctly.

### Containers

Many HPC clusters support running containers through runtimes such as
[Apptainer](https://apptainer.org/) (formerly Singularity),
[Pyxis](https://github.com/NVIDIA/pyxis) + [Enroot](https://github.com/NVIDIA/enroot),
[Podman](https://podman.io/), or
[Charliecloud](https://hpc.github.io/charliecloud/). This is an alternative
to environment modules, as the RAPIDS container image ships with CUDA and all
RAPIDS libraries pre-installed and does not need any additional configuration.

Check with your cluster admin which container runtime is available. The
examples below cover Apptainer and Pyxis + Enroot, two of the most common
setups on HPC clusters.

GPU containers also require NVIDIA container runtime tooling on compute nodes,
including `nvidia-container-cli` from
[`libnvidia-container`](https://github.com/NVIDIA/libnvidia-container). If
Pyxis fails while starting the container and references `nvidia-container-cli`,
ask your cluster admin to install the NVIDIA container runtime packages on the
compute nodes.

#### Apptainer

[Apptainer](https://apptainer.org/) is a container runtime designed for HPC.
The `--nv` flag exposes the host GPU drivers to the container.

```bash
apptainer pull rapids.sif docker://{{ rapids_container }}
```

#### Pyxis + Enroot

[Enroot](https://github.com/NVIDIA/enroot) is NVIDIA's lightweight container
runtime for HPC. [Pyxis](https://github.com/NVIDIA/pyxis) is a Slurm plugin
that integrates Enroot into Slurm, adding `--container-*` flags to `srun` and
`sbatch` so you can launch containerized jobs directly through the scheduler.
Pyxis + Enroot is pre-installed on many GPU clusters including NVIDIA DGX
systems.

Import the RAPIDS container image as a squashfs file. We recommend
pre-importing large images to avoid re-downloading on every job.

Note that Enroot uses `#` instead of `/` to separate the registry hostname
from the image path.

```bash
enroot import --output rapids.sqsh 'docker://{{ rapids_container.replace("/", "#", 1) }}'
```

## Run a Single GPU Job

[cudf.pandas](https://docs.rapids.ai/api/cudf/stable/cudf_pandas/) lets you
accelerate existing pandas code on a GPU with no code changes. You run your
script with `python -m cudf.pandas` instead of `python` and pandas operations
are automatically dispatched to the GPU.

The following example uses pandas to generate and aggregate random data.

```python
# my_script.py
import pandas as pd

df = pd.DataFrame({"x": range(1_000_000), "y": range(1_000_000)})
df["group"] = df["x"] % 100
result = df.groupby("group").agg(["mean", "sum", "count"])
print(result)
```

### Interactive

#### With modules

```bash
srun -p gpu --gres=gpu:1 --pty bash
module load rapids/{{ rapids_version }}
python -m cudf.pandas my_script.py
```

#### With containers

`````{tab-set}

````{tab-item} Apptainer

The `--nv` flag exposes the host GPU drivers to the container.

```bash
srun -p gpu --gres=gpu:1 apptainer exec --nv rapids.sif \
    python -m cudf.pandas my_script.py
```

````

````{tab-item} Pyxis + Enroot

The `--container-image` flag is provided by Pyxis. Use `--container-mounts`
to make your data and scripts available inside the container.

```bash
srun -p gpu --gres=gpu:1 \
    --container-image=./rapids.sqsh \
    --container-mounts=$(pwd):/work --container-workdir=/work \
    python -m cudf.pandas /work/my_script.py
```

````

`````

### Batch

Write a Slurm batch script to run the same workload without an interactive
session. This is the typical workflow for production jobs. Save the script in a
shared filesystem so compute nodes can access it and so the Slurm output file is
written somewhere visible after the job completes.

```bash
#!/usr/bin/env bash
#SBATCH --job-name=rapids-cudf
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00

module load rapids/{{ rapids_version }}
python -m cudf.pandas my_script.py
```

```bash
sbatch rapids_job.sh
```

```{relatedexamples}

```
