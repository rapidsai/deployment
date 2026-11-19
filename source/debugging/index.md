---
review_priority: "index"
html_theme.sidebar_secondary.remove: true
---

# Debugging & Profiling

A GPU workload that runs isn't necessarily a fast one. The GPU executes parallel work very quickly, but a workflow also pays for cold starts, data movement between host and device, Python overhead, synchronization, and any CPU-only stages left in the path. When GPU code runs but doesn't get the speedup you expected, or the GPU looks idle while the program is busy, the cause is usually one of those costs rather than the GPU itself.

The pages in this section document the tools that answer three questions, from the bottom of the stack up:

- **Is my environment healthy?** Confirm that the driver, the Python CUDA runtime, and the CUDA-X libraries can all see the GPU.
- **Is the GPU busy?** Watch utilization and memory while a workload runs.
- **Where does the time go?** Profile the Python side and the GPU timeline to find the bottleneck.

## Which tool should I use?

| Symptom                                                                         | First tool                               | Page                                 |
| ------------------------------------------------------------------------------- | ---------------------------------------- | ------------------------------------ |
| The host may not see the GPU                                                    | `nvidia-smi`                             | {doc}`Health checks <health-checks>` |
| Python may not see CUDA devices                                                 | `cuda.core`                              | {doc}`Health checks <health-checks>` |
| You're not sure the environment is consistent, or need details for a bug report | `rapids doctor`, `rapids debug --json`   | {doc}`Health checks <health-checks>` |
| The GPU may be idle during a run                                                | `nvtop`, `watch nvidia-smi`, NVDashboard | {doc}`Monitoring <monitoring>`       |
| Python preprocessing may dominate                                               | `cProfile` + SnakeViz                    | {doc}`Profiling <profiling>`         |
| Transfers, launch gaps, or synchronization may dominate                         | Nsight Systems (`nsys`)                  | {doc}`Profiling <profiling>`         |

```{tip}
For a hands-on, step-by-step walkthrough of this material, see the [GPU deployment tutorial](https://github.com/rapidsai-community/gpu-deployment-tutorial).
```

## Guides

`````{gridtoctree} 1 2 2 3
:gutter: 2 2 2 2

````{grid-item-card}
:link: health-checks
:link-type: doc
Verify your environment
^^^
Check the driver, the Python CUDA runtime, and CUDA-X libraries, and collect environment details for a bug report.

{bdg}`nvidia-smi`
{bdg}`cuda.core`
{bdg}`rapids doctor`
{bdg}`rapids debug`
````

````{grid-item-card}
:link: monitoring
:link-type: doc
Monitor GPU usage
^^^
Watch GPU utilization and memory live, from the terminal or inside JupyterLab.

{bdg}`nvidia-smi`
{bdg}`nvtop`
{bdg}`NVDashboard`
````

````{grid-item-card}
:link: profiling
:link-type: doc
Profile GPU workloads
^^^
Find out where the time goes with Python profilers and Nsight Systems GPU timelines, using a worked example.

{bdg}`cProfile`
{bdg}`SnakeViz`
{bdg}`Nsight Systems`
````

`````
