"""Preprocessing flow — runs cuDF-based graph formation and logs metadata to MLflow."""

import logging
import os
import sys

import mlflow
from prefect import flow

from pipeline.config import (
    DATA_ROOT,
    DEFAULT_FRAUD_RATIO,
    DEFAULT_UNDER_SAMPLE,
    MLFLOW_PREPROCESS_EXPERIMENT_NAME,
    RAW_CSV_PATH,
)
from pipeline.tasks.mlflow_utils import get_or_create_experiment

logger = logging.getLogger(__name__)


@flow(name="preprocess", log_prints=True)
def preprocess_flow(
    raw_csv_path: str = RAW_CSV_PATH,
    output_base_path: str = DATA_ROOT,
    fraud_ratio: float = DEFAULT_FRAUD_RATIO,
    under_sample: bool = DEFAULT_UNDER_SAMPLE,
) -> dict:
    """Preprocess raw TabFormer CSV into graph data for training.

    Steps:
    1. Run cuDF-based preprocessing (adapted from blueprint)
    2. Log metadata to MLflow
    """
    # Step 1: Run preprocessing (import here because it requires cuDF/GPU)
    scripts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "scripts")
    sys.path.insert(0, os.path.abspath(scripts_dir))
    from preprocess_tabformer import preprocess_data

    metadata, user_mask_map, mx_mask_map, tx_mask_map = preprocess_data(
        raw_csv_path=raw_csv_path,
        output_base_path=output_base_path,
        fraud_ratio=fraud_ratio,
        under_sample=under_sample,
    )

    logger.info(
        "Preprocessing complete: %d transactions, %d users, %d merchants",
        metadata["num_transactions"],
        metadata["num_users"],
        metadata["num_merchants"],
    )

    # Step 2: Log to MLflow
    experiment_id = get_or_create_experiment(MLFLOW_PREPROCESS_EXPERIMENT_NAME)
    with mlflow.start_run(experiment_id=experiment_id, run_name="preprocess"):
        mlflow.log_params(
            {
                "preprocess.fraud_ratio": fraud_ratio,
                "preprocess.under_sample": under_sample,
            }
        )
        mlflow.log_metrics(
            {
                "preprocess.row_count": float(metadata["row_count"]),
                "preprocess.num_users": float(metadata["num_users"]),
                "preprocess.num_merchants": float(metadata["num_merchants"]),
                "preprocess.num_transactions": float(metadata["num_transactions"]),
            }
        )
        mlflow.set_tag("stage", "preprocess")

    gnn_dir = os.path.join(output_base_path, "gnn")
    return {
        "output_base_path": output_base_path,
        "gnn_dir": gnn_dir,
        "metadata": metadata,
        "masks": {
            "user": user_mask_map,
            "merchant": mx_mask_map,
            "transaction": tx_mask_map,
        },
    }


if __name__ == "__main__":
    preprocess_flow()
