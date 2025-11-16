# inference.py
from my_utils.threads_utils import limit_threads
from detection import run_detection
from feature_extraction import extract_and_store  # use the existing function
from my_utils.db_utils import load_numpy, load_model, save_json
from my_utils.config import CLASSIFIER_PATH, CROPS_DIR, FEATURES_DIR, PREPROC_DIR
from pathlib import Path
import numpy as np
import os

def run_inference():
    limit_threads()
    
    # 1️ Run detection to generate crops
    run_detection()
    
    # 2️ Extract features (or use existing ones)
    embeddings_path = Path(PREPROC_DIR) / "embeddings.npy"
    labels_path = Path(FEATURES_DIR) / "hybrid_labels.npy"
    
    if embeddings_path.exists() and labels_path.exists():
        print("[INFO] Loading existing embeddings for inference...")
        X = load_numpy(str(embeddings_path))
        labels = load_numpy(str(labels_path))
    else:
        print("[INFO] Extracting features for inference...")
        extract_and_store(CROPS_DIR)
        if not embeddings_path.exists():
            raise RuntimeError("Feature extraction failed: embeddings not created.")
        X = load_numpy(str(embeddings_path))
        # Save dummy labels if not already present
        crop_paths = sorted(list(Path(CROPS_DIR).rglob("*.jpg")))
        labels = np.array([Path(p).parent.name for p in crop_paths])
        np.save(labels_path, labels)
    
    # 3️ Load classifier
    if not Path(CLASSIFIER_PATH).exists():
        raise FileNotFoundError("Classifier missing. Train first.")
    clf = load_model(str(CLASSIFIER_PATH))
    
    # 4️ Run predictions
    preds = clf.predict(X)
    
    # 5️ Save predictions
    crop_paths = sorted(list(Path(CROPS_DIR).rglob("*.jpg")))
    out = [{"crop": str(p), "pred": p_i} for p, p_i in zip(crop_paths, preds)]
    save_json(out, Path(FEATURES_DIR) / "inference_predictions.json")
    print("[INFO] Inference done. Predictions saved.")
    return out

if __name__ == "__main__":
    run_inference()
