#!/bin/bash
# Copyright (c) 2024-2025, NVIDIA CORPORATION.
###############################
# Deployment Version Updater #
###############################

## Usage
# bash update-version.sh <new_version>

# Format is YY.MM.PP - no leading 'v' or trailing 'a'
NEXT_FULL_TAG=$1

# Get <major>.<minor> for next version
NEXT_MAJOR=$(echo "$NEXT_FULL_TAG" | awk '{split($0, a, "."); print a[1]}')
NEXT_MINOR=$(echo "$NEXT_FULL_TAG" | awk '{split($0, a, "."); print a[2]}')
NEXT_SHORT_TAG=${NEXT_MAJOR}.${NEXT_MINOR}

# Calculate the next nightly version
NEXT_MINOR_INT=$((10#$NEXT_MINOR))
NEXT_NIGHTLY_MINOR=$((NEXT_MINOR_INT + 2))
NEXT_NIGHTLY_MINOR=$(printf "%02d" $NEXT_NIGHTLY_MINOR)
NEXT_NIGHTLY_TAG=${NEXT_MAJOR}.${NEXT_NIGHTLY_MINOR}

echo "Preparing release $NEXT_FULL_TAG with next nightly version $NEXT_NIGHTLY_TAG"

# Inplace sed replace; workaround for Linux and Mac
function sed_runner() {
    sed -i.bak ''"$1"'' "$2" && rm -f "${2}".bak
}

# Update stable_version and nightly_version in conf.py
sed_runner "s/stable_version = \"[0-9.]*\"/stable_version = \"${NEXT_SHORT_TAG}\"/" source/conf.py
sed_runner "s/nightly_version = \"[0-9.]*\"/nightly_version = \"${NEXT_NIGHTLY_TAG}\"/" source/conf.py

# Update container references in README.md
sed_runner "s/\"rapids_container\": \"nvcr.io\/nvidia\/rapidsai\/base:[0-9.]*-/\"rapids_container\": \"nvcr.io\/nvidia\/rapidsai\/base:${NEXT_SHORT_TAG}-/" README.md
sed_runner "s/\"rapids_container\": \"rapidsai\/base:[0-9.]*a-/\"rapids_container\": \"rapidsai\/base:${NEXT_NIGHTLY_TAG}a-/" README.md

echo "Version update complete"
