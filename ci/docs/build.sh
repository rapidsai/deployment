#!/bin/bash
# Copyright (c) 2020-2022, NVIDIA CORPORATION.
#################################
# RAPIDS Deployment Docs build script for CI #
#################################

if [ -z "$PROJECT_WORKSPACE" ]; then
    echo ">>>> ERROR: Could not detect PROJECT_WORKSPACE in environment"
    echo ">>>> WARNING: This script contains git commands meant for automated building, do not run locally"
    exit 1
fi

export DOCS_WORKSPACE="$WORKSPACE/docs"
export PROJECTS=(deployment)

export PATH=/conda/bin:/usr/local/cuda/bin:$PATH
. /opt/conda/etc/profile.d/conda.sh
conda activate rapids

make html

#Commit to Website
cd $DOCS_WORKSPACE

for PROJECT in ${PROJECTS[@]}; do
    mkdir -p api/$PROJECT/$BRANCH_VERSION
    rm -rf $DOCS_WORKSPACE/api/$PROJECT/$BRANCH_VERSION/*
done


mv $PROJECT_WORKSPACE/build/html/* $DOCS_WORKSPACE/api/deployment/$BRANCH_VERSION