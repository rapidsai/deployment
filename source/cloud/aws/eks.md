---
review_priority: "p1"
---

# AWS Elastic Kubernetes Service (EKS)

RAPIDS can be deployed on AWS via the [Elastic Kubernetes Service](https://aws.amazon.com/eks/) (EKS).

To run RAPIDS you'll need a Kubernetes cluster with GPUs available.

## Prerequisites

First you'll need to have the [`aws` CLI tool](https://aws.amazon.com/cli/) and [`eksctl` CLI
tool](https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html) installed along with
[`kubectl`](https://kubernetes.io/docs/tasks/tools/), [`helm`](https://helm.sh/docs/intro/install/), for managing
Kubernetes.

Ensure you are logged into the `aws` CLI.

```console
$ aws configure
```

## Create the Kubernetes cluster

Now we can launch a GPU enabled EKS cluster with `eksctl`.

```{note}
1. You will need to create or import a public SSH key to be able to execute the following command.
In your aws console under `EC2` in the side panel under Network & Security > Key Pairs, you can create a
key pair or import (see "Actions" dropdown) one you've created locally.

2. If you are not using your default AWS profile, add `--profile <your-profile>` to the following command.
```

```console
$ eksctl create cluster rapids \
                      --version 1.30 \
                      --nodes 3 \
                      --node-type=g4dn.xlarge \
                      --timeout=40m \
                      --ssh-access \
                      --ssh-public-key <public key ID> \  # Name assigned during creation of your key in aws console
                      --region us-east-1 \
                      --zones=us-east-1c,us-east-1b,us-east-1d \
                      --auto-kubeconfig
```

With this command, you’ve launched an EKS cluster called `rapids`. You’ve specified that it should use nodes of type
`p3.8xlarge`. We also specified that we don't want to install the NVIDIA drivers as we will do that with the NVIDIA
operator.

To access the cluster we need to pull down the credentials.
Add `--profile <your-profile>` if you are not using the default profile.

```console
$ aws eks --region us-east-1 update-kubeconfig --name rapids
```

## Install drivers

As we selected a GPU node type EKS will automatically install drivers for us. We can verify this by listing the NVIDIA
driver plugin Pods.

```console
$ kubectl get po -n kube-system -l name=nvidia-device-plugin-ds
NAME                                   READY   STATUS    RESTARTS   AGE
nvidia-device-plugin-daemonset-kv7t5   1/1     Running   0          52m
nvidia-device-plugin-daemonset-rhmvx   1/1     Running   0          52m
nvidia-device-plugin-daemonset-thjhc   1/1     Running   0          52m
```

```{note}
By default this plugin will install the latest version on the NVIDIA drivers on every Node. If you need more control
over your driver installation we recommend that when creating your cluster you set
`eksctl create cluster --install-nvidia-plugin=false ...` and then install drivers yourself using the [NVIDIA GPU
Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/getting-started.html).
```

After you have confirmed your drivers are installed, you are ready to test your cluster.

```{include} ../../_includes/check-gpu-pod-works.md

```

## Install RAPIDS

Now that you have a GPU enabled Kubernetes cluster on EKS you can install RAPIDS with [any of the supported
methods](../../platforms/kubernetes).

## Clean up

You can also delete the EKS cluster to stop billing with the following command.

```console
$ eksctl delete cluster --region=us-east-1 --name=rapids
Deleting cluster rapids...⠼
```

```{relatedexamples}

```
