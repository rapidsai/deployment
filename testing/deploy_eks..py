### RUN WITH python eks_deploy.py 2>&1 | tee test-deploy<some number>.txt so you can see your output ###
### TODOs: 
### 1. create wrapper script to have it run 


import nbformat
import pandas as pd
import cudf
import platform
import os
import pynvml
import sys
import timeit
import argparse

from datetime import datetime
from nbconvert.preprocessors import ExecutePreprocessor

import subprocess
import pexpect
import os
import argparse
from datetime import date
import math

# auto get most likely next release
rap_ver = date.today().month
rap_year = date.today().year

def getnextrelease(f):
    return math.ceil(f / 2.) * 2

rap_ver = getnextrelease(rap_ver)
if (rap_ver < 10):
    rap_ver = "0"+str(rap_ver)
else:
    rap_ver = str(rap_ver)

rap_year = str(rap_year)
rap_ver = rap_year[2:]+"."+rap_ver
print(rap_ver)

parser = argparse.ArgumentParser()

# add arguments to the parser
parser.add_argument("--clusterName", default="rapids-eks-deploy")
parser.add_argument("--aws_pem", default="", help= "Please provide a path to save your private key")
parser.add_argument("--pubName", default="", help= "Please provide a path to save your public key")
parser.add_argument("--instance", default='p3.8xlarge', choices= ['p3.2xlarge','p3.8xlarge','p3.4xlarge'])
parser.add_argument("--verbose", default='n', choices=["y", "n"])
parser.add_argument("--runType", default='testing', choices=["testing", "deployment","release", "prereqs"])
parser.add_argument("--root", default='y', choices=["y", "n"])
parser.add_argument("--release", default='nightly', choices=["stable", "nightly"]) # doesn't work yet, may go into parent script

def get_eks():
    def install_eks():
        print(f'curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_{PLATFORM}.tar.gz"')
        os.system(f'curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_{PLATFORM}.tar.gz"')
        os.system("mkdir tmp")
        os.system(f'tar -xzf eksctl_{PLATFORM}.tar.gz -C tmp && rm eksctl_{PLATFORM}.tar.gz')
        os.system("ls tmp")
        os.system(f"mv tmp/eksctl /usr/local/bin/eksctl")
        if not root:
            os.system(f"mv tmp/eksctl {eksctl}")
            os.system(f"mv tmp/eksctl ~/.local/bin")
        print("complete")

    def check_eks(verbose):
        result = subprocess.run([eksctl,'version'], capture_output=True, text=True, check=False)
        if verbose:
            if result.stdout != "":
                print("output", result.stdout)
            if result.stderr != "":
                print("error", result.stderr)
        return result
    
    import subprocess
    platform = subprocess.check_output(['uname', '-s'], text=True)
    print(platform)
    ARCH="amd64"
    PLATFORM= platform.strip()+"_"+ARCH
    try:
        eks_result= check_eks(verbose)
    except:
        install_eks()
        eks_result = check_eks(verbose)
    install_results.append(eks_result)
    
def get_aws():
    # install aws
    def install_aws():
        os.system('apt install unzip')
        os.system('curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"')
        os.system("unzip awscliv2.zip")
        if not root:
            os.system("./aws/install -i ~/.local/aws-cli -b ~/.local/bin")
        else:
            os.system("./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update")

    def check_aws(verbose):
        result = subprocess.run([aws,'--version'], capture_output=True, text=True, check=False)
        if verbose:
            if result.stdout != "":
                print("output", result.stdout)
            if result.stderr != "":
                print("error", result.stderr)
        return result
    
    def config_aws(verbose):
        print("in config")
        output = []
        lines = creds.split("\n")
        print(lines[0])
        print(lines[1])
        for i in range (1, len(lines)-1): # get AWS creds only
            # print(lines[i])
            line = lines[i].split("= ")
            # print(line)
            line = line[1].strip()
            output.append(line)
        # print(output)
        child = pexpect.spawn('aws configure')
        # print("process spawned")
        child.delaybeforesend = 2
        # print(child)
        child.expect ('Key ID*') 
        child.sendline (output[0]) 
        child.expect ('Access Key* ')
        child.sendline (output[1]) 
        # print("Both keys inputed")
        child.expect ('name* ')
        child.sendline ("\r\n")
        child.expect ('format* ')
        child.sendline ("\r\n")
        # print("done")
        #child.interact()
        prompt = child.after
        if verbose:
            print(prompt)
    import subprocess

    try:
        aws_result= check_aws(verbose)
    except:
        install_aws()
        aws_result = check_aws(verbose)
    if runType != "prereqs":
        try:
            config_aws(verbose)
        except:
            print("AWS confiuration failure.  Script will only INSTALL PREREQS.  Please fix your AWS credentials and try again")
            runType == "prereqs"
    install_results.append(aws_result)
    
