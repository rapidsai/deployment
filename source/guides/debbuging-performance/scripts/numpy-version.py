# Simplified EOF analysis for benchmarking purposes.
#
# This script is a deliberate simplification of the full analysis in eof-analysis.ipynb.
# It exists to isolate and time the core SVD computation without the overhead of
# data preparation steps. Two key shortcuts are taken:
#
#   1. No climatology subtraction — anomalies are computed by removing the 2025
#      time-mean at each grid point instead of subtracting the 1981-2010 long-term
#      climatology.It mixes the seasonal cycle into the anomalies, so the
#      resulting EOF patterns are not physically meaningful.
#
#   2. No area weighting — latitude weights (sqrt(cos(lat))) are omitted, so polar
#      grid cells are treated as equal in area to tropical ones. This inflates the
#      contribution of high-latitude variability to the SVD.
#
# For more meaningful results, check eof-analysis.ipynb.

import time

import numpy as np
import xarray as xr

ds = xr.open_dataset("air.sig995.2025.nc")  # 4x daily, sigma 0.995

t0 = time.perf_counter()

air = ds["air"]
T = np.asarray(air)
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

elapsed = time.perf_counter() - t0
print(f"Time for EOF/PC calculation: {elapsed:.3f} s")
