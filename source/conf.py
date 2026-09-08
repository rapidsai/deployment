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

project = "NVIDIA RAPIDS Deployment Documentation"
html_title = "RAPIDS Deployment Documentation"
copyright = f"{datetime.date.today().year}, NVIDIA"
author = "NVIDIA"

# Single modifiable version for all of the docs - easier for future updates
stable_version = "26.08"
nightly_version = "26.10"
cuda_major = "13"  # drives container tags and pip wheel suffixes (cudf-cu13, ...)
python_version = "3.13"  # Python version for conda commands
cuda_tag = f"cuda{cuda_major}-py{python_version}"
stable_cuda_range = (
    "cuda-version>=13.0,<=13.2"  # CUDA version pins on Conda for the stable release
)
nightly_cuda_range = (
    "cuda-version>=13.0,<=13.3"  # CUDA version pins on Conda for the nightly release
)

versions = {
    "stable": {
        "rapids_version": stable_version,
        "rapids_api_docs_version": "stable",
        "rapids_container": f"nvcr.io/nvidia/rapidsai/base:{stable_version}-{cuda_tag}",
        "rapids_notebooks_container": f"nvcr.io/nvidia/rapidsai/notebooks:{stable_version}-{cuda_tag}",
        "rapids_conda_channel": "rapidsai",
        "rapids_conda_channels": "-c rapidsai -c conda-forge",
        "rapids_conda_packages": f"rapids={stable_version} python={python_version} '{stable_cuda_range}'",
        "rapids_pip_index": "https://pypi.nvidia.com",
        "rapids_pip_version": stable_version,
        "rapids_cuda_major": cuda_major,
        "rapids_cuda_version_range": stable_cuda_range,
        # AzureML is pinned to CUDA 12 currently (driver 535.x supports only CUDA 12.x).
        "rapids_container_cuda12": f"rapidsai/base:{stable_version}-cuda12-py{python_version}",
    },
    "nightly": {
        "rapids_version": f"{nightly_version}",
        "rapids_api_docs_version": "nightly",
        "rapids_container": f"rapidsai/base:{nightly_version + 'a'}-{cuda_tag}",
        "rapids_notebooks_container": f"rapidsai/notebooks:{nightly_version + 'a'}-{cuda_tag}",
        "rapids_conda_channel": "rapidsai-nightly",
        "rapids_conda_channels": "-c rapidsai-nightly -c conda-forge",
        "rapids_conda_packages": f"rapids={nightly_version} python={python_version} '{nightly_cuda_range}'",
        "rapids_pip_index": "https://pypi.anaconda.org/rapidsai-wheels-nightly/simple",
        "rapids_pip_version": f"{nightly_version}.*,>=0.0.0a0",
        "rapids_cuda_major": cuda_major,
        "rapids_cuda_version_range": nightly_cuda_range,
        # AzureML is pinned to CUDA 12 currently (driver 535.x supports only CUDA 12.x).
        "rapids_container_cuda12": f"rapidsai/base:{nightly_version + 'a'}-cuda12-py{python_version}",
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
    "sphinx_reredirects",
    "sphinx_llm.txt",
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
copybutton_line_continuation_character = "\\"


suppress_warnings = ["myst.header", "myst.nested_header"]

# -- Options for notebooks -------------------------------------------------

nb_execution_mode = "off"
rapids_deployment_notebooks_base_url = (
    "https://github.com/rapidsai/deployment/blob/main/source/"
)

# -- Options for HTML output -------------------------------------------------

html_theme_options = {
    "analytics": {
        "google_analytics_id": "G-02WR7CRJ3Z",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/rapidsai/deployment",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
    "public_docs_features": os.environ.get("CI") == "true",
    "external_links": [
        {"name": "Docs Home", "url": "https://docs.rapids.ai/"},
    ],
    "show_toc_level": 1,
    "navbar_align": "right",
    "secondary_sidebar_items": [
        "page-toc",
        "notebooks-extra-files-nav",
        "notebooks-tags",
        "deployment-feedback",
    ],
}

# The navbar version switcher is a static template override
# (``_templates/version-switcher.html``) with hardcoded links straight to the
# published nightly/stable docs.
# Three-state detection via DEPLOYMENT_DOCS_BUILD_STABLE:
#   "true"  → stable  (CI tag build)
#   "false" → nightly (CI non-tag build; CI always sets the var explicitly)
#   unset   → dev     (local or ReadTheDocs preview build)
_stable_env = os.environ.get("DEPLOYMENT_DOCS_BUILD_STABLE")
if _stable_env == "true":
    deployment_version_label = "stable"
elif _stable_env == "false":
    deployment_version_label = "nightly"
else:
    deployment_version_label = "dev"

html_context = {
    "deployment_version_label": deployment_version_label,
}

html_sidebars = {
    "examples/index": ["sidebar-nav-bs", "notebooks-tag-filter"],
}

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "nvidia_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "dask": ("https://docs.dask.org/en/latest/", None),
    "distributed": ("https://distributed.dask.org/en/latest/", None),
    "dask_kubernetes": ("https://kubernetes.dask.org/en/latest/", None),
    "dask_cuda": ("https://docs.nvidia.com/dask-cuda/latest/", None),
}

redirects = {
    "platforms/brev-dev": "../../cloud/nvidia/brev/",
    "guides/l4-gcp": "../../cloud/gcp/",
}


def setup(app):
    app.add_css_file("css/custom.css")
    app.add_js_file("js/notebook-gallery.js", loading_method="defer")
