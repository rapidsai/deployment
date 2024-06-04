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
- EC2 instance type: must support RAPIDS-compatible GPUs ([see the RAPIDS docs](https://docs.rapids.ai/install#system-req))
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
    cluster_arn= "<cluster arn>",
    n_workers=<num_workers>,
    worker_gpu=<num_gpus>,
    skip_cleaup=True,
    scheduler_timeout="20 minutes",
)
```

````{note}
When you call this command for the first time, `ECSCluster()` will automatically create a **security group** with the same name as the ECS cluster you created above..

However, if the Dask cluster creation fails or you'd like to reuse the same ECS cluster for subsequent runs of `ECSCluster()`, then you will need to provide this security group value.

```shell
security_groups=["sg-0fde781be42651"]

````

[**cluster_arn**] = ARN of an existing ECS cluster to use for launching tasks <br />

[**num_workers**] = number of workers to start on cluster creation <br />

[**num_gpus**] = number of GPUs to expose to the worker, this must be less than or equal to the number of GPUs in the instance type you selected for the ECS cluster (e.g `1` for `p3.2xlarge`).<br />

[**skip_cleanup**] = if True, Dask workers won't be automatically terminated when cluster is shut down <br />

[**execution_role_arn**] = ARN of the IAM role that allows the Dask cluster to create and manage ECS resources <br />

[**task_role_arn**] = ARN of the IAM role that the Dask workers assume when they run <br />

[**scheduler_timeout**] = maximum time scheduler will wait for workers to connect to the cluster

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

You can scale down or delete the Dask cluster, but the ECS cluster will continue to run (and incur charges!) until you also scale it down or shut down altogether. <br />

If you are planning to use the ECS cluster again soon, it is probably preferable to reduce the nodes to zero.

```{relatedexamples}

```
