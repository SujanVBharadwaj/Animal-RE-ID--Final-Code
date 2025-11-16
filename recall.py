# recall.py — Top-1 retrieval + auto-add unknown images to FAISS + display best match
import json
import faiss
import shutil
import numpy as np
import cv2
from pathlib import Path
from image_based_mapping import image_based_matching
from feature_extraction import extract_features
from patternextract import extract_pattern
from my_utils.config import FEATURES_DIR, CROPS_DIR, FAISS_INDEX_PATH


# ------------------------------------------------------------
# Utility: Check if image is already in combined_feature_db
# ------------------------------------------------------------
def image_exists_in_db(img_path: Path):
    meta_path = FEATURES_DIR / "combined_feature_db.json"
    if not meta_path.exists():
        return False

    with open(meta_path, "r") as f:
        meta = json.load(f)

    normalized = str(img_path).replace("\\", "/").lower()

    for entry in meta:
        if entry["image_path"].replace("\\", "/").lower() == normalized:
            return True
    return False


# ------------------------------------------------------------
# Predict class using nearest-neighbor FAISS similarity
# ------------------------------------------------------------
def predict_class_via_faiss(img_path: Path):
    deep = extract_features(img_path)
    patt = extract_pattern(img_path)

    deep_norm = deep / (np.linalg.norm(deep) + 1e-8)
    patt_norm = patt / (np.linalg.norm(patt) + 1e-8)
    combined = np.concatenate([deep_norm, patt_norm]).astype("float32").reshape(1, -1)

    # Load index + metadata
    index = faiss.read_index(str(FAISS_INDEX_PATH))
    meta_path = FEATURES_DIR / "combined_feature_db.json"
    meta = json.load(open(meta_path, "r"))

    distances, indices = index.search(combined, 1)
    nearest_idx = indices[0][0]

    return meta[nearest_idx]["class"]


# ------------------------------------------------------------
# Add unknown image into crops + FAISS + metadata
# ------------------------------------------------------------
def add_unknown_image(img_path: Path):
    print("[INFO] New image detected → Adding to FAISS")

    # Step 1: Predict class using FAISS nearest neighbor
    predicted_class = predict_class_via_faiss(img_path)
    print(f"[INFO] Predicted species = {predicted_class}")

    # Step 2: Copy into crops/<class>/
    class_dir = CROPS_DIR / predicted_class
    class_dir.mkdir(parents=True, exist_ok=True)

    copied_path = class_dir / img_path.name
    shutil.copy(str(img_path), str(copied_path))
    print(f"[INFO] Copied to {copied_path}")

    # Step 3: Extract features
    deep = extract_features(copied_path)
    patt = extract_pattern(copied_path)

    deep_norm = deep / (np.linalg.norm(deep) + 1e-8)
    patt_norm = patt / (np.linalg.norm(patt) + 1e-8)
    combined_vec = np.concatenate([deep_norm, patt_norm]).astype("float32")

    # Step 4: Update FAISS
    index = faiss.read_index(str(FAISS_INDEX_PATH))
    index.add(combined_vec.reshape(1, -1))
    faiss.write_index(index, str(FAISS_INDEX_PATH))
    print("[INFO] FAISS updated")

    # Step 5: Update metadata
    meta_path = FEATURES_DIR / "combined_feature_db.json"
    meta = json.load(open(meta_path, "r"))

    new_entry = {
        "id": f"{predicted_class}_{len(meta)+1}",
        "class": predicted_class,
        "image_path": str(copied_path),
        "deep_dim": len(deep_norm),
        "pattern_dim": len(patt_norm)
    }

    meta.append(new_entry)
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    print("[INFO] Metadata updated")

    return copied_path


# ------------------------------------------------------------
# MAIN Recall Pipeline (existing logic + new auto-add)
# ------------------------------------------------------------
def run_recall_pipeline(input_image_path):
    input_image_path = Path(input_image_path)
    print("[INFO] Running Recall Pipeline...")

    # --------------------------------------------------------
    # Condition Check: Is this image already part of FAISS DB?
    # --------------------------------------------------------
    if not image_exists_in_db(input_image_path):
        print("[WARN] Image NOT found in FAISS → Adding it first...")
        input_image_path = add_unknown_image(input_image_path)
    else:
        print("[INFO] Image already in FAISS. Using existing logic...")

    # --------------------------------------------------------
    # Existing logic (unchanged)
    # --------------------------------------------------------
    ranked_gallery, metrics = image_based_matching(input_image_path, top_k=5)

    if not ranked_gallery:
        print("[ERROR] No matches found.")
        return None

    best = ranked_gallery[0]
    best_image_path = Path(best["image_path"])
    best_id = best_image_path.parent.name.lower()

    print("\n=== BEST MATCH FOUND ===")
    print(f"Predicted Animal ID : {best_id}")
    print(f"Best Match Image    : {best_image_path}")

    # Display image
    img = cv2.imread(str(best_image_path))
    if img is not None:
        cv2.imshow(f"Best Match: {best_id}", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return {
        "predicted_id": best_id,
        "best_match_image": str(best_image_path),
        "ranked_gallery": ranked_gallery,
    }


if __name__ == "__main__":
    test_img = Path("D:/final_project_code/new_tiger.jpg")
    run_recall_pipeline(test_img)
