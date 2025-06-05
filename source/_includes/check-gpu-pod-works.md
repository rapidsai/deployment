Let's create a sample Pod that uses some GPU compute to make sure that everything is working as expected.

```bash
cat << EOF | kubectl create -f -
apiVersion: v1
kind: Pod
metadata:
  name: cuda-vectoradd
spec:
  restartPolicy: OnFailure
  containers:
  - name: cuda-vectoradd
    image: "nvidia/samples:vectoradd-cuda11.6.0-ubuntu18.04"
    resources:
       limits:
         nvidia.com/gpu: 1
EOF
```

```console
$ kubectl logs pod/cuda-vectoradd
[Vector addition of 50000 elements]
Copy input data from the host memory to the CUDA device
CUDA kernel launch with 196 blocks of 256 threads
Copy output data from the CUDA device to the host memory
Test PASSED
Done
```

If you see `Test PASSED` in the output, you can be confident that your Kubernetes cluster has GPU compute set up correctly.

Next, clean up that Pod.

```console
$ kubectl delete pod cuda-vectoradd
pod "cuda-vectoradd" deleted
```
