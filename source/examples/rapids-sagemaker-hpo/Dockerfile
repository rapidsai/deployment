FROM rapidsai/base:24.06a-cuda11.8-py3.10 

ENV AWS_DATASET_DIRECTORY="10_year"
ENV AWS_ALGORITHM_CHOICE="XGBoost"
ENV AWS_ML_WORKFLOW_CHOICE="multiGPU"
ENV AWS_CV_FOLDS="10"

# ensure printed output/log-messages retain correct order
ENV PYTHONUNBUFFERED=True
    
# install a few more dependencies
RUN conda install --yes -n base \
        cupy \
        flask \
        protobuf \
        sagemaker

# path where SageMaker looks for code when container runs in the cloud
ENV CLOUD_PATH="/opt/ml/code"

# copy our latest [local] code into the container 
COPY . $CLOUD_PATH

WORKDIR $CLOUD_PATH
ENTRYPOINT ["./entrypoint.sh"]

# ensure printed output/log-messages retain correct order
ENV PYTHONUNBUFFERED=True
    
# install a few more dependencies
RUN conda install --yes -n base \
        cupy \
        flask \
        protobuf \
        sagemaker

# path where SageMaker looks for code when container runs in the cloud
ENV CLOUD_PATH="/opt/ml/code"

# copy our latest [local] code into the container 
COPY . $CLOUD_PATH

WORKDIR $CLOUD_PATH
ENTRYPOINT ["./entrypoint.sh"]
