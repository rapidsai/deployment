# IBM Kubernetes Service (IKS)

RAPIDS can be deployed on IBM Cloud via IBM Cloud managed Kubernetes service (IKS) using Helm. More details can be found at our **[helm docs.](https://helm.rapids.ai/docs/csp.html)**

**1. Install.** Install and configure dependencies in your local environment: kubectl, helm, IBM cloud cli and IBM Kubernetes Service (KS) plugin.

**2. Login to IBM CLI.** Login to IBM cloud on CLI using below command.

```shell
$ ibmcloud login -a cloud.ibm.com -r <region> -g <resource-group-name>
```

**3. Create your cluster:**

```shell
$ ibmcloud ks cluster create classic 
    --name <CLUSTER_NAME> \
    --zone dal10 \
    --flavor gx2-8x64x1v100 \
    --hardware dedicated \ 
    --workers 1 \
    --version <kubernetes_version> \
```

<CLUSTER_NAME> = Name of the IKS cluster. This will be auto generated if not specified. <br>
<kubernetes_version> = Kubernetes version, the tested version for this deployment is 1.21.14. <br>

Upon successful creation, you would get the cluster id, note that down, it would be required in next step to connect to the cluster.

**4. Connect your cluster:**

```shell
$ ibmcloud ks cluster config --cluster <cluster-id>
```
<cluster-id> = When creating the cluster using IBM KS CLI, use that cluster id to connect to the cluster.

**5. Install GPU addon:**

```shell
$ kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/1.0.0-beta4/nvidia-device-plugin.yml
```

**6. Install RAPIDS helm repo:**

```shell
$ helm repo add rapidsai https://helm.rapids.ai
$ helm repo update
```

**7. Install helm chart:**

```shell
$ helm install --set dask.scheduler.serviceType="LoadBalancer" --set dask.jupyter.serviceType="LoadBalancer" rapidstest rapidsai/rapidsai
```

**8. Accessing your cluster:**

```shell
$ kubectl get svc
NAME                TYPE          CLUSTER-IP      EXTERNAL-IP                                                               PORT(S)                         AGE
kubernetes          ClusterIP     10.100.0.1      <none>                                                                    443/TCP                         12m
rapidsai-jupyter    LoadBalancer  10.100.251.155  a454a9741455544cfa37fc4ac71caa53-868718558.us-east-1.elb.amazonaws.com    80:30633/TCP                    85s
rapidsai-scheduler  LoadBalancer  10.100.11.182   a9c703f1c002f478ea60d9acaf165bab-1146605388.us-east-1.elb.amazonaws.com   8786:30346/TCP,8787:32444/TCP   85s
```

**9. Delete the cluster:** List and delete services running in the cluster to release resources

```shell
$ kubectl get svc --all-namespaces
$ kubectl delete svc <SERVICE_NAME>
```

<SERVICE_NAME> = Name of the services which have an EXTERNAL-IP value and are required to be removed to release resources.

Delete the cluster and its associated nodes

```shell
$ ibmcloud ks cluster rm --cluster <cluster_name_or_ID>
```

**9. Uninstall the helm chart:**

```shell
$ helm uninstall rapidstest
```
