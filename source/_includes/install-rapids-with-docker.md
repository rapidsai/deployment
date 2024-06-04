There are a selection of methods you can use to install RAPIDS which you can see via the [RAPIDS release selector](https://docs.rapids.ai/install#selector).

For this example we are going to run the RAPIDS Docker container so we need to know the name of the most recent container.
On the release selector choose **Docker** in the **Method** column.

Then copy the commands shown:

```bash
docker pull {{ rapids_container }}
docker run --gpus all --rm -it \
    --shm-size=1g --ulimit memlock=-1 \
    -p 8888:80 -p 8787:8787 -p 8786:8786 \
    {{ rapids_notebooks_container }}
```

```{note}
If you see a "docker socket permission denied" error while running these commands try closing and reconnecting your
SSH window. This happens because your user was added to the `docker` group only after you signed in.
```
