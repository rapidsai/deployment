"""Evaluate flow — champion/challenger comparison via Triton native versioning."""

import logging
import os

import numpy as np
from prefect import flow

from pipeline.config import (
    DECISION_THRESHOLD,
    MIN_IMPROVEMENT,
    MODEL_OUTPUT_DIR,
    PROMOTION_METRIC,
    TEST_DATA_DIR,
    TRITON_HTTP_URL,
    TRITON_MODEL_NAME,
    TRITON_MODEL_REPO,
)
from pipeline.tasks.data import load_test_data
from pipeline.tasks.mlflow_utils import (
    get_champion_metrics,
    log_evaluation_metrics,
    log_promotion_decision,
)
from pipeline.tasks.triton import (
    health_check,
    reload_model,
    score_model_version,
    stage_challenger_version,
)

logger = logging.getLogger(__name__)


@flow(name="evaluate", log_prints=True)
def evaluate_flow(
    challenger_run_id: str,
    challenger_artifacts_path: str = MODEL_OUTPUT_DIR,
    test_data_dir: str = TEST_DATA_DIR,
    triton_url: str = TRITON_HTTP_URL,
    model_name: str = TRITON_MODEL_NAME,
    model_repo_path: str = TRITON_MODEL_REPO,
    promotion_metric: str = PROMOTION_METRIC,
    min_improvement: float = MIN_IMPROVEMENT,
    decision_threshold: float = DECISION_THRESHOLD,
) -> dict:
    """Compare a newly trained model against the current champion via Triton.

    Stages the challenger as the next version in Triton's model repository,
    scores both versions on held-out test data, and decides whether the
    challenger should be promoted based on the configured metric and threshold.
    Results are logged to the same MLflow run that was created during training.
    """
    # Step 1: Stage challenger as next version
    source_artifacts = os.path.join(
        challenger_artifacts_path,
        "python_backend_model_repository",
        model_name,
        "1",
    )
    champion_version, challenger_version = stage_challenger_version(
        source_artifacts, model_repo_path, model_name,
    )

    # Step 2: Reload model to pick up new version
    reload_model(triton_url, model_name)

    # Step 3: Load test data
    test_data = load_test_data(test_data_dir)
    labels = test_data["edge_label_user_to_merchant"]
    if hasattr(labels, "to_numpy"):
        labels = labels.to_numpy(dtype=np.int32)
    if hasattr(labels, "values"):
        labels = labels.values
    labels = np.asarray(labels, dtype=np.int32).ravel()

    # Remove labels from inference data
    inference_data = {k: v for k, v in test_data.items() if not k.startswith("edge_label_")}

    # Step 4: Score challenger
    challenger_metrics = score_model_version(
        triton_url, model_name, challenger_version,
        inference_data, labels, decision_threshold,
    )

    # Step 5: Score champion (if exists)
    champion_metrics = None
    if champion_version > 0:
        if health_check(triton_url, model_name, champion_version):
            champion_metrics = score_model_version(
                triton_url, model_name, champion_version,
                inference_data, labels, decision_threshold,
            )
        else:
            champion_metrics = get_champion_metrics(model_name)

    # Step 6: Decide promotion
    if champion_metrics is None:
        should_promote = True
        reason = "First model deployment — auto-promoted"
    else:
        challenger_val = challenger_metrics.get(promotion_metric, 0)
        champion_val = champion_metrics.get(promotion_metric, 0)
        should_promote = challenger_val > champion_val + min_improvement
        reason = (
            f"Challenger {promotion_metric}={challenger_val:.4f} vs "
            f"champion {promotion_metric}={champion_val:.4f} "
            f"(delta={challenger_val - champion_val:.4f}, min={min_improvement})"
        )

    logger.info("Promotion decision: %s — %s", "PROMOTE" if should_promote else "REJECT", reason)

    # Step 7: Log to MLflow
    log_evaluation_metrics(challenger_run_id, challenger_metrics, champion_metrics)
    log_promotion_decision(challenger_run_id, should_promote, reason)

    return {
        "should_promote": should_promote,
        "champion_version": champion_version,
        "challenger_version": challenger_version,
        "challenger_run_id": challenger_run_id,
        "challenger_metrics": challenger_metrics,
        "champion_metrics": champion_metrics,
        "reason": reason,
    }


if __name__ == "__main__":
    import sys
    evaluate_flow(challenger_run_id=sys.argv[1] if len(sys.argv) > 1 else "manual")
