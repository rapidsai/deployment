## Setting up your instance

Navigate to the Brev.dev console and click on "Create your first instance"

![Alt Text](/_static/images/platforms/brev/brev1.png)

Select Container Mode

![Alt Text](/_static/images/platforms/brev/brev2.png)

Attach the NVIDIA RAPIDS Container

![Alt Text](/_static/images/platforms/brev/brev3.png)

Configure your own instance

![Alt Text](/_static/images/platforms/brev/brev4.png)

And hit Deploy

![Alt Text](/_static/images/platforms/brev/brev5.png)

## Accessing your instance

To create and use a Jupyter Notebook: Click "Open Notebook" at the top right after the page has deployed

![Alt Text](/_static/images/platforms/brev/brev8.png)

On VS Code:

Go to VS Code and type:

```bash
brev open
```

And it will automatically open a new VS Code window for you to use with RAPIDS. 

On Terminal 
Type: 

```bash
brev shell 
```

SSH
### Forwarding a Port Locally:
Assuming your Jupyter Notebook is running on port 8888 in your Brev environment, you can forward this port to your local machine using the following SSH command:

```bash
ssh -L 8888:localhost:8888 <username>@<ip> -p 22
```

This command forwards port 8888 on your local machine to port 8888 on the remote Brev environment.

Or for port 2222 (default port)
```bash
ssh <username>@<ip> -p 2222
```

Replace username with your username and ip with the ip listed if it's different.

### Accessing the Service:
After running the command, open your web browser and navigate to your local host. You will be able to access the Jupyter Notebook running in your Brev environment as if it were running locally.

Access the Jupyter Notebook via the Tunnel:

The "Deployments" section will show that your Jupyter Notebook is running on port 8888, and it is accessible via a shareable URL Ex: "jupyter0-i55ymhsr8.brevlab.com".

Click on the link or copy and paste the URL into your web browser's address bar to access the Jupyter Notebook interface directly.

### Share the Service:
If you want to share access to this service with others, you can click on the "Share a Service" button.

You can also manage access by clicking "Edit Access" to control who has the ability to use this service.

## Check that your notebook has GPU Capabilities

![Alt Text](/_static/images/platforms/brev/brev6.png)

## Test RAPIDS

![Alt Text](/_static/images/platforms/brev/brev7.png)

### Resources:
* [text](https://brev.dev/)