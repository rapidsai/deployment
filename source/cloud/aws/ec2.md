---
review_priority: "p1"
---

# Elastic Compute Cloud (EC2)

## Create Instance

Create a new [EC2 Instance](https://aws.amazon.com/ec2/) with GPUs, the [NVIDIA Driver](https://www.nvidia.co.uk/Download/index.aspx) and the [NVIDIA Container Runtime](https://developer.nvidia.com/nvidia-container-runtime).

NVIDIA maintains an [Amazon Machine Image (AMI) that pre-installs NVIDIA drivers and container runtimes](https://aws.amazon.com/marketplace/pp/prodview-7ikjtg3um26wq), we recommend using this image as the starting point.

1. Open the [**EC2 Dashboard**](https://console.aws.amazon.com/ec2/home).
1. Select **Launch Instance**.
1. In the AMI selection box search for "nvidia", then switch to the **AWS Marketplace AMIs** tab.
1. Select **NVIDIA GPU-Optimized AMI** and click "Select". Then, in the new popup, select **Subscribe on Instance Launch**.
1. In **Key pair** select your SSH keys (create these first if you haven't already).
1. Under network settings create a security group (or choose an existing) with inbound rules that allows SSH access on
   port `22` and also allow ports `8888,8786,8787` to access Jupyter and Dask. For outbound rules, allow all traffic.
1. Select **Launch**.

## Connect to the instance

Next we need to connect to the instance.

1. Open the [**EC2 Dashboard**](https://console.aws.amazon.com/ec2/home).
2. Locate your VM and note the **Public IP Address**.
3. In your terminal run `ssh ubuntu@<ip address>`.

```{note}
If you use the AWS Console, please use the default `ubuntu` user to ensure the NVIDIA driver installs on the first boot.
```

````{tip}
Depending on where your ssh key is, when connecting via SSH you might need to do

```console
$ ssh -i <path-to-your-ssh-key-dir>/your-key-file.pem ubuntu@<ip address>
```

If you get prompted with a `WARNING: UNPROTECTED PRIVATE KEY FILE!`, and get a
**"Permission denied"** as a result of this.

Change the permissions of your key file to be less permissive by doing
`chmod 400 your_key_file.pem`, and you should be good to go.
````

## Install RAPIDS

```{include} ../../_includes/install-rapids-with-docker.md

```

```{note}
If you see a "modprobe: FATAL: Module nvidia not found in directory /lib/modules/6.2.0-1011-aws" while first connecting to the EC2 instance, try logging out and reconnecting again.
```

## Test RAPIDS

```{include} ../../_includes/test-rapids-docker-vm.md

```

```{relatedexamples}

```
