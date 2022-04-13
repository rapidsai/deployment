# RAPIDS Deployment Documentation

## Building

As a prerequisite, a RAPIDS compatible GPU is required to build the docs since the notebooks in the docs execute the code to generate the HTML output.

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


## Developing

When developing docs locally it can be nice to view them in your browser and have changes
reflected immediately. You can do this with [sphinx-autobuild](https://github.com/executablebooks/sphinx-autobuild). This tool will build your
docs as above but will also host them on a local web server. It will watch for file changes,
rebuild automatically and tell the browser page to reload. Magic!

```bash
$ sphinx-autobuild source build/html
[sphinx-autobuild] > sphinx-build ./source ./build/html
Running Sphinx v4.5.0
...
build succeeded.

The HTML pages are in build.
[I 220413 12:13:40 server:335] Serving on http://127.0.0.1:8000
```

