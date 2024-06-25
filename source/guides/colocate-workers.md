# Colocate Dask workers on Kubernetes while using nodes with multiple GPUs

To optimize performance when working with nodes that have multiple GPUs, a best practice is to schedule Dask workers in a tightly grouped manner, thereby minimizing communication overhead between worker pods. This guide provides a step-by-step process for adding pod affinities to worker pods ensuring they are scheduled together as much as possible on Google Kubernetes Engine (GKE), but the principles can be adapted for use with other Kubernetes distributions.

## Prerequisites

First you'll need to have the [`gcloud` CLI tool](https://cloud.google.com/sdk/gcloud) installed along with [`kubectl`](https://kubernetes.io/docs/tasks/tools/), [`helm`](https://helm.sh/docs/intro/install/), etc for managing Kubernetes.

Ensure you are logged into the `gcloud` CLI.

```console
$ gcloud init
```

## Create the Kubernetes cluster

Now we can launch a GPU enabled GKE cluster.

```console
$ gcloud container clusters create rapids-gpu \
  --accelerator type=nvidia-tesla-a100,count=2 --machine-type a2-highgpu-2g \
  --zone us-central1-c --release-channel stable
```

With this command, you’ve launched a GKE cluster called `rapids-gpu`. You’ve specified that it should use nodes of type
a2-highgpu-2g, each with two A100 GPUs.

## Install drivers

