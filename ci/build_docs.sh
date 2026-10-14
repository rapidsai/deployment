#!/usr/bin/env bash

# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

# Keep the candidate build command aligned with the normal deployment docs job.
# The shared candidate workflow disables public publishing and stages the
# rendered build/dirhtml tree as a private, cataloged artifact afterward.
RAPIDS_DOCS_RELEASE_TAGS="$(git tag --list)" uv run make dirhtml SPHINXOPTS="-W --keep-going -n"
