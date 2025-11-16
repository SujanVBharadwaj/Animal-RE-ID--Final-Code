import numpy as np
import cv2
from pathlib import Path
import torch

# COCO keypoints order (standard for keypointrcnn and YOLO pose)
COCO_KP_NAMES = [
    "nose", "left_eye", "right_eye",
    "left_ear", "right_ear",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle"
]


def compute_named_keypoints_from_torch(kp_array, threshold=0.5):
    """Convert torch-style (N, K, 3) keypoints into named dict."""
    if kp_array is None or len(kp_array) == 0:
        return {}
    inst = kp_array[0]  # first detected instance
    named = {}
    for i, (x, y, v) in enumerate(inst):
        score = float(v)
        named[COCO_KP_NAMES[i]] = (float(x), float(y), score) if score >= threshold else None

    # derived joint: lowerback (midpoint between hips)
    left = named.get("left_hip")
    right = named.get("right_hip")
    if left and right:
        lx, ly, _ = left
        rx, ry, _ = right
        mx, my = (lx + rx) / 2.0, (ly + ry) / 2.0
        named["lowerback"] = (mx, my, (left[2] + right[2]) / 2.0)
    else:
        named["lowerback"] = None
    return named


def extract_pose_named(pose_model_type, pose_model, crop_bgr, conf_thresh=0.3):
    """
    pose_model_type: "ultralytics" (YOLOv8/v11 pose) or "torchvision"
    pose_model: loaded model object
    crop_bgr: single cropped image (BGR)
    returns: dict {keypoint_name: (x, y, score) or None}
    """
    if pose_model_type == "ultralytics":
        img_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        results = pose_model.predict(img_rgb, verbose=False)
        if not results or len(results) == 0:
            return {}

        r = results[0]

        # --- YOLOv11/YOLOv8 pose structure handling ---
        try:
            kps = None
            if hasattr(r, "keypoints") and r.keypoints is not None:
                # Ultralytics unified API for YOLOv8/v9/v10/v11
                kps_obj = r.keypoints
                coords = None
                confs = None

                # YOLOv11 keypoints might expose numpy arrays directly
                if hasattr(kps_obj, "xy"):
                    coords = kps_obj.xy[0] if isinstance(kps_obj.xy, list) else kps_obj.xy
                elif hasattr(kps_obj, "data"):
                    coords = kps_obj.data[0, :, :2].cpu().numpy()
                elif isinstance(kps_obj, np.ndarray):
                    coords = kps_obj

                if hasattr(kps_obj, "conf"):
                    confs = kps_obj.conf[0].cpu().numpy() if isinstance(kps_obj.conf, torch.Tensor) else kps_obj.conf
                elif hasattr(kps_obj, "data") and kps_obj.data.shape[-1] == 3:
                    confs = kps_obj.data[0, :, 2].cpu().numpy()

                if coords is None:
                    return {}

                named = {}
                for i, name in enumerate(COCO_KP_NAMES):
                    if i < len(coords):
                        x, y = float(coords[i][0]), float(coords[i][1])
                        s = float(confs[i]) if confs is not None else 1.0
                        named[name] = (x, y, s) if s >= conf_thresh else None
                    else:
                        named[name] = None

                # Add lowerback
                left = named.get("left_hip")
                right = named.get("right_hip")
                if left and right:
                    mx, my = (left[0] + right[0]) / 2.0, (left[1] + right[1]) / 2.0
                    named["lowerback"] = (mx, my, (left[2] + right[2]) / 2.0)
                else:
                    named["lowerback"] = None

                return named
            else:
                return {}
        except Exception as e:
            print(f"[pose_utils] Pose extraction failed: {e}")
            return {}

    # --- TorchVision Keypoint R-CNN fallback ---
    else:
        import torchvision.transforms as T
        img_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        tensor = T.ToTensor()(img_rgb)
        with torch.no_grad():
            out = pose_model([tensor.to(next(pose_model.parameters()).device)])[0]
        if "keypoints" not in out or len(out["keypoints"]) == 0:
            return {}
        kps = out["keypoints"].cpu().numpy()  # (N, K, 3)
        return compute_named_keypoints_from_torch(kps, threshold=0.5)
