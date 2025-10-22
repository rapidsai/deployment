---
review_priority: "p1"
---

# Elastic Compute Cloud (EC2)

## Create Instance

Create a new [EC2 Instance](https://aws.amazon.com/ec2/) with GPUs, the [NVIDIA Driver](https://www.nvidia.co.uk/Download/index.aspx) and the [NVIDIA Container Runtime](https://developer.nvidia.com/nvidia-container-runtime).

NVIDIA maintains an [Amazon Machine Image (AMI) that pre-installs NVIDIA drivers and container runtimes](https://aws.amazon.com/marketplace/pp/prodview-7ikjtg3um26wq), we recommend using this image as the starting point.

`````{tab-set}

````{tab-item} via AWS Console
:sync: console

1. Open the [**EC2 Dashboard**](https://console.aws.amazon.com/ec2/home).
1. Select **Launch Instance**.
1. In the AMI selection box search for "nvidia", then switch to the **AWS Marketplace AMIs** tab.
1. Select **NVIDIA GPU-Optimized AMI** and click "Select". Then, in the new popup, select **Subscribe on Instance Launch**.
1. In **Key pair** select your SSH keys (create these first if you haven't already).
1. Under network settings create a security group (or choose an existing) with inbound rules that allows SSH access on
   port `22` and also allow ports `8888,8786,8787` to access Jupyter and Dask. For outbound rules, allow all traffic.
1. Select **Launch**.

````

````{tab-item} via AWS CLI
:sync: cli

1. Set the following environment variables first. Edit any of them to match your preferred region, instance type, or naming convention.

   ```bash
   REGION=us-east-1
   INSTANCE_TYPE=g5.xlarge
   KEY_NAME=rapids-ec2-key
   SG_NAME=rapids-ec2-sg
   VM_NAME=rapids-ec2
   ```

2. Accept the NVIDIA Marketplace subscription before using the AMI: open the [NVIDIA GPU-Optimized AMI listing](https://aws.amazon.com/marketplace/pp/prodview-7ikjtg3um26wq), choose **Continue to Subscribe**, then select **Accept Terms**. Wait for the status to show as active.

3. Find the most recent NVIDIA Marketplace AMI ID in `us-east-1`.

   ```bash
   AMI_ID=$(aws ec2 describe-images \
       --region "$REGION" \
       --filters "Name=name,Values=*NVIDIA*VMI*Base*" "Name=state,Values=available" \
       --query 'Images | sort_by(@, &CreationDate)[-1].ImageId' \
       --output text)
   echo "$AMI_ID"
   ```

4. Create an SSH key pair and secure it locally (if you already have a key, update `KEY_NAME` and skip this step).

   ```bash
   aws ec2 create-key-pair --region "$REGION" --key-name "$KEY_NAME" \
       --query 'KeyMaterial' --output text > "${KEY_NAME}.pem"
   chmod 400 "${KEY_NAME}.pem"
   ```

5. Create a security group that allows SSH on `22` plus the Jupyter (`8888`) and Dask (`8786`, `8787`) ports, and keep outbound traffic open. Replace `0.0.0.0/0` with a narrower CIDR if you want to restrict inbound access.

   ```bash
   VPC_ID=$(aws ec2 describe-vpcs \
       --region "$REGION" \
       --query 'Vpcs[0].VpcId' \
       --output text)
   echo "$VPC_ID"

   SG_ID=$(aws ec2 create-security-group \
       --region "$REGION" \
       --group-name "$SG_NAME" \
       --description "RAPIDS EC2 security group" \
       --vpc-id "$VPC_ID" \
       --query 'GroupId' \
       --output text)
   echo "$SG_ID"
   ```

   ```bash
   aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" \
       --protocol tcp --port 22 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" \
       --protocol tcp --port 8888 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" \
       --protocol tcp --port 8786 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" \
       --protocol tcp --port 8787 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-egress --region "$REGION" --group-id "$SG_ID" \
       --protocol all --cidr 0.0.0.0/0
   ```

6. Launch an EC2 instance with the NVIDIA AMI.

   ```bash
   INSTANCE_ID=$(aws ec2 run-instances \
       --region "$REGION" \
       --image-id "$AMI_ID" \
       --count 1 \
       --instance-type "$INSTANCE_TYPE" \
       --key-name "$KEY_NAME" \
       --security-group-ids "$SG_ID" \
       --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$VM_NAME}]" \
       --query 'Instances[0].InstanceId' \
       --output text)
   echo "$INSTANCE_ID"
   ```
````

`````

## Connect to the instance

Next we need to connect to the instance.

`````{tab-set}

````{tab-item} via AWS Console
:sync: console

1. Open the [**EC2 Dashboard**](https://console.aws.amazon.com/ec2/home).
2. Locate your VM and note the **Public IP Address**.
3. In your terminal run `ssh ubuntu@<ip address>`.

```{note}
If you use the AWS Console, please use the default `ubuntu` user to ensure the NVIDIA driver installs on the first boot.
```

````

````{tab-item} via AWS CLI
:sync: cli

1. Wait for the instance to pass health checks.

   ```bash
   aws ec2 wait instance-status-ok --region "$REGION" --instance-ids "$INSTANCE_ID"
   ```

2. Retrieve the public IP address and use it to connect via SSH

   ```bash
   PUBLIC_IP=$(aws ec2 describe-instances \
       --region "$REGION" \
       --instance-ids "$INSTANCE_ID" \
       --query 'Reservations[0].Instances[0].PublicIpAddress' \
       --output text)
   echo "$PUBLIC_IP"
   ```

3. Connect over SSH using the key created earlier.

   ```bash
   ssh -i "${KEY_NAME}.pem" ubuntu@"$PUBLIC_IP"
   ```

```{note}
If you see `WARNING: UNPROTECTED PRIVATE KEY FILE!`, run `chmod 400 rapids-ec2-key.pem` before retrying.
```

````

`````

## Install RAPIDS

```{include} ../../_includes/install-rapids-with-docker.md

```

```{note}
If you see a "modprobe: FATAL: Module nvidia not found in directory /lib/modules/6.2.0-1011-aws" while first connecting to the EC2 instance, try logging out and reconnecting again.
```

## Test RAPIDS

```{include} ../../_includes/test-rapids-docker-vm.md

```

```{relatedexamples}

```
