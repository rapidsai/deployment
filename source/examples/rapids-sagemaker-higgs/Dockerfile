ARG RAPIDS_IMAGE

FROM $RAPIDS_IMAGE as rapids

RUN apt-get update && apt-get install -y --no-install-recommends build-essential

RUN source activate rapids && pip install sagemaker-training

# Copies the training code inside the container
COPY rapids-higgs.py /opt/ml/code/rapids-higgs.py

# Defines rapids-higgs.py as script entry point
ENV SAGEMAKER_PROGRAM rapids-higgs.py
