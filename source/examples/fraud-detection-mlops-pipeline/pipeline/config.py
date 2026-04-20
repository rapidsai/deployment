"""Centralized configuration for the fraud detection MLOps pipeline."""

import os

from dotenv import load_dotenv

load_dotenv()

# --- Paths ---

DATA_ROOT = os.getenv("DATA_ROOT", "/data/TabFormer")
RAW_CSV_PATH = os.path.join(DATA_ROOT, "raw", "card_transaction.v1.csv")
GNN_DATA_DIR = os.path.join(DATA_ROOT, "gnn")
TEST_DATA_DIR = os.path.join(DATA_ROOT, "gnn", "test_gnn")
MODEL_OUTPUT_DIR = os.getenv("MODEL_OUTPUT_DIR", "/data/trained_models")
TRITON_MODEL_REPO = os.getenv("TRITON_MODEL_REPO", "/models")

# --- Infrastructure ---

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5050")
MLFLOW_EXPERIMENT_NAME = "fraud-detection-training"
MLFLOW_PREPROCESS_EXPERIMENT_NAME = "fraud-detection-preprocess"
PREFECT_API_URL = os.getenv("PREFECT_API_URL", "http://localhost:4200/api")
TRITON_HTTP_URL = os.getenv("TRITON_HTTP_URL", "localhost:8000")
TRITON_GRPC_URL = os.getenv("TRITON_GRPC_URL", "localhost:8001")

# --- Training ---

NGC_API_KEY = os.getenv("NGC_API_KEY", "")
TRAINING_IMAGE = "nvcr.io/nvidia/cugraph/financial-fraud-training:2.0.0"
TRITON_MODEL_NAME = "prediction_and_shapley"

DEFAULT_GNN_PARAMS = {
    "hidden_channels": 32,
    "n_hops": 2,
    "layer": "SAGEConv",
    "dropout_prob": 0.1,
    "batch_size": 4096,
    "fan_out": 10,
    "num_epochs": 8,
}

DEFAULT_XGB_PARAMS = {
    "max_depth": 6,
    "learning_rate": 0.2,
    "num_parallel_tree": 3,
    "num_boost_round": 512,
    "gamma": 0.0,
}

# --- Preprocessing ---

DEFAULT_FRAUD_RATIO = 0.1
DEFAULT_UNDER_SAMPLE = True

# --- Evaluation ---

PROMOTION_METRIC = "f1_score"
MIN_IMPROVEMENT = 0.0
DECISION_THRESHOLD = 0.5
