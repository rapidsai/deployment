"""Training tasks — config generation and container lifecycle."""

import json
import logging
import os
import subprocess

from prefect import task

from pipeline.config import TRAINING_IMAGE

logger = logging.getLogger(__name__)


@task(name="generate-training-config")
def generate_training_config(
    data_dir: str,
    output_dir: str,
    gnn_params: dict,
    xgb_params: dict,
    config_dir: str = ".",
) -> str:
    """Build training JSON config and write to disk.

    The training container expects:
    - paths.data_dir = /data (container mount point)
    - paths.output_dir = /trained_models (container mount point)
    """
    config = {
        "paths": {
            "data_dir": "/data",
            "output_dir": "/trained_models",
        },
        "models": [
            {
                "kind": "GNN_XGBoost",
                "gpu": "single",
                "hyperparameters": {
                    "gnn": gnn_params,
                    "xgb": xgb_params,
                },
            }
        ],
    }

    config_path = os.path.join(config_dir, "training_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    logger.info("Training config written to %s", config_path)
    return config_path


@task(name="run-training-container")
def run_training_container(
    data_dir: str,
    output_dir: str,
    config_path: str,
    training_image: str = TRAINING_IMAGE,
    gpu_device: str = "0",
) -> None:
    """Run the financial-fraud-training container.

    Includes NCCL workarounds for cloud instances without InfiniBand:
    forces socket-based communication, bypassing UCX and OFI plugins.
    """
    cmd = [
        "docker", "run",
        "--rm",
        "--gpus", f"device={gpu_device}",
        "--cap-add", "SYS_NICE",
        "--shm-size=8g",
        "--privileged",
        "-e", "NCCL_IB_DISABLE=1",
        "-e", "NCCL_NET=Socket",
        "-e", "NCCL_SOCKET_IFNAME=eth0",
        "-e", "NCCL_P2P_DISABLE=1",
        "-e", "NCCL_SHM_DISABLE=1",
        "-v", f"{data_dir}:/data",
        "-v", f"{output_dir}:/trained_models",
        "-v", f"{config_path}:/app/config.json",
        "--entrypoint", "bash",
        training_image,
        "-c", "torchrun --standalone --nproc_per_node=1 /app/main.py --config /app/config.json",
    ]
    logger.info("Running training container: %s", " ".join(cmd))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Training container failed:\nstdout: %s\nstderr: %s", result.stdout, result.stderr)
        raise RuntimeError(f"Training container exited with code {result.returncode}: {result.stderr}")

    logger.info("Training container completed successfully")
