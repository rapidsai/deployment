#!/bin/bash

# turn on bash's job control
set -m

# Start the primary process and put it in the background
jupyter-lab --notebook-dir=/home/rapids/notebooks --ip=0.0.0.0 --no-browser --NotebookApp.token='' --NotebookApp.allow_origin='*' --allow-root &

# Start the deployment testing script helper process
python /home/rapids/notebooks/extra/deployment/testing/deploy_eks.sh

# the my_helper_process might need to know how to wait on the
# primary process to start before it does its work and returns


# now we bring the primary process back into the foreground
# and leave it there
fg %1