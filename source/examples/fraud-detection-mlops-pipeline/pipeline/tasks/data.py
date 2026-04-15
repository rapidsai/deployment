"""Data loading tasks."""

import logging
import os

import numpy as np
import pandas as pd
from prefect import task

logger = logging.getLogger(__name__)


@task(name="load-test-data")
def load_test_data(test_data_dir: str) -> dict:
    """Load heterogeneous graph test data for inference.

    Adapted from preprocess_TabFormer_lp.load_hetero_graph().
    Returns dict with node features, edge indices, edge attrs, labels, and feature masks.
    """
    nodes_dir = os.path.join(test_data_dir, "nodes")
    edges_dir = os.path.join(test_data_dir, "edges")
    out = {}

    # Load node features and feature masks
    if os.path.isdir(nodes_dir):
        for fname in sorted(os.listdir(nodes_dir)):
            if fname.endswith(".csv") and not fname.endswith("_feature_mask.csv"):
                node_name = fname[: -len(".csv")]
                node_df = pd.read_csv(os.path.join(nodes_dir, fname))
                out[f"x_{node_name}"] = node_df.to_numpy(dtype=np.float32)

                mask_path = os.path.join(nodes_dir, f"{node_name}_feature_mask.csv")
                if os.path.exists(mask_path):
                    mask = (
                        pd.read_csv(mask_path, header=None)
                        .to_numpy(dtype=np.int32)
                        .ravel()
                    )
                else:
                    mask = np.zeros(node_df.shape[1], dtype=np.int32)
                out[f"feature_mask_{node_name}"] = mask

    # Load edges: base, attrs, labels, feature masks
    base_edges = {}
    edge_attrs = {}
    edge_labels = {}
    edge_feature_masks = {}

    if os.path.isdir(edges_dir):
        for fname in sorted(os.listdir(edges_dir)):
            if not fname.endswith(".csv"):
                continue
            path = os.path.join(edges_dir, fname)
            if fname.endswith("_attr.csv"):
                edge_name = fname[: -len("_attr.csv")]
                edge_attrs[edge_name] = pd.read_csv(path)
            elif fname.endswith("_label.csv"):
                edge_name = fname[: -len("_label.csv")]
                edge_labels[edge_name] = pd.read_csv(path)
            elif fname.endswith("_feature_mask.csv"):
                edge_name = fname[: -len("_feature_mask.csv")]
                edge_feature_masks[edge_name] = pd.read_csv(path, header=None)
            else:
                edge_name = fname[: -len(".csv")]
                base_edges[edge_name] = pd.read_csv(path)

    for edge_name, df in base_edges.items():
        out[f"edge_index_{edge_name}"] = df.to_numpy(dtype=np.int64).T
        if edge_name in edge_attrs:
            out[f"edge_attr_{edge_name}"] = edge_attrs[edge_name].to_numpy(
                dtype=np.float32
            )
        if edge_name in edge_feature_masks:
            out[f"edge_feature_mask_{edge_name}"] = (
                edge_feature_masks[edge_name].to_numpy(dtype=np.int32).ravel()
            )
        elif edge_name in edge_attrs:
            out[f"edge_feature_mask_{edge_name}"] = np.zeros(
                edge_attrs[edge_name].shape[1], dtype=np.int32
            )

    for label_edge_name, label_df in edge_labels.items():
        out[f"edge_label_{label_edge_name}"] = label_df

    return out
