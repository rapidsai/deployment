from docutils.nodes import Text, admonition, inline, paragraph
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from sphinx.addnodes import pending_xref
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


class Docref(BaseAdmonition, SphinxDirective):
    node_class = admonition
    required_arguments = 1

    def run(self):
        doc = self.arguments[0]
        self.arguments = ["See Documentation"]
        self.options["classes"] = ["docref"]
        nodes = super().run()
        custom_xref = pending_xref(
            reftype="myst",
            refdomain="std",
            refexplicit=True,
            reftarget=doc,
            refdoc=self.env.docname,
            refwarn=True,
        )
        text_wrapper = inline()
        text_wrapper += Text("Visit the documentation >>")
        custom_xref += text_wrapper
        wrapper = paragraph()
        wrapper["classes"] = ["visit-link"]
        wrapper += custom_xref
        nodes[0] += wrapper
        return nodes


def setup(app: Sphinx) -> dict:
    app.add_directive("docref", Docref)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
