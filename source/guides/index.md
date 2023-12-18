---
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
:link: l4-gcp
:link-type: doc
L4 on Google Cloud Platform
^^^
How to setup a VM instance on GCP with an L4 GPU.

{bdg-primary}`Google Cloud Platform`
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
