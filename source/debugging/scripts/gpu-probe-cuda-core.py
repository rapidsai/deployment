# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import cuda.core.system as system

device_count = system.get_num_devices()
print(f"device count: {device_count}")

for index in range(device_count):
    device = system.Device(index=index)
    memory = device.memory_info
    print(f"device {index}: {device.name}")
    print(f"  compute capability: {device.cuda_compute_capability}")
    print(
        f"  memory: {memory.total / 1024**3:.1f} GiB total, {memory.free / 1024**3:.1f} GiB free"
    )
