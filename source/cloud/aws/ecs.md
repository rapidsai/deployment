# Elastic Container Service (ECS)

RAPIDS can be deployed on a multi-node ECS cluster using Dask’s dask-cloudprovider management tools. For more details, see our **[blog post on
deploying on ECS.](https://medium.com/rapids-ai/getting-started-with-rapids-on-aws-ecs-using-dask-cloud-provider-b1adfdbc9c6e)**

## Run from within AWS

The following steps assume you are running from within the same AWS VPC. One way to ensure this is to use
[AWS EC2 Single Instance](https://docs.rapids.ai/deployment/stable/cloud/aws/ec2.html) as your development environment.

### Setup AWS credentials

First, you will need AWS credentials to interact with the AWS CLI. If someone else manages your AWS account, you will need to
get these keys from them. <br />

You can provide these credentials to dask-cloudprovider in a number of ways, but the easiest is to setup your
local environment using the AWS command line tools:

```shell
$ pip install awscli
$ aws configure
```

### Install dask-cloudprovider

To install, you will need to run the following:

```shell
$ pip install dask-cloudprovider[aws]
```

## Create an ECS cluster

In the AWS console, visit the ECS dashboard and on the left-hand side, click “Clusters” then **Create Cluster**

Give the cluster a name e.g.`rapids-cluster`

For Networking, select the default VPC and all the subnets available in that VPC

Select "Amazon EC2 instances" for the Infrastructure type and configure your settings:

- Operating system: must be Linux-based architecture
- EC2 instance type: must support RAPIDS-compatible GPUs (Pascal or greater), e.g `p3.2xlarge`
- Desired capacity: number of maximum instances to launch (default maximum 5)
- SSH Key pair

Review your settings then click on the "Create" button and wait for the cluster creation to complete.

## Create a Dask cluster

Get the Amazon Resource Name (ARN) for the cluster you just created.

Set `AWS_REGION` environment variable to your **[default region](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-regions)**, for instance `us-east-1`

```shell
AWS_REGION=[REGION]
```

Create the ECSCluster object in your Python session:

```python
from dask_cloudprovider.aws import ECSCluster

cluster = ECSCluster(
    cluster_arn=[CLUSTER_ARN],
    n_workers=[NUM_WORKERS],
    worker_gpu=[NUM_GPUS],
    skip_cleaup=True,
    execution_role_arn=[EXECUTION_ROLE_ARN],
    task_role_arn=[TASK_ROLE_ARN],
    scheduler_timeout="20 minutes",
)
```

````{note}
When calling this command for the first time, a security group that matches the cluster name will automatically be created. <br />

However, if the cluster creation fails and you want to use the same cluster for subsequent runs of ECSCluster(), you'll need to provide the `security_groups` parameter with the value of the security group, e.g

```shell
security_groups=["sg-0fde781be42651"]

````

[**CLUSTER_ARN**] = The ARN of an existing ECS cluster to use for launching tasks <br />

[**NUM_WORKERS**] = Number of workers to start on cluster creation <br />

[**NUM_GPUS**] = The number of GPUs to expose to the worker, this must be less than or equal to the number of GPUs in the instance type you selected for the ECS cluster (e.g `1` for `p3.2xlarge`).<br />

[**skip_cleanup**] = If True, Dask workers won't be automatically terminated when cluster is shut down <br />

[**EXECUTION_ROLE_ARN**] = The ARN of the IAM role that allows the Dask cluster to create and manage ECS resources <br />

[**TASK_ROLE_ARN**] = The ARN of the IAM role that the Dask workers assume when they run <br />

[**scheduler_timeout**] = The maximum time scheduler will wait for workers to connect to the cluster

## Test RAPIDS

Create a distributed client for our cluster:

```python
from dask.distributed import Client

client = Client(cluster)
```

Load sample data and test the cluster!

```python
import dask, cudf, dask_cudf

ddf = dask.datasets.timeseries()
gdf = ddf.map_partitions(cudf.from_pandas)
gdf.groupby("name").id.count().compute().head()
```

```shell
Out[34]:
Xavier 99495
Oliver 100251
Charlie 99354
Zelda 99709
Alice 100106
Name: id, dtype: int64
```

## Cleanup

Your cluster will continue to run (and incur charges!) until you shut it down. You can either scale down to zero instances, or shut it down altogether. <br />

If you are planning to use the cluster again soon, it is probably preferable to reduce the nodes to zero.

```{relatedexamples}

```
