"""Training flow — config generation, container execution, MLflow logging."""

import logging
import tempfile

from prefect import flow

from pipeline.config import (
    DEFAULT_GNN_PARAMS,
    DEFAULT_XGB_PARAMS,
    GNN_DATA_DIR,
    MLFLOW_EXPERIMENT_NAME,
    MODEL_OUTPUT_DIR,
    TRAINING_IMAGE,
)
from pipeline.tasks.mlflow_utils import get_or_create_experiment, log_training_run
from pipeline.tasks.training import generate_training_config, run_training_container

logger = logging.getLogger(__name__)


@flow(name="train", log_prints=True)
def train_flow(
    data_dir: str = GNN_DATA_DIR,
    output_dir: str = MODEL_OUTPUT_DIR,
    gnn_params: dict | None = None,
    xgb_params: dict | None = None,
    experiment_name: str = MLFLOW_EXPERIMENT_NAME,
    run_tags: dict | None = None,
    training_image: str = TRAINING_IMAGE,
    gpu_device: str = "0",
) -> str:
    """Train the GNN + XGBoost fraud detection model.

    Steps:
    1. Generate training config JSON from parameters
    2. Run the financial-fraud-training container
    3. Validate model outputs were produced
    4. Log everything to MLflow

    Returns the MLflow run ID.
    """
    gnn_params = gnn_params or DEFAULT_GNN_PARAMS
    xgb_params = xgb_params or DEFAULT_XGB_PARAMS

    # Step 1: Generate config
    with tempfile.TemporaryDirectory() as config_dir:
        config_path = generate_training_config(
            data_dir=data_dir,
            output_dir=output_dir,
            gnn_params=gnn_params,
            xgb_params=xgb_params,
            config_dir=config_dir,
        )

        # Step 2: Run training container
        run_training_container(
            data_dir=data_dir,
            output_dir=output_dir,
            config_path=config_path,
            training_image=training_image,
            gpu_device=gpu_device,
        )

        # Step 3: Log to MLflow
        experiment_id = get_or_create_experiment(experiment_name)
        run_id = log_training_run(
            experiment_id=experiment_id,
            gnn_params=gnn_params,
            xgb_params=xgb_params,
            config_path=config_path,
            model_output_dir=output_dir,
            tags=run_tags,
        )

    logger.info("Training complete — MLflow run ID: %s", run_id)
    return run_id


if __name__ == "__main__":
    train_flow()
