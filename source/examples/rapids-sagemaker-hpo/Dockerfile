ARG RAPIDS_IMAGE

FROM $RAPIDS_IMAGE as rapids

ENV AWS_DATASET_DIRECTORY="10_year"
ENV AWS_ALGORITHM_CHOICE="XGBoost"
ENV AWS_ML_WORKFLOW_CHOICE="multiGPU"
ENV AWS_CV_FOLDS="10"

# ensure printed output/log-messages retain correct order
ENV PYTHONUNBUFFERED=True

# add sagemaker-training-toolkit [ requires build tools ], flask [ serving ], and dask-ml
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && source activate rapids \
    && pip3 install sagemaker-training cupy-cuda11x flask dask-ml \
    && pip3 install --upgrade protobuf

# path where SageMaker looks for code when container runs in the cloud
ENV CLOUD_PATH="/opt/ml/code"

# copy our latest [local] code into the container
COPY . $CLOUD_PATH

# make the entrypoint script executable
RUN chmod +x $CLOUD_PATH/entrypoint.sh

WORKDIR $CLOUD_PATH
ENTRYPOINT ["./entrypoint.sh"]
