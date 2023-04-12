# RAPIDS on Google CoLab

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

Checks to make sure that the GPU is RAPIDS compatible, Installs the **current stable** version of RAPIDSAI's core libraries, which are: cuDF, cuML, cuGraph and xgboost.
By default, you can install using `pip` but it is recommended to use `conda` with the [RAPIDS Conda Colab Template](https://colab.research.google.com/drive/1TAAi_szMfWqRfHVfjGSqnGVLr_ztzUM9) notebook if you need to install any RAPIDS Extended libraries OR nightly version.

```console
# This gets the RAPIDS-Colab install files and test checks your GPU.
# Please read the output of this cell.  If your Colab Instance is not RAPIDS compatible, it will warn you and give you remediation steps.

!git clone https://github.com/rapidsai/rapidsai-csp-utils.git
!python rapidsai-csp-utils/colab/pip-install.py

# Installing RAPIDS with conda is now 'python rapidsai-csp-utils/colab/install_rapids.py <release> <packages>'
# The <release> options are 'stable' and 'nightly'. Leaving it blank or adding any other words will default to stable.
!python rapidsai-csp-utils/colab/env-check.py
!bash rapidsai-csp-utils/colab/update_gcc.sh
!python rapidsai-csp-utils/colab/install_rapids.py stable

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

For an overview of how you can access and work with your own datasets in Colab, check out this [guide](https://towardsdatascience.com/3-ways-to-load-csv-files-into-colab-7c14fcbdcb92).
For more RAPIDS examples, check out our RAPIDS [notebooks](https://github.com/rapidsai/notebooks) and [notebooks-contrib](https://github.com/rapidsai/notebooks-contrib) repos
