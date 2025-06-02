# KServe

[KServe](https://kserve.github.io/website) is a standard model inference platform built for Kubernetes. It provides
consistent interface for multiple machine learning frameworks. In this page, we will show you how to deploy RAPIDS
models using KServe.

```{note}
These instructions were tested against KServe v0.10 running on [Kubernetes
v1.21](https://kubernetes.io/blog/2021/04/08/kubernetes-1-21-release-announcement/).
```

## Setting up Kubernetes cluster with GPU access

First, you should set up a Kubernetes cluster with access to NVIDIA GPUs. Visit [the Cloud Section](/cloud/index) for
guidance.

## Installing KServe

Visit [Getting Started with KServe](https://kserve.github.io/website/latest/get_started/) to install KServe in your
Kubernetes cluster. If you are starting out, we recommend the use of the "Quickstart" script (`quick_install.sh`)
provided in the page. On the other hand, if you are setting up a production-grade system, follow direction in
[Administration Guide](https://kserve.github.io/website/latest/admin/serverless/serverless) instead.

## Setting up First InferenceService

Once KServe is installed, visit [First
InferenceService](https://kserve.github.io/website/latest/get_started/first_isvc/) to quickly set up a first inference
endpoint. (The example uses the [Support Vector Machine from
scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html) to classify [the Iris
dataset](https://scikit-learn.org/stable/auto_examples/datasets/plot_iris_dataset.html).) Follow through all the steps
carefully and make sure everything works. In particular, you should be able to submit inference requests using cURL.

## Setting up InferenceService with Triton-FIL

[The FIL backend for Triton Inference Server](https://github.com/triton-inference-server/fil_backend) (Triton-FIL in
short) is an optimized inference runtime for many kinds of tree-based models including: XGBoost, LightGBM, scikit-learn,
and cuML RandomForest. We can use Triton-FIL together with KServe and serve any tree-based models.

The following manifest sets up an inference endpoint using Triton-FIL:

```yaml
# triton-fil.yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: triton-fil
spec:
  predictor:
    triton:
      storageUri: gs://path-to-gcloud-storage-bucket/model-directory
      runtimeVersion: 22.12-py3
```

where `model-directory` is set up with the following hierarchy:

```text
model-directory/
\__ model/
   \__ config.pbtxt
   \__ 1/
      \__ [model file goes here]
```

where `config.pbtxt` contains the configuration for the Triton-FIL backend.
A typical `config.pbtxt` is given below, with explanation interspersed as
`#` comments. Before use, make sure to remove `#` comments and fill in
the blanks.

```text
backend: "fil"
max_batch_size: 32768
input [
  {
    name: "input__0"
    data_type: TYPE_FP32
    dims: [ ___ ]   # Number of features (columns) in the training data
  }
]
output [
 {
    name: "output__0"
    data_type: TYPE_FP32
    dims: [ 1 ]
  }
]

instance_group [{ kind: KIND_AUTO }]
    # Triton-FIL will intelligently choose between CPU and GPU

parameters [
  {
    key: "model_type"
    value: { string_value: "_____" }
      # Can be "xgboost", "xgboost_json", "lightgbm", or "treelite_checkpoint"
      # See subsections for examples
  },
  {
    key: "output_class"
    value: { string_value: "____" }
      # true (if classifier), or false (if regressor)
  },
  {
    key: "threshold"
    value: { string_value: "0.5" }
      # Threshold for predicing the positive class in a binary classifier
  }
]

dynamic_batching {}
```

We will show you concrete examples below. But first some general notes:

- The payload JSON will look different from the First InferenceService example:

```json
{
  "inputs" : [
    {
      "name" : "input__0",
      "shape" : [ 1, 6 ],
      "datatype" : "FP32",
      "data" : [0, 0, 0, 0, 0, 0]
  ],
  "outputs" : [
    {
      "name" : "output__0",
      "parameters" : { "classification" : 2 }
    }
  ]
}
```

- Triton-FIL uses v2 version of KServe protocol, so make sure to use `v2` URL when sending inference request:

```console
$ INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
$ INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway \
  -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')
$ SERVICE_HOSTNAME=$(kubectl get inferenceservice <endpoint name> -n kserve-test \
  -o jsonpath='{.status.url}' | cut -d "/" -f 3)

$ curl -v -H "Host: ${SERVICE_HOSTNAME}" -H "Content-Type: application/json" \
  "http://${INGRESS_HOST}:${INGRESS_PORT}/v2/models/<endpoint name>/infer" \
  -d @./payload.json
```

### XGBoost

To deploy an XGBoost model, save it using the JSON format:

```python
import xgboost as xgb

clf = xgb.XGBClassifier(...)
clf.fit(X, y)
clf.save_model("my_xgboost_model.json")  # Note the .json extension
```

Rename the model file to `xgboost.json`, as this is convention used by Triton-FIL.
After moving the model file into the model directory, the directory should look like this:

```text
model-directory/
\__ model/
   \__ config.pbtxt
   \__ 1/
      \__ xgboost.json
```

In `config.pbtxt`, set `model_type="xgboost_json"`.

### cuML RandomForest

To deploy a cuML random forest, save it as a Treelite checkpoint file:

```python
from cuml.ensemble import RandomForestClassifier as cumlRandomForestClassifier

clf = cumlRandomForestClassifier(...)
clf.fit(X, y)
clf.convert_to_treelite_model().to_treelite_checkpoint("./checkpoint.tl")
```

Rename the checkpoint file to `checkpoint.tl`, as this is convention used by Triton-FIL. After moving the model file
into the model directory, the directory should look like this:

```text
model-directory/
\__ model/
   \__ config.pbtxt
   \__ 1/
      \__ checkpoint.tl
```

### Configuring Triton-FIL

Triton-FIL offers many configuration options, and we only showed you a few of them. Please visit [FIL Backend Model
Configuration](https://github.com/triton-inference-server/fil_backend/blob/main/docs/model_config.md) to check out the
rest.
