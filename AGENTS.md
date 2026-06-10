# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Project Overview

This is the **RAPIDS Deployment Documentation** repository - a Sphinx-based documentation site that provides deployment guides, platform-specific instructions, and workflow examples for running RAPIDS (GPU-accelerated data science libraries) across various cloud platforms, HPC environments, and containerized systems.

## Build Commands

### Development

```bash
# Install dependencies (creates .venv and installs from uv.lock)
uv venv && uv sync --locked

# Build and auto-reload docs with live server at http://127.0.0.1:8000
uv run sphinx-autobuild -b dirhtml source build/html

# Clear build cache
uv run make clean

# Build static site to build/html
uv run make dirhtml

# Build with warnings as errors (CI mode)
uv run make dirhtml SPHINXOPTS="-W --keep-going -n"
```

### Dependency Management

```bash
# Upgrade dependencies (updates uv.lock)
uv lock --upgrade
```

## Linting and Pre-commit

This project uses **pre-commit** to enforce code quality automatically:

```bash
# Install pre-commit hooks
pre-commit install

# Run linters manually on all files
pre-commit run --all-files
```

Linters used:

- **black** and **black-jupyter** - Python code formatting
- **prettier** - Markdown, JSON, YAML formatting
- **markdownlint** - Markdown style consistency
- **ruff** - Python linting (pycodestyle, pyflakes, isort, pyupgrade, flake8-bugbear)
- **shellcheck** - Shell script validation
- **codespell** - Spell checking

## Repository Architecture

### Documentation Structure

```text
source/
├── cloud/               # Cloud provider deployment guides (AWS, Azure, GCP, IBM, NVIDIA)
├── platforms/           # Platform integrations (Databricks, Kubeflow, Snowflake, etc.)
├── examples/            # Jupyter notebook workflow examples (galleries with tags)
├── guides/              # Technical guides (MIG, InfiniBand, scheduler optimizations)
├── tools/               # Documentation for dask-cuda and Kubernetes tools
├── developer/           # Developer resources (CI/CD with RAPIDS)
├── _includes/           # Reusable markdown snippets
├── _static/             # Static assets (CSS, JS, images)
├── _templates/          # Jinja2 templates for Sphinx
└── conf.py              # Sphinx configuration
```

### Custom Sphinx Extensions

Located in `extensions/` directory. These are critical to the documentation system:

1. **rapids_version_templating.py** - Jinja2 templating for version substitution
   - Allows `{{ rapids_container }}` or `~~~rapids_api_docs_version~~~` in docs
   - Pulls versions from `conf.py` `versions` dict
   - Use `{{ ... }}` for text, `~~~...~~~` for URLs

2. **rapids_related_examples.py** - Notebook gallery and cross-linking system
   - Reads tags from first cell of Jupyter notebooks
   - Tags are hierarchical (e.g., `cloud/aws/sagemaker`)
   - Creates `relatedexamples` directive to show notebooks with matching tags
   - Powers the example gallery with filtering by tag namespace

3. **rapids_notebook_files.py** - Discovers supporting files for notebooks
   - Auto-lists Dockerfiles, scripts, configs alongside notebooks

4. **rapids_grid_toctree.py** - Grid layout for table of contents

5. **rapids_admonitions.py** - Custom admonitions like `docref`

### Notebook Examples System

Example notebooks live in `source/examples/{example-name}/notebook.ipynb`:

**Critical Requirements:**

- First cell must be markdown with at least one `#` heading
- Add hierarchical tags to first cell metadata (e.g., `cloud/aws/eks`, `tools/dask`)
- Tags create bidirectional links: notebooks appear on tagged doc pages, doc pages appear on notebook pages
- Add notebook path to `notebookgallerytoctree` in `source/examples/index.md`
- Supporting files (Dockerfiles, scripts) go in same directory and are auto-discovered

**Tag Organization:**

- Root namespace becomes filter category (e.g., `cloud`, `platform`, `tools`)
- Full tag path shows in UI (e.g., `cloud/aws/sagemaker`)
- Keep root namespaces consistent to avoid UI clutter
- Custom tag CSS can be added in `source/_static/css/custom.css` as `.tag-{name}`

### Version Management

The `versions` dict in `source/conf.py` manages RAPIDS versions:

```python
versions = {
    "stable": {
        "rapids_version": "25.12",
        "rapids_container": "nvcr.io/nvidia/rapidsai/base:25.12-cuda12-py3.13",
        ...
    },
    "nightly": {
        "rapids_version": "26.02",
        "rapids_container": "rapidsai/base:26.02a-cuda12-py3.13",
        ...
    }
}
```

- Builds use `nightly` by default (local dev, PR previews, main branch)
- Set `DEPLOYMENT_DOCS_BUILD_STABLE=true` to use `stable` (done automatically on tag builds)
- Before release: update both `stable` (new release) and `nightly` (next version)

## Releasing

Docs are continuously deployed via `.github/workflows/build-and-deploy.yml`:

- **main branch** → `deployment/nightly` at docs.rapids.ai
- **tags** → `deployment/stable` at docs.rapids.ai

To release:

```bash
export RELEASE=x.x.x  # e.g., 25.12.0 (see https://docs.rapids.ai/resources/versions/)

# Update versions in source/conf.py first, then:
git commit --allow-empty -m "Release $RELEASE"
git tag -a $RELEASE -m "Version $RELEASE"
git push upstream --tags
```

## Writing Guidelines

### Markdown Style

- Use **MyST Markdown** (not reStructuredText)
- Follow [Kubernetes style guide](https://kubernetes.io/docs/contribute/style/style-guide/) for API objects (use `UpperCamelCase`: `Pod`, `Deployment`, not `pod`)
- Use `console` blocks for commands with output (start lines with `$`)
- Use `bash` blocks for scripts or commands without output
- Add custom `docref` admonitions to link to related pages:

````markdown
```{docref} /cloud/gcp/gke
For detailed GKE setup, see the documentation.
```
````

### Code Formatting

- Python notebooks: formatted with **black-jupyter** (line length 120)
- Python extensions: must pass **ruff** checks
- Never include sensitive info (API keys, tokens) in examples

## CI/CD

- **pre-commit.yml** - Runs linters on all PRs
- **build-and-deploy.yml** - Builds docs and deploys to S3/CloudFront on push to main or tags

Test your changes match CI expectations by running:

```bash
uv run make clean && uv run make dirhtml SPHINXOPTS="-W --keep-going -n"
```

This treats warnings as errors (`-W`), continues on errors (`--keep-going`), and enables nitpicky mode (`-n`).
