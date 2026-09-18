# Xarray example debugging

Get data

```bash
wget "https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/surface/air.sig995.2025.nc"
```

and

```bash
wget https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.derived/surface/air.sig995.4Xday.1981-2010.ltm.nc
```

- More of a real example in notebook
- scripts are adapted to look at performance
- run on brev
  - install env,
  - update kernel
  - install nvdashboard
  - think of numpy version in a notebook. convert to script with nbconvert.

One of the things we can do is look at nv dashboard

For conda, look st this common setup <https://docs.rapids.ai/deployment/nightly/examples/cuml-ray-hpo/notebook/#environment-setup>

On brev

```bash
uv pip install jupyterlab_nvdashboard

sudo systemctl restart jupyter.service
```

Install conda

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"

bash Miniforge3-$(uname)-$(uname -m).sh  # Follow the prompts and choose yes to update your shell profile to automatically initialize conda
```

```bash
source ~/.bashrc

```
