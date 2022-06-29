# Cloud Service Providers

## Amazon Web Services (AWS)
RAPIDS can be deployed on Amazon Web Services (AWS) in several ways. See the
list of accelerated instance types below:

| Cloud <br> Provider | Inst. <br> Type | Inst. <br> Name  | GPU <br> Count | GPU <br> Type | xGPU <br> RAM | xGPU <br> RAM Total |
| :------------------ | --------------- | ---------------- | -------------- | ------------- | ------------- | ------------------: |
| AWS                 | G4dn            | g4dn\.xlarge     | 1              | T4            | 16 (GB)       | 16 (GB)             |
| AWS                 | G4dn            | g4dn\.12xlarge   | 4              | T4            | 16 (GB)       | 64 (GB)             |
| AWS                 | G4dn            | g4dn\.metal      | 8              | T4            | 16 (GB)       | 128 (GB)            |
| AWS                 | P3              | p3\.2xlarge      | 1              | V100          | 16 (GB)       | 16 (GB)             |
| AWS                 | P3              | p3\.8xlarge      | 4              | V100          | 16 (GB)       | 64 (GB)             |
| AWS                 | P3              | p3\.16xlarge     | 8              | V100          | 16 (GB)       | 128 (GB)            |
| AWS                 | P3              | p3dn\.24xlarge   | 8              | V100          | 32 (GB)       | 256 (GB)            |
| AWS                 | P4              | p4d\.24xlarge    | 8              | A100          | 40 (GB)       | 320 (GB)            |
| AWS                 | G5              | g5\.xlarge       | 1              | A10G          | 24 (GB)       | 24 (GB)             |
| AWS                 | G5              | g5\.2xlarge      | 1              | A10G          | 24 (GB)       | 24 (GB)             |
| AWS                 | G5              | g5\.4xlarge      | 1              | A10G          | 24 (GB)       | 24 (GB)             |
| AWS                 | G5              | g5\.8xlarge      | 1              | A10G          | 24 (GB)       | 24 (GB)             |
| AWS                 | G5              | g5\.16xlarge     | 1              | A10G          | 24 (GB)       | 24 (GB)             |
| AWS                 | G5              | g5\.12xlarge     | 4              | A10G          | 24 (GB)       | 96 (GB)             |
| AWS                 | G5              | g5\.24xlarge     | 4              | A10G          | 24 (GB)       | 96 (GB)             |
| AWS                 | G5              | g5\.48xlarge     | 8              | A10G          | 24 (GB)       | 192 (GB)            |

### AWS Single Instance (EC2)

There are multiple ways you can deploy RAPIDS on a single instance, but the easiest is to use the RAPIDS docker image:

