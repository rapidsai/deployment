from functools import partial

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.directives.other import TocTree
from sphinx_design.grids import GridDirective


def find_linked_documents(node):
    """Find all referenced documents in a node tree.

    Walks the nodes and yield the reftarget attribute for any that have it set.

    """
    for child in node.traverse():
        try:
            if child.attributes["reftarget"]:
                yield child.attributes["reftarget"]
        except (AttributeError, KeyError):
            pass


class CardGridTocTree(GridDirective):
    """An extension of sphinx_design.grids.GridDirective that also add referenced docs to the toctree.

    For any element within the grid which links to another page with the ``link-type`` ``doc`` the
    doc gets added to the toctree of that page.

    """

    def run(self) -> list[nodes.Node]:
        output = nodes.container()

        # Generate the card grid
        grid = nodes.section(ids=["toctreegrid"])
        grid += super().run()[0]
        output += grid

        # Update the content with the document names referenced in the card grid ready for toctree generation
        self.content.data = [doc for doc in find_linked_documents(grid)]

        # Generate the actual toctree but ensure it is hidden
        self.options["hidden"] = True
        self.parse_content = partial(TocTree.parse_content, self)
        toctree = TocTree.run(self)[0]
        output += toctree

        return [output]


def setup(app: Sphinx) -> dict:
    app.add_directive("gridtoctree", CardGridTocTree)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
