---
review_priority: "p0"
---

# NVIDIA Brev

The [NVIDIA Brev](https://brev.nvidia.com/) platform provides you a one stop menu of available GPU instances across many cloud providers, including [Amazon Web Services](https://aws.amazon.com/) and [Google Cloud](https://cloud.google.com), with CUDA, Python, Jupyter Lab, all set up.

## Brev Instance Setup

There are two options to get you up and running with RAPIDS in a few steps, thanks to the Brev RAPIDS quickstart:

1. Brev GPU Environments - quickly get the GPU, across most clouds, to get your work done.
2. Brev Launchables - quickly create one-click starting, reusable instances that you customized to your MLOps needs.

### Option 1. Setting up your Brev GPU Environment

1. Navigate to the [Brev](https://brev.nvidia.com/org) and click on "Create Environment".

![Screenshot of the "Create your first environment" UI](/_static/images/platforms/brev/brev-gpu-env.png)

2. Choose a compute type.

```{hint}
New users commonly choose `L4` GPUs for trying things out.
```

![Screenshot of the "Choose a compute type" UI](/_static/images/platforms/brev/brev-compute.png)

3. Select the "Edit" button to change the software configuration container or runtime (the default is "VM Mode w/ Jupyter")

![Screenshot of the "Editing container or runtime" UI](/_static/images/platforms/brev/brev-edit-software-config.png)

4. Select "Single Container", choose the RAPIDS release, python and CUDA versions, under the "NVIDIA RAPIDS" Container
   selector and hit "Apply".

![Screenshot showing "Single Container" highlighted](/_static/images/platforms/brev/brev-single-container.png)

5. Give your instance a name and hit "Deploy".

![Screenshot of the instance creation summary screen with the deploy button highlighted](/_static/images/platforms/brev/brev-deploy.png)

### Option 2. Setting up your Brev Launchable

Brev Launchables are shareable environment configurations that combine code, containers, and compute into a single
portable recipe. This option is most applicable if you want to set up a custom environment for a blueprint, like
our [Single-cell Analysis Blueprint](https://github.com/NVIDIA-AI-Blueprints/single-cell-analysis-blueprint/).
However, you can use this to create quick-start templates for many different kinds of projects when you want users to
drop into an environment that is ready to go (e.g. tutorials, workshops, demos, etc.).

You can read more about Brev Launchables in the [Launchables documentation](https://docs.nvidia.com/brev/concepts/launchables).

Go to [Brev's Launchable Creator](https://brev.nvidia.com/launchables/create) (requires an account) and follow the instructions for all of the sections below

#### Details

Give your Launchable a name and, optionally, a description.

#### Default Hardware Configuration

Choose a GPU instance type and set the disk storage. People deploying your Launchable can pick a different
configuration, so this is the default rather than a fixed choice.

![Screenshot of the "Default hardware configuration" UI](/_static/images/platforms/brev/brev-launchable-hardware-config.png)

#### Software Configuration

Select Docker Compose, then provide a `docker-compose.yaml` by URL or from a local file, which gets validated.

In the template below, if you are working with a repository, replace `<name_of_your_github_repo>` in the `volumes` entry below with the name of your repository. See the Source section below for more details.

Leave **Install Jupyter on the host** turned off. It installs a separate JupyterLab on the instance on port `8888`, the same port the container publishes, and the RAPIDS container already serves JupyterLab with the example notebooks.

```yaml
services:
  jupyter:
    image: "{{rapids_notebooks_container}}"
    pull_policy: always
    ulimits:
      memlock: -1
      stack: 67108864
    shm_size: 1g
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    environment:
      - EXTRA_CONDA_PACKAGES # Value comes from a launch parameter of the same name
    ports:
      - "8888:8888" # Expose JupyterLab
    volumes:
      # Repo cloned by the Source section, mounted alongside the example notebooks.
      # Remove this entry if you are not adding a repository.
      - /home/ubuntu/<name_of_your_github_repo>:/home/rapids/notebooks/<name_of_your_github_repo>
    user: root
    command: jupyter-lab --notebook-dir=/home/rapids/notebooks --ip=0.0.0.0 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.allow_origin='*'
    restart: unless-stopped
```

![Screenshot of the "Software configuration" UI with "Docker Compose" selected](/_static/images/platforms/brev/brev-launchable-software-config.png)

#### Source

Choose how to provide code files: no code files, a public git repository, or code already embedded in your container.

A git repository is cloned onto the instance at `/home/ubuntu/<name_of_your_github_repo>`, not into the container. To make it visible in JupyterLab, mount it alongside the example notebooks using the `volumes` entry shown above, replacing `<name_of_your_github_repo>` with the name of your repository. Remove the `volumes` entry if you are not adding a repository.

![Screenshot of the "Source" UI with "I have code files in a git repository" selected](/_static/images/platforms/brev/brev-launchable-source.png)

#### Network

Add a Secure Link for port `8888`. This gives JupyterLab a public URL fronted by NVIDIA authentication. The Secure
Link name becomes part of that URL, so a name like `jupyter` is easier to recognise later.

![Screenshot of the "Network" UI with a Secure Link on port 8888](/_static/images/platforms/brev/brev-launchable-network.png)

#### Launch Parameters

This is an optional step. Launch parameters collect values when someone deploys your Launchable and expose them as environment variables during container startup.

This is useful for adding your own libraries to the container via `EXTRA_CONDA_PACKAGES`. Add a launch parameter of that name, set any defaults as you see fit, and then list the variable by name in the compose file so its value is passed into the container. While deploying your Launchable, you can then install extra packages each time without editing the Launchable itself:

```yaml
environment:
  - EXTRA_CONDA_PACKAGES
```

![Screenshot of the "Launch parameters" UI with an EXTRA_CONDA_PACKAGES parameter](/_static/images/platforms/brev/brev-launchable-launch-parameters.png)

#### View Access

Choose whether the Launchable is visible to your organization or to anyone with the link.
Then create the Launchable.

![Screenshot of the "View access" UI](/_static/images/platforms/brev/brev-launchable-view-access.png)

#### Deploying the Launchable

Once created, the Launchable has its own page, which is where you can deploy an instance from and share it for broader use. From there you can change the instance type, adjust the storage, fill in any launch parameters, name the instance, and deploy.

```{figure} /_static/images/platforms/brev/brev-launchable-deploy.png
---
alt: Screenshot of the Launchable page showing instance type, setup values, and the "Deploy Launchable" button
width: 410px
align: center
---
```

```{note}
The Launchable reports that the build has finished before JupyterLab is ready. The container still has to start, and
any packages in `EXTRA_CONDA_PACKAGES` are installed before JupyterLab launches, so the Secure Link can take a minute
or two longer to show the Jupyterlab UI.
```

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
$ sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/brevdev/brev-cli/main/bin/install-latest.sh)" && brev login
```

#### 2.1 Brev CLI using Visual Studio Code

To connect to your Brev instance from VS Code open a new VS Code window and run:

```bash
$ brev open <instance-id>
```

It will automatically open a new VS Code window for you to use with RAPIDS.

#### 2.2 Brev CLI using SSH via your Terminal

To access your Brev instance from the terminal run:

```bash
$ brev shell <instance-id>
```

##### Forwarding a Port Locally

Assuming your Jupyter Notebook is running on port `8888` in your Brev environment, you can forward this port to your local machine using the following SSH command:

```bash
$ ssh -L 8888:localhost:8888 <username>@<ip> -p 22
```

This command forwards port `8888` on your local machine to port `8888` on the remote Brev environment.

Or for port `2222` (default port).

```bash
$ ssh <username>@<ip> -p 2222
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
$ apt update
```

```bash
$ apt install git -y
```
