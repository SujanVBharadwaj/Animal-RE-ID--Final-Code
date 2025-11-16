# my_utils/metrics_utils.py
import json
import numpy as np
from sklearn.metrics import (
    precision_recall_fscore_support,
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.metrics import silhouette_score, calinski_harabasz_score, adjusted_rand_score
from my_utils.config import METRICS_DIR
from pathlib import Path

def save_classification_metrics(y_true, y_pred, labels=None, filename="classification_metrics.json"):
    p, r, f1, sup = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, labels=labels, zero_division=0, output_dict=True)
    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist() if labels is not None else confusion_matrix(y_true, y_pred).tolist()
    out = {
        "precision_per_class": np.asarray(p).tolist(),
        "recall_per_class": np.asarray(r).tolist(),
        "f1_per_class": np.asarray(f1).tolist(),
        "support_per_class": np.asarray(sup).tolist(),
        "accuracy": float(acc),
        "classification_report": report,
        "confusion_matrix": cm
    }
    Path(METRICS_DIR).mkdir(parents=True, exist_ok=True)
    with open(Path(METRICS_DIR) / filename, "w") as f:
        json.dump(out, f, indent=2)
    return out

def save_clustering_metrics(X, labels, filename="clustering_metrics.json"):
    out = {}
    if len(set(labels)) > 1 and X.shape[0] > 1:
        out["silhouette"] = float(silhouette_score(X, labels))
        out["calinski_harabasz"] = float(calinski_harabasz_score(X, labels))
        out["adjusted_rand"] = float(adjusted_rand_score(labels, labels))
    Path(METRICS_DIR).mkdir(parents=True, exist_ok=True)
    with open(Path(METRICS_DIR) / filename, "w") as f:
        json.dump(out, f, indent=2)
    return out
