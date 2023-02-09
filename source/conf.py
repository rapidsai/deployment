# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import datetime
import os
import sys

# -- Project information -----------------------------------------------------

project = "RAPIDS Deployment Documentation"
copyright = f"{datetime.date.today().year}, NVIDIA"
author = "NVIDIA"

versions = {
    "stable": {
        "rapids_container": "rapidsai/rapidsai-core:22.12-cuda11.5-runtime-ubuntu20.04-py3.9",
        "rapids_conda_channels": "-c rapidsai -c conda-forge -c nvidia",
        "rapids_conda_packages": "rapids=22.12 python=3.9 cudatoolkit=11.5",
    },
    "nightly": {
        "rapids_container": "rapidsai/rapidsai-core-nightly:23.02-cuda11.5-runtime-ubuntu20.04-py3.9",
        "rapids_conda_channels": "-c rapidsai-nightly -c conda-forge -c nvidia",
        "rapids_conda_packages": "rapids=23.02 python=3.9 cudatoolkit=11.5",
    },
}
rapids_version = (
    versions["stable"]
    if os.environ.get("DEPLOYMENT_DOCS_BUILD_STABLE", "false") == "true"
    else versions["nightly"]
)

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
sys.path.insert(0, os.path.abspath("../extensions"))
extensions = [
    "sphinx.ext.intersphinx",
    "myst_nb",
    "sphinxcontrib.mermaid",
    "sphinx_design",
    "sphinx_copybutton",
    "rapids_notebook_files",
    "rapids_related_examples",
    "rapids_grid_toctree",
    "rapids_version_templating",
]

myst_enable_extensions = ["colon_fence"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for notebooks -------------------------------------------------

nb_execution_mode = "off"
rapids_deployment_notebooks_base_url = (
    "https://github.com/rapidsai/deployment/blob/main/source/"
)

# -- Options for HTML output -------------------------------------------------

html_theme_options = {
    "external_links": [],
    "github_url": "https://github.com/rapidsai/deployment",
    "twitter_url": "https://twitter.com/rapidsai",
    "show_toc_level": 1,
    "navbar_align": "right",
    "secondary_sidebar_items": [
        "page-toc",
        "notebooks-extra-files-nav",
        "notebooks-tags",
    ],
}

html_sidebars = {
    "**": ["sidebar-nav-bs", "sidebar-ethical-ads"],
    "index": [],
    "examples/index": ["notebooks-tag-filter", "sidebar-ethical-ads"],
}

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_logo = "_static/RAPIDS-logo-purple.png"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "dask": ("https://docs.dask.org/en/latest/", None),
    "distributed": ("https://distributed.dask.org/en/latest/", None),
    "dask_kubernetes": ("https://kubernetes.dask.org/en/latest/", None),
    "dask_cuda": ("https://docs.rapids.ai/api/dask-cuda/stable/", None),
}


def setup(app):
    app.add_css_file("https://docs.rapids.ai/assets/css/custom.css")
    app.add_css_file("css/custom.css")
    app.add_js_file(
        "https://docs.rapids.ai/assets/js/custom.js", loading_method="defer"
    )
    app.add_js_file("js/nav.js", loading_method="defer")
    app.add_js_file("js/notebook-gallery.js", loading_method="defer")
