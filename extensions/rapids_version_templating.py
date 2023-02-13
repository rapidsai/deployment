def version_template(app, docname, source):
    """Substitute versions into each page.

    This allows documentation pages and notebooks to substiture in values like
    the latest container image using jinja2 syntax.

    E.g

        # My doc page

        The latest container image is {{ rapids_container }}.

    """

    # Make sure we're outputting HTML
    if app.builder.format != "html":
        return
    src = source[0]
    rendered = app.builder.templates.render_string(src, app.config.rapids_version)
    source[0] = rendered


def setup(app):
    app.add_config_value("rapids_version", {}, "html")
    app.connect("source-read", version_template)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
