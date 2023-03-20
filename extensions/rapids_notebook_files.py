import contextlib
import os
import pathlib
import re
import shutil
import tempfile
from functools import partial


def template_func(app, match):
    return app.builder.templates.render_string(match.group(), app.config.rapids_version)


def walk_files(app, dir, outdir):
    outdir.mkdir(parents=True, exist_ok=False)
    related_notebook_files = {}
    for page in dir.glob("*"):
        if page.is_dir():
            related_notebook_files[page.name] = walk_files(
                app, page, outdir / page.name
            )
        else:
            with contextlib.suppress(OSError):
                os.remove(str(outdir / page.name))
            if "ipynb" in page.name:
                with open(str(page)) as reader:
                    notebook = reader.read()
                    with open(str(outdir / page.name), "w") as writer:
                        writer.write(
                            re.sub(
                                r"\{\{.*?\}\}",
                                partial(template_func, app),
                                notebook,
                            )
                        )
            else:
                shutil.copy(str(page), str(outdir / page.name))
            related_notebook_files[page.name] = page.name
    return related_notebook_files


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
        output_root = pathlib.Path(app.builder.outdir)
        rel_page_parent = pathlib.Path(pagename).parent
        path_to_page_parent = source_root / rel_page_parent
        path_to_output_parent = output_root / rel_page_parent

        # Copy all related files to output and apply templating
        context["related_notebook_files"] = walk_files(
            app, path_to_page_parent, path_to_output_parent
        )

        # Make archive of related files
        archive_path = path_to_output_parent / "all_files.zip"
        with contextlib.suppress(OSError):
            os.remove(str(archive_path))
        with tempfile.NamedTemporaryFile() as tmpf:
            shutil.make_archive(
                tmpf.name,
                "zip",
                str(path_to_output_parent.parent),
                str(path_to_output_parent.name),
            )
            shutil.move(tmpf.name + ".zip", str(archive_path))
        context["related_notebook_files_archive"] = archive_path.name


def setup(app):
    app.add_config_value("rapids_deployment_notebooks_base_url", "", "html")
    app.connect("html-page-context", find_notebook_related_files)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