Next, [install the NVIDIA drivers](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus#installing_drivers) onto each node.

```console
$ kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded-latest.yaml
daemonset.apps/nvidia-driver-installer created
```

Verify that the NVIDIA drivers are successfully installed.

```console
$ kubectl get po -A --watch | grep nvidia
kube-system   nvidia-driver-installer-6zwcn                                 1/1     Running   0         8m47s
kube-system   nvidia-driver-installer-8zmmn                                 1/1     Running   0         8m47s
kube-system   nvidia-driver-installer-mjkb8                                 1/1     Running   0         8m47s
kube-system   nvidia-gpu-device-plugin-5ffkm                                1/1     Running   0         13m
kube-system   nvidia-gpu-device-plugin-d599s                                1/1     Running   0         13m
kube-system   nvidia-gpu-device-plugin-jrgjh                                1/1     Running   0         13m
```

After your drivers are installed, you are ready to test your cluster.

```{include} ../_includes/check-gpu-pod-works.md

```

### Installing Dask operator with Helm

The operator has a Helm chart which can be used to manage the installation of the operator. Follow the instructions provided in the [Dask documention](https://kubernetes.dask.org/en/latest/installing.html#installing-with-helm), or alternatively can be installed via:

```console
$ helm install --create-namespace -n dask-operator --generate-name --repo https://helm.dask.org dask-kubernetes-operator
NAME: dask-kubernetes-operator-1666875935
NAMESPACE: dask-operator
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Operator has been installed successfully.
```

## Configuring a RAPIDS `DaskCluster`

To configure the `DaskCluster` resource to run RAPIDS you need to set a few things:

- The container image must contain RAPIDS, the [official RAPIDS container images](/tools/rapids-docker) are a good choice for this.
- The Dask workers must be configured with one or more NVIDIA GPU resources.
- The worker command must be set to `dask-cuda-worker`.

## Creating a RAPIDS `DaskCluster` using `kubectl`

Here is an example resource manifest for launching a RAPIDS Dask cluster with worker pod affinity

```yaml
# rapids-dask-cluster.yaml
apiVersion: kubernetes.dask.org/v1
kind: DaskCluster
metadata:
  name: rapids-dask-cluster
  labels:
    dask.org/cluster-name: rapids-dask-cluster
spec:
  worker:
    replicas: 2
    spec:
      containers:
        - name: worker
          image: { { rapids_container } }
          imagePullPolicy: "IfNotPresent"
          args:
            - dask-cuda-worker
            - --name
            - $(DASK_WORKER_NAME)
          resources:
            limits:
              nvidia.com/gpu: "1"
      affinity:
        podAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: dask.org/component
                      operator: In
                      values:
                        - worker
                topologyKey: kubernetes.io/hostname
  scheduler:
    spec:
      containers:
        - name: scheduler
          image: { { rapids_container } }
          imagePullPolicy: "IfNotPresent"
          env:
          args:
            - dask-scheduler
          ports:
            - name: tcp-comm
              containerPort: 8786
              protocol: TCP
            - name: http-dashboard
              containerPort: 8787
              protocol: TCP
          readinessProbe:
            httpGet:
              port: http-dashboard
              path: /health
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              port: http-dashboard
              path: /health
            initialDelaySeconds: 15
            periodSeconds: 20
          resources:
            limits:
              nvidia.com/gpu: "1"
    service:
      type: ClusterIP
      selector:
        dask.org/cluster-name: rapids-dask-cluster
        dask.org/component: scheduler
      ports:
        - name: tcp-comm
          protocol: TCP
          port: 8786
          targetPort: "tcp-comm"
        - name: http-dashboard
          protocol: TCP
          port: 8787
          targetPort: "http-dashboard"
```

You can create this cluster with `kubectl`.

```console
$ kubectl apply -f rapids-dask-cluster.yaml
```

### Manifest breakdown

Most of this manifest is explained in the [Dask Operator](https://docs.rapids.ai/deployment/stable/tools/kubernetes/dask-operator/#example-using-kubecluster) documentation in the tools section of the RAPIDS documentation.

The only addition made to the example from the above documentation page is the following section in the worker configuration

```yaml
# ...
affinity:
podAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
        podAffinityTerm:
        labelSelector:
            matchExpressions:
            - key: dask.org/component
                operator: In
                values:
                - worker
        topologyKey: kubernetes.io/hostname
# ...
```

For the Dask Worker pod configuration, we are setting a pod affinity using the name of the node as the topology key. [Pod affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#inter-pod-affinity-and-anti-affinity) in Kubernetes allows you to constrain which nodes the Pod can be scheduled on and allows you to configure a set of workloads that should be co-located in the same defined topology, in this case, preferring to place two worker pods on the same node. This is also intended to be a soft requirement as we are using the `preferredDuringSchedulingIgnoredDuringExecution` type of pod affinity. The Kubernetes scheduler tries to find a node which meets the rule. If a matching node is not available, the Kubernetes scheduler still schedules the pod on any available node. This ensures that you will not face any issues with the Dask cluster even if placing worker pods on nodes already in use is not possible.

### Accessing your Dask cluster

Once you have created your `DaskCluster` resource we can use `kubectl` to check the status of all the other resources it created for us.

```console
$ kubectl get all -l dask.org/cluster-name=rapids-dask-cluster -o wide
NAME                                                                 READY   STATUS    RESTARTS   AGE   IP           NODE                                         NOMINATED NODE   READINESS GATES
pod/rapids-dask-cluster-default-worker-12a055b2db-7b5bf8f66c-9mb59   1/1     Running   0          2s    10.244.2.3   gke-rapids-gpu-1-default-pool-d85b49-2545    <none>           <none>
pod/rapids-dask-cluster-default-worker-34437735ae-6fdd787f75-sdqzg   1/1     Running   0          2s    10.244.2.4   gke-rapids-gpu-1-default-pool-d85b49-2545    <none>           <none>
pod/rapids-dask-cluster-scheduler-6656cb88f6-cgm4t                   0/1     Running   0          3s    10.244.3.3   gke-rapids-gpu-1-default-pool-d85b49-2f31    <none>           <none>

NAME                                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE   SELECTOR
service/rapids-dask-cluster-scheduler   ClusterIP   10.96.231.110   <none>        8786/TCP,8787/TCP   3s    dask.org/cluster-name=rapids-dask-cluster,dask.org/component=scheduler
```

Here you can see our scheduler pod and two worker pods along with the scheduler service. The two worker pods are placed in the same node as desired, while the scheduler pod is placed on a different node.

If you have a Python session running within the Kubernetes cluster (like the [example one on the Kubernetes page](/platforms/kubernetes)) you should be able
to connect a Dask distributed client directly.

```python
from dask.distributed import Client

client = Client("rapids-dask-cluster-scheduler:8786")
```

Alternatively if you are outside of the Kubernetes cluster you can change the `Service` to use [`LoadBalancer`](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) or [`NodePort`](https://kubernetes.io/docs/concepts/services-networking/service/#type-nodeport) or use `kubectl` to port forward the connection locally.

```console
$ kubectl port-forward svc/rapids-dask-cluster-service 8786:8786
Forwarding from 127.0.0.1:8786 -> 8786
```

```python
from dask.distributed import Client

client = Client("localhost:8786")
```

## Example using `KubeCluster`

In additon to creating clusters via `kubectl` you can also do so from Python with {class}`dask_kubernetes.operator.KubeCluster`. This class implements the Dask Cluster Manager interface and under the hood creates and manages the `DaskCluster` resource for you. You can also generate a spec with make_cluster_spec() which KubeCluster uses internally and then modify it with your custom options. We will use this to add node affinity to the scheduler.
In the following example, the same cluster configuration as the `kubectl` example is used.

```python
from dask_kubernetes.operator import KubeCluster, make_cluster_spec

spec = make_cluster_spec(
    name="rapids-dask-cluster",
    image={{ rapids_container }},
    n_workers=2,
    resources={"limits": {"nvidia.com/gpu": "1"}},
    worker_command="dask-cuda-worker",
)
```

To add the node affinity to the worker, you can create a custom dictionary specifying the type of pod affinity and the topology key.

```python
affinity_config = {
    "podAffinity": {
        "preferredDuringSchedulingIgnoredDuringExecution": [
            {
                "weight": 100,
                "podAffinityTerm": {
                    "labelSelector": {
                        "matchExpressions": [
                            {
                                "key": "dask.org/component",
                                "operator": "In",
                                "values": ["worker"],
                            }
                        ]
                    },
                    "topologyKey": "kubernetes.io/hostname",
                },
            }
        ]
    }
}
```

Now you can add this configuration to the spec created in the previous step, and create the Dask cluster using this custom spec.

```python
spec["spec"]["worker"]["spec"]["affinity"] = affinity_config
cluster = KubeCluster(custom_cluster_spec=spec)
```

If we check with `kubectl` we can see the above Python generated the same `DaskCluster` resource as the `kubectl` example above.

```console
$ kubectl get daskclusters
NAME                  AGE
rapids-dask-cluster   3m28s

$ kubectl get all -l dask.org/cluster-name=rapids-dask-cluster -o wide
NAME                                                                 READY   STATUS    RESTARTS   AGE   IP           NODE                                         NOMINATED NODE   READINESS GATES
pod/rapids-dask-cluster-default-worker-12a055b2db-7b5bf8f66c-9mb59   1/1     Running   0          2s    10.244.2.3   gke-rapids-gpu-1-default-pool-d85b49-2545    <none>           <none>
pod/rapids-dask-cluster-default-worker-34437735ae-6fdd787f75-sdqzg   1/1     Running   0          2s    10.244.2.4   gke-rapids-gpu-1-default-pool-d85b49-2545    <none>           <none>
pod/rapids-dask-cluster-scheduler-6656cb88f6-cgm4t                   0/1     Running   0          3s    10.244.3.3   gke-rapids-gpu-1-default-pool-d85b49-2f31    <none>           <none>

NAME                                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE   SELECTOR
service/rapids-dask-cluster-scheduler   ClusterIP   10.96.231.110   <none>        8786/TCP,8787/TCP   3s    dask.org/cluster-name=rapids-dask-cluster,dask.org/component=scheduler
```

With this cluster object in Python we can also connect a client to it directly without needing to know the address as Dask will discover that for us. It also automatically sets up port forwarding if you are outside of the Kubernetes cluster.

```python
from dask.distributed import Client

client = Client(cluster)
```

This object can also be used to scale the workers up and down.

```python
cluster.scale(5)
```

And to manually close the cluster.

```python
cluster.close()
```

```{note}
By default the `KubeCluster` command registers an exit hook so when the Python process exits the cluster is deleted automatically. You can disable this by setting `KubeCluster(..., shutdown_on_close=False)` when launching the cluster.

This is useful if you have a multi-stage pipeline made up of multiple Python processes and you want your Dask cluster to persist between them.

You can also connect a `KubeCluster` object to your existing cluster with `cluster = KubeCluster.from_name(name="rapids-dask")` if you wish to use the cluster or manually call `cluster.close()` in the future.
```
