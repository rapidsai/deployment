# Azure ML Cluster

You can use Azure Machine Learning compute cluster to distribute a training or inference jobs across a cluster of Azure-managed GPU compute nodes.

All you’ll need to do is copy your RAPIDS training script and libraries as a Docker container image and ask

## AzureML Studio

### Instantiate workspace

Use config.file to initate your Machine learning workspace

```console
from azureml.core import Workspace
ws = Workspace.from_config()
```

### Create AML Compute

You will need to create a compute target using Azure ML managed compute (AmlCompute) for remote training.

Note: Be sure to check limits within your available region. This article includes details on the default limits and how to request more quota.

The steps used Azure CLI to set up , but you can also python SDK or portal

vm_size describes the virtual machine type and size that will be used in the cluster. RAPIDS requires NVIDIA Pascal or newer architecture, you will need to specify compute targets from one of NC_v2, NC_v3, ND or ND_v2 GPU virtual machines in Azure; these are VMs that are provisioned with P40 and V100 GPUs. Let's create an AmlCompute cluster of Standard_NC6s_v3 GPU VMs:

```console
from azureml.core.compute import AmlCompute

provisioning_config = AmlCompute.provisioning_configuration(
                                vm_size = 'Standard_NC12s_v3', # Use VM with more than one GPU for multi-GPU option
                                max_nodes = 5,
                                idle_seconds_before_scaledown = 300
                                )

# Create the cluster
    gpu_cluster = ComputeTarget.create(ws, gpu_cluster_name, provisioning_config)
```

### Setup Environment

Use RAPIDS docker image from DockerHub to set the environment in these quick steps:

```console
from azureml.core import Environment
from azureml.core.runconfig import DockerConfiguration

environment_name = 'rapids_hpo'
env = Environment(environment_name)

docker_config = DockerConfiguration(use_docker=True) # enable docker
env.docker.base_image = 'rapidsai/rapidsai-cloud-ml:latest' # pull latest rapids image

```

Having built our environment and custom logic, we can now assemble all components into an `ScriptRunConfig` class to submit
hyperparameter optimization tuning jobs. Estimators have been deprecated in Azure

```console
src = ScriptRunConfig(source_directory,
                      arguments,
                      compute_target,
                      script,
                      environment,
                      docker_runtime_config)

hyperdrive_run_config = HyperDriveConfig(run_config,
                                         hyperparameter_sampling,
                                         primary_metric_name,
                                         primary_metric_goal=PrimaryMetricGoal.MAXIMIZE,
                                         max_total_runs,
                                         max_concurrent_runs)
```
