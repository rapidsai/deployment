# Azure ML Cluster

Launch Azure Machine Learning compute cluster to distribute your RAPIDS training or inference jobs across single or multi-GPU compute nodes. The Compute cluster scales up automatically when a job is submitted, executes in a containerized environment and packages your model dependencies in a Docker container.

## Pre-requisites

All you need to get started is an Azure machine learning workspace and development environment:

- [Python SDK v2 for Azure Machine Learning](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-ml-readme?view=azure-python)
- [Azure CLI extension for machine learning (v2)](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli?tabs=public)

### Instantiate workspace

If using the Python SDK, connect to your workspace using details from your config file. Make sure to replace `subscription_id`,`resource_group`, and `workspace_name` with your own.

```console

# Enter details of your AML workspace
subscription_id = '<SUBSCRIPTION_ID>'
resource_group = '<RESOURCE_GROUP>'
workspace = '<AZUREML_WORKSPACE_NAME>'

# connect to the workspace
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    DefaultAzureCredential(), subscription_id, resource_group, workspace
)
```

### Create AMLCompute

You will need to create a compute target using Azure ML managed compute (AmlCompute) for remote training. Note: Be sure to check limits within your available region. This article includes details on the default limits and how to request more quota.

`size`: The VM family of the nodes, specify compute targets from one of NC_v2, NC_v3, ND or ND_v2 GPU virtual machines in Azure (e.g `Standard_NC12s_v3`)

`max_instances`: The max number of nodes to autoscale up to when you run a job

NOTE:
You may choose to use low-priority VMs to run your workloads. These VMs don't have guaranteed availability but allow you to take advantage of Azure's unused capacity at a significant cost savings. The amount of available capacity can vary based on size, region, time of day, and more.

````console
from azure.ai.ml.entities import AmlCompute

cluster_low_pri = AmlCompute(
    name="gpu-cluster",
    size="STANDARD_NC6S_V3",
    min_instances=0,
    max_instances=2,
    idle_time_before_scale_down=120,
    tier="low_priority",
)
ml_client.begin_create_or_update(cluster_low_pri).result()


### Setup Environment

Use RAPIDS docker image from DockerHub to set the environment in these quick steps:

```console


````

Having built our environment and custom logic, we can now assemble all components into an `X` class to submit
hyperparameter optimization tuning jobs. Estimators have been deprecated in Azure

```console

```
