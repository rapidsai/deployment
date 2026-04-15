"""MLflow utility tasks — experiment management, metrics, model registry."""

import logging

import mlflow
from mlflow import MlflowClient
from prefect import task

from pipeline.config import (
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI,
    TRITON_MODEL_NAME,
)

logger = logging.getLogger(__name__)

# Configure once — all functions in this module use the same tracking server
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


@task(name="get-or-create-experiment")
def get_or_create_experiment(experiment_name: str = MLFLOW_EXPERIMENT_NAME) -> str:
    """Get existing MLflow experiment or create a new one. Returns experiment ID."""
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is not None:
        return experiment.experiment_id
    experiment_id = mlflow.create_experiment(experiment_name)
    logger.info("Created MLflow experiment '%s' (id=%s)", experiment_name, experiment_id)
    return experiment_id


@task(name="log-training-run")
def log_training_run(
    experiment_id: str,
    gnn_params: dict,
    xgb_params: dict,
    config_path: str,
    model_output_dir: str,
    tags: dict | None = None,
) -> str:
    """Create an MLflow run logging hyperparams, config artifact, and model artifacts.

    Returns the MLflow run ID.
    """
    with mlflow.start_run(experiment_id=experiment_id) as run:
        # Log hyperparameters (flatten with prefix)
        for k, v in gnn_params.items():
            mlflow.log_param(f"gnn.{k}", v)
        for k, v in xgb_params.items():
            mlflow.log_param(f"xgb.{k}", v)

        # Log config as artifact
        mlflow.log_artifact(config_path)

        # Log model artifacts directory
        mlflow.log_artifacts(model_output_dir, artifact_path="model")

        # Tags
        run_tags = {"trigger": "automated"}
        if tags:
            run_tags.update(tags)
        mlflow.set_tags(run_tags)

        logger.info("Logged training run %s", run.info.run_id)
        return run.info.run_id


@task(name="log-evaluation-metrics")
def log_evaluation_metrics(
    run_id: str,
    challenger_metrics: dict,
    champion_metrics: dict | None,
) -> None:
    """Log evaluation metrics to an existing MLflow run."""
    with mlflow.start_run(run_id=run_id):
        # Log challenger metrics
        mlflow.log_metrics({f"challenger_{k}": v for k, v in challenger_metrics.items()})

        # Log champion metrics and delta if champion exists
        if champion_metrics:
            mlflow.log_metrics({f"champion_{k}": v for k, v in champion_metrics.items()})
            deltas = {
                f"{k}_delta": challenger_metrics.get(k, 0) - champion_metrics.get(k, 0)
                for k in challenger_metrics
            }
            mlflow.log_metrics(deltas)


@task(name="get-champion-metrics")
def get_champion_metrics(model_name: str = TRITON_MODEL_NAME) -> dict | None:
    """Retrieve metrics for the current champion model from MLflow registry.

    Returns None if no champion exists (first deployment).
    """
    client = MlflowClient(MLFLOW_TRACKING_URI)

    versions = client.search_model_versions(f"name='{model_name}'")
    champion_version = None
    for v in versions:
        if "champion" in (v.aliases or []):
            champion_version = v
            break

    if champion_version is None:
        logger.info("No champion model found — this is the first deployment")
        return None

    run = client.get_run(champion_version.run_id)
    metrics = dict(run.data.metrics)
    logger.info("Champion metrics (run %s): %s", champion_version.run_id, metrics)
    return metrics


@task(name="register-champion")
def register_champion(run_id: str, model_name: str = TRITON_MODEL_NAME) -> None:
    """Register a model version and assign the 'champion' alias."""
    client = MlflowClient(MLFLOW_TRACKING_URI)

    # Register model version
    model_uri = f"runs:/{run_id}/model"
    mv = mlflow.register_model(model_uri, model_name)

    # Move champion alias to this version
    client.set_registered_model_alias(model_name, "champion", mv.version)
    logger.info("Registered %s version %s as champion (run %s)", model_name, mv.version, run_id)


@task(name="log-promotion-decision")
def log_promotion_decision(run_id: str, should_promote: bool, reason: str = "") -> None:
    """Log the promotion decision to the MLflow run."""
    with mlflow.start_run(run_id=run_id):
        mlflow.set_tag("promotion_decision", "promoted" if should_promote else "rejected")
        if reason:
            mlflow.set_tag("promotion_reason", reason)
