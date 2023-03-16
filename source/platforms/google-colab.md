# RAPIDS on Google CoLab

## 1. Set the Runtime

In Google Colab, click the `Runtime` dropdown at the top toolbar, then `Change Runtime Type`

![Screenshot of create runtime and runtime type](../../images/.png)

Choose GPU for Hardware Accelerator

![Screenshot of gpu for hardware accelerator](../../images/.png)

## 2. Check GPU type

Check the output of `!nvidia-smi` to make sure you've been allocated a Tesla T4, P4, or P100.

![Screenshot of nvidia-smi](../../images/.png)

## 3. Run RAPIDS install script

Checks to make sure that the GPU is RAPIDS compatible, and Installs the current stable version of RAPIDSAI's core libraries using pip, which are: cuDF, cuML, cuGraph and xgboost.

This setup should take about 3-4 minutes. Please use the [RAPIDS Conda Colab Template notebook] if you need to install any of RAPIDS Extended libraries OR nightly version of any library .

```console
# This get the RAPIDS-Colab install files and test check your GPU.  Run this and the next cell only.
# Please read the output of this cell.  If your Colab Instance is not RAPIDS compatible, it will warn you and give you remediation steps.

!git clone https://github.com/rapidsai/rapidsai-csp-utils.git
!python rapidsai-csp-utils/colab/pip-install.py
```

## 4. Test Rapids

```console
import cudf, cuml
cudf__version__
cuml__version__

```

## Next steps

For an overview of how you can access and work with your own datasets in Colab, check out this guide.
