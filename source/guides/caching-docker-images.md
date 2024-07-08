# Caching Docker Images For Autoscaling Workloads

The [Dask Autoscaler](https://kubernetes.dask.org/en/latest/operator_resources.html#daskautoscaler) leverages Dask's adaptive mode and allows the scheduler to scale the number of workers up and down based on the task graph.

However, when the Dask cluster is scaling up and down, there are no assurances that the new worker pod will be scheduled on the same node from which a worker pod was previously removed. When scheduling on a new node, the cluster pull penalty will have to be paid when downloading the Docker image.

## Using a Daemonset to cache images

A [Daemonset](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) in Kubernetes ensures that all nodes run a copy of a pod. We will create a Daemonset with the RAPIDS image, ensuring that Dask worker pods created with this image will not be stuck in pending state when tasks are scheduled.

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

This Daemonset is created in the `image-cache` namespace. In the `initContainers` section, we specify the image to be pulled to the cluster. Any known command that will exit successfully can be used. And the `pause` container ensures that the pod goes into a Running phase but does not take up resources on the container.

Upon applying this Daemonset, once all the pre-puller pods are in Running state, you know that the images have been pulled on all nodes. When the Kubernetes cluster is scaled, images will be pulled automatically on any new nodes added as well.
