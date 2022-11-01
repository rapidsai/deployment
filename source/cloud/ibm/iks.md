# IBM Kubernetes Service (IKS)

RAPIDS can be deployed on IBM Cloud via IBM Cloud managed Kubernetes service (IKS) using any of the [supported Kubernetes installation methods](../../platforms/kubernetes).

## Install pre-requisites

Install and configure dependencies in your local environment: [kubectl](https://kubernetes.io/docs/tasks/tools/), [helm](https://helm.sh/), [IBM cloud cli](https://cloud.ibm.com/docs/cli?topic=cli-getting-started) and [IBM Kubernetes Service (KS) plugin](https://cloud.ibm.com/docs/containers?topic=containers-cs_cli_install).

## Login to IBM CLI

```shell
$ ibmcloud login -a cloud.ibm.com -r <region>
$ ibmcloud target -g <resource group>
```

```{note}
You can list regions with `$ ibmcloud regions` and resource groups with `$ ibmcloud resource groups`.
```

## Create a Kubernetes cluster

```shell
$ ibmcloud ks cluster create classic \
    --name <CLUSTER_NAME> \
    --zone dal10 \
    --flavor gx2-8x64x1v100 \
    --hardware dedicated \
    --workers 1 \
    --version <kubernetes_version>
```

`<CLUSTER_NAME>` = Name of the IKS cluster. This will be auto generated if not specified. <br>
`<kubernetes_version>` = Kubernetes version, the tested version for this deployment is 1.21.14. <br>

Upon successful creation, you would get the cluster id, note that down, it will be required in the next step to connect to the cluster.

## Connect to the cluster

```shell
$ ibmcloud ks cluster config --cluster <cluster_id>
```

`<cluster_id>` = When creating the cluster using IBM KS CLI, use that cluster id to connect to the cluster.

## Install GPU drivers

```shell
$ helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
$ helm repo update
$ helm install --wait --generate-name \
     -n gpu-operator --create-namespace \
     nvidia/gpu-operator
```

## Install RAPIDS

Follow any of the [Kubernetes installation methods to install and use RAPIDS](../../platforms/kubernetes).

## Delete the cluster

When you are finished delete the Kubernetes cluster.

Before you delete the cluster you need to manually delete services running in the cluster with external IPs to release network resources.

```shell
$ kubectl get svc --all-namespaces
$ kubectl delete svc <SERVICE_NAME>
```

`<SERVICE_NAME>` = Name of the services which have an `EXTERNAL-IP` value.

Delete the cluster and its associated nodes.

```shell
$ ibmcloud ks cluster rm --cluster <cluster_name_or_ID>
```