def get_kubectl():
    # install kubectrl
    def install_kubectl():
        os.system('curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"')
        os.system('curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"')
        if not root:
            os.system("mv ./kubectl ~/.local/bin/kubectl") # no root
            os.system("chmod +x kubectl")
            os.system(f"mv ./kubectl {kubectl}")
        else:
            os.system(f"install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl")

    def check_kubectl(verbose):
        result = subprocess.run([kubectl,'version','--client'], capture_output=True, text=True, check=False)
        if verbose:
            if result.stdout != "":
                print("output", result.stdout)
            if result.stderr != "":
                print("error", result.stderr)
        return result
    import subprocess

    try:
        kube_result= check_kubectl(verbose)
    except:
        install_kubectl()
        kube_result= check_kubectl(verbose)
    install_results.append(kube_result)

def get_helm():
    # install Helm
    def install_helm():
        os.system("curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3")
        os.system("chmod 700 get_helm.sh")
        os.system("./get_helm.sh")

    def check_helm(verbose):
        result = subprocess.run([helm,'version'], capture_output=True, text=True, check=False)
        if verbose:
            if result.stdout != "":
                print("output", result.stdout)
            if result.stderr != "":
                print("error", result.stderr)
        return result
    import subprocess

    try:
        helm_result= check_helm(verbose)
    except:
        install_helm()
        helm_result = check_helm(verbose)
    install_results.append(helm_result)
def check_aws():
    result = subprocess.run(['ls',f'{hd}/.aws/'], capture_output=True, text=True, check=False)
    if verbose:
        if result.stdout != "":
            print("output", result.stdout)
        if result.stderr != "":
            print("error", result.stderr)
    install_results.append(result)
    
def check_install():
    failed = False
    fail_install = []
    for r in install_results:
        if r.returncode != 0:
            failed = True
            fail_install.append([r.args, r.returncode, r.stderr])
    if failed == False:
        print("Setup installed correctly")
        return True, None
    else:
        print(fail_install)
        return False, fail_install
    if verbose:
        print(install_result)

def get_creds():
    print("Enter/Paste your AWS creds, then hit <ENTER>.")
    no_of_lines = 3
    lines = "[default]\n"
    for i in range(no_of_lines):
        lines+=input()+"\n"
    return lines

def set_aws_config(path):
    file1 = open(path, "w")
    L = ["[default]\n",
         "region = none\n",
         "role_arn = arn:aws:iam::561241433344:role/eksctlMinPolicyRole\n",
         "output =  none\n",
         "source_profile = default"]
    file1.writelines(L)
    file1.close()
    
def set_aws_creds(path, creds):
    file1 = open(path, "w")
    file1.writelines(creds)
    file1.close()
    
def eks_create_cluster(name, pub, instance):
    print(f'{eksctl} create cluster {name} \
                      --version 1.24 \
                      --nodes 3 \
                      --node-type={instance} \
                      --timeout=40m \
                      --ssh-access \
                      --ssh-public-key {pub}  \
                      --region us-east-1 \
                      --zones=us-east-1c,us-east-1b,us-east-1d \
                      --auto-kubeconfig \
                      --install-nvidia-plugin=false')
    os.system(f'{eksctl} create cluster {name} \
                      --version 1.24 \
                      --nodes 3 \
                      --node-type={instance} \
                      --timeout=40m \
                      --ssh-access \
                      --ssh-public-key {pub}  \
                      --region us-east-1 \
                      --zones=us-east-1c,us-east-1b,us-east-1d \
                      --auto-kubeconfig \
                      --install-nvidia-plugin=false')

def apply_rapids():
    result = subprocess.run(['kubectl','apply','-f','rapids-notebook.yaml'], capture_output=True, text=True, check=False)
    if verbose:
        if result.stdout != "":
            print("output", result.stdout)
        if result.stderr != "":
            print("error", result.stderr)
    return result

def fwd_rapids():
    result = subprocess.run(['kubectl','port-forward','service/rapids-notebook','9888'], capture_output=True, text=True, check=False)
    if verbose:
        if result.stdout != "":
            print("output", result.stdout)
        if result.stderr != "":
            print("error", result.stderr)
    return result
    
