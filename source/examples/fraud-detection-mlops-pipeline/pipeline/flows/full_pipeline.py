"""Full pipeline orchestrator — chains preprocess → train → evaluate → deploy."""

import logging
import os

from prefect import flow

from pipeline.config import (
    DATA_ROOT,
    DEFAULT_FRAUD_RATIO,
    DEFAULT_GNN_PARAMS,
    DEFAULT_UNDER_SAMPLE,
    DEFAULT_XGB_PARAMS,
    MIN_IMPROVEMENT,
    MODEL_OUTPUT_DIR,
    RAW_CSV_PATH,
    TRITON_HTTP_URL,
    TRITON_MODEL_REPO,
)
from pipeline.flows.deploy import deploy_flow
from pipeline.flows.evaluate import evaluate_flow
from pipeline.flows.preprocess import preprocess_flow
from pipeline.flows.train import train_flow

logger = logging.getLogger(__name__)


@flow(name="full-pipeline", log_prints=True)
def full_pipeline_flow(
    raw_csv_path: str = RAW_CSV_PATH,
    data_output_path: str = DATA_ROOT,
    model_output_dir: str = MODEL_OUTPUT_DIR,
    triton_url: str = TRITON_HTTP_URL,
    model_repo_path: str = TRITON_MODEL_REPO,
    fraud_ratio: float = DEFAULT_FRAUD_RATIO,
    under_sample: bool = DEFAULT_UNDER_SAMPLE,
    gnn_params: dict | None = None,
    xgb_params: dict | None = None,
    min_improvement: float = MIN_IMPROVEMENT,
    skip_preprocess: bool = False,
) -> dict:
    """End-to-end fraud detection pipeline.

    Chains all four stages as subflows. Each stage runs as a child flow
    within the same process, with results passed directly between stages.

    Set skip_preprocess=True if graph data already exists from a previous run.
    """
    gnn_params = gnn_params or DEFAULT_GNN_PARAMS
    xgb_params = xgb_params or DEFAULT_XGB_PARAMS

    logger.info("Starting full pipeline")

    # Stage 1: Preprocess
    if not skip_preprocess:
        preprocess_result = preprocess_flow(
            raw_csv_path=raw_csv_path,
            output_base_path=data_output_path,
            fraud_ratio=fraud_ratio,
            under_sample=under_sample,
        )
        logger.info(
            "Preprocessing complete: %d transactions",
            preprocess_result["metadata"]["num_transactions"],
        )

    # Stage 2: Train
    gnn_data_dir = os.path.join(data_output_path, "gnn")
    run_id = train_flow(
        data_dir=gnn_data_dir,
        output_dir=model_output_dir,
        gnn_params=gnn_params,
        xgb_params=xgb_params,
    )
    logger.info("Training complete — run_id: %s", run_id)

    # Stage 3: Evaluate
    test_data_dir = os.path.join(data_output_path, "gnn", "test_gnn")
    eval_result = evaluate_flow(
        challenger_run_id=run_id,
        challenger_artifacts_path=model_output_dir,
        test_data_dir=test_data_dir,
        triton_url=triton_url,
        model_repo_path=model_repo_path,
        min_improvement=min_improvement,
    )
    logger.info(
        "Evaluation: %s — %s",
        "PROMOTE" if eval_result["should_promote"] else "REJECT",
        eval_result["reason"],
    )

    # Stage 4: Deploy
    deploy_result = deploy_flow(
        eval_result=eval_result,
        triton_url=triton_url,
        model_repo_path=model_repo_path,
    )
    logger.info("Deploy: %s", deploy_result["action"])

    return {
        "status": "complete",
        "train_run_id": run_id,
        "eval_result": eval_result,
        "deploy_result": deploy_result,
    }


if __name__ == "__main__":
    full_pipeline_flow()
