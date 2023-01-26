from functools import cache

import nbformat
from docutils import nodes
from docutils.parsers.rst.states import RSTState
from docutils.statemachine import ViewList
from markdown_it import MarkdownIt
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import nested_parse_with_titles


@cache
def read_notebook_tags(path: str) -> list[str]:
    """Read metadata tags from first cell of a notebook file."""
    notebook = nbformat.read(path, as_version=4)
    try:
        return notebook.cells[0]["metadata"]["tags"]
    except KeyError:
        return []


def generate_notebook_grid_myst(
    notebooks: list[str], env: BuildEnvironment
) -> list[str]:
    """Generate sphinx-design grid of notebooks in MyST markdown.

    Take a list of notebook documents and render out some MyST markdown displaying those
    documents in a grid of cards.

    """
    md = []
    md.append("`````{grid} 1 2 2 3")
    md.append(":gutter: 2 2 2 2")
    md.append("")

    for notebook in notebooks:
        md.append("````{grid-item-card}")
        md.append(":link: /" + notebook)
        md.append(":link-type: doc")
        try:
            md.append(get_title_for_notebook(env.doc2path(notebook)))
        except ValueError:
            md.append(notebook)
        md.append("^" * len(notebook))
        md.append("")
        for tag in read_notebook_tags(env.doc2path(notebook)):
            md.append("{bdg-primary}`" + tag.split("/")[-1] + "`")
        md.append("````")
        md.append("")

    md.append("`````")

    return md


def parse_markdown(markdown: list[str], state: RSTState) -> list[nodes.Node]:
    """Render markdown into nodes."""
    node = nodes.section()
    node.document = state.document
    vl = ViewList(markdown, "fakefile.md")
    nested_parse_with_titles(state, vl, node)
    return node.children


def get_title_for_notebook(path: str) -> str:
    """Read a notebook file and find the top-level heading."""
    notebook = nbformat.read(path, as_version=4)
    for cell in notebook.cells:
        if cell["cell_type"] == "markdown":
            cell_source = MarkdownIt().parse(cell["source"])
            for i, token in enumerate(cell_source):
                next_token = cell_source[i + 1]
                if (
                    token.type == "heading_open"
                    and token.tag == "h1"
                    and next_token.type == "inline"
                ):
                    return next_token.content
    raise ValueError("No top-level heading found")


class RelatedExamples(SphinxDirective):
    def run(self) -> list[nodes.Node]:
        output = nodes.section(ids=["relatedexamples"])

        if self.env.docname in self.env.notebook_tag_map:
            output += nodes.title("Related Examples", "Related Examples")
            grid_markdown = generate_notebook_grid_myst(
                notebooks=self.env.notebook_tag_map[self.env.docname],
                env=self.env,
            )
            for node in parse_markdown(
                markdown=grid_markdown,
                state=self.state,
            ):
                output += node

        return [output]


def build_tag_map(app: Sphinx, env: BuildEnvironment, docnames: list[str]):
    """Walk notebooks and update tag map.

    Once Sphinx has decided which pages to build, iterate over the notebooks
    and build the ``env.notebook_tag_map`` based on the tags of the first cell.

    If any notebooks have been updated as part of this build then add all of the
    pages with related tags to the build to ensure they are up to date.

    """

    env.notebook_tag_map = {}

    # If no pages are being rebuilt skip generating the tag map
    if not docnames:
        return

    # Build notebook tag map
    for doc in env.found_docs:
        path = app.env.doc2path(doc)
        if path.endswith("ipynb"):
            for tag in read_notebook_tags(path):
                try:
                    env.notebook_tag_map[tag].append(doc)
                except KeyError:
                    env.notebook_tag_map[tag] = [doc]

    # If notebooks have been modified add all docnames from env.found_docs that match the tags to docnames
    if any([app.env.doc2path(doc).endswith("ipynb") for doc in docnames]):
        for tag in env.notebook_tag_map.keys():
            if tag in env.found_docs:
                # FIXME This doesn't seem to be working correctly as the pages aren't being rebuilt
                docnames.append(doc)


def setup(app: Sphinx) -> dict:
    app.connect("env-before-read-docs", build_tag_map)
    app.add_directive("relatedexamples", RelatedExamples)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