def set_up_key(path, name):
    print(path, name)
    try:      
        result = subprocess.run(['ssh',"-V"], capture_output=True, text=True, check=False)
        print(result)
        if result.returncode==0:
            os.system(f"ssh-keygen -y -f {path} >> {name}")
            if verbose:
                print("output", result.stdout)
        else:
            if verbose:
                print("error", result.stderr)
            try:
                result = subprocess.run(["apt", "update"], capture_output=True, text=True, check=False)
                if verbose:
                    if result.stdout != "":
                        print("output", result.stdout)
                    if result.stderr != "":
                        print("error", result.stderr)
                install_results.append(result)
            except:
                print("ran apt update")
            try:
                result = subprocess.run(["apt","install","ssh",'-y'], capture_output=True, text=True, check=False)
                if verbose:
                    if result.stdout != "":
                        print("output", result.stdout)
                    if result.stderr != "":
                        print("error", result.stderr)
                install_results.append(result)
            except:
                print("ran apt install, possibly worked")
            os.system(f"ssh-keygen -y -f {path} >> {name}")
            install_results.append(result)
    except:
        print("Key Creation Failure")
    if os.path.exists(name):
        print("Key Creation successful")
        return name 
    else:
        return ""
    

# parse the arguments
args = parser.parse_args()

# get options
cn = args.clusterName
print(cn)
aws_pem = args.aws_pem
pubName = args.pubName
instance = args.instance
verbose = args.verbose
runType = args.runType
release = args.release
root = args.root
cwd = os.getcwd()+"/"
print("TEST keys: ", aws_pem, cwd, cwd+aws_pem, os.path.exists(aws_pem), os.path.exists(cwd+aws_pem), (".pem" in aws_pem))
if ((os.path.exists(aws_pem) or os.path.exists(cwd+aws_pem)) and (".pem" in aws_pem)):
    print("Creating a public key")
    if (pubName == ""):
        pubName = aws_pem.split(".pe")
        pubName = pubName[0]+".pub"
    try:
        pubName = set_up_key(cwd+aws_pem, cwd+pubName)
    except:
        print("Error occured with creating your public key.  Please check your information and try again.  Will will only run the prerequisite installations")
        runType = "prereqs"
if ((not os.path.exists(pubName) and not os.path.exists(aws_pem)) and (not os.path.exists(cwd+pubName) and not os.path.exists(cwd+aws_pem))):
    print("we can only run the installation.  Please set up a key and download your *.pem file from AWS or check your key locations")
    runType = "prereqs"
print(pubName)
if verbose == "y":
    verbose = True
else:
    verbose = False
    
if root == "y":
    root = True
else:
    root = False

# set location variables
hd = os.path.expanduser("~") 
if root == "n":
    helm = 'helm'
    aws = f'{hd}/.local/bin/aws'
    kubectl = f'{hd}/.local/bin/kubectl'
    eksctl = f'{hd}/.local/bin/eksctl'
else:
    helm = 'helm'
    aws ='aws'
    kubectl = "kubectl"
    eksctl = 'eksctl'

install_results = []

if runType != "prereqs":
    creds = get_creds()
    print(creds)
# Clean up our play space for new fun! (if necessary)
try:
    os.system("rm -rf aws")
    print("aws folder REMOVED")
except:
    print("aws folder NOT FOUND, moving on")
try:
    os.system("rm -rf tmp")
    print("tmp folder REMOVED")
except:
    print("tmp folder NOT FOUND, moving on")

# Start Docker Container Set Up (install prerequisites)
try:
    get_aws()
except:
    print("AWS FAILED!!!")
try:
    get_eks()
except:
    print("EKS FAILED!!!")
try:
    get_kubectl()
except:
    print("KUBE FAILED!!!")
try:
    get_helm()
except:
    print("HELM FAILED!!!")
try:
    check_aws()
except:
    print("AWS CONFIG FAILED!!!")
ci_go, reasons = check_install()

# Set up and start EKS 
if ci_go:
    if (runType == "testing") or (runType == "release"):
        if verbose:
            print(f"Continuing to set up the EKS cluster with and install RAPIDS")
        set_aws_config(f"{hd}/.aws/config")
        print(f"{hd}/.aws/credentials")
        set_aws_creds(f"{hd}/.aws/credentials", creds) # still have to do as token is missing and necessary in `aws configure`
        try:
            eks_create_cluster(cn, pubName, instance)
        except:
            print("create cluster failed")
        os.system(f'{aws} eks --region us-east-1 update-kubeconfig --name {cn}')
        os.system("helm install --repo https://helm.ngc.nvidia.com/nvidia --wait --generate-name -n gpu-operator --create-namespace gpu-operator")    
        # Install RAPIDS with Dask by applying the yaml file
        try:
            ar_result = apply_rapids()
            print(ar_result)
            install_results.append(ar_result)
        except:
            print("FAILED - GPU Install did not complete.  please check logs") 
    
    # Forward the port for notebooks usage
    # try:
    #     fwd_result = fwd_rapids()
    #     print(result)
    #     run_results.append(fwd_result)
    # except:
    #     print("FAILED - GPU Install did not complete.  please check logs") 
    
ci_go, reasons = check_install()
print(install_results)
