# How to Setup InfiniBand on Azure

## Build VM
* Create new VM instance.
* Select `East US` region.
* Change `Availability options` to `Availability set` and create a set.
    * If building multiple instances put additional instances in the same set.
* Use the 2nd Gen Ubuntu 18.04 image.
    * Search all images for `Ubuntu Server 20.04` and choose the second one down on the list.
* Change size to `ND40rs_v2`.
* Set password login with credentials.
    * User `someuser`
    * Password `somepassword`
* Leave all other options as default.

## Install software
Before installing the drivers ensure the system is up to date.

```
sudo apt update
sudo apt upgrade -y
```

## NVIDIA Drivers
```
sudo apt-get install linux-headers-$(uname -r)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-drivers
```

Restart VM instance and run `nvidia-smi` to verify driver installation.

```
$ nvidia-smi
Mon Nov 14 20:32:39 2022       
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 520.61.05    Driver Version: 520.61.05    CUDA Version: 11.8     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  Tesla V100-SXM2...  On   | 00000001:00:00.0 Off |                    0 |
| N/A   34C    P0    41W / 300W |    445MiB / 32768MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
|   1  Tesla V100-SXM2...  On   | 00000002:00:00.0 Off |                    0 |
| N/A   37C    P0    43W / 300W |      4MiB / 32768MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
|   2  Tesla V100-SXM2...  On   | 00000003:00:00.0 Off |                    0 |
| N/A   34C    P0    42W / 300W |      4MiB / 32768MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
|   3  Tesla V100-SXM2...  On   | 00000004:00:00.0 Off |                    0 |
| N/A   35C    P0    44W / 300W |      4MiB / 32768MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
|   4  Tesla V100-SXM2...  On   | 00000005:00:00.0 Off |                    0 |
| N/A   35C    P0    41W / 300W |      4MiB / 32768MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
|   5  Tesla V100-SXM2...  On   | 00000006:00:00.0 Off |                    0 |
| N/A   36C    P0    43W / 300W |      4MiB / 32768MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
|   6  Tesla V100-SXM2...  On   | 00000007:00:00.0 Off |                    0 |
| N/A   37C    P0    44W / 300W |      4MiB / 32768MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
|   7  Tesla V100-SXM2...  On   | 00000008:00:00.0 Off |                    0 |
| N/A   38C    P0    44W / 300W |      4MiB / 32768MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
                                                                               
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|    0   N/A  N/A      1396      G   /usr/lib/xorg/Xorg                427MiB |
|    0   N/A  N/A      1762      G   /usr/bin/gnome-shell               16MiB |
|    1   N/A  N/A      1396      G   /usr/lib/xorg/Xorg                  4MiB |
|    2   N/A  N/A      1396      G   /usr/lib/xorg/Xorg                  4MiB |
|    3   N/A  N/A      1396      G   /usr/lib/xorg/Xorg                  4MiB |
|    4   N/A  N/A      1396      G   /usr/lib/xorg/Xorg                  4MiB |
|    5   N/A  N/A      1396      G   /usr/lib/xorg/Xorg                  4MiB |
|    6   N/A  N/A      1396      G   /usr/lib/xorg/Xorg                  4MiB |
|    7   N/A  N/A      1396      G   /usr/lib/xorg/Xorg                  4MiB |
+-----------------------------------------------------------------------------+
```

## InfiniBand Driver

From [Azure docs](https://learn.microsoft.com/en-us/azure/virtual-machines/workloads/hpc/enable-infiniband)

```
MOFED_VERSION=5.0-2.1.8.0
MOFED_OS=ubuntu20.04
pushd /tmp
curl -fSsL https://www.mellanox.com/downloads/ofed/MLNX_OFED-${MOFED_VERSION}/MLNX_OFED_LINUX-${MOFED_VERSION}-${MOFED_OS}-x86_64.tgz | tar -zxpf -
cd MLNX_OFED_LINUX-*
sudo ./mlnxofedinstall
popd
```