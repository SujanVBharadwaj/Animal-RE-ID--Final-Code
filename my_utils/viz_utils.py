# my_utils/viz_utils.py
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
from my_utils.config import METRICS_DIR, TSNE_SAMPLE
from pathlib import Path

Path(METRICS_DIR).mkdir(parents=True, exist_ok=True)

def plot_confusion_matrix(cm, labels, outpath=None):
    plt.figure(figsize=(8,6))
    sns.heatmap(np.array(cm), annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted"); plt.ylabel("True"); plt.title("Confusion Matrix")
    plt.tight_layout()
    outpath = outpath or (Path(METRICS_DIR) / "confusion_matrix.png")
    plt.savefig(str(outpath), dpi=150); plt.close()

def plot_feature_importance(importances, outpath=None, top_k=40):
    idxs = np.argsort(importances)[::-1][:top_k]
    vals = importances[idxs]
    names = [f"f{int(i)}" for i in idxs]
    plt.figure(figsize=(10,8))
    sns.barplot(x=vals, y=names)
    plt.title("Top feature importances")
    plt.tight_layout()
    outpath = outpath or (Path(METRICS_DIR) / "feature_importance.png")
    plt.savefig(str(outpath), dpi=150); plt.close()

def plot_embeddings(X, y, outpath=None, method="tsne", sample=TSNE_SAMPLE):
    if X.shape[0] > sample:
        rng = np.random.RandomState(42)
        idx = rng.choice(X.shape[0], sample, replace=False)
        Xs = X[idx]; ys = np.array(y)[idx]
    else:
        Xs = X; ys = y
    le = LabelEncoder()
    ys_enc = le.fit_transform(ys)
    if method == "pca":
        reducer = PCA(n_components=2, random_state=42)
    else:
        reducer = TSNE(n_components=2, random_state=42, init="pca")
    Z = reducer.fit_transform(Xs)
    plt.figure(figsize=(10,8))
    scatter = plt.scatter(Z[:,0], Z[:,1], c=ys_enc, cmap="tab20", s=8)
    handles = []
    classes = le.classes_
    for i, c in enumerate(classes):
        handles.append(plt.Line2D([], [], marker="o", color=plt.cm.tab20(i % 20), linestyle="", markersize=6))
    plt.legend(handles, classes, bbox_to_anchor=(1.05,1), loc="upper left", fontsize=8)
    plt.title(f"Embeddings ({method})")
    plt.tight_layout()
    outpath = outpath or (Path(METRICS_DIR) / f"embeddings_{method}.png")
    plt.savefig(str(outpath), dpi=150); plt.close()
