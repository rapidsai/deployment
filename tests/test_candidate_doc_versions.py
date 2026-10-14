from pathlib import Path
import runpy

import pytest


CONF_PATH = Path(__file__).parents[1] / "source" / "conf.py"


def load_conf() -> dict:
    return runpy.run_path(str(CONF_PATH))


def test_candidate_docs_use_train_frozen_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAPIDS_RELEASE_CANDIDATE_VERSION", "26.12")
    monkeypatch.setenv("DEPLOYMENT_DOCS_BUILD_STABLE", "false")

    config = load_conf()

    assert config["rapids_version"]["rapids_version"] == "26.12"
    assert config["rapids_version"]["rapids_pip_version"] == "26.12"
    assert "rapids=26.12" in config["rapids_version"]["rapids_conda_packages"]
    assert config["rapids_version"]["rapids_container"].endswith(":26.12-cuda13-py3.13")


def test_non_candidate_doc_version_selection_is_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RAPIDS_RELEASE_CANDIDATE_VERSION", raising=False)
    monkeypatch.setenv("DEPLOYMENT_DOCS_BUILD_STABLE", "false")

    config = load_conf()

    assert config["rapids_version"]["rapids_version"] == "26.12"
    assert config["rapids_version"]["rapids_api_docs_version"] == "nightly"


def test_candidate_docs_reject_malformed_frozen_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RAPIDS_RELEASE_CANDIDATE_VERSION", "26.12.0")

    with pytest.raises(ValueError, match="must be YY.MM"):
        load_conf()
