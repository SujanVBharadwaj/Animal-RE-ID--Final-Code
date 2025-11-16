# feature_extraction.py
import numpy as np
import torch
from torchvision import models, transforms
from PIL import Image
from tqdm import tqdm
from pathlib import Path
import faiss

from my_utils.config import PREPROC_DIR, DEVICE, SEED
from my_utils.db_utils import save_numpy, save_json

torch.manual_seed(SEED)


# Load pretrained ResNet50 backbone
resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
resnet = torch.nn.Sequential(*list(resnet.children())[:-1])  # remove classifier head
resnet.eval().to(DEVICE)

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])


def extract_features(img_path):
    """
    Extract deep feature embeddings using ResNet50.
    """
    img = Image.open(img_path).convert("RGB")
    x = preprocess(img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        feat = resnet(x).squeeze().cpu().numpy()
    return feat


def extract_and_store(crops_dir):
    """
    Extract deep features from all crop images and store.
    """
    crops_dir = Path(crops_dir)
    crop_paths = sorted(crops_dir.rglob("*.jpg"))

    if not crop_paths:
        print(f"[WARN] No crop images found in {crops_dir}")
        return None, None

    features, metas = [], []

    for p in tqdm(crop_paths, desc="Feature Extraction"):
        try:
            f = extract_features(p)
            features.append(f)
            metas.append({"path": str(p), "label": Path(p).parent.name})
        except Exception as e:
            print(f"[WARN] Skipped {p}: {e}")

    X = np.vstack(features)
    save_numpy(X, Path(PREPROC_DIR) / "embeddings.npy")
    save_json(metas, Path(PREPROC_DIR) / "meta.json")
    print(f"[INFO] Saved deep features: {X.shape}")

    # FAISS index for deep features
    dim = X.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(X.astype(np.float32))
    faiss_path = Path(PREPROC_DIR) / "faiss_index.index"
    faiss.write_index(index, str(faiss_path))
    print(f"[INFO] FAISS index created with {index.ntotal} deep vectors")

    return X, metas
