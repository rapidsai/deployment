"""Workflow Examples gallery, driven by ``source/examples/examples.yml``.

``examples.yml`` holds the controlled vocabulary for the gallery filters and one
entry per example notebook. Platforms and tools are docnames, so the docs
navigation is their vocabulary and labels come from each page's ``short_title``
front matter (falling back to its title).

The ``{examplegallery}`` directive renders the gallery on ``examples/index`` and the
hidden toctree that puts the examples in the navigation. Every platform and tool
page an example points to gets an "Examples" section appended automatically, and
each example page gets an "About this example" block in its right sidebar
(``_templates/examples-about.html``).

Examples are listed in recommendation order everywhere: those with ``verified``
set come first, newest release first, then the rest by the date in the notebook's
``_Month, Year_`` line. ``verified`` is for maintainers and never rendered.
"""

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from html import escape
from pathlib import Path
from urllib.parse import quote

import yaml
from docutils import nodes
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.directives.other import TocTree
from sphinx.util import logging

logger = logging.getLogger(__name__)

EXAMPLES_YML = "examples/examples.yml"
DESCRIPTION_LIMIT = 120
SECTION_CARDS = 6
MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
WRITTEN = re.compile(rf"^_({'|'.join(MONTHS)}),? (\d{{4}})_\s*$", re.MULTILINE)
VERIFIED = re.compile(r"^(\d{2})\.(\d{2})$")
PLATFORM_ROOTS = ("local", "hpc", "cloud/", "platforms/")
FACETS = {
    "platform": "Platform",
    "task": "Task",
    "library": "Library",
    "scale": "Scale",
    "dataset": "Dataset",
    "format": "Format",
    "storage": "Storage",
}
# Optional facets, shown behind "More filters" in the gallery
ADVANCED_FACETS = ("dataset", "format", "storage")


@dataclass
class Example:
    docname: str
    title: str | None
    description: str
    platform: list[str]
    tools: list[str]
    library: list[str]
    task: list[str]
    scale: str
    dataset: list[str]
    format: list[str]
    storage: list[str]
    topics: list[str]
    verified: tuple[int, int] | None
    written: tuple[int, int] | None


class examples_placeholder(nodes.General, nodes.Element):
    """Replaced with HTML once every page is read and URIs can be resolved."""


def warn(message: str) -> None:
    logger.warning(f"{EXAMPLES_YML}: {message}")


def load_examples(app: Sphinx, env, added, changed, removed) -> list[str]:
    """Read examples.yml before any page is read, and re-read every page when it changes."""
    text = Path(app.srcdir, EXAMPLES_YML).read_text()
    digest = hashlib.sha256(text.encode()).hexdigest()
    changed_yml = getattr(env, "rapids_examples_digest", digest) != digest
    env.rapids_examples_digest = digest

    data = yaml.safe_load(text)
    env.rapids_vocabulary = vocabulary = data["vocabulary"]
    examples = [parse_example(env, entry, vocabulary) for entry in data["examples"]]
    env.rapids_examples = sorted(examples, key=recommendation_order)

    for page in vocabulary.get("buttons", []):
        if page not in env.found_docs:
            warn(f"button '{page}' is not a page")

    listed = {example.docname for example in examples}
    for docname in sorted(env.found_docs):
        if (
            docname.startswith("examples/")
            and docname.endswith("/notebook")
            and docname not in listed
        ):
            warn(f"{docname} has no entry, add one for it")

    return sorted(env.found_docs) if changed_yml else []


