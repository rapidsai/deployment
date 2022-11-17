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
sudo apt-get update
sudo apt-get upgrade -y
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

Restart VM instance
```
sudo reboot
```

Then run `nvidia-smi` to verify driver installation.

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
On Ubuntu 20.04
```
sudo apt-get install -y automake dh-make git libcap2 libnuma-dev libtool make pkg-config udev curl librdmacm-dev rdma-core
sudo apt-get install -y libgfortran5 bison chrpath flex graphviz gfortran tk dpatch quilt swig tcl
VERSION="5.8-1.0.1.1"
TARBALL="MLNX_OFED_LINUX-$VERSION-ubuntu20.04-x86_64.tgz"
wget https://content.mellanox.com/ofed/MLNX_OFED-${VERSION}/$TARBALL
tar zxvf ${TARBALL}
cd MLNX_OFED_LINUX-$VERSION-ubuntu20.04-x86_64
sudo ./mlnxofedinstall
```

Check install
```
$ lsmod | grep nv_peer_mem
nv_peer_mem            16384  0
ib_core               430080  9 rdma_cm,ib_ipoib,nv_peer_mem,iw_cm,ib_umad,rdma_ucm,ib_uverbs,mlx5_ib,ib_cm
nvidia              55201792  895 nvidia_uvm,nv_peer_mem,nvidia_modeset
```
## Enable IPoIB
```
sudo sed -i -e 's/# OS.EnableRDMA=y/OS.EnableRDMA=y/g' /etc/waagent.conf
```
Reboot
```
sudo reboot
```

## Check IB
```
ip addr show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 60:45:bd:a7:42:cc brd ff:ff:ff:ff:ff:ff
    inet 10.6.0.5/24 brd 10.6.0.255 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::6245:bdff:fea7:42cc/64 scope link 
       valid_lft forever preferred_lft forever
3: eth1: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 00:15:5d:33:ff:16 brd ff:ff:ff:ff:ff:ff
4: enP44906s1: <BROADCAST,MULTICAST,SLAVE,UP,LOWER_UP> mtu 1500 qdisc mq master eth0 state UP group default qlen 1000
    link/ether 60:45:bd:a7:42:cc brd ff:ff:ff:ff:ff:ff
    altname enP44906p0s2
5: ibP59423s2: <BROADCAST,MULTICAST> mtu 4092 qdisc noop state DOWN group default qlen 256
    link/infiniband 00:00:09:27:fe:80:00:00:00:00:00:00:00:15:5d:ff:fd:33:ff:16 brd 00:ff:ff:ff:ff:12:40:1b:80:1d:00:00:00:00:00:00:ff:ff:ff:ff
    altname ibP59423p0s2

$ nvidia-smi topo -m
	GPU0	GPU1	GPU2	GPU3	GPU4	GPU5	GPU6	GPU7	CPU Affinity	NUMA Affinity
GPU0	 X 	NV2	NV1	NV2	NODE	NODE	NV1	NODE	0-19	0
GPU1	NV2	 X 	NV2	NV1	NODE	NODE	NODE	NV1	0-19	0
GPU2	NV1	NV2	 X 	NV1	NV2	NODE	NODE	NODE	0-19	0
GPU3	NV2	NV1	NV1	 X 	NODE	NV2	NODE	NODE	0-19	0
GPU4	NODE	NODE	NV2	NODE	 X 	NV1	NV1	NV2	0-19	0
GPU5	NODE	NODE	NODE	NV2	NV1	 X 	NV2	NV1	0-19	0
GPU6	NV1	NODE	NODE	NODE	NV1	NV2	 X 	NV2	0-19	0
GPU7	NODE	NV1	NODE	NODE	NV2	NV1	NV2	 X 	0-19	0

Legend:

  X    = Self
  SYS  = Connection traversing PCIe as well as the SMP interconnect between NUMA nodes (e.g., QPI/UPI)
  NODE = Connection traversing PCIe as well as the interconnect between PCIe Host Bridges within a NUMA node
  PHB  = Connection traversing PCIe as well as a PCIe Host Bridge (typically the CPU)
  PXB  = Connection traversing multiple PCIe bridges (without traversing the PCIe Host Bridge)
  PIX  = Connection traversing at most a single PCIe bridge
  NV#  = Connection traversing a bonded set of # NVLinks

```

## Install UCX-Py and tools
```
$ wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
$ bash Miniconda3-latest-Linux-x86_64.sh
```
Accept the default and allow conda init to run. Then start a new shell.

Create a conda environment (see ucx-py docs)

```
$ conda create -n ucxpy -c conda-forge -c rapidsai python=3.7 ipython ucx-proc=*=gpu ucx ucx-py dask distributed numpy cupy pytest pynvml -y
...
$ conda activate ucxpy
```
Clone ucx-py repo locally

```
git clone https://github.com/rapidsai/ucx-py.git
cd ucx-py/benchmarks
```

## Run benchmarks
[GitHub Issue on Benchmarks](https://github.com/rapidsai/ucx-py/issues/311)