---
html_theme.sidebar_secondary.remove: true
---

# Guides

`````{grid} 1 2 2 3
:gutter: 2 2 2 2

````{grid-item-card}
:link: mig
:link-type: doc
Multi-Instance GPUs
^^^
Use RAPIDS with Multi-Instance GPUs

{bdg-primary}`Dask Cluster`
{bdg-primary}`XGBoost with Dask Cluster`
````

````{grid-item-card}
:link: azure/infiniband
:link-type: doc
Infiniband on Azure
^^^
How to setup InfiniBand on Azure.

{bdg-primary}`Microsoft Azure`
````

````{grid-item-card}
:link: scheduler-gpu-requirements
:link-type: doc
Does the Dask scheduler need a GPU?
^^^
Guidance on Dask scheduler software and hardware requirements.

{bdg-primary}`Dask`
````

`````

```{toctree}
:maxdepth: 2
:caption: Guides
:hidden:

mig
azure/infiniband
scheduler-gpu-requirements
```
