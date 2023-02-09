import pathlib


def find_notebook_related_files(app, pagename, templatename, context, doctree):
    """Find related files for Jupyter Notebooks in the examples section.

    Example notebooks should be placed in /source/examples in their own directories.
    This extension walks through the directory when each notebook is rendered and generates
    a list of all the other files in the directory.

    The goal is to set a list of GitHub URLs in the template context so we can render
    them in the sidebar. To get the GitHub url we use the ``rapids_deployment_notebooks_base_url`` config
    option which shows the base url for where the source files are on GitHub.

    """
    if "examples/" in pagename and context["page_source_suffix"] == ".ipynb":
        source_root = pathlib.Path(__file__).parent / ".." / "source"
        base_url = app.config.rapids_deployment_notebooks_base_url
        rel_page_parent = pathlib.Path(pagename).parent
        path_to_page_parent = source_root / rel_page_parent

        related_notebook_dirs = []
        related_notebook_files = []
        for page in path_to_page_parent.glob("*"):
            if "ipynb" not in page.name:
                url = f"{base_url}{rel_page_parent}/{page.name}"
                if (path_to_page_parent / page).is_dir():
                    related_notebook_dirs.append((page.name + "/", url))
                else:
                    related_notebook_files.append((page.name, url))

        context["related_notebook_files"] = (
            related_notebook_dirs + related_notebook_files
        )


def setup(app):
    app.add_config_value("rapids_deployment_notebooks_base_url", "", "html")
    app.connect("html-page-context", find_notebook_related_files)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
