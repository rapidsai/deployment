# L4 GPUs on a Google Cloud Platform (GCP)

[L4 GPUs](https://www.nvidia.com/en-us/data-center/l4/) are a more energy and computationally efficient option compared to T4 GPUs. L4 GPUs are [generally available on GCP](https://cloud.google.com/blog/products/compute/introducing-g2-vms-with-nvidia-l4-gpus) to run your workflows with RAPIDS.

## Compute Engine Instance

### Create the Virtual Machine

To create a VM instance with an L4 GPU to run RAPIDS:

1. Open [**Compute Engine**](https://console.cloud.google.com/compute/instances).
1. Select **Create Instance**.
1. Under the **Machine configuration** section, select **GPUs** and then select `NVIDIA L4` in the **GPU type** dropdown.
1. Under the **Boot Disk** section, click **CHANGE** and select `Deep Learning on Linux` in the **Operating System** dropdown.
1. It is also recommended to increase the default boot disk size to something like `100GB`.
1. Once you have customized other attributes of the instance, click **CREATE**.

### Allow network access

To access Jupyter and Dask we will need to set up some firewall rules to open up some ports.

#### Create the firewall rule

1. Open [**VPC Network**](https://console.cloud.google.com/networking/networks/list).
2. Select **Firewall** and **Create firewall rule**
3. Give the rule a name like `rapids` and ensure the network matches the one you selected for the VM.
4. Add a tag like `rapids` which we will use to assign the rule to our VM.
5. Set your source IP range. We recommend you restrict this to your own IP address or your corporate network rather than `0.0.0.0/0` which will allow anyone to access your VM.
6. Under **Protocols and ports** allow TCP connections on ports `22,8786,8787,8888`.

#### Assign it to the VM

1. Open [**Compute Engine**](https://console.cloud.google.com/compute/instances).
2. Select your VM and press **Edit**.
3. Scroll down to **Networking** and add the `rapids` network tag you gave your firewall rule.
4. Select **Save**.

### Connect to the VM

Next we need to connect to the VM.

1. Open [**Compute Engine**](https://console.cloud.google.com/compute/instances).
2. Locate your VM and press the **SSH** button which will open a new browser tab with a terminal.

### Install CUDA and NVIDIA Container Toolkit

Since [GCP recommends CUDA 12](https://cloud.google.com/compute/docs/gpus/install-drivers-gpu#no-secure-boot) on L4 VM, we will be upgrading CUDA.

1. [Install CUDA Toolkit 12](https://developer.nvidia.com/cuda-downloads) in your VM and accept the default prompts with the following commands.

```bash
$ wget https://developer.download.nvidia.com/compute/cuda/12.1.1/local_installers/cuda_12.1.1_530.30.02_linux.run
$ sudo sh cuda_12.1.1_530.30.02_linux.run
```

1. [Install NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#setting-up-nvidia-container-toolkit) with the following commands.

```bash
$ sudo apt-get update
$ sudo apt-get install -y nvidia-container-toolkit
$ sudo nvidia-ctk runtime configure --runtime=docker
$ sudo systemctl restart docker
```

### Install RAPIDS

```{include} ../_includes/install-rapids-with-docker.md

```

### Test RAPIDS

```{include} ../_includes/test-rapids-docker-vm.md

```

### Clean up

Once you are finished head back to the [Deployments](https://console.cloud.google.com/compute/instances) page and delete the instance you created.

```{relatedexamples}

```
