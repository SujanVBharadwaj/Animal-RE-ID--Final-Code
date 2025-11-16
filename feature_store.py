# feature_store.py
import json
import numpy as np
import faiss
from pathlib import Path
from my_utils.config import CROPS_DIR, FEATURES_DIR, FAISS_INDEX_PATH
from feature_extraction import extract_features
from patternextract import extract_pattern


def build_feature_database():
    """
    Builds a FAISS database where each entry is a combined [deep + pattern] feature vector.
    Metadata preserves separate components for interpretability.
    """
    print("[INFO] Building unified feature+pattern FAISS database...")

    combined_vectors = []
    metadata = []

    animal_dirs = [d for d in CROPS_DIR.iterdir() if d.is_dir()]

    for animal_dir in animal_dirs:
        animal_class = animal_dir.name
        crop_images = list(animal_dir.glob("*.jpg"))

        for idx, img_path in enumerate(crop_images, start=1):
            try:
                deep_vec = extract_features(img_path)
                pattern_vec = extract_pattern(img_path)

                if deep_vec is None or pattern_vec is None:
                    continue

                # Normalize both
                deep_vec = deep_vec / (np.linalg.norm(deep_vec) + 1e-8)
                pattern_vec = pattern_vec / (np.linalg.norm(pattern_vec) + 1e-8)

                # Combine (concatenate) both
                combined = np.concatenate([deep_vec, pattern_vec]).astype("float32")

                entry_id = f"{animal_class}_{idx}"
                combined_vectors.append(combined)

                metadata.append({
                    "id": entry_id,
                    "class": animal_class,
                    "image_path": str(img_path),
                    "deep_dim": len(deep_vec),
                    "pattern_dim": len(pattern_vec)
                })

            except Exception as e:
                print(f"[WARN] Skipping {img_path.name}: {e}")

    if not combined_vectors:
        print("[ERROR] No valid combined features extracted.")
        return

    X = np.vstack(combined_vectors)
    dim = X.shape[1]

    # Build FAISS index on combined space
    index = faiss.IndexFlatL2(dim)
    index.add(X)

    # Save FAISS + metadata
    FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_PATH))

    metadata_path = FEATURES_DIR / "combined_feature_db.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[INFO] Unified FAISS database built successfully!")
    print(f"→ FAISS Index: {FAISS_INDEX_PATH}")
    print(f"→ Metadata: {metadata_path}")
