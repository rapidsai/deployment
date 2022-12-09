# Sagemaker

RAPIDS also works with AWS SageMaker. We’ve written a **[detailed
blog post](https://medium.com/rapids-ai/running-rapids-experiments-at-scale-using-amazon-sagemaker-d516420f165b)**
with **[examples](https://github.com/rapidsai/cloud-ml-examples/tree/main/aws)**
for how to use Sagemaker with RAPIDS to run HPO experiments at scale.

To get started:

0. Upload train/test data to S3 

   - We offer the dataset for this demo in a public bucket hosted in either the `us-east-1` or `us-west-2` regions:
   > https://s3.console.aws.amazon.com/s3/buckets/sagemaker-rapids-hpo-us-east-1/   
   > https://s3.console.aws.amazon.com/s3/buckets/sagemaker-rapids-hpo-us-west-2/
   
   
1. Create a SageMaker Notebook Instance

   - Sign in to the Amazon SageMaker console at 
   > https://console.aws.amazon.com/sagemaker/
   
   - Choose **Notebook Instances**, then choose 'Create notebook instance'.


2. On the Create notebook instance page, provide the following information (if a field is not mentioned, leave the default values):
   - For **Notebook instance name**, type a name for your notebook instance.
   - For **Instance type**, we recommend you choose a lightweight instance (e.g., ml.t2.medium) since the notebook instance will only be used to build the container and launch work.
   - For **IAM role**, choose Create a new role, then choose Create role.
   - For **Git repositories**, choose 'Clone a public Git repository to this notebook instance only' and add the cloud-ml-examples repository to the URL
   > https://github.com/rapidsai/cloud-ml-examples 
   - Choose 'Create notebook instance'. 
   
   - In a few minutes, Amazon SageMaker launches an ML compute instance — when its ready you should see several links appear in the Actions tab of the **Notebook Instances** section, click on **Open JupyerLab** to launch into the notebook.   
   > Note: If you see Pending to the right of the notebook instance in the Status column, your notebook is still being created. The status will change to InService when the notebook is ready for use.


3. Run Notebook
   - Once inside JupyterLab you should be able to navigate to the notebook in the root directory named **aws/rapids_sagemaker_hpo.ipynb** or 
   **aws/rapids_sagemaker_higgs**. 