**1. Initiate.** Initiate an instance supported by RAPIDS. See the introduction
section for a list of supported instance types. It is recommended to use an AMI
that already includes the required NVIDIA drivers, such as the **[Amazon Linux 2
AMI with NVIDIA TESLA GPU
Driver](https://aws.amazon.com/marketplace/pp/Amazon-Web-Services-Amazon-Linux-2-AMI-with-NVIDIA/B07S5G9S1Z)**
or the **[AWS Deep Learning
AMI.](https://docs.aws.amazon.com/dlami/latest/devguide/what-is-dlami.html)**

**2. Credentials.** Using the credentials supplied by AWS, log into the instance
via SSH. For a short guide on launching your instance and accessing it, read the
Getting Started with Amazon EC2 documentation.

**3. Install.** Install [Docker and the NVIDIA Docker
runtime](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
in the AWS instance. This step is not required if you are using AWS Deep
Learning AMI.

**4. Install.** Install RAPIDS docker image. The docker container can be
customized by using the options provided in the **[Getting
Started](https://rapids.ai/start.html)** page of RAPIDS. Example of an image
that can be used is provided below:

```shell
$ docker pull rapidsai/rapidsai:cuda11.2-runtime-ubuntu18.04
$ docker run --gpus all --rm -it -p 8888:8888 -p 8787:8787 -p 8786:8786 \
    rapidsai/rapidsai:cuda11.2-runtime-ubuntu18.04-py3.7
```

**5. Test RAPIDS.** Test it! The RAPIDS docker image will start a Jupyter
notebook instance automatically. You can log into it by going to the IP address
provided by AWS on port 8888.

### AWS Cluster via Dask

RAPIDS can be deployed on a multi-node ECS cluster using Dask’s
dask-cloudprovider management tools. For more details, see our **[blog post on
deploying on
ECS.](https://medium.com/rapids-ai/getting-started-with-rapids-on-aws-ecs-using-dask-cloud-provider-b1adfdbc9c6e)**

**0. Run from within AWS.** The following steps assume you are running them from
within the same AWS VPC. One way to ensure this is to run through the [AWS
Single Instance (EC2)](#aws-single-instance-ec2) instructions and then run these steps from
there.

**1. Setup AWS credentials.** First, you will need AWS credentials to allow us
to interact with the AWS CLI. If someone else manages your AWS account, you will
need to get these keys from them. You can provide these credentials to
dask-cloudprovider in a number of ways, but the easiest is to setup your local
environment using the AWS command line tools:

```shell
$ pip install awscli
$ aws configure
```

**2. Install dask-cloudprovider.** To install, you will need to run the following:

```shell
$ pip install dask-cloudprovider[aws]
```

**3. Create an EC2 cluster:** In the AWS console, visit the ECS dashboard. From
the “Clusters” section on the left hand side, click “Create Cluster”.

Make sure to select an EC 2 Linux + Networking cluster so that we can specify
our networking options.

Give the cluster a name EX. `rapids-cluster`.

Change the instance type to one that supports RAPIDS-supported GPUs (see
introduction section for list of supported instance types). For this example, we
will use `p3.2xlarge`, each of which comes with one NVIDIA V100 GPU.

In the networking section, select the default VPC and all the subnets available
in that VPC.

All other options can be left at defaults. You can now click “create” and wait
for the cluster creation to complete.

**4. Create a Dask cluster:**

Get the Amazon Resource Name (ARN) for the cluster you just created.

Set `AWS_DEFAULT_REGION` environment variable to your **[default region](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-regions)**:

```shell
$ export AWS_DEFAULT_REGION=[REGION]
```

[REGION] = code fo the region being used.

Create the ECSCluster object in your Python session:

```python
from dask_cloudprovider.aws import ECSCluster
cluster = ECSCluster(cluster_arn=[CLUSTER_ARN],
                     n_workers=[NUM_WORKERS],
                     worker_gpu=[NUM_GPUS]
                     )
```

[CLUSTER_ARN] = The ARN of an existing ECS cluster to use for launching tasks <br />
[NUM_WORKERS] = Number of workers to start on cluster creation. <br />
[NUM_GPUS] = The number of GPUs to expose to the worker, this must be less than or equal to the number of GPUs in the instance type you selected for the ECS cluster (e.g `1` for `p3.2xlarge`).

**5. Test RAPIDS.** Create a distributed client for our cluster:

```python
from dask.distributed import Client
client = Client(cluster)
```

Load sample data and test the cluster!

```python
import dask, cudf, dask_cudf
ddf = dask.datasets.timeseries()
gdf = ddf.map_partitions(cudf.from_pandas)
gdf.groupby('name').id.count().compute().head()
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

**6. Cleanup.** Your cluster will continue to run (and incur charges!) until you
shut it down. You can either scale the number of nodes down to zero instances,
or shut it down altogether. If you are planning to use the cluster again soon,
it is probably preferable to reduce the nodes to zero.

### AWS Cluster via Kubernetes

RAPIDS can be deployed on AWS via AWS’s managed Kubernetes service (EKS) using Helm. More details can be found at our **[helm docs.](https://helm.rapids.ai/docs/csp.html)**

**1. Install.** Install and configure dependencies in your local environment: kubectl, helm, awscli, and eksctl.

**2. Public Key.** Create a public key if you don't have one.

**3. Create your cluster:**

```shell
$ eksctl create cluster \
    --name [CLUSTER_NAME] \
    --version 1.14 \
    --region [REGION] \
    --nodegroup-name gpu-workers \
    --node-type [NODE_INSTANCE] \
    --nodes  [NUM_NODES] \
    --nodes-min 1 \
    --nodes-max [MAX_NODES] \
    --node-volume-size [NODE_SIZE] \
    --ssh-access \
    --ssh-public-key ~/path/to/id_rsa.pub \
    --managed
```
[CLUSTER_NAME] = Name of the EKS cluster. This will be auto generated if not specified. <br>
[NODE_INSTANCE] = Node instance type to be used. Select one of the instance types supported by RAPIDS Refer to the introduction section for a list of supported instance types. <br>
[NUM_NODES] = Number of nodes to be used. <br>
[MAX_NODES] = Maximum size of the nodes. <br>
[NODE_SIZE] = Size of the nodes. <br>

Update the path to the ssh-public-key to point to the folder and file where your public key is saved.

**4. Install GPU addon:**

```shell
$ kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/1.0.0-beta4/nvidia-device-plugin.yml
```

**5. Install RAPIDS helm repo:**

```shell
$ helm repo add rapidsai https://helm.rapids.ai
$ helm repo update
```

**6. Install helm chart:**

```shell
$ helm install --set dask.scheduler.serviceType="LoadBalancer" --set dask.jupyter.serviceType="LoadBalancer" rapidstest rapidsai/rapidsai
```

**7. Accessing your cluster:**

```shell
$ kubectl get svc
NAME                TYPE          CLUSTER-IP      EXTERNAL-IP                                                               PORT(S)                         AGE
kubernetes          ClusterIP     10.100.0.1      <none>                                                                    443/TCP                         12m
rapidsai-jupyter    LoadBalancer  10.100.251.155  a454a9741455544cfa37fc4ac71caa53-868718558.us-east-1.elb.amazonaws.com    80:30633/TCP                    85s
rapidsai-scheduler  LoadBalancer  10.100.11.182   a9c703f1c002f478ea60d9acaf165bab-1146605388.us-east-1.elb.amazonaws.com   8786:30346/TCP,8787:32444/TCP   85s
```

**7. ELB IP address:** **[Convert the DNS address provided above as the
EXTERNAL-IP address to an IPV4
address](https://aws.amazon.com/premiumsupport/knowledge-center/elb-find-load-balancer-IP/)**.
Then use the obtained IPV4 address to visit the rapidsai-jupyter service in your
browser!


**8. Delete the cluster:** List and delete services running in the cluster to release resources

```shell
$ kubectl get svc --all-namespaces
$ kubectl delete svc [SERVICE_NAME]
```
[SERVICE_NAME] = Name of the services which have an EXTERNAL-IP value and are required to be removed to release resources.

Delete the cluster and its associated nodes

```shell
$ eksctl delete cluster --region=[REGION] --name=[CLUSTER_NAME]
```

**9. Uninstall the helm chart:**

```shell
$ helm uninstall rapidstest
```

### AWS Sagemaker

RAPIDS also works with AWS SageMaker. We’ve written a **[detailed
guide](https://medium.com/rapids-ai/running-rapids-experiments-at-scale-using-amazon-sagemaker-d516420f165b)**
with **[examples](https://github.com/rapidsai/cloud-ml-examples/tree/main/aws)**
for how to use Sagemaker with RAPIDS, but the simplest version is:

**1. Start.** Start a Sagemaker hosted Jupyter notebook instance on AWS.

**2. Clone.** **[Clone the example
repository](https://github.com/shashankprasanna/sagemaker-rapids.git)** which
includes all required setup and some example data and code.

**3. Run.** Start running the sagemaker-rapids.ipynb jupyter notebook.

For more details, including on running large-scale HPO jobs on Sagemaker with
RAPIDS, check out the **[detailed
guide](https://medium.com/rapids-ai/running-rapids-experiments-at-scale-using-amazon-sagemaker-d516420f165b)**
and **[examples.](https://github.com/rapidsai/cloud-ml-examples/tree/main/aws)**

## Google Clould Platform (GCP)
### Vertex AI
### Single Instance
### Cluster on Dataproc with Dask CloudProvider
### GKE
## Microsoft Azure
### Azure ML
### Single Instance
### Cluster with Dask CloudProvider
### Azure Kubernetes
