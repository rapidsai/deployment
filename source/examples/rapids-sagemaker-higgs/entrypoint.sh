#!/bin/bash

# [description]
#
# SageMaker runs your image like 'docker run train'.
# ref: https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html#your-algorithms-inference-code-run-image
#
# This entrypoint is used to override the entrypoint in the base image, to ensure
# that that works as expected.
#

set -e

if [[ "$1" == "train" ]]; then
    echo -e "@ entrypoint -> launching training script \n"
    # 'train' entrypoint is defined by 'pip install sagemaker-training'
    train "${@}"
else
    echo -e "@ entrypoint -> did not recognize option '${1}' \n"
    exit 1
fi
