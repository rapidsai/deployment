For kafka deployment

we will deploy Kafka in AWS EKS using Strimzi with KRaft mode.

Step 1:

- Deploy strimzi operator

```bash
kubectl create -f 'https://strimzi.io/install/latest?namespace=default'
```

Step 2: Deploy Apache Kafka in KRaft Mode

get kafka-single-node.yaml from [https://strimzi.io/examples/latest/kafka/kafka-single-node.yaml](https://strimzi.io/examples/latest/kafka/kafka-single-node.yaml)

or

```bash
curl -o kafka-single-node.yaml https://raw.githubusercontent.com/strimzi/strimzi-kafka-operator/refs/tags/0.46.0/examples/kafka/kafka-single-node.yaml
```

modify the name of the cluster and the size of the volume to 5Gi the default 100Gi
and it's too much.

Notice that we don't need to create a service since strimzi created `<cluster-name>-kafka-bootstrap`

to connect to it, in our case we can connect from another pod in the same namespace

as `kafka-cluster-kafka-bootstrap:9092`

if we are in a diff namespace

`kafka-cluster-kafka-bootstrap.<namespace>.svc.cluster.local:9092`

we have `kafka-create-topics.yaml`

which allows us to create topics via strimzi operator.
input: here we will constantly write from our producer pod and results will host the results
after pipeline (ideally use via UI)

create cluster with eks

eksctl create cluster morpheus-rapids \
 --profile eks \
 --version 1.32 \
--nodes 3 \
 --node-type=g4dn.xlarge \
 --timeout=40m \
 --ssh-access \
 --ssh-public-key nclementi_eks_rapids_testing \
 --region us-east-1 \
 --zones=us-east-1c,us-east-1b,us-east-1d \
 --auto-kubeconfig

aws eks --region us-east-1 update-kubeconfig --name morpheus-rapids --profile eks

make gp2 default EDIT: we are running on ephemeral storage now due to permissions

```bash
kubectl patch storageclass gp2 -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

kubectl port-forward svc/kafka-ui 8080:80
