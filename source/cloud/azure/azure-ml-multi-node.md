# Azure ML Compute cluster

Launch Azure's [ML Compute cluster](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-attach-compute-cluster?tabs=python) to distribute your RAPIDS training jobs across single or multi-GPU compute nodes. The Compute cluster scales up automatically when a job is submitted, and executes in a containerized environment, packaging your model dependencies in a Docker container.

## Pre-requisites

All you need to get started is an Azure machine learning workspace and development environment must be installed with [Python SDK v2](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-ml-readme?view=azure-python)or [Azure CLI v2](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli?tabs=public). You could install Azure Machine Learning on your local computer but is recommended to use Azure's compute instance that is fully configured with all necessary packages and tools.

### Instantiate workspace

If using the Python SDK, connect to your workspace either by explicitly providing the workspace details or load from `config.json` file.
Make sure to replace `subscription_id`,`resource_group`, and `workspace_name` with your own.

```console
# Get a handle to the workspace
ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id="<SUBSCRIPTION_ID>",
    resource_group_name="<RESOURCE_GROUP>",
    workspace_name="<AML_WORKSPACE_NAME>",
)

# or load details from config file
ml_client = MLClient.from_config(credential=DefaultAzureCredential(),
                                path="path_to_config_file",
                                )
```

### Create AMLCompute

You will need to create a compute target using Azure ML managed compute (AmlCompute) for remote training. Note: Be sure to check limits within your available region. This [article](link) includes details on the default limits and how to request more quota.

`size`: The VM family of the nodes, specify compute targets from one of `NC_v2`, `NC_v3`, `ND` or `ND_v2` GPU virtual machines in Azure (e.g `Standard_NC12s_v3`)

`max_instances`: The max number of nodes to autoscale up to when you run a job

```{note}
You may choose to use low-priority VMs to run your workloads. These VMs don't have guaranteed availability but allow you to take advantage of Azure's unused capacity at a significant cost savings. The amount of available capacity can vary based on size, region, time of day, and more.
```

```console
gpu_compute = AmlCompute(
    name="gpu-cluster",
    type="amlcompute",
    size="STANDARD_NC12S_V3",
    max_instances=2,
    idle_time_before_scale_down=300,
    tier="low_priority", # optional
)
ml_client.begin_create_or_update(gpu_compute).result()
```

### Upload data to Datastore

### Custom RAPIDS Environment

Instead of using a prebuilt image, you can define an environment from a Docker build context. Simply specify the directory that will serve as the build context. which should contain a Dockerfile (less than 1MB in size) and any other necessary files.

```console
from azure.ai.ml.entities import Environment, BuildContext

env_docker_image = Environment(
    build=BuildContext(path="Dockerfile_path"),
    name="rapids-docker-image",
    description="Rapids training Environment")

ml_client.environments.create_or_update(env_docker_image)
```

### Run Example Notebook

Now that we have our environment and custom logic, we can configure and run `command` to submit hyperparameter optimization tuning jobs.
Navigate to the [source/examples/rapids-azureml-hpo/notebook.ipynb](/examples/rapids-azureml-hpo/notebook) notebook for detailed instructions on how to do so.
