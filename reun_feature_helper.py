import torch
import torch.nn as nn
from torchvision import models, transforms
from torch.utils.data import DataLoader
from pathlib import Path
import numpy as np
from tqdm import tqdm
from my_utils.config import *
from my_utils.db_utils import create_or_load_index, add_vectors, load_metadata
from PIL import Image
import faiss
import os

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
FEATURES_DIR = Path(DEEP_FEATURE_DIR) if 'DEEP_FEATURE_DIR' in globals() else Path("features")
FEATURES_DIR.mkdir(parents=True, exist_ok=True)
FINE_TUNED_MODEL_PATH = FEATURES_DIR / "resnet_finetuned_best.pth"


def _get_tfms(train=False):
    size = RESNET_INPUT if 'RESNET_INPUT' in globals() else (224, 224)
    if train:
        return transforms.Compose([
            transforms.Resize(size),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])
    else:
        return transforms.Compose([
            transforms.Resize(size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])


def fine_tune_resnet_once(crops_dir, epochs=6, lr=1e-4):
    """Fine-tune ResNet if not already done"""
    if FINE_TUNED_MODEL_PATH.exists():
        return

    ds_root = Path(crops_dir)
    if not ds_root.exists():
        return

    imgs = list(ds_root.rglob("*.jpg"))
    if len(imgs) < 8:
        return

    from torchvision import datasets
    from torch.utils.data import random_split
    ds = datasets.ImageFolder(str(ds_root), transform=_get_tfms(train=True))
    if len(ds) < 8:
        return

    val_size = max(1, int(0.2 * len(ds)))
    train_size = len(ds) - val_size
    train_ds, val_ds = random_split(ds, [train_size, val_size], generator=torch.Generator().manual_seed(SEED))

    train_dl = DataLoader(train_ds, batch_size=16, shuffle=True, num_workers=0)
    val_dl = DataLoader(val_ds, batch_size=16, shuffle=False, num_workers=0)

    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    for name, param in model.named_parameters():
        if "layer4" not in name and "fc" not in name:
            param.requires_grad = False

    num_classes = len(ds.classes)
    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(512, num_classes)
    )
    model = model.to(DEVICE)

    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.CrossEntropyLoss()

    best_acc = 0.0
    for epoch in range(epochs):
        model.train()
        for imgs, labels in train_dl:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            out = model(imgs)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()
        scheduler.step()

        # Validation
        model.eval()
        vpreds, vtargs = [], []
        with torch.no_grad():
            for imgs, labels in val_dl:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                out = model(imgs)
                vpreds.extend(out.argmax(1).cpu().numpy())
                vtargs.extend(labels.cpu().numpy())

        val_acc = (np.array(vpreds) == np.array(vtargs)).mean() if len(vtargs) else 0.0
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), FINE_TUNED_MODEL_PATH)


def get_embedding_model():
    """Return ResNet model for feature extraction"""
    model = models.resnet50(weights=None)
    model.fc = nn.Identity()
    model = model.to(DEVICE)
    if FINE_TUNED_MODEL_PATH.exists():
        try:
            sd = torch.load(FINE_TUNED_MODEL_PATH, map_location=DEVICE)
            model.load_state_dict(sd, strict=False)
        except Exception:
            pass
    model.eval()
    return model


def extract_and_store(crops_dir):
    """Force rebuild embeddings and FAISS index"""
    crops_dir = Path(crops_dir)
    if not crops_dir.exists():
        raise ValueError("Crops dir does not exist")

    # 1️ Clear previous FAISS + metadata
    PREPROC_DIR_PATH = Path(PREPROC_DIR)
    PREPROC_DIR_PATH.mkdir(parents=True, exist_ok=True)
    for f in ["faiss_index.ivfpq", "metadata.json", "embeddings.npy"]:
        fp = PREPROC_DIR_PATH / f
        if fp.exists():
            os.remove(fp)
            print(f"[INFO] Deleted old file: {fp}")

    fine_tune_resnet_once(crops_dir)

    # 2️ Collect crops
    all_crops = sorted([p for p in crops_dir.rglob("*_annotated.jpg")])
    if not all_crops:
        all_crops = sorted([p for p in crops_dir.rglob("*.jpg")])

    if not all_crops:
        raise RuntimeError("No crops found in folder!")

    # 3️ Extract features
    model = get_embedding_model()
    tfm = _get_tfms(train=False)

    feats = []
    metas = []
    for p in tqdm(all_crops, desc="Feature Extraction", unit="img", ncols=100):
        try:
            img = Image.open(p).convert("RGB")
            inp = tfm(img).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                feat = model(inp).cpu().numpy().reshape(-1).astype("float32")
            feats.append(feat)
            metas.append({"path": str(p), "label": Path(p).parent.name})
        except Exception as e:
            print(f"[WARN] Failed on {p}: {e}")
            continue

    if not feats:
        raise RuntimeError("No valid embeddings extracted!")

    feats_arr = np.vstack(feats).astype("float32")
    dim = feats_arr.shape[1]
    index = create_or_load_index(dim)
    add_vectors(index, feats_arr, metas)

    # 4️ Save FAISS + embeddings
    FAISS_PATH = PREPROC_DIR_PATH / "faiss_index.ivfpq"
    EMBED_PATH = PREPROC_DIR_PATH / "embeddings.npy"

    faiss.write_index(index, str(FAISS_PATH))
    np.save(EMBED_PATH, feats_arr)
    print(f"[INFO] Saved FAISS index → {FAISS_PATH}")
    print(f"[INFO] Saved embeddings → {EMBED_PATH}")

    return len(all_crops)


if __name__ == "__main__":
    crops_root = Path(CROPS_DIR)
    print(f"Rebuilding embeddings from crops in: {crops_root}")
    n = extract_and_store(crops_root)
    print(f"✅ Completed: {n} embeddings extracted and stored.")
