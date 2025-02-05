ARG RAPIDS_IMAGE

FROM $RAPIDS_IMAGE as rapids

# Installs a few more dependencies
RUN conda install --yes -n base \
        cupy \
        flask \
        protobuf \
        'sagemaker-python-sdk>=2.239.0'

# Copies the training code inside the container
COPY rapids-higgs.py /opt/ml/code/rapids-higgs.py

# Defines rapids-higgs.py as script entry point
# ref: https://docs.aws.amazon.com/sagemaker/latest/dg/adapt-training-container.html
ENV SAGEMAKER_PROGRAM rapids-higgs.py

# override entrypoint from the base image with one that accepts
# 'train' and 'serve' (as SageMaker expects to provide)
COPY entrypoint.sh /opt/entrypoint.sh
ENTRYPOINT ["/opt/entrypoint.sh"]
