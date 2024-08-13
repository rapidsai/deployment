import re

from docutils import nodes
from copy import deepcopy


class TextNodeVisitor(nodes.GenericNodeVisitor):
    def __init__(self, app, *args, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)

    def default_visit(self, node):
        pass

    def visit_paragraph(self, node):
        # what_line = "visit_paragraph"
        # import pdb; pdb.set_trace()
        pass

    def visit_reference(self, node) -> None:
        """
        Replace template strings in URLs. These are ``docutils.nodes.Reference`` objects
        in ``docutils``.

        See https://sourceforge.net/p/docutils/code/9881/tree/trunk/docutils/docutils/nodes.py#l2599
        """
        # references to anchors will not have the "refuri" attribute. For example, markdown like this:
        #
        #   [Option 1](use-an-Azure-marketplace-VM-image)
        #
        # Will have attributes like this:
        #
        #   {'ids': [], 'classes': [], 'names': [], 'dupnames': [], 'backrefs': [], 'internal': True, 'refid': 'use-an-azure-marketplace-vm-image'}
        #
        if "refuri" not in node.attributes:
            return
        
        # if "~~~" in node.attributes["refuri"]:
        #     import pdb; pdb.set_trace()

        # find templated bits in the URI and replace them with '{{' template markers that Jinja2 will understand
        uri_str = deepcopy(node.attributes)["refuri"]
        uri_str = re.sub(r"~~~(.*?)~~~", r"{{ \1 }}", uri_str)

        # fill in appropriate values based on app context
        uri_str = re.sub(r"(?<!\$)\{\{.*?\}\}", self.template_func, uri_str)

        # update the document
        node.attributes["refuri"] = uri_str

        #node.attributes["refuri"] = re.sub(r"(?<!\$)\{\{.*?\}\}", self.template_func, uri_str)
        #re.sub(r"(?<!\$)\{\{.*?\}\}", self.template_func, 'https://docs.rapids.ai/api/cuml/{{rapids_api_docs_version}}/api.html#random-forest')
        node.parent.replace(node, node)
        # new_node = nodes.reference(
        #     re.sub(r"\~\~\~rapids_api_docs_version\~\~\~", self.app.config.rapids_version["rapids_api_docs_version"], new_node.astext())
        # )
        # import pdb; pdb.set_trace()

    # def visit_Element(self, node):
    #     # ref: https://sourceforge.net/p/docutils/code/HEAD/tree/trunk/docutils/docutils/nodes.py#l2753
    #     what_line = "17"
    #     import pdb; pdb.set_trace()

    def visit_Text(self, node):
        new_node = nodes.Text(
            re.sub(r"(?<!\$)\{\{.*?\}\}", self.template_func, node.astext())
        )
        # if "docs.rapids.ai" in str(new_node.astext()):
        #     import pdb; pdb.set_trace()
        # new_node = nodes.Text(
        #     re.sub(r"\~\~\~rapids_api_docs_version\~\~\~", self.app.config.rapids_version["rapids_api_docs_version"], new_node.astext())
        # )
        node.parent.replace(node, new_node)

    def template_func(self, match):
        return self.app.builder.templates.render_string(
            match.group(), self.app.config.rapids_version
        )


def version_template(app, doctree, docname):
    """Substitute versions into each page.

    This allows documentation pages and notebooks to substitute in values like
    the latest container image using jinja2 syntax.

    E.g

        # My doc page

        The latest container image is {{ rapids_container }}.

    """
    doctree.walk(TextNodeVisitor(app, doctree))


def setup(app):
    app.add_config_value("rapids_version", {}, "html")
    app.connect("doctree-resolved", version_template)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