def parse_example(env, entry: dict, vocabulary: dict) -> Example:
    path = entry.get("path", "")
    docname = f"examples/{path}/notebook"
    where = path or "an entry without a path"
    if docname not in env.found_docs:
        warn(f"{where}: no notebook at source/{docname}.ipynb")

    description = entry.get("description", "")
    if not description or len(description) > DESCRIPTION_LIMIT:
        warn(
            f"{where}: description must be one sentence of at most {DESCRIPTION_LIMIT} characters"
        )

    platform = entry.get("platform", [])
    if not platform:
        warn(f"{where}: needs at least one platform, use 'local' if it runs anywhere")
    for page in platform:
        if not page.startswith(PLATFORM_ROOTS) or page not in env.found_docs:
            warn(
                f"{where}: platform '{page}' is not a page under local, hpc, cloud/ or platforms/"
            )
    tools = entry.get("tools", [])
    for page in tools:
        if not page.startswith("tools/") or page not in env.found_docs:
            warn(f"{where}: tool '{page}' is not a page under tools/")

    aliases = vocabulary.get("aliases", {})
    library = check_values(
        where, "library", entry.get("library", []), library_labels(vocabulary), aliases
    )
    task = check_values(
        where, "task", entry.get("task", []), vocabulary["task"], aliases
    )
    scale = entry.get("scale", "")
    check_values(where, "scale", [scale], vocabulary["scale"], aliases)
    data = {
        facet: check_values(
            where, facet, entry.get(facet, []), vocabulary[facet], aliases, False
        )
        for facet in ADVANCED_FACETS
    }

    verified = None
    if "verified" in entry:
        match = VERIFIED.match(str(entry["verified"]))
        if match:
            verified = (int(match[1]), int(match[2]))
        else:
            warn(f'{where}: verified must be a RAPIDS release like "26.10" (quoted)')

    return Example(
        docname=docname,
        title=entry.get("title"),
        description=description,
        platform=platform,
        tools=tools,
        library=library,
        task=task,
        scale=scale,
        **data,
        topics=entry.get("topics", []),
        verified=verified,
        written=written_date(env, docname, where),
    )


def check_values(
    where: str,
    facet: str,
    values: list[str],
    allowed: dict,
    aliases: dict,
    required: bool = True,
) -> list[str]:
    if required and not values:
        warn(f"{where}: needs at least one {facet}")
    for value in values:
        if value in aliases:
            warn(f"{where}: use {facet} '{aliases[value]}' instead of '{value}'")
        elif value not in allowed:
            warn(
                f"{where}: unknown {facet} '{value}', expected one of {', '.join(allowed)}"
            )
    return values


def written_date(env, docname: str, where: str) -> tuple[int, int] | None:
    """The year and month from the notebook's ``_Month, Year_`` line."""
    if docname not in env.found_docs:
        return None
    notebook = json.loads(Path(env.doc2path(docname)).read_text())
    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            match = WRITTEN.search("".join(cell["source"]))
            if match:
                return int(match[2]), MONTHS.index(match[1]) + 1
    warn(f"{where}: the notebook needs a '_Month, Year_' line under its title")
    return None


def recommendation_order(example: Example):
    """Verified examples first, newest release first, then newest written first."""
    verified = example.verified or (0, 0)
    written = example.written or (0, 0)
    return (example.verified is None, [-n for n in verified], [-n for n in written])


def library_labels(vocabulary: dict) -> dict:
    """Library values are grouped for the dropdown, flatten them for lookups."""
    return {
        value: label
        for group in vocabulary["library"].values()
        for value, label in group.items()
    }


def facet_labels(vocabulary: dict, facet: str) -> dict:
    return library_labels(vocabulary) if facet == "library" else vocabulary[facet]


def page_label(env, docname: str) -> str:
    """A page's short_title front matter, falling back to its title."""
    short_title = env.metadata.get(docname, {}).get("short_title")
    if short_title:
        return short_title
    return env.titles[docname].astext() if docname in env.titles else docname


def example_title(env, example: Example) -> str:
    if example.title:
        return example.title
    return (
        env.titles[example.docname].astext()
        if example.docname in env.titles
        else example.docname
    )


def platform_group(docname: str, vocabulary: dict) -> str:
    """The page a platform rolls up into: its cloud provider's index page, else itself."""
    parts = docname.split("/")
    if (
        parts[0] == "cloud"
        and len(parts) == 3
        and docname not in vocabulary.get("standalone", [])
    ):
        return f"cloud/{parts[1]}/index"
    return docname


