import re
from copy import deepcopy
from typing import TYPE_CHECKING

from docutils import nodes

if TYPE_CHECKING:
    import sphinx


class RapidsCustomNodeVisitor(nodes.SparseNodeVisitor):
    """
    Post-process the text generated by Sphinx.

    ``docutils`` breaks documents down into different Python classes that
    roughly correspond to the HTML document object model ("DOM").

    The only node types that will be modified by this class are those with
    a corresponding ``visit_{node_class}`` method defined.

    For a list of all the available types, see
    https://sourceforge.net/p/docutils/code/9881/tree/trunk/docutils/docutils/nodes.py#l2630
    """

    def __init__(self, app: "sphinx.application.Sphinx", *args, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)

    def visit_reference(self, node: nodes.reference) -> None:
        """
        Replace template strings in URLs. These are ``docutils.nodes.reference`` objects.

        See https://sourceforge.net/p/docutils/code/9881/tree/trunk/docutils/docutils/nodes.py#l2599
        """
        # references to anchors will not have the "refuri" attribute. For example, markdown like this:
        #
        #   [Option 1](use-an-Azure-marketplace-VM-image)
        #
        # Will have attributes like this:
        #
        #   {'ids': [], 'classes': [], 'names': [], 'dupnames': [], 'backrefs': [],
        #    'internal': True, 'refid': 'use-an-azure-marketplace-vm-image'}
        #
        if "refuri" not in node.attributes:
            return

        # find templated bits in the URI and replace them with '{{' template markers that Jinja2 will understand
        uri_str = deepcopy(node.attributes)["refuri"]
        uri_str = re.sub(r"~~~(.*?)~~~", r"{{ \1 }}", uri_str)

        # fill in appropriate values based on app context
        node.attributes["refuri"] = re.sub(
            r"(?<!\$)\{\{.*?\}\}", self.template_func, uri_str
        )

        # update the document
        if node.parent:
            node.parent.replace(node, node)

    def visit_Text(self, node: nodes.Text) -> None:
        """
        Replace template strings in generic text.
        This roughly corresponds to HTML ``<p>``, ``<pre>``, and similar elements.
        """
        new_node = nodes.Text(
            re.sub(r"(?<!\$)\{\{.*?\}\}", self.template_func, node.astext())
        )
        if node.parent:
            node.parent.replace(node, new_node)

    def template_func(self, match: re.Match) -> str:
        """
        Replace template strings like ``{{ rapids_version }}`` with real
        values like ``24.10``.
        """
        return self.app.builder.templates.render_string(
            source=match.group(), context=self.app.config.rapids_version
        )


def version_template(
    app: "sphinx.application.Sphinx",
    doctree: "sphinx.addnodes.document",
    docname: str,
) -> None:
    """Substitute versions into each page.

    This allows documentation pages and notebooks to substitute in values like
    the latest container image using jinja2 syntax.

    E.g

        # My doc page

        The latest container image is {{ rapids_container }}.

    """
    doctree.walk(RapidsCustomNodeVisitor(app, doctree))


def setup(app: "sphinx.application.Sphinx") -> None:
    app.add_config_value("rapids_version", {}, "html")
    app.connect("doctree-resolved", version_template)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
