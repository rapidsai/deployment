# How to Setup InfiniBand on Azure

[Azure GPU optmized virtual machines](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-gpu) provide
low latency and high bandwidth InfiniBand network. This guide walks through the steps to enable InfiniBand to
optimize network performance.

## Build a Virtual Machine

Start by creating a GPU optimized VM from the Azure portal. Below is an example that we will use
for demonstration.

- Create new VM instance.
- Select `East US` region.
- Change `Availability options` to `Availability set` and create a set.
  - If building multiple instances put additional instances in the same set.
- Use the 2nd Gen Ubuntu 18.04 image.
  - Search all images for `Ubuntu Server 20.04` and choose the second one down on the list.
- Change size to `ND40rs_v2`.
- Set password login with credentials.
  - User `someuser`
  - Password `somepassword`
- Leave all other options as default.

Then connect to the VM using your preferred method.

## Install software

Before installing the drivers ensure the system is up to date.

```shell
sudo apt-get update
sudo apt-get upgrade -y
```

## NVIDIA Drivers

The commands below, should work for Ubuntu. See the [CUDA Toolkit documentation](https://docs.nvidia.com/cuda/index.html#installation-guides) for details on installing on other operating systems.

```shell
sudo apt-get install linux-headers-$(uname -r)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-drivers
```

Restart VM instance

```shell
sudo reboot
```

Once the VM boots, reconnect and run `nvidia-smi` to verify driver installation.

```shell
nvidia-smi
```

```shell
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

```shell
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

```shell
$ lsmod | grep nv_peer_mem
nv_peer_mem            16384  0
ib_core               430080  9 rdma_cm,ib_ipoib,nv_peer_mem,iw_cm,ib_umad,rdma_ucm,ib_uverbs,mlx5_ib,ib_cm
nvidia              55201792  895 nvidia_uvm,nv_peer_mem,nvidia_modeset
```

## Enable IPoIB

```shell
sudo sed -i -e 's/# OS.EnableRDMA=y/OS.EnableRDMA=y/g' /etc/waagent.conf
```

Reboot and reconnect.

```shell
sudo reboot
```

## Check IB

```shell
ip addr show
```

```shell
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
```

```shell
nvidia-smi topo -m
```

```shell
        GPU0    GPU1    GPU2    GPU3    GPU4    GPU5    GPU6    GPU7    CPU Affinity    NUMA Affinity
GPU0    X       NV2     NV1     NV2     NODE    NODE    NV1     NODE    0-19            0
GPU1    NV2     X       NV2     NV1     NODE    NODE    NODE    NV1     0-19            0
GPU2    NV1     NV2     X       NV1     NV2     NODE    NODE    NODE    0-19            0
GPU3    NV2     NV1     NV1     X       NODE    NV2     NODE    NODE    0-19            0
GPU4    NODE    NODE    NV2     NODE    X       NV1     NV1     NV2     0-19            0
GPU5    NODE    NODE    NODE    NV2     NV1     X       NV2     NV1     0-19            0
GPU6    NV1     NODE    NODE    NODE    NV1     NV2     X       NV2     0-19            0
GPU7    NODE    NV1     NODE    NODE    NV2     NV1     NV2     X       0-19            0

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

```shell
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Accept the default and allow conda init to run. Then start a new shell.

Create a conda environment (see ucx-py docs)

```shell
conda create -n ucxpy -c conda-forge -c rapidsai python=3.7 ipython ucx-proc=*=gpu ucx ucx-py dask distributed numpy cupy pytest pynvml rmm cudf dask-cudf dask-cuda -y
...
conda activate ucxpy
```

Clone ucx-py repo locally

```shell
git clone https://github.com/rapidsai/ucx-py.git
cd ucx-py/benchmarks
```

## Run Tests

Start by running the UCX-Py test suite, from within the `ucx-py` repo:

```shell
pytest -vs tests/
pytest -vs ucp/_libs/tests/
```

Now check to see if IB works, for that you can run some of the benchmarks that we include in UCX-Py, for example:

```shell
# Let UCX pick the best transport (expecting NVLink when available,
# otherwise IB, or TCP in worst case) on devices 0 and 1
python -m ucp.benchmarks.send_recv --server-dev 0 --client-dev 1 -o rmm --reuse-alloc -n 128MiB

# Force TCP-only on devices 0 and 1
UCX_TLS=tcp,cuda_copy python -m ucp.benchmarks.send_recv --server-dev 0 --client-dev 1 -o rmm --reuse-alloc -n 128MiB
```

We expect the first case above to have much higher bandwidth than the second. If you happen to have both
NVLink and IB connectivity, then you may limit to the specific transport by specifying `UCX_TLS`, e.g.:

```shell
# NVLink (if available) or TCP
UCX_TLS=tcp,cuda_copy,cuda_ipc

# IB (if available) or TCP
UCX_TLS=tcp,cuda_copy,rc

```

## Run Benchmarks

Finally, let's run the [merge benchmark](https://github.com/rapidsai/dask-cuda/blob/branch-22.12/dask_cuda/benchmarks/local_cudf_merge.py) from `dask-cuda`. This benchmark uses Dask to do a distributed merge across all of the GPUs avaliable
on your VM. Merge operations in this setting are harder to do because they require communication intensive shuffle
operations (see the [Dask documentation](https://docs.dask.org/en/stable/dataframe-best-practices.html#avoid-full-data-shuffling)
for more on this type of operation). In this case, the benchmark will perform an "all-to-all" shuffle, where each dataframe
will be shuffled before a partition-wise merge. This will require a lot of communication among the GPUs, so network performance
will be very important.

Below we are running for devices 0..7, you will want to adjust that for the number of devices available on your VM, the default
is to run on GPU 0 only. Additionally, `--chunk-size 100_000_000` is a safe value for 32GB GPUs, you may
adjust that proportional to the size of the GPU you have (it scales linearly, so `50_000_000` should
be good for 16GB or `150_000_000` for 48GB). Please note that TCP will be much slower, so you may
choose to adjust to the maximum size you can get for UCX to see how far you can push it, but you
may want to run on a much smaller workload such as 10_000_000 to compare TCP and UCX.

```shell
# Default Dask TCP communication protocol
python -m dask_cuda.benchmarks.local_cudf_merge --devs 0,1,2,3,4,5,6,7 --chunk-size 100_000_000
```

```shell
Merge benchmark
--------------------------------------------------------------------------------
Backend                   | dask
Merge type                | gpu
Rows-per-chunk            | 100000000
Base-chunks               | 8
Other-chunks              | 8
Broadcast                 | default
Protocol                  | tcp
Device(s)                 | 0,1,2,3,4,5,6,7
RMM Pool                  | True
Frac-match                | 0.3
Worker thread(s)          | 1
Data processed            | 23.84 GiB
Number of workers         | 8
================================================================================
Wall clock                | Throughput
--------------------------------------------------------------------------------
57.57 s                   | 424.07 MiB/s
48.90 s                   | 499.23 MiB/s
39.20 s                   | 622.78 MiB/s
================================================================================
Throughput                | 502.77 MiB/s +/- 44.85 MiB/s
Bandwidth                 | 48.13 MiB/s +/- 1.02 MiB/s
Wall clock                | 48.56 s +/- 7.50 s
================================================================================
(w1,w2)                   | 25% 50% 75% (total nbytes)
--------------------------------------------------------------------------------
(0,1)                     | 51.78 MiB/s 83.47 MiB/s 144.55 MiB/s (5.49 GiB)
(0,2)                     | 33.87 MiB/s 58.94 MiB/s 97.58 MiB/s (5.17 GiB)
(0,3)                     | 34.56 MiB/s 45.30 MiB/s 75.15 MiB/s (5.68 GiB)
(0,4)                     | 37.01 MiB/s 48.28 MiB/s 51.71 MiB/s (2.93 GiB)
(0,5)                     | 24.41 MiB/s 37.80 MiB/s 56.43 MiB/s (2.93 GiB)
(0,6)                     | 38.36 MiB/s 52.35 MiB/s 77.86 MiB/s (2.93 GiB)
(0,7)                     | 36.19 MiB/s 52.29 MiB/s 64.63 MiB/s (2.10 GiB)
(1,0)                     | 46.21 MiB/s 81.88 MiB/s 98.75 MiB/s (3.26 GiB)
(1,2)                     | 50.77 MiB/s 70.97 MiB/s 80.89 MiB/s (3.26 GiB)
(1,3)                     | 25.68 MiB/s 38.14 MiB/s 60.16 MiB/s (2.61 GiB)
(1,4)                     | 31.84 MiB/s 42.65 MiB/s 58.16 MiB/s (3.26 GiB)
(1,5)                     | 51.90 MiB/s 61.35 MiB/s 96.84 MiB/s (3.54 GiB)
(1,6)                     | 33.88 MiB/s 56.01 MiB/s 81.22 MiB/s (5.49 GiB)
(1,7)                     | 30.74 MiB/s 49.46 MiB/s 104.65 MiB/s (4.94 GiB)
(2,0)                     | 39.59 MiB/s 54.21 MiB/s 116.96 MiB/s (4.05 GiB)
(2,1)                     | 42.26 MiB/s 55.04 MiB/s 76.33 MiB/s (3.82 GiB)
(2,3)                     | 34.84 MiB/s 61.06 MiB/s 73.21 MiB/s (3.72 GiB)
(2,4)                     | 50.12 MiB/s 65.37 MiB/s 95.88 MiB/s (4.05 GiB)
(2,5)                     | 48.31 MiB/s 57.80 MiB/s 76.18 MiB/s (3.49 GiB)
(2,6)                     | 46.99 MiB/s 54.70 MiB/s 100.22 MiB/s (6.01 GiB)
(2,7)                     | 39.05 MiB/s 47.92 MiB/s 58.91 MiB/s (3.21 GiB)
(3,0)                     | 37.08 MiB/s 46.98 MiB/s 88.88 MiB/s (3.21 GiB)
(3,1)                     | 49.80 MiB/s 63.95 MiB/s 135.50 MiB/s (4.14 GiB)
(3,2)                     | 37.47 MiB/s 53.44 MiB/s 62.49 MiB/s (2.93 GiB)
(3,4)                     | 53.08 MiB/s 60.91 MiB/s 113.20 MiB/s (3.49 GiB)
(3,5)                     | 32.44 MiB/s 61.33 MiB/s 75.88 MiB/s (3.21 GiB)
(3,6)                     | 40.30 MiB/s 51.87 MiB/s 61.19 MiB/s (4.84 GiB)
(3,7)                     | 46.50 MiB/s 65.59 MiB/s 98.70 MiB/s (4.89 GiB)
(4,0)                     | 43.95 MiB/s 49.44 MiB/s 60.26 MiB/s (3.21 GiB)
(4,1)                     | 33.57 MiB/s 47.84 MiB/s 56.19 MiB/s (3.26 GiB)
(4,2)                     | 52.98 MiB/s 55.80 MiB/s 67.02 MiB/s (2.65 GiB)
(4,3)                     | 46.39 MiB/s 58.78 MiB/s 67.99 MiB/s (2.89 GiB)
(4,5)                     | 61.69 MiB/s 81.93 MiB/s 102.84 MiB/s (7.40 GiB)
(4,6)                     | 47.68 MiB/s 51.31 MiB/s 66.77 MiB/s (2.93 GiB)
(4,7)                     | 49.62 MiB/s 62.32 MiB/s 64.63 MiB/s (4.61 GiB)
(5,0)                     | 28.66 MiB/s 36.47 MiB/s 48.18 MiB/s (3.21 GiB)
(5,1)                     | 43.90 MiB/s 55.00 MiB/s 65.83 MiB/s (5.77 GiB)
(5,2)                     | 46.87 MiB/s 55.64 MiB/s 63.94 MiB/s (3.21 GiB)
(5,3)                     | 40.65 MiB/s 64.80 MiB/s 73.22 MiB/s (2.89 GiB)
(5,4)                     | 47.33 MiB/s 61.01 MiB/s 74.85 MiB/s (5.73 GiB)
(5,6)                     | 44.10 MiB/s 53.02 MiB/s 64.72 MiB/s (5.45 GiB)
(5,7)                     | 41.58 MiB/s 46.51 MiB/s 58.29 MiB/s (2.93 GiB)
(6,0)                     | 35.33 MiB/s 55.42 MiB/s 80.52 MiB/s (5.17 GiB)
(6,1)                     | 32.96 MiB/s 59.96 MiB/s 76.62 MiB/s (3.26 GiB)
(6,2)                     | 33.62 MiB/s 47.27 MiB/s 64.46 MiB/s (2.93 GiB)
(6,3)                     | 34.95 MiB/s 49.26 MiB/s 113.79 MiB/s (5.12 GiB)
(6,4)                     | 35.31 MiB/s 41.76 MiB/s 68.44 MiB/s (2.93 GiB)
(6,5)                     | 34.80 MiB/s 55.53 MiB/s 62.96 MiB/s (2.93 GiB)
(6,7)                     | 42.69 MiB/s 54.73 MiB/s 67.85 MiB/s (2.37 GiB)
(7,0)                     | 41.34 MiB/s 60.72 MiB/s 97.10 MiB/s (6.01 GiB)
(7,1)                     | 37.56 MiB/s 60.58 MiB/s 90.88 MiB/s (4.38 GiB)
(7,2)                     | 44.00 MiB/s 49.94 MiB/s 87.90 MiB/s (8.24 GiB)
(7,3)                     | 44.30 MiB/s 67.68 MiB/s 83.67 MiB/s (3.73 GiB)
(7,4)                     | 47.55 MiB/s 61.13 MiB/s 102.56 MiB/s (3.77 GiB)
(7,5)                     | 45.17 MiB/s 63.80 MiB/s 112.65 MiB/s (4.05 GiB)
(7,6)                     | 38.23 MiB/s 49.51 MiB/s 67.60 MiB/s (3.21 GiB)
================================================================================
Worker index              | Worker address
--------------------------------------------------------------------------------
0                         | tcp://127.0.0.1:42179
1                         | tcp://127.0.0.1:38595
2                         | tcp://127.0.0.1:36879
3                         | tcp://127.0.0.1:45435
4                         | tcp://127.0.0.1:37125
5                         | tcp://127.0.0.1:45465
6                         | tcp://127.0.0.1:34047
7                         | tcp://127.0.0.1:39975
================================================================================

```

```shell
# UCX protocol
python -m dask_cuda.benchmarks.local_cudf_merge --devs 0,1,2,3,4,5,6,7 --chunk-size 100_000_000 --protocol ucx
```

```shell
Merge benchmark
--------------------------------------------------------------------------------
Backend                   | dask
Merge type                | gpu
Rows-per-chunk            | 100000000
Base-chunks               | 8
Other-chunks              | 8
Broadcast                 | default
Protocol                  | ucx
Device(s)                 | 0,1,2,3,4,5,6,7
RMM Pool                  | True
Frac-match                | 0.3
TCP                       | None
InfiniBand                | None
NVLink                    | None
Worker thread(s)          | 1
Data processed            | 23.84 GiB
Number of workers         | 8
================================================================================
Wall clock                | Throughput
--------------------------------------------------------------------------------
13.60 s                   | 1.75 GiB/s
14.82 s                   | 1.61 GiB/s
11.57 s                   | 2.06 GiB/s
================================================================================
Throughput                | 1.79 GiB/s +/- 106.12 MiB/s
Bandwidth                 | 159.90 MiB/s +/- 9.51 MiB/s
Wall clock                | 13.33 s +/- 1.34 s
================================================================================
(w1,w2)                   | 25% 50% 75% (total nbytes)
--------------------------------------------------------------------------------
(0,1)                     | 120.07 MiB/s 122.18 MiB/s 150.56 MiB/s (2.65 GiB)
(0,2)                     | 110.85 MiB/s 120.68 MiB/s 146.13 MiB/s (4.89 GiB)
(0,3)                     | 117.21 MiB/s 121.43 MiB/s 150.61 MiB/s (2.65 GiB)
(0,4)                     | 120.05 MiB/s 122.21 MiB/s 150.50 MiB/s (2.65 GiB)
(0,5)                     | 115.88 MiB/s 121.16 MiB/s 138.80 MiB/s (4.89 GiB)
(0,6)                     | 117.23 MiB/s 122.19 MiB/s 150.60 MiB/s (2.65 GiB)
(0,7)                     | 120.40 MiB/s 127.51 MiB/s 166.64 MiB/s (4.89 GiB)
(1,0)                     | 118.93 MiB/s 128.47 MiB/s 167.54 MiB/s (2.65 GiB)
(1,2)                     | 118.26 MiB/s 130.97 MiB/s 149.37 MiB/s (2.65 GiB)
(1,3)                     | 118.32 MiB/s 130.94 MiB/s 149.35 MiB/s (2.65 GiB)
(1,4)                     | 118.23 MiB/s 130.97 MiB/s 145.69 MiB/s (2.65 GiB)
(1,5)                     | 118.58 MiB/s 147.64 MiB/s 187.46 MiB/s (7.12 GiB)
(1,6)                     | 118.17 MiB/s 124.39 MiB/s 149.36 MiB/s (2.65 GiB)
(1,7)                     | 120.22 MiB/s 138.89 MiB/s 170.63 MiB/s (4.89 GiB)
(2,0)                     | 103.78 MiB/s 109.10 MiB/s 124.28 MiB/s (2.65 GiB)
(2,1)                     | 103.71 MiB/s 109.15 MiB/s 124.31 MiB/s (2.65 GiB)
(2,3)                     | 105.01 MiB/s 110.17 MiB/s 123.77 MiB/s (4.89 GiB)
(2,4)                     | 105.07 MiB/s 110.16 MiB/s 126.63 MiB/s (4.89 GiB)
(2,5)                     | 102.21 MiB/s 103.77 MiB/s 111.24 MiB/s (2.65 GiB)
(2,6)                     | 103.73 MiB/s 108.97 MiB/s 124.18 MiB/s (2.65 GiB)
(2,7)                     | 105.00 MiB/s 115.59 MiB/s 128.08 MiB/s (4.89 GiB)
(3,0)                     | 105.66 MiB/s 113.46 MiB/s 140.83 MiB/s (2.93 GiB)
(3,1)                     | 104.51 MiB/s 113.27 MiB/s 124.69 MiB/s (2.65 GiB)
(3,2)                     | 105.68 MiB/s 121.09 MiB/s 152.76 MiB/s (2.93 GiB)
(3,4)                     | 104.06 MiB/s 107.01 MiB/s 122.69 MiB/s (2.93 GiB)
(3,5)                     | 105.27 MiB/s 112.59 MiB/s 126.22 MiB/s (2.93 GiB)
(3,6)                     | 108.03 MiB/s 114.38 MiB/s 186.48 MiB/s (5.45 GiB)
(3,7)                     | 104.22 MiB/s 109.21 MiB/s 121.15 MiB/s (5.17 GiB)
(4,0)                     | 120.46 MiB/s 124.20 MiB/s 196.94 MiB/s (5.17 GiB)
(4,1)                     | 120.97 MiB/s 131.15 MiB/s 178.33 MiB/s (5.17 GiB)
(4,2)                     | 163.68 MiB/s 275.96 MiB/s 367.61 MiB/s (5.17 GiB)
(4,3)                     | 104.13 MiB/s 109.68 MiB/s 124.05 MiB/s (2.93 GiB)
(4,5)                     | 435.21 MiB/s 743.65 MiB/s 1.80 GiB/s (2.65 GiB)
(4,6)                     | 449.39 MiB/s 733.81 MiB/s 1.87 GiB/s (3.21 GiB)
(4,7)                     | 468.57 MiB/s 754.75 MiB/s 1.55 GiB/s (2.93 GiB)
(5,0)                     | 109.45 MiB/s 118.01 MiB/s 123.14 MiB/s (2.65 GiB)
(5,1)                     | 111.60 MiB/s 118.35 MiB/s 119.24 MiB/s (4.89 GiB)
(5,2)                     | 104.97 MiB/s 110.63 MiB/s 114.62 MiB/s (4.89 GiB)
(5,3)                     | 137.82 MiB/s 147.80 MiB/s 172.47 MiB/s (2.65 GiB)
(5,4)                     | 518.69 MiB/s 831.95 MiB/s 1.94 GiB/s (4.89 GiB)
(5,6)                     | 516.97 MiB/s 816.57 MiB/s 2.42 GiB/s (2.65 GiB)
(5,7)                     | 524.66 MiB/s 836.36 MiB/s 1.97 GiB/s (2.65 GiB)
(6,0)                     | 210.92 MiB/s 235.82 MiB/s 313.85 MiB/s (7.12 GiB)
(6,1)                     | 121.58 MiB/s 133.68 MiB/s 147.33 MiB/s (4.89 GiB)
(6,2)                     | 103.04 MiB/s 108.67 MiB/s 109.33 MiB/s (2.65 GiB)
(6,3)                     | 108.93 MiB/s 111.87 MiB/s 112.13 MiB/s (2.65 GiB)
(6,4)                     | 654.69 MiB/s 1.33 GiB/s 3.39 GiB/s (4.89 GiB)
(6,5)                     | 442.62 MiB/s 652.70 MiB/s 4.13 GiB/s (2.65 GiB)
(6,7)                     | 618.86 MiB/s 661.75 MiB/s 0.93 GiB/s (2.65 GiB)
(7,0)                     | 117.09 MiB/s 120.16 MiB/s 124.30 MiB/s (2.65 GiB)
(7,1)                     | 210.83 MiB/s 227.30 MiB/s 272.82 MiB/s (2.65 GiB)
(7,2)                     | 103.47 MiB/s 110.98 MiB/s 124.21 MiB/s (2.65 GiB)
(7,3)                     | 104.28 MiB/s 111.12 MiB/s 141.26 MiB/s (7.12 GiB)
(7,4)                     | 620.20 MiB/s 691.52 MiB/s 2.93 GiB/s (2.65 GiB)
(7,5)                     | 604.36 MiB/s 772.47 MiB/s 2.69 GiB/s (2.65 GiB)
(7,6)                     | 614.80 MiB/s 770.38 MiB/s 1.71 GiB/s (2.65 GiB)
================================================================================
Worker index              | Worker address
--------------------------------------------------------------------------------
0                         | ucx://127.0.0.1:42213
1                         | ucx://127.0.0.1:39353
2                         | ucx://127.0.0.1:60637
3                         | ucx://127.0.0.1:59643
4                         | ucx://127.0.0.1:52613
5                         | ucx://127.0.0.1:44077
6                         | ucx://127.0.0.1:54887
7                         | ucx://127.0.0.1:38623
================================================================================
```
