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
  --accelerator type=nvidia-tesla-a100,count=2,gpu-driver-version=disabled --machine-type a2-highgpu-2g \
  --zone us-central1-c --release-channel stable \
  --node-labels="gke-no-default-nvidia-gpu-device-plugin=true"
```

With this command, you’ve launched a GKE cluster called `rapids-gpu-kubeflow` with nodes of type `a2-highgpu-2g`, which has two A100 GPUs. GKE's automatic GPU driver installation and default NVIDIA GPU device plugin are disabled so that the [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/google-gke.html) can configure the GPU stack that RAPIDS needs.

````{note}
After creating your cluster, if you get a message saying

```text
CRITICAL: ACTION REQUIRED: gke-gcloud-auth-plugin, which is needed for continued use of kubectl, was not found or is not
executable. Install gke-gcloud-auth-plugin for use with kubectl by following https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl#install_plugin
```
You will need to install the `gke-gcloud-auth-plugin` to be able to get the credentials. To do so,

```bash
$ gcloud components install gke-gcloud-auth-plugin
```
````

## Get the cluster credentials

```bash
$ gcloud container clusters get-credentials rapids-gpu-kubeflow \
    --zone us-central1-c
```

With this command, your `kubeconfig` is updated with credentials and endpoint information for the `rapids-gpu-kubeflow` cluster.

## Install GPU drivers and Operator

Create a namespace for the NVIDIA GPU Operator.

```bash
$ kubectl create ns gpu-operator
```

Create a resource quota for critical GPU Operator Pods.

```bash
kubectl apply -n gpu-operator -f - << EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: gpu-operator-quota
spec:
  hard:
    pods: 100
  scopeSelector:
    matchExpressions:
    - operator: In
      scopeName: PriorityClass
      values:
        - system-node-critical
        - system-cluster-critical
EOF
```

Install the Google driver installer DaemonSet. This command is for Container-Optimized OS nodes, which GKE uses by default. For Ubuntu nodes, use the Ubuntu driver installer manifest from the [GKE manual driver installation documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus#installing_drivers).

```bash
$ kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
$ kubectl rollout status daemonset/nvidia-driver-installer -n kube-system --timeout=300s
```

Install the NVIDIA GPU Operator with the GKE-specific driver and toolkit paths.

```bash
$ helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
$ helm repo update
$ helm install --wait gpu-operator \
  -n gpu-operator \
  nvidia/gpu-operator \
  --version=v26.3.2 \
  --set hostPaths.driverInstallDir=/home/kubernetes/bin/nvidia \
  --set toolkit.installDir=/home/kubernetes/bin/nvidia \
  --set cdi.enabled=true \
  --set cdi.default=true \
  --set driver.enabled=false
```

```{note}
On GKE 1.33 and later, NVIDIA documents a known `containerd` configuration issue that can prevent GPU Operator toolkit Pods from starting. If you hit this, follow NVIDIA's `RUNTIME_CONFIG_SOURCE=file` ClusterPolicy workaround in the [NVIDIA GPU Operator with Google GKE prerequisites](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/google-gke.html#prerequisites).
```

Verify that the GPU Operator Pods are running.

```console
$ kubectl get pods -n gpu-operator
NAME                                                         READY   STATUS      RESTARTS   AGE
gpu-operator-5c7cf8b4f6-bx4rg                               1/1     Running     0          11m
nvidia-container-toolkit-daemonset-vr8fv                    1/1     Running     0          8m
nvidia-cuda-validator-4nljj                                 0/1     Completed   0          2m
nvidia-device-plugin-daemonset-jfbcj                        1/1     Running     0          8m
nvidia-operator-validator-fcrr6                             1/1     Running     0          8m
```

Verify that GPUs are allocatable on the node.

```console
$ kubectl get nodes -o=custom-columns='NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu'
NAME                                                  GPU
gke-rapids-gpu-kubeflow-default-pool-00000000-0000   2
```

Once the GPU Operator Pods are running and GPUs are allocatable, you are ready to test your cluster.

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
