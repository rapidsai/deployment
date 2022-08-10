Kubernetes
==========

RAPIDS integrates with Kubernetes in many ways depending on your use case.

## Interactive Notebook

For single-user interactive sessions you can run the [RAPIDS docker image](/tools/rapids-docker) which contains a conda environment with the RAPIDS libraries and Jupyter for interactive use.

You can run this directly on Kubernetes as a `Pod` and expose Jupyter via a `Service`. For example:

```yaml
# rapids-notebook.yaml
apiVersion: v1
kind: Service
metadata:
  name: rapids-notebook
  labels:
    app: rapids-notebook
spec:
  type: NodePort
  ports:
  - port: 8888
    name: http
    targetPort: 8888
    nodePort: 30002
  selector:
    app: rapids-notebook
---
apiVersion: v1
kind: Pod
metadata:
  name: rapids-notebook
  labels:
    app: rapids-notebook
spec:
  securityContext:
    fsGroup: 0
  containers:
  - name: rapids-notebook
    image: rapidsai/rapidsai-core:22.06-cuda11.5-runtime-ubuntu20.04-py3.9
    resources:
      limits:
        nvidia.com/gpu: 1
    ports:
    - containerPort: 8888
      name: notebook
```

```console
$ kubectl apply -f rapids-notebook.yaml
```

This makes Jupyter accessible on port `30002` of your Kubernetes nodes via `NodePort` service. Alternatvely you could use a `LoadBalancer` service type [if you have one configured](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/) or a `ClusterIP` and use `kubectl` to port forward the port locally and access it that way.

```console
$ kubectl port-forward service/rapids-notebook 8888
```

Then you can open port `8888` in your browser to access Jupyter and use RAPIDS.


```{figure} /images/kubernetes-jupyter.png
---
alt: Screenshot of the RAPIDS container running Jupyter showing the nvidia-smi command with a GPU listed
---
```

## Helm Chart

TODO

## Dask Operator

TODO

## Dask Gateway

TODO
