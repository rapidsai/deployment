"""
Publish this build to docs.nvidia.com: configure the navbar version switcher
and write the files CI needs, only when ``rapids_docs_publishing`` is enabled
(conf.py turns it on for CI builds).

The switcher is populated by the browser from ``<rapids_docs_url>/versions.json``
and highlights the entry whose ``version`` matches this build (the nightly
version on main, shown as "latest"; the stable version on a release).

After the HTML build, everything below lands in ``build/publish``:

    publish.env     TARGET=26.08 / latest, the directory this build publishes
                    to, read by the workflow into step outputs
    versions.json   data for the navbar version switcher: "latest" first, then
                    every released version (from ``rapids_docs_release_tags``,
                    the repository's git tags) at or above
                    ``rapids_docs_first_version``, newest first and marked preferred

``versions.json`` is skipped for a patch release of an older version, so an
old checkout can never overwrite the "latest" label with a stale value.
"""

import json
import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from sphinx.util import logging

if TYPE_CHECKING:
    import sphinx

logger = logging.getLogger(__name__)

RELEASE_TAG = re.compile(r"^v(\d\d\.\d\d)\.\d\d$")


def _as_tuple(version: str) -> tuple[int, ...]:
    """``"26.08"`` -> ``(26, 8)``, so versions compare numerically rather than as text."""
    return tuple(int(part) for part in version.split("."))


def released_versions(tags: list[str], first_version: str) -> list[str]:
    """``YY.MM`` of every release tag at or above ``first_version``, newest first."""
    versions = {match.group(1) for match in map(RELEASE_TAG.match, tags) if match}
    versions = {v for v in versions if _as_tuple(v) >= _as_tuple(first_version)}
    return sorted(versions, key=_as_tuple, reverse=True)


def versions_json(
    docs_url: str, latest_version: str, released: list[str]
) -> list[dict]:
    """Switcher entries: ``latest`` first, then ``released``, its newest marked preferred."""
    entries = [{"name": v, "url": f"{docs_url}/{v}/", "version": v} for v in released]
    if entries:
        entries[0]["preferred"] = "true"
    return [
        {"name": "latest", "url": f"{docs_url}/latest/", "version": latest_version},
        *entries,
    ]


def configure_switcher(_app: "sphinx.application.Sphinx", config) -> None:
    """Point the theme's version switcher at versions.json for publishing builds."""
    # config-inited handlers receive (app, config); only the config is needed here
    if not config.rapids_docs_publishing:
        return
    config.html_theme_options["switcher"] = {
        "json_url": f"{config.rapids_docs_url.rstrip('/')}/versions.json",
        "version_match": config.rapids_version["rapids_version"],
    }
    # CI builds with -W; do not let a failed fetch of versions.json fail the build.
    config.html_theme_options["check_switcher"] = False


def write_publish_files(app: "sphinx.application.Sphinx", exception) -> None:
    """After a publishing build, write build/publish/{publish.env,versions.json} for CI."""
    if exception is not None or app.builder.format != "html":
        return
    if not app.config.rapids_docs_publishing:
        return

    docs_url = app.config.rapids_docs_url.rstrip("/")
    version = app.config.rapids_version["rapids_version"]
    stable = app.config.rapids_version["rapids_api_docs_version"] == "stable"
    target = version if stable else "latest"

    publish_dir = Path(app.outdir).parent / "publish"
    shutil.rmtree(publish_dir, ignore_errors=True)
    publish_dir.mkdir(parents=True)

    released = released_versions(
        app.config.rapids_docs_release_tags, app.config.rapids_docs_first_version
    )
    if stable and version not in released:
        # the tag that triggered a release build must be visible, or the switcher
        # would silently omit the version being published
        logger.warning(
            "no release tag v%s.* found at or above rapids_docs_first_version=%s",
            version,
            app.config.rapids_docs_first_version,
        )
    # A patch release of an older version leaves the switcher data alone.
    write_versions = not (stable and released and version != released[0])
    if write_versions:
        data = versions_json(docs_url, app.config.rapids_docs_latest_version, released)
        (publish_dir / "versions.json").write_text(json.dumps(data, indent=2) + "\n")

    (publish_dir / "publish.env").write_text(
        f"TARGET={target}\nVERSIONS_JSON={str(write_versions).lower()}\n"
    )


def setup(app: "sphinx.application.Sphinx") -> dict:
    """Register the ``rapids_docs_*`` config values and hook into the build."""
    app.add_config_value("rapids_docs_publishing", False, "html")
    app.add_config_value("rapids_docs_url", "", "html")
    app.add_config_value("rapids_docs_first_version", "", "html")
    app.add_config_value("rapids_docs_latest_version", "", "html")
    app.add_config_value("rapids_docs_release_tags", [], "html")
    app.connect("config-inited", configure_switcher)
    app.connect("build-finished", write_publish_files)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
