import torch
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = "D:/final_project_code/Dataset"

# Outputs
OUTPUT_ROOT = PROJECT_ROOT / "outputs"
CROPS_DIR = OUTPUT_ROOT / "crops"
PREPROC_DIR = OUTPUT_ROOT / "features/deep"
PATTERN_DIR = OUTPUT_ROOT / "features/pattern"
MODELS_DIR = OUTPUT_ROOT / "models"
METRICS_DIR = OUTPUT_ROOT / "metrics"
VIS_DIR = OUTPUT_ROOT / "visualizations"
DETECTIONS_DIR = OUTPUT_ROOT / "detections"
FEATURES_DIR = OUTPUT_ROOT / "features"
DEEP_FEATURE_DIR = PREPROC_DIR  # alias for backward compatibility
FAISS_INDEX_PATH = OUTPUT_ROOT / "features/deep/faiss_index.index"
CLASSIFIER_PATH = Path("D:/final_project_code/outputs/models/best_model.pkl")



for p in (OUTPUT_ROOT, CROPS_DIR, PREPROC_DIR, PATTERN_DIR,
          MODELS_DIR, METRICS_DIR, VIS_DIR, DETECTIONS_DIR):
    p.mkdir(parents=True, exist_ok=True)

# Runtime
SEED = 42
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# MegaDetector weights
# MegaDetector (weights)
MEGADETECTOR_URL = "https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt"
MEGA_WEIGHTS = MODELS_DIR / "md_v5a.0.0.pt"

# Detection params
CONF_THRES = 0.2
IOU_THRES = 0.45
CROP_PADDING = 30

# Pose model
POSE_WEIGHTS = "yolov8n-pose.pt"
POSE_MODEL_PATH = MODELS_DIR / POSE_WEIGHTS

# Deep features
RESNET_INPUT = (224, 224)
RESNET_EMBEDDING_DIM = 2048

# Pattern features
LBP_RADIUS = 3
LBP_POINTS = 8 * LBP_RADIUS
COLOR_HIST_BINS = 48
N_CLUSTERS_PATTERN = 8

# Classifier
CLASSIFIER_PATH = MODELS_DIR / "best_classifier.joblib"
TRAIN_FLAG = MODELS_DIR / "trained.flag"
