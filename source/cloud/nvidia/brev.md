---
review_priority: "p0"
---

# NVIDIA Brev

The [NVIDIA Brev](https://brev.dev/) platform provides you a one stop menu of available GPU instances across many cloud providers, including [Amazon Web Services](https://aws.amazon.com/) and [Google Cloud](https://cloud.google.com), with CUDA, Python, Jupyter Lab, all set up.

## Brev Instance Setup 
There are two ways that you can get up and running with RAPIDS in a few quicks thanks to the Brev RAPIDS quickstart:
1. Brev GPU Instances - quickly get the GPU, across most clouds, to get your work done.
2. Brev Launchables - quickly create one-click starting, reusable instances that you customized to your MLOps needs.

### 1. Setting up your Brev GPU Instance

1. Navigate to the [Brev console](https://console.brev.dev/) and click on "Create your first instance".

![Screenshot of the "Create your first instance" UI](/_static/images/platforms/brev/brev1.png)

2. Select "Container Mode".

![Screenshot showing "Container Mode" highlighted](/_static/images/platforms/brev/brev2.png)

3. Attach the "NVIDIA RAPIDS" Container.

![Screenshot showing the "NVIDIA RAPIDS" container highlighted](/_static/images/platforms/brev/brev3.png)

4. Configure your own instance.

![Screenshot of the "Create your Instance" UI with an NVIDIA T4 GPU highlighted](/_static/images/platforms/brev/brev4.png)

5. And hit "Deploy".

![Screenshot of the instance creation summary screen with the deploy button highlighted](/_static/images/platforms/brev/brev5.png)

### 2. Setting up your Brev Launchable
1. Click Create Launchable
1. Click **Compute** and select your GPU based on GPU type, number of GPUs, the cloud provider, and/or budget you have.  It is good to understand your GPU requirements before picking an instance, or use it to figure out which instance.  Once selected, click **Save** 
1. Click ** Container**.  When adding the **Container**, you can use the NVIDIA RAPIDS Container, use Docker Compose and edit our example yaml so that it preinstalls any additional conda or pip packages into your container before entry.  
  1. If you just need standard NVIDIA RAPIDS install, Select **Container Mode > NVIDIA RAPIDS Container**. If using the Base Container, you may need to preinstall Jupyter.  If using the Notebooks Container, **Do not** Preinstall Jupyter, as that will break your instance.
  1. If you need a customized environment, with additional packages on top of NVIDIA RAPIDSm use **Docker Compose** When using Docker Compose, you can upload a docker-compse yaml file.  Here is an example docker-compose file, **[docker/brev/docker-compose-nb-2412.yaml](https://github.com/clara-parabricks-workflows/single-cell-analysis-blueprint/raw/main/docker/brev/docker-compose-nb-2412.yaml)** that you can use as your base.  **Do not** Preinstall Jupyter when using that file, as it already will be installed.
  1. Click **Save**
1. Click **Files** and add in any publicly avaialble single file or  github repository.  Click **Save**
1. In **Ports**, please open ports **8888, 8787, and 8786**.  Name port 8888 `jupyter` so Brev can treat it as a Jupyter-Lab based instance and provide an **Open Notebook** button.  Click **Save**
1. Name your Launchable, then Save your Launchable!
1. Whenever you're ready to use your Launchable, Select your Launchable and hit **Deploy Launchable** 

## Accessing your instance
There are a few ways to access your instance:
1. Directly access Jupyter Lab from the Brev GUI
1. Using the Brev CLI to connect to your instance....
  1. Using Visual Studio Code
  1. Using SSH via your terminal
1. Access using the Brev tunnel
1. Sharing a service with others

### 1. Jupyter Notebook

To create and use a Jupyter Notebook, click "Open Notebook" at the top right after the page has deployed.

![Screenshot of the instance UI with the "Open Notebook" button highlighted](/_static/images/platforms/brev/brev8.png)

### 2. Brev CLI Install
If you want to access your launched Brev instance(s) via Visual Studio Code or SSH using terminal, you need to install the [Brev CLI according to these instructions](https://docs.nvidia.com/brev/latest/brev-cli.html).

#### 2.1 Brev CLI using Visual Studio Code

To connect to your Brev instance from VS Code open a new VS Code window and run:

```bash
brev open
```

It will automatically open a new VS Code window for you to use with RAPIDS.

#### 2.2 Brev CLI using SSH via your Terminal

To access your Brev instance from the terminal run:

```bash
brev shell
```

##### Forwarding a Port Locally

Assuming your Jupyter Notebook is running on port `8888` in your Brev environment, you can forward this port to your local machine using the following SSH command:

```bash
ssh -L 8888:localhost:8888 <username>@<ip> -p 22
```

This command forwards port `8888` on your local machine to port `8888` on the remote Brev environment.

Or for port `2222` (default port).

```bash
ssh <username>@<ip> -p 2222
```

Replace `username` with your username and `ip` with the ip listed if it's different.

##### Accessing the Service

After running the command, open your web browser and navigate to your local host. You will be able to access the Jupyter Notebook running in your Brev environment as if it were running locally.

#### 3. Access the Jupyter Notebook via the Tunnel

The "Deployments" section will show that your Jupyter Notebook is running on port `8888`, and it is accessible via a shareable URL Ex: `jupyter0-i55ymhsr8.brevlab.com`.

Click on the link or copy and paste the URL into your web browser's address bar to access the Jupyter Notebook interface directly.

##### 4. Share the Service

If you want to share access to this service with others, you can click on the "Share a Service" button.

You can also manage access by clicking "Edit Access" to control who has the ability to use this service.

### Check that your notebook has GPU Capabilities

You can verify that you have your requested GPU by running the `nvidia-smi` command.

![Screenshot of a notebook terminal running the command nvidia-smi and showing the NVIDIA T4 GPU in the output](/_static/images/platforms/brev/brev6.png)

### Test RAPIDS

You can verify your RAPIDS installation is working by importing `cudf` and creating a GPU dataframe.

![Screenshot of a notebook cell importing and using cudf](/_static/images/platforms/brev/brev7.png)



### Resources and tips

- [Brev Docs](https://brev.dev/)
- Please note: Git is not preinstalled in the RAPIDS container, but can be installed into the container when it is running using
```
apt update
apt install git -y
```
