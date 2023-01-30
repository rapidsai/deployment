
from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.application import Sphinx
from sphinx.directives.other import TocTree
from sphinx.util.nodes import nested_parse_with_titles


class CardGridTocTree(TocTree):
    # TODO Enable configuring all grid options and arguments
    # https://sphinx-design.readthedocs.io/en/latest/grids.html#grid-options
    # This probably would require changing this class to inherit from ``sphinx_design.grids.GridDirective``
    # and instantiating the TocTree class part way through and ensuring it is configured well enough
    # to call run.

    def run(self) -> list[nodes.Node]:
        output = nodes.container()

        # Generate the card grid
        grid = nodes.section(ids=["toctreegrid"])
        # TODO Stop manipulating markdown here
        content = ViewList(
            ["`````{grid} 1 2 2 3", ":gutter: 2 2 2 2"] + self.content.data + ["`````"],
            "fakefile.md",
        )
        nested_parse_with_titles(self.state, content, grid)
        output += grid

        # Update the content with the document names ready for toctree generation
        # TODO get the doc names from walking the grid nodes rather than manipulating the markdown
        self.content.data = [
            line.replace(":link:", "").strip()
            for line in self.content.data
            if ":link:" in line
        ]

        # Generate the actual toctree but ensure it is hidden
        self.options["hidden"] = True
        toctree = super().run()
        output += toctree

        return [output]


def setup(app: Sphinx) -> dict:
    app.add_directive("cardgridtoctree", CardGridTocTree)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
