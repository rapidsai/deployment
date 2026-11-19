# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import time

import cupy as cp
import numpy as np
import xarray as xr

ds = xr.open_dataset("air.sig995.2025.nc")

t0 = time.perf_counter()
air = ds["air"]
T = cp.asarray(air)
ntime, nlat, nlon = T.shape

# Build X = anomalies (time x space) on the GPU
X = T.reshape(ntime, nlat * nlon)
X = X - X.mean(axis=0, keepdims=True)

# Bring back to NumPy for np.linalg.svd
X = X.get()

# EOF via SVD on CPU
U, S, Vt = np.linalg.svd(X, full_matrices=False)

eof1 = Vt[0, :].reshape(nlat, nlon)
pc1 = U[:, 0] * S[0]
var_frac1 = (S[0] ** 2) / np.sum(S**2)

elapsed = time.perf_counter() - t0
print(f"shape: {T.shape}")
print(f"naive total seconds: {elapsed:.3f}")
print(f"first mode variance fraction: {float(var_frac1):.4f}")
print("bottleneck: the matrix returns to CPU before the expensive SVD")
