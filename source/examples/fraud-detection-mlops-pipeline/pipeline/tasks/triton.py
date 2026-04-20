"""Triton Inference Server tasks — version management, model control API, health checks."""

import logging
import os
import shutil
import time

import numpy as np
import tritonclient.http as httpclient
from prefect import task

from pipeline.config import TRITON_MODEL_NAME

logger = logging.getLogger(__name__)


@task(name="get-current-version")
def get_current_version(
    model_repo_path: str, model_name: str = TRITON_MODEL_NAME
) -> int:
    """Get the highest version number in the Triton model repository.

    Returns 0 if the model directory doesn't exist.
    """
    model_dir = os.path.join(model_repo_path, model_name)
    if not os.path.isdir(model_dir):
        return 0

    versions = []
    for entry in os.listdir(model_dir):
        entry_path = os.path.join(model_dir, entry)
        if os.path.isdir(entry_path) and entry.isdigit():
            versions.append(int(entry))

    return max(versions) if versions else 0


@task(name="stage-challenger-version")
def stage_challenger_version(
    challenger_artifacts_path: str,
    model_repo_path: str,
    model_name: str = TRITON_MODEL_NAME,
) -> tuple[int, int]:
    """Copy challenger model artifacts as the next version in the Triton model repo.

    Args:
        challenger_artifacts_path: Path to the version directory with model files
            (e.g., .../python_backend_model_repository/prediction_and_shapley/1/)
        model_repo_path: Root of the Triton model repository
        model_name: Triton model name

    Returns:
        (champion_version, challenger_version) tuple
    """
    champion_version = get_current_version.fn(model_repo_path, model_name)
    challenger_version = champion_version + 1

    target_dir = os.path.join(model_repo_path, model_name, str(challenger_version))
    shutil.copytree(challenger_artifacts_path, target_dir)

    # Ensure config.pbtxt has version_policy { all {} } so both versions are served
    config_path = os.path.join(model_repo_path, model_name, "config.pbtxt")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config_text = f.read()
        if "version_policy" not in config_text:
            with open(config_path, "a") as f:
                f.write("\nversion_policy { all {} }\n")
            logger.info("Added version_policy { all {} } to config.pbtxt")

    logger.info(
        "Staged challenger as version %d (champion is version %d)",
        challenger_version,
        champion_version,
    )
    return champion_version, challenger_version


@task(name="reload-model")
def reload_model(
    triton_url: str,
    model_name: str,
    timeout: int = 120,
) -> None:
    """Unload then reload a model in Triton to pick up filesystem changes.

    Since load_model/unload_model operate on the entire model (not individual versions),
    this is how we refresh Triton's view of available versions.
    """
    client = httpclient.InferenceServerClient(url=triton_url)
    try:
        client.unload_model(model_name)
    except Exception:
        pass  # Model might not be loaded yet

    client.load_model(model_name)

    # Wait for model to be ready
    start = time.time()
    while time.time() - start < timeout:
        try:
            if client.is_server_ready() and client.is_model_ready(model_name):
                logger.info("Model %s reloaded successfully", model_name)
                return
        except Exception:
            pass
        time.sleep(2)

    raise TimeoutError(f"Model {model_name} not ready after {timeout}s")


@task(name="health-check")
def health_check(
    triton_url: str,
    model_name: str,
    version: int,
    timeout: int = 30,
) -> bool:
    """Check if a specific model version is ready and responsive."""
    try:
        client = httpclient.InferenceServerClient(url=triton_url)
        return client.is_model_ready(model_name, model_version=str(version))
    except Exception as e:
        logger.warning("Health check failed for %s v%d: %s", model_name, version, e)
        return False


@task(name="score-model-version")
def score_model_version(
    triton_url: str,
    model_name: str,
    version: int,
    test_data: dict,
    labels: np.ndarray,
    decision_threshold: float = 0.5,
) -> dict:
    """Send test data to a specific Triton model version and compute metrics.

    Returns dict with f1_score, precision, recall, accuracy.
    """
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    from tritonclient.http import InferInput, InferRequestedOutput

    client = httpclient.InferenceServerClient(url=triton_url)

    # Build inputs from test_data dict
    inputs = []
    for key, value in test_data.items():
        if key.startswith("x_"):
            dtype = "FP32"
        elif key.startswith("feature_mask_"):
            dtype = "INT32"
        elif key.startswith("edge_feature_mask_"):
            dtype = "INT32"
        elif key.startswith("edge_index_"):
            dtype = "INT64"
        elif key.startswith("edge_attr_"):
            dtype = "FP32"
        elif key == "COMPUTE_SHAP":
            dtype = "BOOL"
        else:
            continue

        inp = InferInput(key, list(value.shape), datatype=dtype)
        inp.set_data_from_numpy(value)
        inputs.append(inp)

    # Add COMPUTE_SHAP = False for evaluation (faster)
    if "COMPUTE_SHAP" not in test_data:
        shap_flag = np.array([False], dtype=np.bool_)
        inp = InferInput("COMPUTE_SHAP", [1], datatype="BOOL")
        inp.set_data_from_numpy(shap_flag)
        inputs.append(inp)

    outputs = [InferRequestedOutput("PREDICTION")]

    response = client.infer(
        model_name,
        inputs=inputs,
        model_version=str(version),
        outputs=outputs,
    )

    predictions = response.as_numpy("PREDICTION")
    y_pred = (predictions > decision_threshold).astype(int).ravel()
    y_true = labels.ravel()

    metrics = {
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
    }
    logger.info("Model %s v%d metrics: %s", model_name, version, metrics)
    return metrics


@task(name="cleanup-version-artifacts")
def cleanup_version_artifacts(
    model_repo_path: str,
    model_name: str,
    version: int,
) -> None:
    """Remove a version directory from the model repository."""
    version_dir = os.path.join(model_repo_path, model_name, str(version))
    if os.path.isdir(version_dir):
        shutil.rmtree(version_dir)
        logger.info("Cleaned up version %d artifacts", version)
