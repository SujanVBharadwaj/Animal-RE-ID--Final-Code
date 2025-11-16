# train.py
from detection import run_detection
from patternextract import run_pattern_extraction
from feature_extraction import extract_and_store
from feature_store import build_feature_database
from classifier import train_and_select
from my_utils.config import CROPS_DIR
from pathlib import Path
import numpy as np


def main():
    print("[INFO] Starting unified feature training pipeline...")

    # 1️ Detect and crop animal images
    detections = run_detection()

    # 2️ Extract pattern features
    X_pattern = run_pattern_extraction(detections)
    if X_pattern is None:
        print("[ERROR] Pattern extraction failed.")
        return

    # 3️ Extract deep features
    X_deep, metas = extract_and_store(CROPS_DIR)
    if X_deep is None:
        print("[ERROR] Deep feature extraction failed.")
        return

    # 4️ Build unified feature + pattern FAISS database
    build_feature_database()

    # 5️ Prepare classifier labels
    y = np.array([Path(det["crop_path"]).parent.name for det in detections[:len(X_deep)]])

    # 6️ Train classifier using deep embeddings
    best_model, summary = train_and_select(X_deep, y)
    print("[INFO] Training complete. Model summary:", summary)


if __name__ == "__main__":
    main()
