# IBM Cloud

```{toctree}
---
maxdepth: 2
caption: IBM Cloud
---
single-node
iks
```

RAPIDS can be deployed on IBM Cloud in several ways. See the
list of accelerated instance types below:

| Cloud <br> Provider | Inst. <br> Type |vCPUs | Inst. <br> Name  | GPU <br> Count | GPU <br> Type | xGPU <br> RAM | xGPU <br> RAM Total |
| :------------------ | --------------- | ---- |----------------- | -------------- | ------------- | ------------- | ------------------: |
| IBM                 | V100 GPU        | 8    | gx2-8x64x1v100   | 1              | NVIDIA Tesla  | 16 (GB)       |             64 (GB) |
| IBM                 | V100 GPU        | 16   | gx2-16x128x1v100 | 1              | NVIDIA Tesla  | 16 (GB)       |            128 (GB) |
| IBM                 | V100 GPU        | 16   | gx2-16x128x2v100 | 2              | NVIDIA Tesla  | 16 (GB)       |            128 (GB) |
| IBM                 | V100 GPU        | 32   | gx2-32x256x2v100 | 2              | NVIDIA Tesla  | 16 (GB)       |            256 (GB) |