def platform_pages(example: Example, vocabulary: dict) -> set[str]:
    """Every platform page an example belongs to: its own, implied ones and their providers."""
    implies = vocabulary.get("implies", {})
    pages = set()
    for docname in example.platform:
        for page in (docname, *([implies[docname]] if docname in implies else [])):
            pages |= {page, platform_group(page, vocabulary)}
    return pages


def examples_on(env, docname: str) -> list[Example]:
    """The examples listed on a platform or tool page, in recommendation order."""
    return [
        example
        for example in env.rapids_examples
        if docname in platform_pages(example, env.rapids_vocabulary)
        or docname in example.tools
    ]


def nav_order(env) -> dict[str, int]:
    """Position of every page in a depth-first walk of the navigation."""
    order = {}

    def walk(docname):
        if docname not in order:
            order[docname] = len(order)
            for child in env.toctree_includes.get(docname, []):
                walk(child)

    walk(env.config.root_doc)
    return order


class ExampleGallery(TocTree):
    """The filterable gallery of every example, plus a hidden toctree of them."""

    has_content = False
    option_spec = {}

    def run(self) -> list[nodes.Node]:
        entries = []
        for example in self.env.rapids_examples:
            target = example.docname.removeprefix("examples/")
            entries.append(f"{example.title} <{target}>" if example.title else target)
            # Re-render the gallery when a notebook's title or date changes
            self.env.note_dependency(self.env.doc2path(example.docname))
        self.content = StringList(entries)
        self.options = {"hidden": True}
        return [*super().run(), examples_placeholder(kind="gallery")]


def card(env, example: Example, href: str, data: dict | None = None) -> str:
    vocabulary = env.rapids_vocabulary
    platforms = [page_label(env, docname) for docname in example.platform]
    meta = [
        platforms[0] + (f" +{len(platforms) - 1}" if len(platforms) > 1 else ""),
        (
            library_labels(vocabulary).get(example.library[0], "")
            if example.library
            else ""
        ),
        vocabulary["task"].get(example.task[0], "") if example.task else "",
    ]
    attributes = "".join(
        f' data-{key}="{escape(value)}"' for key, value in (data or {}).items()
    )
    return (
        f'<article class="eg-card"{attributes}>'
        f'<h3 class="eg-card-title"><a href="{escape(href)}">{escape(example_title(env, example))}</a></h3>'
        f'<p class="eg-card-desc">{escape(example.description)}</p>'
        f'<p class="eg-card-meta">{escape(" · ".join(part for part in meta if part))}</p>'
        "</article>"
    )


def search_text(env, example: Example) -> str:
    """Everything the gallery search matches against, lowercased."""
    vocabulary = env.rapids_vocabulary
    pages = (
        platform_pages(example, vocabulary) | set(example.platform) | set(example.tools)
    )
    words = [example_title(env, example), example.description]
    words += example.topics
    if example.docname in env.titles:
        words.append(env.titles[example.docname].astext())
    for page in pages:
        words.append(page_label(env, page))
        if page in env.titles:
            words.append(env.titles[page].astext())
    for facet in ("library", "task", "scale", *ADVANCED_FACETS):
        values = getattr(example, facet)
        for value in [values] if isinstance(values, str) else values:
            words += [value, facet_labels(vocabulary, facet).get(value, "")]
    values = {*example.library, *example.dataset, *example.format, *example.storage}
    words += [
        alias
        for alias, value in vocabulary.get("aliases", {}).items()
        if value in values
    ]
    return " ".join(words).lower()


def option(value: str, label: str, count: int, kind: str = "") -> str:
    return (
        f'<label class="eg-option{kind}"><input type="checkbox" value="{escape(value)}">'
        f'<span class="eg-option-label">{escape(label)}</span><span class="eg-n">{count}</span></label>'
    )


def facet_menu(facet: str, body: str) -> str:
    return menu(FACETS[facet], [facet], f'<div data-facet="{facet}">{body}</div>')


def menu(title: str, facets: list[str], body: str) -> str:
    """A dropdown holding the options of one or more facets."""
    return (
        f'<details class="eg-facet" data-facets="{" ".join(facets)}">'
        f'<summary>{escape(title)}<span class="eg-selected"></span></summary>'
        f'<div class="eg-menu">{body}</div></details>'
    )


