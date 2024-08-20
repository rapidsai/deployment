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

# Single modifiable version for all of the docs - easier for future updates
stable_version = "24.08"
nightly_version = "24.10"

versions = {
    "stable": {
        "rapids_version": stable_version,
        "rapids_api_docs_version": "stable",
        "rapids_container": f"nvcr.io/nvidia/rapidsai/base:{stable_version}-cuda12.5-py3.11",
        "rapids_notebooks_container": f"nvcr.io/nvidia/rapidsai/notebooks:{stable_version}-cuda12.5-py3.11",
        "rapids_conda_channels": "-c rapidsai -c conda-forge -c nvidia",
        "rapids_conda_packages": f"rapids={stable_version} python=3.11 cuda-version=12.5",
    },
    "nightly": {
        "rapids_version": f"{nightly_version}-nightly",
        "rapids_api_docs_version": "nightly",
        "rapids_container": f"rapidsai/base:{nightly_version + 'a'}-cuda12.5-py3.11",
        "rapids_notebooks_container": f"rapidsai/notebooks:{nightly_version + 'a'}-cuda12.5-py3.11",
        "rapids_conda_channels": "-c rapidsai-nightly -c conda-forge -c nvidia",
        "rapids_conda_packages": f"rapids={nightly_version} python=3.11 cuda-version=12.5",
    },
}
rapids_version = (
    versions["stable"]
    if os.environ.get("DEPLOYMENT_DOCS_BUILD_STABLE", "false") == "true"
    else versions["nightly"]
)
rapids_version["rapids_conda_channels_list"] = [
    channel
    for channel in rapids_version["rapids_conda_channels"].split(" ")
    if channel != "-c"
]
rapids_version["rapids_conda_packages_list"] = rapids_version[
    "rapids_conda_packages"
].split(" ")

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
sys.path.insert(0, os.path.abspath("../extensions"))
extensions = [
    "IPython.sphinxext.ipython_console_highlighting",
    "sphinx.ext.intersphinx",
    "myst_nb",
    "sphinxcontrib.mermaid",
    "sphinx_design",
    "sphinx_copybutton",
    "rapids_notebook_files",
    "rapids_related_examples",
    "rapids_grid_toctree",
    "rapids_version_templating",
    "rapids_admonitions",
]

myst_enable_extensions = ["colon_fence", "dollarmath"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

suppress_warnings = ["myst.header", "myst.nested_header"]

# -- Options for notebooks -------------------------------------------------

nb_execution_mode = "off"
rapids_deployment_notebooks_base_url = (
    "https://github.com/rapidsai/deployment/blob/main/source/"
)

# -- Options for HTML output -------------------------------------------------

html_theme_options = {
    "header_links_before_dropdown": 7,
    # https://github.com/pydata/pydata-sphinx-theme/issues/1220
    "icon_links": [],
    "logo": {
        "link": "https://docs.rapids.ai/",
    },
    "github_url": "https://github.com/rapidsai/",
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
