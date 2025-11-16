# identity_association.py
import json
import numpy as np
from pathlib import Path
from my_utils.db_utils import load_model
from my_utils.config import CLASSIFIER_PATH, FEATURES_DIR
from feature_extraction import extract_features
from patternextract import extract_pattern


def identity_association(query_image_path):
    """
    Runs identity association using the trained classifier.
    Auto-detects whether the classifier expects deep-only or combined (deep+pattern) features.
    Returns predicted label and metrics.
    """

    # Load model
    model_path = Path(CLASSIFIER_PATH)
    if not model_path.exists():
        raise FileNotFoundError(f"Missing trained model: {model_path}")

    model = load_model(str(model_path))
    exp_dim = getattr(model, "n_features_in_", None)

    # Extract features
    deep_feat = extract_features(query_image_path).astype(np.float32).reshape(1, -1)
    pattern_feat = extract_pattern(query_image_path).astype(np.float32).reshape(1, -1)
    combined_feat = np.concatenate([deep_feat, pattern_feat], axis=1)

    # Select the correct vector based on model expectation
    if exp_dim is None:
        # Some sklearn pipelines hide this attribute
        print("[WARN] Model feature dimension unknown; using deep features.")
        X_input = deep_feat
        used = "deep"
    elif exp_dim == deep_feat.shape[1]:
        X_input = deep_feat
        used = "deep"
    elif exp_dim == combined_feat.shape[1]:
        X_input = combined_feat
        used = "combined"
    elif exp_dim < combined_feat.shape[1]:
        # Truncate combined vector to expected size
        X_input = combined_feat[:, :exp_dim]
        used = f"combined_truncated_{exp_dim}"
    else:
        X_input = deep_feat
        used = "fallback_deep"

    print(f"[INFO] Model expects {exp_dim} features; using {used} vector ({X_input.shape[1]}D).")

    # Predict label
    predicted_label = model.predict(X_input)[0]

    # Save metrics
    metrics = {
        "predicted_label": predicted_label,
        "feature_dim_used": X_input.shape[1],
        "feature_type": used,
        "precision": 1.0,  # placeholder until ground-truth eval
        "recall": 1.0
    }

    out_path = Path(FEATURES_DIR) / "identity_association_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"[INFO] Identity association complete → Results saved to {out_path}")
    print(f"[INFO] Predicted Animal: {predicted_label}")
    return predicted_label, metrics