def render_gallery(app: Sphinx, docname: str) -> str:
    env = app.env
    vocabulary = env.rapids_vocabulary
    examples = env.rapids_examples
    order = nav_order(env)

    def by_nav(page):
        return order.get(page, len(order))

    platform_counts = Counter(
        page for example in examples for page in platform_pages(example, vocabulary)
    )
    groups = sorted(
        {platform_group(page, vocabulary) for page in platform_counts}, key=by_nav
    )
    platform_menu = ""
    for group in groups:
        children = sorted(
            (
                page
                for page in platform_counts
                if page != group and platform_group(page, vocabulary) == group
            ),
            key=by_nav,
        )
        platform_menu += (
            '<div class="eg-group">'
            + option(
                group,
                page_label(env, group),
                platform_counts[group],
                " eg-option--group",
            )
            + "".join(
                option(
                    page,
                    page_label(env, page),
                    platform_counts[page],
                    " eg-option--child",
                )
                for page in children
            )
            + "</div>"
        )
    # A button needs a dropdown option to drive, so skip platforms without examples
    buttons = [page for page in vocabulary.get("buttons", []) if page in groups]

    def flat_menu(facet: str, labels: dict) -> str:
        counts = Counter(
            value for example in examples for value in getattr(example, facet)
        )
        return "".join(
            option(value, label, counts[value])
            for value, label in labels.items()
            if counts[value]
        )

    library_menu = "".join(
        f'<p class="eg-menu-heading">{escape(heading)}</p>{flat_menu("library", labels)}'
        for heading, labels in vocabulary["library"].items()
    )
    scale_counts = Counter(example.scale for example in examples)
    scale_menu = "".join(
        option(value, label, scale_counts[value])
        for value, label in vocabulary["scale"].items()
        if scale_counts[value]
    )

    cards = "".join(
        card(
            env,
            example,
            app.builder.get_relative_uri(docname, example.docname),
            {
                "platform": " ".join(sorted(platform_pages(example, vocabulary))),
                "task": " ".join(example.task),
                "library": " ".join(example.library),
                "scale": example.scale,
                **{
                    facet: " ".join(getattr(example, facet))
                    for facet in ADVANCED_FACETS
                },
                # Topics can contain spaces ("random forest")
                "topics": "|".join(example.topics),
                "docname": example.docname,
                "search": search_text(env, example),
            },
        )
        for example in examples
    )
    aliases = json.dumps(vocabulary.get("aliases", {}))
    site_search = app.builder.get_relative_uri(docname, "search")
    return (
        f'<div class="eg" id="examples-gallery" data-aliases="{escape(aliases)}">'
        '<div class="eg-search"><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i>'
        '<input id="eg-search" type="search" autocomplete="off" role="combobox" '
        'aria-autocomplete="list" aria-expanded="false" aria-controls="eg-suggestions" '
        'placeholder="Search examples, e.g. &quot;hpo gke&quot;" aria-label="Search workflow examples">'
        '<ul id="eg-suggestions" class="eg-suggestions" role="listbox" aria-label="Suggestions" hidden></ul>'
        "</div>"
        '<div class="eg-platforms" role="group" aria-label="Platform">'
        + "".join(
            f'<button type="button" class="eg-platform" data-value="{escape(group)}" aria-pressed="false">'
            f"{escape(page_label(env, group))}</button>"
            for group in buttons
        )
        + '<button type="button" class="eg-platform eg-more">More</button></div>'
        '<div class="eg-services" role="group" aria-label="Services" hidden></div>'
        '<div class="eg-toolbar"><div class="eg-facets">'
        + facet_menu("platform", platform_menu)
        + facet_menu("task", flat_menu("task", vocabulary["task"]))
        + facet_menu("library", library_menu)
        + facet_menu("scale", scale_menu)
        + menu(
            "More filters",
            list(ADVANCED_FACETS),
            "".join(
                f'<div data-facet="{facet}"><p class="eg-menu-heading">{FACETS[facet]}</p>'
                f"{flat_menu(facet, vocabulary[facet])}</div>"
                for facet in ADVANCED_FACETS
            ),
        )
        + f'</div><p class="eg-count" aria-live="polite">{len(examples)} examples</p></div>'
        '<div class="eg-chips" hidden></div>'
        f'<div class="eg-grid">{cards}</div>'
        '<p class="eg-empty" hidden>No examples match. '
        '<button type="button" class="eg-clear">Clear filters</button> or '
        f'<a class="eg-site-search" href="{escape(site_search)}">search the whole site</a>.</p>'
        "</div>"
    )


