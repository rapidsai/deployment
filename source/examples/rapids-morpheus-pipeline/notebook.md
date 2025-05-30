# Deploying an End-to-End Kafka Streaming SI Detection Pipeline with cuDF, Morpheus, and Triton on EKS

In this example workflow, we demonstrate how to deploy an NVIDIA GPU-accelerated streaming
pipeline for Sensitive Information (SI) detection using [Morpheus](https://docs.nvidia.com/morpheus/), [cuDF](https://docs.rapids.ai/api/cudf/stable/), and [Triton
Inference Server](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/) on [Amazon EKS](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html).

We build upon the existing Morpheus
[NLP SI Detection example](https://docs.nvidia.com/morpheus/examples/nlp_si_detection/readme.html)
and enhance it to showcase a production-style end-to-end deployment integrated with Apache Kafka
for data streaming.

This extended pipeline can be found in [in this github repository](https://github.com/rapidsai/deployment/source/examples/rapids-morpheus-pipeline/scripts/pipeline-dockerfile/run_pipeline_kafka.py) includes the following components:

- **Kafka Data Streaming Source Stage**: We introduce Apache Kafka for streaming data. A custom
  Kafka producer was created to continuously publish network data to a Kafka topic.

- **cuDF Message Filtering Stage**: The data stream first flows through a message filtering stage
  that leverages `cuDF` to preprocess and filter messages based on custom logic.
  [stage code here](https://github.com/rapidsai/deployment/source/examples/rapids-morpheus-pipeline/scripts/pipeline-dockerfile/message_filter_stage.py)

- **SI Detection with Morpheus and Triton**: The filtered data passes through multiple stages to
  prepare data for inference, perform the inference and classify the data. We use Morpheus' provided NLP SI Detection
  model to identify potentially sensitive information in the network packet data. For more details on the model
  check the original example on the [Morpheus documentation](https://docs.nvidia.com/morpheus/examples/nlp_si_detection/readme.html#background)

- **cuDF Network Traffic Analysis Stage**: We incorporate an additional analysis stage using `cuDF` to perform
  some network traffic analytics for enriched context and anomaly detection. [Stage code here](https://github.com/rapidsai/deployment/source/examples/rapids-morpheus-pipeline/scripts/pipeline-dockerfile/network_traffic_analyzer_stage.py)

- **Kafka Output Sink**: Finally, the processed and enriched data, with SI detection results
  and traffic insights, is published to a downstream Kafka topic for further processing, alerting,
  or storage.

The entire pipeline is containerized and deployed on **Amazon EKS**, leveraging Kubernetes
for orchestration, scalability, and resiliency in a cloud-native environment.

## Deployment Components

The pipeline is deployed on Amazon EKS using several Kubernetes manifests:

### Kafka Deployment (`k8s/kafka`)

The Kafka cluster is deployed using the [Strimzi Operator](https://strimzi.io/), which simplifies Kafka deployment and
management on Kubernetes. See instructions on section [Deploying on EKS](deploying-on-eks)

The deployment configuration includes:

- Kafka cluster setup `kafka-single-node.yaml`

  This is a modification of the file [https://strimzi.io/examples/latest/kafka/kafka-single-node.yaml](https://strimzi.io/examples/latest/kafka/kafka-single-node.yaml) where we modify:

  - Cluster name to `kafka-cluster`
  - Modify the volume to use `type: ephemeral` and use `sizeLimit: 5Gi` (instead of `size: 100Gi` that corresponded to
    `type: persistent-claim`)

- Kafka topics setup
- Kafka UI

### Kafka Producer Deployment (`k8s/kafka-producer`)

The Kafka producer is deployed as a separate pod using the `kafka-producer.yaml` manifest. It continuously generates
and publishes network data to the Kafka topic. This producer script is containerized using a custom Docker image that can be built using the Dockerfile in the `scripts/producer-dockerfile` directory.

- Uses `kafka-python` for message production.
- Contains the producer script for generating network data.

### Triton-Morpheus Deployment (`k8s/triton`)

The inference server is deployed using the NVIDIA Morpheus- Triton Inference Server docker image
`nvcr.io/nvidia/morpheus/morpheus-tritonserver-models:25.02`.

### Morpheus Pipeline Deployment (`k8s/morpheus-pipeline`)

The core processing pipeline is deployed as a separate pod that, uses an image that can be built using the Dockerfile in
the `pipeline-dockerfile` directory.

- Runs the Morpheus nightly 25.06 conda build
- Contains all pipeline and stage scripts `scripts/pipeline-dockerfile/*.py`
- Processes the streaming data through the various stages

(deploying-on-eks)=

## Deploying on EKS

### Prerequisites

You need to have the [`aws` CLI tool](https://aws.amazon.com/cli/) and [`eksctl` CLI tool](https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html) installed along with [`kubectl`](https://kubernetes.io/docs/tasks/tools/) for managing Kubernetes.

### Launch GPU enabled EKS cluster

We launch a GPU enabled EKS cluster with `eksctl`.

```{note}
1. You will need to create or import a public SSH key to be able to execute the following command.
In your aws console under `EC2` in the side panel under Network & Security > Key Pairs, you can create a
key pair or import (see "Actions" dropdown) one you've created locally.

2. If you are not using your default AWS profile, add `--profile <your-profile>` to the following command.
```

```console
$ eksctl create cluster morpheus-rapids \
    --version 1.32 \
    --nodes 2 \
    --node-type=g4dn.xlarge \
    --timeout=40m \
    --ssh-access \
    --ssh-public-key  <public key ID> \  # Name assigned during creation of your key in aws console\
    --region us-east-1 \
    --zones=us-east-1c,us-east-1b,us-east-1d \
    --auto-kubeconfig
```

To access the cluster we need to pull down the credentials. Add `--profile <your-profile>` if you are not using the
default profile.

```console
$ aws eks --region us-east-1 update-kubeconfig --name morpheus-rapids
```

### Deploy the Strimzi Operator

Strimzi is an open-source project that provides a way to run Apache Kafka on Kubernetes. It
simplifies the deployment and management of Kafka clusters by providing Kubernetes operators that
handle the complex tasks of setting up and maintaining Kafka.

We use `kubectl` to deploy teh operator. In our case we are deploying everything on the default
namespace, and the entire pipeline is design for that.

```console
$ kubectl create -f 'https://strimzi.io/install/latest?namespace=default'
```

### Deploy the pipeline

Get all the files in
[https://github.com/rapidsai/deployment/source/examples/rapids-morpheus-pipeline/k8s](https://github.com/rapidsai/deployment/source/examples/rapids-morpheus-pipeline/k8s)

Then do

```console
$ kubectl apply -f k8s --recursive
```

This will take ~15min to get all teh pods up and running, you will see for a while that the the `morpheus-pipeline` pod
fails and try to reconcile. This happens because the triton inference pod takes a while to get up and running.

### Kafka UI: checking the pipeline results

Once all the pods are running. You can check the input topic and the results topic in the kafka ui

```console
$ kubectl port-forward svc/kafka-ui 8080:80
```

In your browser go to `http://localhost:8080/` and you will see:

![Kafka UI demo](path/to/the.gif)

## Conclusion

This example demonstrates how to build and deploy a production-like, GPU-accelerated streaming pipeline for sensitive
information detection using NVIDIA RAPIDS, Morpheus, and Triton Inference Server on Amazon EKS while integrating Apache Kafka
for data streaming capabilities. This architecture showcases how modern streaming technologies combine with GPU-accelerated
inference to create efficient, production-grade solutions for sensitive information detection.
