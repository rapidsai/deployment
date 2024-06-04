ARG RAPIDS_IMAGE

FROM $RAPIDS_IMAGE as rapids

ENV AWS_DATASET_DIRECTORY="10_year"
ENV AWS_ALGORITHM_CHOICE="XGBoost"
ENV AWS_ML_WORKFLOW_CHOICE="multiGPU"
ENV AWS_CV_FOLDS="10"

# ensure printed output/log-messages retain correct order
ENV PYTHONUNBUFFERED=True

# install a few more dependencies
# (cxx-compiler is necessary because 'sagemaker-training' is only available as a source distribution)
RUN conda install --yes -n base \
        cupy \
        cxx-compiler \
        flask \
        protobuf \
        sagemaker \
 && pip install sagemaker-training

# path where SageMaker looks for code when container runs in the cloud
ENV CLOUD_PATH="/opt/ml/code"

# copy our latest [local] code into the container
COPY . $CLOUD_PATH

# make the entrypoint script executable
RUN chmod +x $CLOUD_PATH/entrypoint.sh

WORKDIR $CLOUD_PATH
ENTRYPOINT ["./entrypoint.sh"]
