# detection.py — YOLO11-based detection & cropping (tiger/deer)
import os
import cv2
import json
import torch
from pathlib import Path
from tqdm import tqdm
from ultralytics import YOLO
from my_utils.config import DATASET_ROOT, CROPS_DIR, DETECTIONS_DIR, DEVICE

# Allowed folder names → these decide crop destination
ALLOWED_CLASSES = ["tiger", "deer"]

# YOLO model
YOLO_WEIGHTS = "yolo11n.pt"


def get_detection_model():
    print(f"[INFO] Loading YOLO11 model: {YOLO_WEIGHTS}")
    return YOLO(YOLO_WEIGHTS)


def load_all_images():
    """Scan Dataset folder for jpg/jpeg/png."""
    exts = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]
    img_list = []
    for ext in exts:
        img_list.extend(Path(DATASET_ROOT).rglob(ext))
    return sorted(img_list)


def run_detection():
    print("[INFO] Starting YOLO11 detection + cropping...")

    det_model = get_detection_model()
    detections = []

    img_paths = load_all_images()

    print(f"[INFO] Total images detected in Dataset: {len(img_paths)}")
    if len(img_paths) == 0:
        print("[ERROR] No images found in Dataset folder.")
        return []

    for img_path in tqdm(img_paths, desc="Processing images", ncols=100):

        # Folder name tells class (tiger/deer)
        folder_label = img_path.parent.name.lower()

        if folder_label not in ALLOWED_CLASSES:
            continue

        img = cv2.imread(str(img_path))
        if img is None:
            continue

        # Run YOLO
        results = det_model(img, conf=0.25, device=DEVICE, verbose=False)
        result = results[0]

        # Skip if no detection
        if not hasattr(result, "boxes") or len(result.boxes) == 0:
            continue

        # Prepare crop folder
        crop_dir = CROPS_DIR / folder_label
        crop_dir.mkdir(parents=True, exist_ok=True)

        # Process each detected box
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())

            # Crop
            crop = img[y1:y2, x1:x2]
            crop_name = f"{folder_label}_{img_path.stem}.jpg"
            crop_path = crop_dir / crop_name
            cv2.imwrite(str(crop_path), crop)

            # Draw green bounding box on original image
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Save detection info
            detections.append({
                "image": str(img_path),
                "label": folder_label,
                "bbox": [x1, y1, x2, y2],
                "crop_path": str(crop_path)
            })

        # Save full image with bounding boxes
        DETECTIONS_DIR.mkdir(parents=True, exist_ok=True)
        out_img_path = DETECTIONS_DIR / f"{img_path.stem}_boxed.jpg"
        cv2.imwrite(str(out_img_path), img)

    # Save detections JSON
    detections_json = DETECTIONS_DIR / "detections.json"
    with open(detections_json, "w", encoding="utf-8") as f:
        json.dump(detections, f, indent=2)

    print("\n[INFO] Detection complete.")
    print(f"→ Crops saved at     : {CROPS_DIR}")
    print(f"→ Boxed images at    : {DETECTIONS_DIR}")
    print(f"→ Detection summary  : {detections_json}")

    return detections
