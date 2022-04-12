# Building Documentation

As a prerequisite, a RAPIDS compatible GPU is required to build the docs since the notebooks in the docs execute the code to generate the HTML output.

## Steps to follow:

In order to build the docs, we need the conda dev environment from cudf and build cudf from source. See build [instructions](https://github.com/rapidsai/cudf/blob/branch-0.13/CONTRIBUTING.md#setting-up-your-build-environment). 

1. Create a conda env with the dependencies to build the deployment docs from source.

```bash
conda env create -f conda/environments/deployment_docs_cuda11.5.yml
```

2. Once the conda environment is built, run the following


```bash
make html
```

This should run Sphinx in your shell, and outputs to `build/html/index.html`.


## View docs web page by opening HTML in browser:

```bash
open built/html/index.html
```

or

Navigate to `/build/html/` folder, i.e., `cd build/html` and then run the following command:

```bash
python -m http.server
```
Then, navigate a web browser to the IP address or hostname of the host machine at port 8000:

```
https://<host IP-Address>:8000
```
Now you can check if your docs edits formatted correctly, and read well.