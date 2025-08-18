---
review_priority: "index"
html_theme.sidebar_secondary.remove: true
---

# Local

Choose your preferred installation method for running RAPIDS

`````{gridtoctree} 1 2 2 2
:gutter: 2 2 2 2

````{grid-item-card}
:link: https://docs.rapids.ai/install#conda
:link-type: url
{fas}`box;sd-text-primary` Conda
^^^
Install RAPIDS using conda
````

````{grid-item-card}
:link: custom-docker
:link-type: doc
{fas}`container;sd-text-primary` Docker
^^^
Install RAPIDS using Docker
````

````{grid-item-card}
:link: https://docs.rapids.ai/install#pip
:link-type: url
{fas}`python;sd-text-primary` pip
^^^
Install RAPIDS using pip
````

````{grid-item-card}
:link: https://docs.rapids.ai/install#wsl2
:link-type: url
{fas}`windows;sd-text-primary` WSL2
^^^
Install RAPIDS on Windows using Windows Subsystem for Linux version 2 (WSL2)
````

`````

:::{toctree}
:hidden:
:maxdepth: 1

custom-docker.md
:::
