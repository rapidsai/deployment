# RAPIDS on Google Colab

## 0. Launch notebook

To get started in [Google Colab](https://colab.research.google.com/), click `File` at the top toolbar to Create new or Upload existing notebook

## 1. Set the Runtime

Click the `Runtime` dropdown and select `Change Runtime Type`

![Screenshot of create runtime and runtime type](../images/googlecolab-select-runtime-type.png)

Choose GPU for Hardware Accelerator

![Screenshot of gpu for hardware accelerator](../images/googlecolab-select-gpu-hardware-accelerator.png)

## 2. Check GPU type

Check the output of `!nvidia-smi` to make sure you've been allocated a Rapids Compatible GPU, i.e [Tesla T4, P4, or P100].

![Screenshot of nvidia-smi](../images/googlecolab-output-nvidia-smi.png)

## 3. Run RAPIDS install script

Checks GPU compatibility with RAPIDS, then installs the latest **stable** versions of RAPIDSAI's core libraries (cuDF, cuML, cuGraph, and xgboost) using `pip`.

```console
# Colab warns and provides remediation steps if it's not compatible with RAPIDS.

!git clone https://github.com/rapidsai/rapidsai-csp-utils.git
!python rapidsai-csp-utils/colab/pip-install.py
```

<br>

If you need to install any RAPIDS Extended libraries or the nightly version, you can use the [RAPIDS Conda Colab Template](https://colab.research.google.com/drive/1TAAi_szMfWqRfHVfjGSqnGVLr_ztzUM9) notebook and install via `conda`.

```console
# The <release> options are 'stable' and 'nightly'. Leaving it blank or adding any other words will default to 'stable'.

!python rapidsai-csp-utils/colab/env-check.py
!bash rapidsai-csp-utils/colab/update_gcc.sh
!python rapidsai-csp-utils/colab/install_rapids.py <release> <packages>
```

## 4. Test Rapids

```console
import cudf

gdf = cudf.DataFrame({"a":[1,2,3],"b":[4,5,6]})
gdf
    a   b
0   1   4
1   2   5
2   3   6

```

## Next steps

Check out this [guide](https://towardsdatascience.com/) for an overview of how to access and work with your own datasets in Colab.

For more RAPIDS examples, check out our RAPIDS [notebooks](https://github.com/rapidsai/notebooks) and [notebooks-contrib](https://github.com/rapidsai/notebooks-contrib) repos
