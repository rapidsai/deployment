---
review_priority: "p1"
---

# AWS Elastic Kubernetes Service (EKS)

RAPIDS can be deployed on AWS via the [Elastic Kubernetes Service](https://aws.amazon.com/eks/) (EKS).

To run RAPIDS you'll need a Kubernetes cluster with GPUs available.

## Prerequisites

First you'll need to have the [`aws` CLI tool](https://aws.amazon.com/cli/) and [`eksctl` CLI tool](https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html) installed along with [`kubectl`](https://kubernetes.io/docs/tasks/tools/) for managing Kubernetes.

Ensure you are logged into the `aws` CLI.

```bash
$ aws configure
```

## Create the Kubernetes cluster

Now we can launch a GPU enabled EKS cluster with `eksctl`.

```{note}
1. You will need to create or import a public SSH key to be able to execute the following command.
In your aws console under `EC2` in the side panel under Network & Security > Key Pairs, you can create a
key pair or import (see "Actions" dropdown) one you've created locally.

2. If you are not using your default AWS profile, add `--profile <your-profile>` to the following command.

3. The `--ssh-public-key` argument is the name assigned during creation of your key in AWS console.
```

```bash
$ eksctl create cluster rapids \
                      --nodes 3 \
                      --node-type=g4dn.xlarge \
                      --timeout=40m \
                      --ssh-access \
                      --ssh-public-key <public key ID> \
                      --region us-east-1 \
                      --zones=us-east-1c,us-east-1b,us-east-1d \
                      --auto-kubeconfig
```

With this command, you've launched an EKS cluster called `rapids`. You've specified that it should use nodes of type `g4dn.xlarge`, which include one NVIDIA T4 GPU each.

When `eksctl` sees an NVIDIA GPU instance type, it selects the correct [EKS-optimized accelerated AMI](https://docs.aws.amazon.com/eks/latest/userguide/ml-eks-optimized-ami.html) and installs the [NVIDIA Kubernetes device plugin](https://docs.aws.amazon.com/eks/latest/eksctl/gpu-support.html) automatically. The EKS-optimized NVIDIA AMI includes the NVIDIA driver, CUDA user-mode driver, and the NVIDIA Container Toolkit.

To access the cluster we need to pull down the credentials.
Add `--profile <your-profile>` if you are not using the default profile.

```bash
$ aws eks --region us-east-1 update-kubeconfig --name rapids
```

## Verify GPU support

Verify that the NVIDIA device plugin Pods are running.

```console
$ kubectl get po -n kube-system -l name=nvidia-device-plugin-ds
NAME                                   READY   STATUS    RESTARTS   AGE
nvidia-device-plugin-daemonset-kv7t5   1/1     Running   0          52m
nvidia-device-plugin-daemonset-rhmvx   1/1     Running   0          52m
nvidia-device-plugin-daemonset-thjhc   1/1     Running   0          52m
```

```{note}
If you need to manage the NVIDIA device plugin version yourself, set `eksctl create cluster --install-nvidia-plugin=false ...` when creating the cluster and then install the device plugin manually. If you choose to install the [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/getting-started.html) on EKS-optimized NVIDIA AMIs, disable the operator's driver and toolkit installation because those components are already included in the AMI.
```

After you have confirmed the device plugin is running, you are ready to test your cluster.

```{include} ../../_includes/check-gpu-pod-works.md

```

## Install RAPIDS

Now that you have a GPU enabled Kubernetes cluster on EKS you can install RAPIDS with [any of the supported methods](../../platforms/kubernetes).

## Clean up

You can also delete the EKS cluster to stop billing with the following command.

```console
$ eksctl delete cluster --region=us-east-1 --name=rapids
Deleting cluster rapids...⠼
```

```{relatedexamples}

```
