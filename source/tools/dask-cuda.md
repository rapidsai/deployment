# dask-cuda

[Dask-CUDA](https://docs.rapids.ai/api/dask-cuda/stable/) is a library extending `LocalCluster` from `dask.distributed` to enable multi-GPU workloads.

## LocalCUDACluster

You can use `LocalCUDACluster` to create a cluster of one or more GPUs on your local machine. You can launch a Dask scheduler on LocalCUDACluster to parallelize and distribute your RAPIDS workflows across multiple GPUs on a single node.

In addition to enabling multi-GPU computation, `LocalCUDACluster` also provides a simple interface for managing the cluster, such as starting and stopping the cluster, querying the status of the nodes, and monitoring the workload distribution.

## Pre-requisites

Before running these instructions, ensure you have installed the [`dask`](https://docs.dask.org/en/stable/install.html) and [`dask-cuda`](https://docs.rapids.ai/api/dask-cuda/nightly/install.html) packages in your local environment

## Cluster setup

### Instantiate a LocalCUDACluster object

The `LocalCUDACluster` class autodetects the GPUs in your system, so if you create it on a machine with two GPUs it will create a cluster with two workers, each of which is responsible for executing tasks on a separate GPU.

```console
cluster = LocalCUDACluster()
```

You can also restrict your cluster to use specific GPUs by setting the `CUDA_VISIBLE_DEVICES` environment variable, or as a keyword argument.

```console
cluster = LocalCUDACluster(CUDA_VISIBLE_DEVICES="0,1")  # Creates one worker for GPUs 0 and 1
```

### Connecting a Dask client

The Dask scheduler coordinates the execution of tasks, whereas the Dask client is the user-facing interface that submits tasks to the scheduler and monitors their progress.

```console
client = Client(cluster)
```

## Test RAPIDS

To test RAPIDS, create a `distributed` client for the cluster and query for the GPU model.

```Python
from dask_cuda import LocalCUDACluster
from dask.distributed import Client

def get_gpu_model():
    import pynvml

    pynvml.nvmlInit()
    return pynvml.nvmlDeviceGetName(pynvml.nvmlDeviceGetHandleByIndex(0))


def main():
    cluster = LocalCUDACluster()
    client = Client(cluster)

    result = client.submit(get_gpu_model).result()
    print(f"{result=}")

if __name__ == "__main__":
    main()
```
