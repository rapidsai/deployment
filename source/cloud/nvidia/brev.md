# NVIDIA Brev

The [NVIDIA Brev](https://brev.dev/) platform provides you with GPU instances on cloud providers including [Amazon Web Services](https://aws.amazon.com/) and [Google Cloud](https://cloud.google.com) with CUDA, Python, Jupyter Lab, all set up.

You can get up and running with RAPIDS in a few quicks thanks to the Brev RAPIDS quickstart.

## Setting up your instance

Navigate to the [Brev console](https://console.brev.dev/) and click on "Create your first instance".

![Screenshot of the "Create your first instance" UI](/_static/images/platforms/brev/brev1.png)

Select "Container Mode".

![Screenshot showing "Container Mode" highlighted](/_static/images/platforms/brev/brev2.png)

Attach the "NVIDIA RAPIDS" Container.

![Screenshot showing the "NVIDIA RAPIDS" container highlighted](/_static/images/platforms/brev/brev3.png)

Configure your own instance.

![Screenshot of the "Create your Instance" UI with an NVIDIA T4 GPU highlighted](/_static/images/platforms/brev/brev4.png)

And hit "Deploy".

![Screenshot of the instance creation summary screen with the deploy button highlighted](/_static/images/platforms/brev/brev5.png)

## Accessing your instance

### Jupyter Notebook

To create and use a Jupyter Notebook, click "Open Notebook" at the top right after the page has deployed.

![Screenshot of the instance UI with the "Open Notebook" button highlighted](/_static/images/platforms/brev/brev8.png)

### Visual Studio Code

To connect to your Brev instance from VS Code open a new VS Code window and run:

```bash
brev open
```

It will automatically open a new VS Code window for you to use with RAPIDS.

### Terminal

To access your Brev instance from the terminal run:

```bash
brev shell
```

### Forwarding a Port Locally

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

### Accessing the Service

After running the command, open your web browser and navigate to your local host. You will be able to access the Jupyter Notebook running in your Brev environment as if it were running locally.

### Access the Jupyter Notebook via the Tunnel

The "Deployments" section will show that your Jupyter Notebook is running on port `8888`, and it is accessible via a shareable URL Ex: `jupyter0-i55ymhsr8.brevlab.com`.

Click on the link or copy and paste the URL into your web browser's address bar to access the Jupyter Notebook interface directly.

#### Share the Service

If you want to share access to this service with others, you can click on the "Share a Service" button.

You can also manage access by clicking "Edit Access" to control who has the ability to use this service.

## Check that your notebook has GPU Capabilities

You can verify that you have your requested GPU by running the `nvidia-smi` command.

![Screenshot of a notebook terminal running the command nvidia-smi and showing the NVIDIA T4 GPU in the output](/_static/images/platforms/brev/brev6.png)

## Test RAPIDS

You can verify your RAPIDS installation is working by importing `cudf` and creating a GPU dataframe.

![Screenshot of a notebook cell importing and using cudf](/_static/images/platforms/brev/brev7.png)

### Resources

- [Brev Docs](https://brev.dev/)
