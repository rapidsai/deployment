---
review_priority: "p0"
---

# NVIDIA Brev

The [NVIDIA Brev](https://brev.nvidia.com/) platform provides you a one stop menu of available GPU instances across many cloud providers, including [Amazon Web Services](https://aws.amazon.com/) and [Google Cloud](https://cloud.google.com), with CUDA, Python, Jupyter Lab, all set up.

## Brev Instance Setup

THere are two options to get you up and running with RAPIDS in a few steps, thanks to the Brev RAPIDS quickstart:

1. Brev GPU Instances - quickly get the GPU, across most clouds, to get your work done.
2. Brev Launchables - quickly create one-click starting, reusable instances that you customized to your MLOps needs.

### Option 1. Setting up your Brev GPU Instance

1. Navigate to the [Brev console](https://brev.nvidia.com/org) and click on "Create your first instance".

![Screenshot of the "Create your first instance" UI](/_static/images/platforms/brev/brev1.png)

2. Select "Container Mode".

![Screenshot showing "Container Mode" highlighted](/_static/images/platforms/brev/brev2.png)

3. Attach the "NVIDIA RAPIDS" Container.

![Screenshot showing the "NVIDIA RAPIDS" container highlighted](/_static/images/platforms/brev/brev3.png)

4. Configure your own instance.

![Screenshot of the "Create your Instance" UI with an NVIDIA T4 GPU highlighted](/_static/images/platforms/brev/brev4.png)

5. And hit "Deploy".

![Screenshot of the instance creation summary screen with the deploy button highlighted](/_static/images/platforms/brev/brev5.png)

### Option 2. Setting up your Brev Launchable

> [!WARNING]  
> Our Docker Compose YAML files have a known issue when using GCP resources on Brev. We recommend using another cloud provider until this is resolved.

1. Go to [Brev’s Launchable Creator](https://brev.nvidia.com/launchables/create) (requires account)  
2. When asked **How would you like to provide your code files?** select "I have code files in a GitHub repository". Enter the URL of this repository. 
3. When asked **What type of runtime environment do you need?** select "With container(s)"
4. Under **Choose a Container Configuration** select "Docker Compose" and click on the toggle to select "I have an existing docker-compose.yaml file".
5. Under **Upload Docker Compose** select "Provide GitHub/Gitlab URL" and provide a link to one of the Docker Compose YAML files in the [docker/brev](../docker/brev) directory. There is a README.md in that directory with instructions on which YAML to select. Note, you need to pass a link to the file in GitHub, not to the `raw.github.com` file (e.g. [docker-compose-nb-2412.yaml](https://github.com/clara-parabricks-workflows/single-cell-analysis-blueprint/blob/main/docker/brev/docker-compose-nb-2412.yaml)). Click "Validate".
6. On the next page, when asked **Do you want a Jupyter Notebook experience?** select "No, I don't want Jupyter (Not Recommended)". We will provide Jupyter in the Docker compose already.
7. In the section title **Do you need to expose services?** make sure that ports `8888`, `8787`, and `8786` are open. Name port 8888 `jupyter` so Brev can treat it as a jupyterlab based instance and provide an Open Notebook button.
8. Select your desired compute environment. Make sure you select sufficient disk size to download the datasets you want to work with. We recommend at least 128GB, unless you want to run the 11M cell notebook, which you will need atleast 200GB. Note, you will not be able to resize the instance once created.
9. Create a name for your launchable, and deploy.

> [!NOTE]
> Git is not installed by default in this container, but it can be installed using
> ```
> apt update
> apt install git -y
> ```

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

If you want to access your launched Brev instance(s) via Visual Studio Code or SSH using terminal, you need to install the [Brev CLI according to these instructions](https://docs.nvidia.com/brev/latest/brev-cli.html) or this code below:

```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/brevdev/brev-cli/main/bin/install-latest.sh)" && brev login
```

#### 2.1 Brev CLI using Visual Studio Code

To connect to your Brev instance from VS Code open a new VS Code window and run:

```bash
brev open <instance-id>
```

It will automatically open a new VS Code window for you to use with RAPIDS.

#### 2.2 Brev CLI using SSH via your Terminal

To access your Brev instance from the terminal run:

```bash
brev shell <instance-id>
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

## Testing your RAPIDS Instance

You can verify your RAPIDS installation is working by importing `cudf` and creating a GPU dataframe.

```python
import cudf

gdf = cudf.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
print(gdf)
```

## Resources and tips

- [Brev Docs](https://brev.dev/)
- Please note: Git is not preinstalled in the RAPIDS container, but can be installed into the container when it is running using

```bash
apt update
apt install git -y
```
