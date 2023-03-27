# RAPIDS on Google CoLab

## 1. Set the Runtime

In [Google Colab](https://colab.research.google.com/), click the `Runtime` dropdown at the top toolbar, then `Change Runtime Type`

![Screenshot of create runtime and runtime type](../../images/googlecolab-select-runtime-type.png)

Choose GPU for Hardware Accelerator

![Screenshot of gpu for hardware accelerator](../../images/googlecolab-select-gpu-hardware-accelerator.png)

## 2. Check GPU type

Check the output of `!nvidia-smi` to make sure you've been allocated a Rapids Compatible GPU, i.e [Tesla T4, P4, or P100].

![Screenshot of nvidia-smi](../../images/googlecolab-output-nvidia-smi.png)

## 3. Run RAPIDS install script

Checks to make sure that the GPU is RAPIDS compatible, Installs the **current stable** version of RAPIDSAI's core libraries using conda, which are: cuDF, cuML, cuGraph and xgboost.
Please use the [RAPIDS Conda Colab Template notebook](https://colab.research.google.com/drive/1TAAi_szMfWqRfHVfjGSqnGVLr_ztzUM9) if you need to install any RAPIDS Extended libraries OR nightly version.

```console
# This gets the RAPIDS-Colab install files and test checks your GPU.
# Please read the output of this cell.  If your Colab Instance is not RAPIDS compatible, it will warn you and give you remediation steps.

!git clone https://github.com/rapidsai/rapidsai-csp-utils.git
!python rapidsai-csp-utils/colab/install_rapids.py
```

## 4. Test Rapids

```console
import cudf, cuml
cudf.__version__
cuml.__version__

```

## Next steps

For an overview of how you can access and work with your own datasets in Colab, check out this [guide](https://towardsdatascience.com/3-ways-to-load-csv-files-into-colab-7c14fcbdcb92).
For more RAPIDS examples, check out our RAPIDS [notebooks](https://github.com/rapidsai/notebooks) and [notebooks-contrib](https://github.com/rapidsai/notebooks-contrib) repos
