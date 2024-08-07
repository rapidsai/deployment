import re

from docutils import nodes


class TextNodeVisitor(nodes.SparseNodeVisitor):
    def __init__(self, app, *args, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)

    def visit_Text(self, node):
        new_node = nodes.Text(
            re.sub(r"(?<!\$)\{\{.*?\}\}", self.template_func, node.astext())
        )
        new_node = nodes.Text(
            re.sub(r"(?<!\$)\~\~\~.*?\~\~\~", self.template_func, new_node.astext())
        )
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
