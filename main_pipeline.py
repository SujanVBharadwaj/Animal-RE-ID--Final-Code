# master_reid_pipeline.py
import json
from pathlib import Path
from recall import run_recall_pipeline
from train import main as full_training_pipeline  # Reuses your train.py
from my_utils.config import FEATURES_DIR


# ---------------------------------------------------------------
# Conditional Animal Re-Identification
# ---------------------------------------------------------------
def conditional_reid(image_path, recall_threshold=0.5):
    print("\n====================================")
    print(f"[INFO] Starting conditional Re-ID on: {image_path}")
    print("====================================")

    try:
        ranked_gallery, metrics = run_recall_pipeline(image_path)
        recall_value = metrics.get("recall", 0)
        print(f"[INFO] Recall score = {recall_value}")
    except Exception as e:
        print(f"[WARN] Recall failed: {e}")
        ranked_gallery, recall_value = None, 0.0

    # If recall low or missing → retrain everything via train.py
    if ranked_gallery is None or recall_value < recall_threshold:
        print("[INFO] Recall insufficient — launching full training pipeline...")
        full_training_pipeline()
        print("[INFO] Retraining complete.")
    else:
        print("[INFO] Recall sufficient — no retraining required.")

    # Optional: log each run
    results_log = FEATURES_DIR / "reid_run_log.json"
    entry = {
        "image": str(image_path),
        "recall": recall_value,
        "triggered_retrain": recall_value < recall_threshold
    }

    if results_log.exists():
        data = json.load(open(results_log))
    else:
        data = []
    data.append(entry)
    json.dump(data, open(results_log, "w"), indent=2)
    print(f"[INFO] Run logged at: {results_log}")


# ---------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------
if __name__ == "__main__":
    test_img = Path("D:/final_project_code/Dataset/test/deer_sample.jpg")
    conditional_reid(test_img, recall_threshold=0.5)
