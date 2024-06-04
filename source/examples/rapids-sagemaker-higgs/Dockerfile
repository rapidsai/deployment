ARG RAPIDS_IMAGE

FROM $RAPIDS_IMAGE as rapids

# Installs a few more dependencies
# (cxx-compiler is necessary because 'sagemaker-training' is only available as a source distribution)
RUN conda install --yes -n base \
        cupy \
        cxx-compiler \
        flask \
        protobuf \
        sagemaker \
 && pip install sagemaker-training

# Copies the training code inside the container
COPY rapids-higgs.py /opt/ml/code/rapids-higgs.py

# Defines rapids-higgs.py as script entry point
ENV SAGEMAKER_PROGRAM rapids-higgs.py

# O
