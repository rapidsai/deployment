# GitHub Actions

GitHub Actions is a popular way to automatically run tests against code hosted on GitHub.

GitHub's free tier includes basic runners (the machines that will run your code) and the paid tier includes support for
[hosted runners with NVIDIA
GPUs](https://github.blog/changelog/2024-07-08-github-actions-gpu-hosted-runners-are-now-generally-available/). This
allows GPU specific code to be exercised as part of a CI workflow.

## Cost

As GPU runners are not included in the free tier projects will have to pay for GPU CI resources. Typically GPU runners
cost a few cents per minute, check out the [GitHub
documentation](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions#per-minute-rates-for-gpu-powered-larger-runners)
for more information.

We recommend that projects set a [spending
limit](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions#about-spending-limits)
on their account/organization. That way your monthly bill will never be a surprise.

We also recommend that you only run GPU CI intentionally rather than on every pull request from every contributor. Check
out the best practices section for more information.

## Getting started

### Setting up your GPU runners

First you'll need to set up a way to pay GitHub. You can do this by [adding a payment
method](https://docs.github.com/en/billing/managing-your-github-billing-settings/adding-or-editing-a-payment-method) to
your organisation.

While you're in your billing settings you should also decide what the maximum is that you wish to spend on GPU CI
functionality and then set a [spending
limit](https://docs.github.com/en/billing/managing-billing-for-github-actions/managing-your-spending-limit-for-github-actions)
on your account.

Next you can go into the GitHub Actions settings for your account and configure a [larger
runner](https://docs.github.com/en/actions/using-github-hosted-runners/using-larger-runners/about-larger-runners). You
can find this settings page by visiting `https://github.com/organizations/<YOUR_ORG>/settings/actions/runners`.

![Screenshot of the GitHub Actions runner configuration page with the new runner button
highlighted](/_static/images/developer/ci/github-actions/new-hosted-runner.png)

Next you need to give your runner a name, for example `linux-nvidia-gpu`, you'll need to remember this for configuring
your workflows later. Then you need to choose your runner settings:

- Under "Platform" select "Linux x64"
- Under "Image" switch to the "Partner" tab and choose "NVIDIA GPU-Optimized Image for AI and HPC"
- Under "Size" switch to the "GPU-powered" tab and select your preferred NVIDIA hardware

![Screenshot of the GitHub Actions runner configuration page a new GPU runner
configured](/_static/images/developer/ci/github-actions/new-runner-config.png)

Then set your preferred maximum concurrency and then choose "Create runner".

### Configuring your workflows

To configure your workflow to use your new GPU runners you need to set the `runs-on` property to match the name you gave
the runner group.

```yaml
name: GitHub Actions GPU Demo
run-name: ${{ github.actor }} is testing out GPU GitHub Actions 🚀
on: [push]
jobs:
  gpu-workflow:
    runs-on: linux-nvidia-gpu
    steps:
      - name: Check GPU is available
        run: nvidia-smi
```

## Best practices

Adding GitHub Actions runners to your project that cost money requires you to put some extra thought into when you want
those workflows to run. Setting a spending cap allows you to keep control of how much you are spending, but you still
want to get the most for your money. Here are some tips on when to effectively use GPU runners in your projects.

### Use labels to trigger workloads

Instead of always triggering your GPU workflows on every push or pull request you can use labels to trigger workflows.
This is a great option if your project is public and anyone can make a pull request with any arbitrary code. You may
want to have a mechanism for a trusted maintainer or collaborator to trigger the GPU workflow manually.

The scikit-learn project solved this by having a label that triggers the workflow.

```yaml
name: NVIDIA GPU workflow
on:
  pull_request:
    types:
      - labeled

jobs:
  tests:
    if: contains(github.event.pull_request.labels.*.name, 'GPU CI')
    runs-on:
      group: linux-nvidia-gpu
    steps: ...
```

The above config specifies a workflow should only be run when the `GPU CI` label is added to the pull request. They then
have a second [label remover
workflow](https://github.com/scikit-learn/scikit-learn/blob/9d39f57399d6f1f7d8e8d4351dbc3e9244b98d28/.github/workflows/cuda-label-remover.yml)
which removed the label again, which allows a maintainer to add it again in the future to trigger the GPU CI workflow
any number of times during the review of the pull request.

### Run nightly

Some projects might not need to run GPU tests for every pull request, but instead might prefer to run a nightly
regression test to ensure that nothing that has been merged has broken GPU functionality.

You can configure a GitHub Actions workflow to run on a schedule and use [an
action](https://github.com/marketplace/actions/failed-build-issue) to open an issue if the workflow fails.

```yaml
name: Nightly GPU Tests

on:
  schedule:
    - cron: "0 0 * * *" # Run every day at 00:00 UTC

jobs:
  tests:
    name: GPU Tests
    runs-on: linux-nvidia-gpu
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          # Run tests here
      - name: Notify failed build
        uses: jayqi/failed-build-issue-action@v1
        if: failure() && github.event.pull_request == null
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### Run only on certain codepaths

You may also want to only run your GPU CI tests when code at certain paths has been modified. To do this you can use the
[`on.push.paths`
filter](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#example-including-paths).

```yaml
name: GPU Tests
on:
  push:
    paths:
      - "src/gpu_submodule/**/*.py"

jobs:
  tests:
    name: GPU Tests
    runs-on: linux-nvidia-gpu
    steps: ...
```

## Further Reading

- [Blog from scikit-learn Developers on their experiences](https://betatim.github.io/posts/github-action-with-gpu/)
