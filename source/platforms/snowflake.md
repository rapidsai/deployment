# Snowflake

You can install RAPIDS on Snowflake via [Snowpark Container Services](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview).

Note: The following instructions are and adaptation of the [Introduction to Snowpark
container Services](https://quickstarts.snowflake.com/guide/intro_to_snowpark_container_services/#0) from the Snowflake documentation.

## Snowflake Requirements

- A non-trial Snowflake account in a supported [AWS region](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview#available-regions).
- A Snowflake account login with a role that has the `ACCOUNTADMIN` role. If not,
  you will need to work with your `ACCOUNTADMIN` to perform the initial account setup.
- Access to `INSTANCE_FAMILY` with NVIDIA GPUs. For this guide we will use `GPU_NV_S`
  (1 NVIDIA A10G - smallest NVIDIA GPU size available for Snowpark Containers to
  get started.)

## Set up the Snowflake environment

In a SQL worksheet in Snowflake, run the following commands to create the role,
database, warehouse, and stage that we need to get started:

```sql
-- Create an CONTAINER_USER_ROLE with required privileges
USE ROLE ACCOUNTADMIN;
CREATE ROLE CONTAINER_USER_ROLE;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE CONTAINER_USER_ROLE;
GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE CONTAINER_USER_ROLE;
GRANT CREATE COMPUTE POOL ON ACCOUNT TO ROLE CONTAINER_USER_ROLE;
GRANT CREATE INTEGRATION ON ACCOUNT TO ROLE CONTAINER_USER_ROLE;
GRANT MONITOR USAGE ON ACCOUNT TO  ROLE  CONTAINER_USER_ROLE;
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE CONTAINER_USER_ROLE;
GRANT IMPORTED PRIVILEGES ON DATABASE snowflake TO ROLE CONTAINER_USER_ROLE;

-- Grant CONTAINER_USER_ROLE to ACCOUNTADMIN
grant role CONTAINER_USER_ROLE to role ACCOUNTADMIN;

-- Create Database, Warehouse, and Image spec stage
USE ROLE CONTAINER_USER_ROLE;
CREATE OR REPLACE DATABASE CONTAINER_HOL_DB;

CREATE OR REPLACE WAREHOUSE CONTAINER_HOL_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 120
  AUTO_RESUME = TRUE;

CREATE STAGE IF NOT EXISTS specs
ENCRYPTION = (TYPE='SNOWFLAKE_SSE');

CREATE STAGE IF NOT EXISTS volumes
ENCRYPTION = (TYPE='SNOWFLAKE_SSE')
DIRECTORY = (ENABLE = TRUE);
```

Then we proceed to create the external access integration, the compute pool (with
GPU resources), and the image repository:

```sql
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE NETWORK RULE ALLOW_ALL_RULE
  TYPE = 'HOST_PORT'
  MODE = 'EGRESS'
  VALUE_LIST= ('0.0.0.0:443', '0.0.0.0:80');

CREATE EXTERNAL ACCESS INTEGRATION ALLOW_ALL_EAI
  ALLOWED_NETWORK_RULES = (ALLOW_ALL_RULE)
  ENABLED = true;

GRANT USAGE ON INTEGRATION ALLOW_ALL_EAI TO ROLE CONTAINER_USER_ROLE;

USE ROLE CONTAINER_USER_ROLE;
CREATE COMPUTE POOL IF NOT EXISTS CONTAINER_HOL_POOL
MIN_NODES = 1
MAX_NODES = 1
INSTANCE_FAMILY = GPU_NV_S; -- instance with GPU

CREATE IMAGE REPOSITORY CONTAINER_HOL_DB.PUBLIC.IMAGE_REPO;

SHOW IMAGE REPOSITORIES IN SCHEMA CONTAINER_HOL_DB.PUBLIC;
```

## Docker image push via SnowCLI

The nest step in the process is to push to the image registry the docker image
you will want to run via the service.

### Build Docker image locally

For this guide, we build an image that starts from the RAPIDS notebook image and
adds some extra snowflake packages.

Create a Dockerfile as follow:

```Dockerfile
FROM rapidsai/notebooks:25.02a-cuda11.8-py3.11-amd64

RUN pip install "snowflake-snowpark-python[pandas]" snowflake-connector-python
```

Notes:

- The `python=3.11`, is the latest supported by the snowflake connector package.
- The `amd64` platform is required for Snowflake.

In the directory where your Dockerfile is located build the image. Notice that
no GPU is needed to build this image.

```bash
docker build --platform=linux/amd64 -t <local_repository>/rapids-nb-snowflake:latest .
```

### Create local environment with SnowCLI

Create a conda/mamba environment with SnowCLI.

```yaml
name: snow-cli
channels:
  - condaforge
dependencies:
  - python=3.11
  - pip
  - pip:
      - snowflake-cli
```

Activate the environment `mamba activate snow-cli` and configure your Snowflake
CLI connection

```bash
snow connection add
```

Follow the wizard.

Note: if you don't recall `<ORG>-<ACCOUNT-NAME>` you can obtain them
by running the following in the Snowflake SQL worksheet.

```sql
SELECT CURRENT_ORGANIZATION_NAME(); --org
SELECT CURRENT_ACCOUNT_NAME();      --account name
```

```bash
connection name : CONTAINER_HOL
account : <ORG>-<ACCOUNT-NAME> # e.g. MYORGANIZATION-MYACCOUNT
user : <snowflake_user_name>
password : <snowflake_password>
role: CONTAINER_USER_ROLE
warehouse : CONTAINER_HOL_WH
database : CONTAINER_HOL_DB
schema : public
host:
port:
region:
authenticator:
private key file:
token file path:
```

Test the connection:

```bash
snow connection test --connection "CONTAINER_HOL"
```

To be able to push the docker image we need to get the snowflake registry hostname
from the repository url. In a Snowflake SQL worksheet run:

```sql
USE ROLE CONTAINER_USER_ROLE;
SHOW IMAGE REPOSITORIES IN SCHEMA CONTAINER_HOL_DB.PUBLIC;
```

You will see that the repository url is `org-account.registry.snowflakecomputing.com/container_hol_db/public/image_repo` where `org-account` refers to your organization and account, the `SNOWFLAKE_REGISTRY_HOSTNAME` is the url up to the `.com`. i.e. `org-account.registry.snowflakecomputing.com`

First we login into the snowflake repository with docker, via terminal:

```bash
docker login <snowflake_registry_hostname> -u <snowflake_user_name>
> prompt for password
```

We tag and push the image, make sure you replace the repository url for `org-account.registry.snowflakecomputing.com/container_hol_db/public/image_repo`:

```bash
docker tag <local_repository>/rapids-nb-snowflake:latest <repository_url>/rapids-nb-snowflake:dev
```

Verify that the new tagged image exists by running:

```bash
docker image list
```

Push the image to snowflake:

```bash
docker push <repository_url>/rapids-nb-snowflake:dev
```

Note: This step will take sometime, while this process completes we can continue
with next step to configure and push the Spec YAML.

When the `docker push` command completes, you can verify that the image exists in your Snowflake Image Repository by running the following in the Snowflake SQL worksheet

```sql
USE ROLE CONTAINER_USER_ROLE;
CALL SYSTEM$REGISTRY_LIST_IMAGES('/CONTAINER_HOL_DB/PUBLIC/IMAGE_REPO');
```

## Configure and Push Spec YAML

Snowpark Container Services are defined and configured using YAML files. There
is support for multiple parameters configurations, refer to then [Snowpark container services specification reference](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/specification-reference) for more information.

Locally, create the following file `rapids-snowpark.yaml`

```yaml
spec:
  containers:
    - name: rapids-nb-snowpark
      image: <org-account>.registry.snowflakecomputing.com/container_hol_db/public/image_repo/rapids-nb-snowflake:dev
      volumeMounts:
        - name: rapids-notebooks
          mountPath: home/rapids/workspace
      resources:
        requests:
          nvidia.com/gpu: 1
        limits:
          nvidia.com/gpu: 1
  endpoints:
    - name: jupyter
      port: 8888
      public: true
    - name: dask-client
      port: 8786
      protocol: TCP
      public: true
    - name: dask-dashboard
      port: 8787
      public: true
  volumes:
    - name: rapids-notebooks
      source: "@volumes/rapids-notebooks"
      uid: 1000
      gid: 1000
```

Notice that in we mounted the `@volumes/rapids-notebooks` internal stage location to our `/home/rapids/workspace` directory inside of our running container. If you create the `workspace` directory when the container is up, what you save there will persist.

We use `snow-cli` to push this `yaml` file:

```bash
snow stage copy rapids-snowpark.yaml @specs --overwrite --connection CONTAINER_HOL
```

Verify that your `yaml` was pushed properly by running the following SQL in the
Snowflake worksheet:

```sql
USE ROLE CONTAINER_USER_ROLE;
LS @CONTAINER_HOL_DB.PUBLIC.SPECS;
```

## Create and Test the Service

Now that we have successfully pushed the image and the spec YAML, we have all
the components in Snowflake to create our service. We only need a service name,
a compute pool and the spec file. Run this SQL in the Snowflake worksheet:

```sql
USE ROLE CONTAINER_USER_ROLE;
CREATE SERVICE CONTAINER_HOL_DB.PUBLIC.rapids_snowpark_service
    in compute pool CONTAINER_HOL_POOL
    from @specs
    specification_file='rapids-snowpark.yaml'
    external_access_integrations = (ALLOW_ALL_EAI);
```

Run the following to verify that the service is successfully running.

```sql
CALL SYSTEM$GET_SERVICE_STATUS('CONTAINER_HOL_DB.PUBLIC.rapids_snowpark_service');
```

Since we specified the `jupyter` endpoint to be public, Snowflake will generate
a url that can be used to access the service via the browser. To get the url,
run in the SQL snowflake worksheet:

```sql
SHOW ENDPOINTS IN SERVICE RAPIDS_SNOWPARK_SERVICE;
```

and copy the url in the browser. You will see a jupyter lab with a set of
notebooks to get started with RAPIDS.

## TODO

- use proper format for notes.
- add screenshot of what you'll see.
- Add note on volume mount and how to use.
- How to close and cleanup.
