---
review_priority: "index"
html_theme.sidebar_secondary.remove: true
---

# Guides

`````{gridtoctree} 1 2 2 3
:gutter: 2 2 2 2

````{grid-item-card}
:link: mig
:link-type: doc
Multi-Instance GPUs
^^^
Use RAPIDS with Multi-Instance GPUs

{bdg}`Dask Cluster`
{bdg}`XGBoost with Dask Cluster`
````

````{grid-item-card}
:link: rapids-docker-with-cuda
:link-type: doc
Building RAPIDS Containers from a custom base image
^^^
Add RAPIDS and CUDA to your existing Docker images

{bdg-primary}`Docker`
{bdg-primary}`CUDA`
````

````{grid-item-card}
:link: azure/infiniband
:link-type: doc
Infiniband on Azure
^^^
How to setup InfiniBand on Azure.

{bdg}`Microsoft Azure`
````

````{grid-item-card}
:link: scheduler-gpu-requirements
:link-type: doc
Does the Dask scheduler need a GPU?
^^^
Guidance on Dask scheduler software and hardware requirements.

{bdg-primary}`Dask`
````

````{grid-item-card}
:link: scheduler-gpu-optimization
:link-type: doc
Optimizing the Dask Scheduler on Kubernetes
^^^
Use a T4 for the scheduler to optimize resource costs on Kubernetes

{bdg-primary}`Dask`
{bdg-primary}`Kubernetes`
{bdg-primary}`dask-operator`
````

````{grid-item-card}
:link: colocate-workers
:link-type: doc
Colocate worker pods on Kubernetes
^^^
Use Pod affinity for the workers to optimize communication overhead on Kubernetes

{bdg-primary}`Dask`
{bdg-primary}`Kubernetes`
{bdg-primary}`dask-operator`
````

````{grid-item-card}
:link: caching-docker-images
:link-type: doc
Caching Docker Images for autoscaling workloads
^^^
Prepull Docker Images while using the Dask Autoscaler on Kubernetes

{bdg-primary}`Dask`
{bdg-primary}`Kubernetes`
{bdg-primary}`dask-operator`
````

````{grid-item-card}
:link: deploy-dask-spark
:link-type: doc
How do Dask and Spark relate to deploying RAPIDS?
^^^
Why does deploying RAPIDS often mean deploying a distributed framework?

{bdg-primary}`Dask`
{bdg-primary}`Spark`
````

`````
