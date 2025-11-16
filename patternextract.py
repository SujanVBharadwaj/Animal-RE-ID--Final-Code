# patternextract.py
import cv2
import numpy as np
from pathlib import Path
from skimage.feature import local_binary_pattern, graycomatrix, graycoprops
from tqdm import tqdm
from my_utils.config import PATTERN_DIR, COLOR_HIST_BINS, LBP_POINTS, LBP_RADIUS
from my_utils.db_utils import save_numpy, save_json

# Pattern feature parameters
COLOR_HIST_BINS = 48
LBP_RADIUS = 3
LBP_POINTS = 8 * LBP_RADIUS


def extract_pattern(img_path):
    """
    Extract combined pattern features:
    - RGB color histogram
    - LBP histogram
    - GLCM texture features
    """
    img = cv2.imread(str(img_path))
    if img is None:
        return None

    features = []

    # Color histogram
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    for ch in range(3):
        hist = cv2.calcHist([img_rgb], [ch], None, [COLOR_HIST_BINS], [0, 256]).flatten()
        hist = hist / (hist.sum() + 1e-6)
        features.extend(hist.tolist())

    # LBP histogram
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lbp = local_binary_pattern(gray, LBP_POINTS, LBP_RADIUS, method="uniform")
    lbp_hist, _ = np.histogram(lbp.ravel(), bins=LBP_POINTS + 2, range=(0, LBP_POINTS + 2))
    lbp_hist = lbp_hist / (lbp_hist.sum() + 1e-6)
    features.extend(lbp_hist.tolist())

    # GLCM features
    gray_norm = (gray / 16).astype(np.uint8)
    distances = [1, 2]
    angles = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]
    for d in distances:
        for a in angles:
            try:
                glcm = graycomatrix(gray_norm, [d], [a], levels=16, symmetric=True, normed=True)
                features.append(float(graycoprops(glcm, 'contrast')[0, 0]))
                features.append(float(graycoprops(glcm, 'dissimilarity')[0, 0]))
                features.append(float(graycoprops(glcm, 'homogeneity')[0, 0]))
                features.append(float(graycoprops(glcm, 'energy')[0, 0]))
            except Exception:
                features.extend([0.0, 0.0, 0.0, 0.0])

    return np.array(features, dtype=np.float32)


def run_pattern_extraction(detections):
    """
    Extract pattern features for all detections.
    """
    features, valid_imgs = [], []

    for det in tqdm(detections, desc="Pattern Extraction"):
        try:
            f = extract_pattern(det["crop_path"])
            if f is not None:
                features.append(f)
                valid_imgs.append(det["crop_path"])
        except Exception:
            continue

    if not features:
        print("[WARN] No pattern features extracted.")
        return None

    X = np.vstack(features)
    save_numpy(X, Path(PATTERN_DIR) / "pattern_features.npy")
    save_json({"n_samples": X.shape[0], "dim": X.shape[1]}, Path(PATTERN_DIR) / "pattern_manifest.json")
    print(f"[INFO] Pattern features saved: {X.shape}")
    return Path(PATTERN_DIR) / "pattern_features.npy"
