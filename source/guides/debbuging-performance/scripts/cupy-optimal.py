import time

import cupy as cp
import numpy as np
import xarray as xr

ds = xr.open_dataset("air.sig995.2025.nc")


t0 = time.perf_counter()

air = ds["air"].cupy.as_cupy()
T = air.data
ntime, nlat, nlon = T.shape

# --- Build X = anomalies (time × space) ---
X = T.reshape(ntime, nlat * nlon)
X = X - X.mean(axis=0, keepdims=True)  # remove 2025 mean at each grid point

# --- EOF via SVD ---
U, S, Vt = np.linalg.svd(X, full_matrices=False)

# First mode
eof1 = Vt[0, :].reshape(nlat, nlon)  # spatial pattern
pc1 = U[:, 0] * S[0]  # time series
var_frac1 = (S[0] ** 2) / np.sum(S**2)  # variance fraction (0–1)

cp.cuda.Stream.null.synchronize()  # wait for cupy to finish the computation

elapsed = time.perf_counter() - t0

print(f"Time for EOF/PC calculation: {elapsed:.3f} s")
