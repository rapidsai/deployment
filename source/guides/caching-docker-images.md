# Caching Docker Images For Autoscaling Workloads

The [Dask Autoscaler](https://kubernetes.dask.org/en/latest/operator_resources.html#daskautoscaler) leverages Dask's adaptive mode and allows the scheduler to scale the number of workers up and down based on the task graph.

When scaling the Dask cluster up or down, there is no guarantee that newly created worker Pods will be scheduled on the same node as previously removed workers. As a result, when a new node is allocated for a worker Pod, the cluster will incur a pull penalty due to the need to download the Docker image.

## Using a Daemonset to cache images

To guarantee that each node runs a consistent workload, we will deploy a Kubernetes [DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) utilizing the RAPIDS image. This DaemonSet will prevent Dask worker Pods created from this image from entering a pending state when tasks are scheduled.

This is an example manifest to deploy a Daemonset with the RAPIDS container.

```yaml
#caching-daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: prepuller
  namespace: image-cache
spec:
  selector:
    matchLabels:
      name: prepuller
  template:
    metadata:
      labels:
        name: prepuller
    spec:
      initContainers:
        - name: prepuller-1
          image: "{{ rapids_container }}"
          command: ["sh", "-c", "'true'"]

      containers:
        - name: pause
          image: gcr.io/google_containers/pause:3.2
          resources:
            limits:
              cpu: 1m
              memory: 8Mi
            requests:
              cpu: 1m
              memory: 8Mi
```

You can create this Daemonset with `kubectl`.

```console
$ kubectl apply -f caching-daemonset.yaml
```

The DaemonSet is deployed in the `image-cache` namespace. In the `initContainers` section, we specify the image to be pulled and cached within the cluster, utilizing any executable command that terminates successfully. Additionally, the `pause` container is used to ensure the Pod transitions into a Running state without consuming resources or running any processes.

When deploying the DaemonSet, after all pre-puller Pods are running successfully, you can confirm that the images have been cached across all nodes in the cluster. As the Kubernetes cluster is scaled up or down, the DaemonSet will automatically pull and cache the necessary images on any newly added nodes, ensuring consistent image availability throughout
