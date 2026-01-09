# Modal

You can run RAPIDS on [Modal](https://modal.com/), a serverless cloud platform for compute-intensive applications. Modal
provides a simple way to deploy Python code, including GPU-accelerated workloads, without managing infrastructure.
Remote containers are launched on-demand and shut down automatically when not in use.

## cudf.pandas Run via Modal Apps

Modal Apps are Python applications that run on Modal's serverless infrastructure. An app is defined using the
`modal.App` object and consists of one or more functions decorated with `@app.function()`. Functions can be invoked
locally (which triggers remote execution).

### Setup

To get started with Modal, first sign up for an account at [modal.com](https://modal.com), and follow the [getting
started](https://modal.com/docs/guide#getting-started) setup.

Modal has a starter tier, that includes enough free credits to run this example, and explore GPU usage for several hours.
For more information, check out the [Modal pricing page](https://modal.com/pricing).

### Example

The example below demonstrates how to use RAPIDS cuDF's pandas accelerator mode on Modal. This example processes NYC
parking violations data and shows how `cudf.pandas` can accelerate `pandas` operations with zero code changes.

```python
from pathlib import Path

import modal

app = modal.App("zcc-cudf-demo")

standalone_python_url = (
    "https://github.com/astral-sh/python-build-standalone/releases/download/20251028/"
    "cpython-3.12.12+20251028-x86_64_v3-unknown-linux-gnu-install_only.tar.gz"
)
install_python_commands = [
    "RUN apt update",
    "RUN apt install -y curl",
    f"RUN curl -L -o /tmp/python-standalone.tar.gz {standalone_python_url}",
    "RUN tar -xzf /tmp/python-standalone.tar.gz -C /tmp",
    "RUN cp -r /tmp/python/* /usr/local",
]

ctk_image = modal.Image.from_registry(
    "nvidia/cuda:12.9.0-runtime-ubuntu24.04",
    setup_dockerfile_commands=install_python_commands,
).entrypoint([])  # removes chatty prints on entry


image = ctk_image.uv_pip_install(
    "cudf-cu12==25.12.*",
).env({"CUDF_PANDAS_RMM_MODE": "async"})


data_cache = {
    "/data": modal.Volume.from_name(
        "nyc-parking-violations-2022", create_if_missing=True
    )
}


@app.function(image=image, gpu="A10", volumes=data_cache)
def run():
    import cudf.pandas

    cudf.pandas.install()

    import pandas as pd
    import urllib.request
    import os
    import time

    # download the file to a distributed Volume
    file_path = "/data/nyc_parking_violations_2022.parquet"
    if not os.path.exists(file_path):
        print("Downloading NYC parking violations dataset...")
        url = "https://data.rapids.ai/datasets/nyc_parking/nyc_parking_violations_2022.parquet"
        urllib.request.urlretrieve(url, file_path)
        print("Done!")


    start_time = time.time()

    df = pd.read_parquet(
        file_path,
        columns=[
            "Registration State",
            "Violation Description",
            "Vehicle Body Type",
            "Issue Date",
            "Summons Number",
        ],
    )

    result = (
        df[["Registration State", "Violation Description"]]
        .value_counts()
        .groupby("Registration State")
        .head(1)
        .sort_index()
        .reset_index()
    )
    end_time = time.time()

        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(f"Result shape: {result.shape}")
        print(result.head())

        # Verify GPU acceleration is working you should see <class 'cudf.pandas.fast_slow_proxy._FastSlowProxyMeta'>
        print(f"DataFrame type: {type(df).__name__}")
```

To run this app locally (which executes remotely on Modal):

```console
$ modal run modal_app.py
...
df:    Registration State           Violation Description  count
0                  99                            <NA>  17550
1                  AB                  14-No Standing     22
2                  AK  PHTO SCHOOL ZN SPEED VIOLATION    125
3                  AL  PHTO SCHOOL ZN SPEED VIOLATION   3668
4                  AR  PHTO SCHOOL ZN SPEED VIOLATION    537
..                ...                             ...    ...
62                 VT  PHTO SCHOOL ZN SPEED VIOLATION   3024
63                 WA    21-No Parking (street clean)   3732
64                 WI                  14-No Standing   1639
65                 WV  PHTO SCHOOL ZN SPEED VIOLATION   1185
66                 WY    21-No Parking (street clean)    138

[67 rows x 3 columns]
<class 'cudf.pandas.fast_slow_proxy._FastSlowProxyMeta'>
```

## Important Caveats of Setup and Usage

### Python Installation Requirements

Modal's default Python installation uses compilation flags that are not compatible with `numba`, which is required by
RAPIDS. To work around this, you must install Python from Astral's standalone Python builds, which include the correct
compilation flags. As we did in the example above, where we are downloading and installing a standalone Python build in
the Docker setup commands.

### RAPIDS Memory Manager (RMM) Mode

Modal containers use `gvisor` for sandboxing, which does not support `cudaMallocManaged`. This means you cannot use the
default `managed_pool` or `managed` RMM modes with `cudf.pandas`.

Instead, you need to set the environment variable `CUDF_PANDAS_RMM_MODE` to `async` as shown in the example code above.

For more details on RMM modes, see the [cudf.pandas
documentation](https://docs.rapids.ai/api/cudf/stable/cudf_pandas/how-it-works/#how-it-works).
