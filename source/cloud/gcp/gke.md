---
review_priority: "p1"
---

# Google Kubernetes Engine

RAPIDS can be deployed on Google Cloud via the [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine) (GKE).

To run RAPIDS you'll need a Kubernetes cluster with GPUs available.

## Prerequisites

First you'll need to have the [`gcloud` CLI tool](https://cloud.google.com/sdk/gcloud) installed along with [`kubectl`](https://kubernetes.io/docs/tasks/tools/), [`helm`](https://helm.sh/docs/intro/install/), etc for managing Kubernetes.

Ensure you are logged into the `gcloud` CLI.

```bash
$ gcloud init
```

## Create the Kubernetes cluster

Now we can launch a GPU enabled GKE cluster.

```bash
$ gcloud container clusters create rapids-gpu-kubeflow \
  --accelerator type=nvidia-tesla-a100,count=2,gpu-driver-version=latest --machine-type a2-highgpu-2g \
  --zone us-central1-c --release-channel stable
```

With this command, you’ve launched a GKE cluster called `rapids-gpu-kubeflow`. You’ve specified that it should use nodes of type a2-highgpu-2g, each with two A100 GPUs, along with the latest GPU drivers for the current GKE version.

````{note}
After creating your cluster, if you get a message saying

```text
CRITICAL: ACTION REQUIRED: gke-gcloud-auth-plugin, which is needed for continued use of kubectl, was not found or is not
executable. Install gke-gcloud-auth-plugin for use with kubectl by following https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl#install_plugin
```
you will need to install the `gke-gcloud-auth-plugin` to be able to get the credentials. To do so,

```bash
$ gcloud components install gke-gcloud-auth-plugin
```
````

## Get the cluster credentials

```bash
$ gcloud container clusters get-credentials rapids-gpu-kubeflow \
    --region=us-central1-c
```

With this command, your `kubeconfig` is updated with credentials and endpoint information for the `rapids-gpu-kubeflow` cluster.

## Verify drivers

Verify that the NVIDIA drivers are successfully installed.

```console
$ kubectl get po -A --watch | grep nvidia
kube-system          nvidia-gpu-device-plugin-medium-cos-h5kkz                       2/2     Running   0          3m42s
kube-system          nvidia-gpu-device-plugin-medium-cos-pw89w                       2/2     Running   0          3m42s
kube-system          nvidia-gpu-device-plugin-medium-cos-wdnm9                       2/2     Running   0          3m42s
```

After GPU device plugin pods are in running state, you are ready to test your cluster.

```{include} ../../_includes/check-gpu-pod-works.md

```

## Install RAPIDS

Now that you have a GPU enables Kubernetes cluster on GKE you can install RAPIDS with [any of the supported methods](../../platforms/kubernetes).

## Clean up

You can also delete the GKE cluster to stop billing with the following command.

```console
$ gcloud container clusters delete rapids-gpu-kubeflow --zone us-central1-c
Deleting cluster rapids...⠼
```

```{relatedexamples}

```
