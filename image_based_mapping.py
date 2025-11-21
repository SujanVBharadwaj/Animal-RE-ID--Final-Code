import numpy as np
import faiss
import json
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from feature_extraction import extract_features
from patternextract import extract_pattern
from my_utils.config import FEATURES_DIR, PREPROC_DIR, PATTERN_DIR, FAISS_INDEX_PATH


def image_based_matching(input_image_path, top_k=5):
    """
    Perform cosine-similarity based retrieval using combined (deep + pattern) features.
    Builds a ranked gallery of top matches and computes retrieval metrics.
    """

    print("[INFO] Performing image-based matching...")

    # --- Load FAISS index ---
    if not Path(FAISS_INDEX_PATH).exists():
        raise FileNotFoundError(f"Missing FAISS index at {FAISS_INDEX_PATH}")
    index = faiss.read_index(str(FAISS_INDEX_PATH))

    # --- Load stored deep and pattern features ---
    deep_path = PREPROC_DIR / "embeddings.npy"
    pattern_path = PATTERN_DIR / "pattern_features.npy"
    deep_meta_path = PREPROC_DIR / "meta.json"
    combined_meta_path = FEATURES_DIR / "combined_feature_db.json"

    if not deep_path.exists() or not pattern_path.exists():
        raise FileNotFoundError("Missing precomputed feature files.")
    if not deep_meta_path.exists() or not combined_meta_path.exists():
        raise FileNotFoundError("Missing metadata for alignment.")

    deep_features = np.load(deep_path)
    pattern_features = np.load(pattern_path)

    with open(deep_meta_path, "r") as f:
        deep_meta = json.load(f)
    with open(combined_meta_path, "r") as f:
        combined_meta = json.load(f)

    # --- Align deep and pattern features by crop filename ---
    deep_map = {Path(m["path"]).stem: i for i, m in enumerate(deep_meta)}
    pattern_map = {Path(m["image_path"]).stem: i for i, m in enumerate(combined_meta)}
    common_keys = list(set(deep_map.keys()) & set(pattern_map.keys()))

    if not common_keys:
        raise ValueError("No matching crop images between deep and pattern features")

    aligned_deep, aligned_pattern, aligned_meta = [], [], []
    for k in common_keys:
        aligned_deep.append(deep_features[deep_map[k]])
        aligned_pattern.append(pattern_features[pattern_map[k]])
        aligned_meta.append(combined_meta[pattern_map[k]])

    deep_features = np.vstack(aligned_deep)
    pattern_features = np.vstack(aligned_pattern)
    metadata = aligned_meta

    print(f"[INFO] Aligned {len(metadata)} crops with both feature types.")

    # --- Combine aligned features ---
    stored_combined = np.hstack([deep_features, pattern_features]).astype(np.float32)

    # --- Extract features from input image ---
    deep_feat = extract_features(input_image_path)
    pattern_feat = extract_pattern(input_image_path)

    if deep_feat is None or pattern_feat is None:
        raise ValueError("Feature extraction failed for input image")

    input_combined = np.concatenate([deep_feat, pattern_feat]).astype(np.float32).reshape(1, -1)

    # --- Compute cosine similarity ---
    cos_scores = cosine_similarity(input_combined, stored_combined).flatten()
    ranked_idx = np.argsort(-cos_scores)[:top_k]
    ranked_gallery = [
        {"rank": r + 1, **metadata[i], "cosine_score": float(cos_scores[i])}
        for r, i in enumerate(ranked_idx)
    ]

    # --- Precision / Recall estimation ---
    top_class = ranked_gallery[0]["class"]
    relevant = [m for m in ranked_gallery if m["class"] == top_class]
    precision = round(len(relevant) / len(ranked_gallery), 3)
    recall = round(len(relevant) / sum(1 for m in metadata if m["class"] == top_class), 3)

    metrics = {"precision": precision}

    # --- Save result JSON ---
    result = {
        "input_image": str(input_image_path),
        "ranked_gallery": ranked_gallery,
        "metrics": metrics,
    }
    out_path = FEATURES_DIR / "image_matching_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"[INFO] Image-based matching complete  → Results saved to {out_path}")
    return ranked_gallery, metrics