def add_examples_section(app: Sphinx, doctree: nodes.document) -> None:
    """Append an Examples section to every platform and tool page an example points to."""
    docname = app.env.current_document.docname
    if not examples_on(app.env, docname):
        return
    section = nodes.section(ids=["workflow-examples"], names=["examples"])
    section += nodes.title("Examples", "Examples")
    section += examples_placeholder(kind="section")
    # Inside the page's top-level section, so it sits under the page title in the TOC
    (doctree.next_node(nodes.section) or doctree).append(section)


def render_section(app: Sphinx, docname: str) -> str:
    env = app.env
    examples = examples_on(env, docname)
    cards = "".join(
        card(env, example, app.builder.get_relative_uri(docname, example.docname))
        for example in examples[:SECTION_CARDS]
    )
    more = ""
    if len(examples) > SECTION_CARDS:
        gallery = app.builder.get_relative_uri(docname, "examples/index")
        query = "search" if docname.startswith("tools/") else "platform"
        value = page_label(env, docname) if query == "search" else docname
        more = (
            f'<p class="eg-see-all"><a href="{escape(gallery)}?{query}={escape(value)}">'
            f"See all {len(examples)} {escape(page_label(env, docname))} examples →</a></p>"
        )
    return f'<div class="eg-grid">{cards}</div>{more}'


def render_placeholders(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    for node in list(doctree.findall(examples_placeholder)):
        if app.builder.format != "html":
            node.replace_self([])
            continue
        render = render_gallery if node["kind"] == "gallery" else render_section
        node.replace_self(nodes.raw("", render(app, docname), format="html"))


def add_about_context(app: Sphinx, pagename: str, templatename, context, doctree):
    """Rows for the "About this example" block, each value linking to the filtered gallery."""
    example = next((e for e in app.env.rapids_examples if e.docname == pagename), None)
    if example is None:
        return
    env = app.env
    vocabulary = env.rapids_vocabulary
    gallery = app.builder.get_relative_uri(pagename, "examples/index")

    def filtered(facet, values, labels):
        return [
            (labels.get(value, value), f"{gallery}?{facet}={value}") for value in values
        ]

    rows = [
        (
            "Platform",
            [(page_label(env, d), f"{gallery}?platform={d}") for d in example.platform],
        ),
        (
            "Tools",
            [
                (page_label(env, d), app.builder.get_relative_uri(pagename, d))
                for d in example.tools
            ],
        ),
        ("Library", filtered("library", example.library, library_labels(vocabulary))),
        ("Task", filtered("task", example.task, vocabulary["task"])),
        ("Scale", filtered("scale", [example.scale], vocabulary["scale"])),
        *(
            (FACETS[facet], filtered(facet, getattr(example, facet), vocabulary[facet]))
            for facet in ADVANCED_FACETS
        ),
        (
            "Topics",
            [(topic, f"{gallery}?search={quote(topic)}") for topic in example.topics],
        ),
    ]
    context["example_about"] = [(heading, links) for heading, links in rows if links]


def setup(app: Sphinx) -> dict:
    app.add_directive("examplegallery", ExampleGallery)
    app.connect("html-page-context", add_about_context)
    app.connect("env-get-outdated", load_examples)
    # Before Sphinx's TOC collector (priority 500) so the section shows in "On this page"
    app.connect("doctree-read", add_examples_section, priority=400)
    app.connect("doctree-resolved", render_placeholders)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
