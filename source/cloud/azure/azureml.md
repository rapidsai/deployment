---
review_priority: "p0"
---

# Azure Machine Learning

RAPIDS can be deployed at scale using [Azure Machine Learning Service](https://learn.microsoft.com/en-us/azure/machine-learning/overview-what-is-azure-machine-learning) and can be scaled up to any size needed.

## Pre-requisites

Use existing or create new Azure Machine Learning workspace through the [Azure portal](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-workspace?tabs=azure-portal#create-a-workspace), [Azure ML Python SDK](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-workspace?tabs=python#create-a-workspace), [Azure CLI](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-workspace-cli?tabs=createnewresources) or [Azure Resource Manager templates](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-workspace-template?tabs=azcli).

Follow these high-level steps to get started:

**1. Create.** Create your Azure Resource Group.

**2. Workspace.** Within the Resource Group, create an Azure Machine Learning service Workspace.

**3. Quota.** Check your Usage + Quota to ensure you have enough quota within your region to launch your desired cluster size.

## Azure ML Compute instance

Although it is possible to install Azure Machine Learning on your local computer, it is recommended to utilize [Azure's ML Compute instances](https://learn.microsoft.com/en-us/azure/machine-learning/concept-compute-instance), fully managed and secure development environments that can also serve as a [compute target](https://learn.microsoft.com/en-us/azure/machine-learning/concept-compute-target?view=azureml-api-2) for ML training.

The compute instance provides an integrated Jupyter notebook service, JupyterLab, Azure ML Python SDK, CLI, and other essential tools.

### Select your instance

Sign in to [Azure Machine Learning Studio](https://ml.azure.com/) and navigate to your workspace on the left-side menu.

Select **New** > **Compute instance** (Create compute instance) > choose a [RAPIDS compatible GPU](https://docs.rapids.ai/install/#system-req) VM size (e.g., `Standard_NC12s_v3`)

![Screenshot of create new notebook with a gpu-instance](../../images/azureml-create-notebook-instance.png)

### Provision RAPIDS setup script

Navigate to the **Applications** section.
Choose "Provision with a creation script" to install RAPIDS and dependencies.

Put the following in a local file called `rapids-azure-startup.sh`:

```bash
#!/bin/bash

sudo -u azureuser -i <<'EOF'
source /anaconda/etc/profile.d/conda.sh
conda create -y -n rapids \
    {{ rapids_conda_channels }} \
    -c microsoft \
    {{ rapids_conda_packages }} \
    'azure-ai-ml>=2024.12' \
    'azure-identity>=24.12' \
    ipykernel

conda activate rapids

python -m ipykernel install --user --name rapids
echo "kernel install completed"
EOF
```

Select `local file`, then `Browse`, and upload that script.

![Screenshot of the provision setup script screen](../../images/azureml-provision-setup-script.png)

Refer to [Azure ML documentation](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-customize-compute-instance) for more details on how to create the setup script.

Launch the instance.

### Select the RAPIDS environment

Once your Notebook Instance is `Running`, open "JupyterLab" and select the `rapids` kernel when working with a new notebook.

## Azure ML Compute cluster

Launch Azure's [ML Compute cluster](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-attach-compute-cluster?tabs=python) to distribute your RAPIDS training jobs across a cluster of single or multi-GPU compute nodes.

The Compute cluster scales up automatically when a job is submitted, and executes in a containerized environment, packaging your model dependencies in a Docker container.

### Instantiate workspace

Use Azure's client libraries to set up some resources.

```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

# Get a handle to the workspace.
#
# Azure ML places the workspace config at the default working
# directory for notebooks by default.
#
# If it isn't found, open a shell and look in the
# directory indicated by 'echo ${JUPYTER_SERVER_ROOT}'.
ml_client = MLClient.from_config(
    credential=DefaultAzureCredential(),
    path="./config.json",
)
```

### Create AMLCompute

You will need to create a [compute target](https://learn.microsoft.com/en-us/azure/machine-learning/concept-compute-target?view=azureml-api-2#azure-machine-learning-compute-managed) using Azure ML managed compute ([AmlCompute](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-ml/0.1.0b4/azure.ai.ml.entities.html)) for remote training.

Note: Be sure to check limits within your available region.

This [article](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-quotas?view=azureml-api-2#azure-machine-learning-compute) includes details on the default limits and how to request more quota.

[**size**]: The VM family of the nodes.
Specify from one of **NC_v2**, **NC_v3**, **ND** or **ND_v2** GPU virtual machines (e.g `Standard_NC12s_v3`)

[**max_instances**]: The max number of nodes to autoscale up to when you run a job

```{note}
You may choose to use low-priority VMs to run your workloads. These VMs don't have guaranteed availability but allow you to take advantage of Azure's unused capacity at a significant cost savings. The amount of available capacity can vary based on size, region, time of day, and more.
```

```python
from azure.ai.ml.entities import AmlCompute

gpu_compute = AmlCompute(
    name="rapids-cluster",
    type="amlcompute",
    size="Standard_NC12s_v3",
    max_instances=3,
    idle_time_before_scale_down=300,  # Seconds of idle time before scaling down
    tier="low_priority",  # optional
)
ml_client.begin_create_or_update(gpu_compute).result()
```

### Access Datastore URI

A [datastore URI](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-access-data-interactive?tabs=adls&view=azureml-api-2#access-data-from-a-datastore-uri-like-a-filesystem-preview) is a reference to a blob storage location (path) on your Azure account. You can copy-and-paste the datastore URI from the AzureML Studio UI:

1. Select **Data** from the left-hand menu > **Datastores** > choose your datastore name > **Browse**
2. Find the file/folder containing your dataset and click the ellipsis (...) next to it.
3. From the menu, choose **Copy URI** and select **Datastore URI** format to copy into your notebook.

![Screenshot of access datastore uri screen](../../images/azureml-access-datastore-uri.png)

### Custom RAPIDS Environment

To run an AzureML experiment, you must specify an [environment](https://learn.microsoft.com/en-us/azure/machine-learning/concept-environments?view=azureml-api-2) that contains all the necessary software dependencies to run the training script on distributed nodes. <br>
You can define an environment from a [pre-built](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-environments-v2?tabs=python&view=azureml-api-2#create-an-environment-from-a-docker-image) docker image or create-your-own from a [Dockerfile](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-environments-v2?tabs=python&view=azureml-api-2#create-an-environment-from-a-docker-build-context) or [conda](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-environments-v2?tabs=python&view=azureml-api-2#create-an-environment-from-a-conda-specification) specification file.

Create your custom RAPIDS docker image using the example below, making sure to install additional packages needed for your workflows.

```dockerfile
# Use latest rapids image with the necessary dependencies
FROM {{ rapids_container }}

RUN conda install --yes -c conda-forge 'dask-ml>=2024.4.4' \
 && pip install azureml-mlflow
```

Now create the Environment, making sure to label and provide a description:

```python
from azure.ai.ml.entities import Environment, BuildContext

# NOTE: 'path' should be a filepath pointing to a directory containing a file named 'Dockerfile'
env_docker_image = Environment(
    build=BuildContext(path="./training-code/"),
    name="rapids-mlflow",
    description="RAPIDS environment with azureml-mlflow",
)

ml_client.environments.create_or_update(env_docker_image)
```

### Submit RAPIDS Training jobs

Now that we have our environment and custom logic, we can configure and run the `command` [class](https://learn.microsoft.com/en-us/python/api/azure-ai-ml/azure.ai.ml?view=azure-python#azure-ai-ml-command) to submit training jobs.

In a notebook cell, copy the example code from this documentation into a new folder.

```ipython
%%bash
mkdir -p ./training-code
repo_url='https://raw.githubusercontent.com/rapidsai/deployment/refs/heads/main/source/examples'

# download training scripts
wget -O ./training-code/train_rapids.py "${repo_url}/rapids-azureml-hpo/train_rapids.py"
wget -O ./training-code/rapids_csp_azure.py "${repo_url}/rapids-azureml-hpo/rapids_csp_azure.py"
touch ./training-code/__init__.py

# create a Dockerfile defining the image the code will run in
cat > ./training-code/Dockerfile <<EOF
FROM {{ rapids_container }}

RUN conda install --yes -c conda-forge 'dask-ml>=2024.4.4' \
 && pip install azureml-mlflow
EOF
```

`inputs` is a dictionary of command-line arguments to pass to the training script.

```python
from azure.ai.ml import command, Input

# replace this with your own dataset
datastore_name = "workspaceartifactstore"
dataset = "airline_20000000.parquet"
data_uri = f"azureml://subscriptions/{ml_client.subscription_id}/resourcegroups/{ml_client.resource_group_name}/workspaces/{ml_client.workspace_name}/datastores/{datastore_name}/paths/{dataset}"

command_job = command(
    environment=f"{env_docker_image.name}:{env_docker_image.version}",
    experiment_name="test_rapids_mlflow",
    code="./training-code",
    command="python train_rapids.py \
                    --data_dir ${{inputs.data_dir}} \
                    --n_bins ${{inputs.n_bins}} \
                    --cv_folds ${{inputs.cv_folds}} \
                    --n_estimators ${{inputs.n_estimators}} \
                    --max_depth ${{inputs.max_depth}} \
                    --max_features ${{inputs.max_features}}",
    inputs={
        "data_dir": Input(type="uri_file", path=data_uri),
        "n_bins": 32,
        "cv_folds": 5,
        "n_estimators": 50,
        "max_depth": 10,
        "max_features": 1.0,
    },
    compute=gpu_compute.name,
)

# submit training job
returned_job = ml_client.jobs.create_or_update(command_job)
```

After creating the job, go to [the "Experiments" page](https://ml.azure.com/experiments) to view logs, metrics, and outputs.

Next, try performing a sweep over a set of hyperparameters.

```python
from azure.ai.ml.sweep import Choice, Uniform

# define hyperparameter space to sweep over
command_job_for_sweep = command_job(
    n_estimators=Choice(values=range(50, 500)),
    max_depth=Choice(values=range(5, 19)),
    max_features=Uniform(min_value=0.2, max_value=1.0),
)

# apply hyperparameter sweep_job
sweep_job = command_job_for_sweep.sweep(
    compute=gpu_compute.name,
    sampling_algorithm="random",
    primary_metric="Accuracy",
    goal="Maximize",
)

# submit job
returned_sweep_job = ml_client.create_or_update(sweep_job)
```

### Clean Up

When you're done, remove the compute resources.

```python
ml_client.compute.begin_delete(gpu_compute.name).wait()
```

```{relatedexamples}

```
