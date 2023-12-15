# How do Dask and Spark relate to deploying RAPIDS?

Throughout the RAPIDS Deployment Documentation we spend a lot of time actually talking about deploying tools like [Dask](https://www.dask.org/) and [Apache Spark](https://spark.apache.org/). This document aims to answer common questions around _"What does deploying RAPIDS really mean?"_ and _"How do Dask and Spark relate to deploying RAPIDS?"_.

To make things clearer let's start by answering questions like _"Which packages make up RAPIDS?"_ and _"Who is in the RAPIDS community?"_.

## The many projects of RAPIDS

RAPIDS is a collection of software libraries and a community of people who build those libraries, however the scope of RAPIDS can feel a little nebulous. One of the core goals of RAPIDS is to integrate with the existing PyData ecosystem, meet Data Scientists and Data Practitioners where they are today and accelerate their workloads using GPUs with little or no code changes. So the lines between RAPIDS and PyData as a whole get a bit blurry.

For the purpose of this document let's define the **Core RAPIDS** libraries as GPU accelerated Python libraries maintained by the RAPIDS team including [cudf](https://github.com/rapidsai/cudf), [cuml](https://github.com/rapidsai/cuml), [cuspatial](https://github.com/rapidsai/cuspatial), [rmm](https://github.com/rapidsai/rmm), [cugraph](https://github.com/rapidsai/cugraph), [raft](https://github.com/rapidsai/raft), etc.

We can also define the **Extended RAPIDS** libraries as projects that tightly integrate with _Core RAPIDS_ libraries and are commonly used together in a workflow, but have their own broader community. This includes projects like [xgboost](https://xgboost.ai/), [cupy](https://github.com/cupy/cupy), [pytorch](https://pytorch.org/), [bokeh](https://github.com/bokeh/bokeh), [plotly](https://github.com/plotly/plotly.py), etc.

Lastly let's define the **Distributed RAPIDS** libraries as projects which take some or all of the libraries from the _Core and Extended RAPIDS_ suite and enable you to run workflows across many GPUs and many Nodes. These libraries include packages from the Dask ecosystem like [dask-cuda](https://github.com/rapidsai/dask-cuda) and [dask-cudf](https://docs.rapids.ai/api/dask-cudf/stable/) as well as the [RAPIDS Accelerator for Apache Spark](https://www.nvidia.com/en-gb/deep-learning-ai/solutions/data-science/apache-spark-3/).

## Installing vs deploying RAPIDS

Another useful thing to define is the difference between _installing_ and _deploying_ RAPIDS. Generally **installing RAPIDS** refers to using `pip` or `conda` to retrieve the RAPIDS libraries and any other libraries you with to use with them and make them importable from a Python environment.

**Deploying RAPIDS** refers to getting infrastructure, installing libraries, bootstrapping distributed frameworks and running workloads.

## Single-node deployments

When starting out with RAPIDS it's common to install some of the _Core RAPIDS_ libraries on a machine with an NVIDIA GPU and begin using them in your Data Science workflows. For example if you are a [Pandas](https://pandas.pydata.org/) user and you have an NVIDIA GPU in your desktop workstation you may choose to install [cudf.pandas](https://docs.rapids.ai/api/cudf/stable/cudf_pandas/) and benefit from the nearly [150x performance gain it can give you with zero code changes](https://developer.nvidia.com/blog/rapids-cudf-accelerates-pandas-nearly-150x-with-zero-code-changes/).

If you don't have an NVIDIA GPU in your machine you may choose to leverage a service like [Google Colab](../platforms/colab) or a [Databricks Notebooks](../platforms/databricks) to provide you with a Python environment and a GPU, then you can install some RAPIDS libraries and get to work.

In these **single-node deployments** the process of deploying RAPIDS involves creating a notebook session with GPU hardware and installing RAPIDS.

## Multi-node and multi-GPU deployments

As you move to larger datasets you will want to scale out to multiple GPUs and **multi-node deployments**.

These deployments have more moving parts in order to get all of your GPUs to work together, so we need to deploy a _Distributed RAPIDS_ framework before we can run our work. As a result the RAPIDS Deployment Documentation spends a lot of time focused on these distributed frameworks, how to set them up, how to leverage them and how to debug things when they go wrong.

### Apache Spark

[Apache Spark](https://spark.apache.org/) is a popular solution for scaling out your CPU workloads in the Data Science community. To achieve our goal of meeting Data Scientists where they are today NVIDIA has created the [RAPIDS Accelerator for Apache Spark](https://www.nvidia.com/en-gb/deep-learning-ai/solutions/data-science/apache-spark-3/).

Built from low-level components from the _Core RAPIDS_ libraries this accelerator is a plugin for Apache Spark 3 that leverages the acceleration of [cudf](https://github.com/rapidsai/cudf) on NVIDIA GPUs low down in the Spark stack. As a user you don't need to rewrite your Spark code, you add GPUs to your Spark cluster hardware and install the plugin. Then you can continue using the Spark APIs like `pyspark` and [Spark SQL](https://spark.apache.org/sql/).

Deploying a **Spark RAPIDS** cluster is therefore very similar to deploying a regular Spark cluster, you make a few different hardware choices and run some extra installation commands to install the plugin. For example if you use [Google Cloud Dataproc](https://cloud.google.com/dataproc), Google's managed Spark service, [deploying _Spark RAPIDS_ on Dataproc](https://docs.nvidia.com/spark-rapids/user-guide/latest/getting-started/google-cloud-dataproc.html#create-a-dataproc-cluster-using-t4s) is still done with the `gcloud dataproc clusters create` command with a few extra configuration options.

### Dask

Another popular choice for distributing PyData workloads is [Dask](https://www.dask.org/). Dask provides distributed PyData APIs including `dask.dataframe` and `dask.array` which use `pandas` and `numpy` under the hood and mimic their APIs. This makes Dask a quick addition for people already familiar with the PyData library ecosystem.

To execute these parallel APIs Dask provides a lightweight cluster framework called `dask.distributed` which can run on a single machine to leverage all of the resources in the machine, or on a large compute cluster to unify many nodes into one compute resource.

Because Dask uses PyData libraries internally and RAPIDS integrates with existing PyData libraries it is easy to compose the two things together and use Dask to distributed over GPU accelerated code. Projects from the _Extended RAPIDS_ ecosystem also include Dask support, for example [XGBoost has an `xgboost.dask` package](https://xgboost.readthedocs.io/en/stable/tutorials/dask.html) for distributing training over a Dask cluster.

Also due to it's lightweight nature Dask has a goal to be able to deploy a Dask cluster anywhere. This could be on a laptop or workstation, on a generic distributed compute platform like [Kubernetes](../platforms/kubernetes) or [SLURM](../hpc) or even on other managed services like [Google Cloud Dataproc](../cloud/gcp/dataproc) or [Databricks](../platforms/databricks) running alongside Spark on the same hardware.

Deploying a **Dask RAPIDS** cluster therefore involves deploying a Dask cluster with additional RAPIDS libraries installed.

## Which platform or framework should I choose?

One of the best things about the PyData and broader open-source Python Data Science ecosystem is that there are many different libraries that you can choose from and many compute environments you can run them on, and if you can't quite find a stack that meets your requirements you can build new components yourself while continuing to leverage others from the community.

It's also very common for Data Scientists to find themselves working in organizations that already have a low-friction path to getting things done which includes many historical choices about which libraries to use.

Our goal in RAPIDS is to empower all Data Scientists to accelerate their workloads with NVIDIA GPUs regardless of which stack you choose. This does give us the challenge of providing and maintaining tools and documentation for every different possible combination of tools out there. As you read through our documentation and look at our tools you will see a reflection of software stacks and compute environments that we hear about our users commonly choosing.

So the best way to influence which frameworks and platforms we document and build tools for is to [tell us](https://github.com/rapidsai/deployment/issues/new) what you're using and what problems you're trying to accelerate.
