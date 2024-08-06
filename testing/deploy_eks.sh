#!/bin/bash

# turn on bash's job control
set -m

# Start the primary process and wait for it to complete
python eks_deploy.py --runType=testing --verbose=y --aws_pem=test.pem --clusterName=cluster 2>&1 | tee test-deploy9.txt # Sample

# Start the port forwarding process and put it to background, as it won't kill until it is dead
kubectl port-forward service/rapids-notebook 9888 --address 0.0.0.0

# Try TMUX for job control?

# the my_helper_process might need to know how to wait on the
# primary process to start before it does its work and returns


# now we bring the primary process back into the foreground
# and leave it there
fg %1