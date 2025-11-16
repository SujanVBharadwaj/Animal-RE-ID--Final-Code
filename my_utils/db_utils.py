# my_utils/db_utils.py
import json
from pathlib import Path
import faiss
import numpy as np
import joblib

# Use DEEP_FEATURE_DIR or fallback to features/
try:
    from my_utils.config import DEEP_FEATURE_DIR
    DB_DIR = Path(DEEP_FEATURE_DIR)
except Exception:
    DB_DIR = Path("features")
DB_DIR.mkdir(parents=True, exist_ok=True)

FAISS_INDEX_PATH = DB_DIR / "faiss_index.ivfpq"
VECTOR_META_PATH = DB_DIR / "faiss_metadata.json"
EMB_ARRAY_PATH = DB_DIR / "embeddings.npy"

# IVFPQ params (tunable)
NLIST = 100
M = 8
NBITS = 8


# ------------------ FAISS Index Management ------------------ #
def _make_index(dimension: int):
    """Build IVFPQ index for given vector dimension."""
    quantizer = faiss.IndexFlatL2(dimension)
    index = faiss.IndexIVFPQ(quantizer, dimension, NLIST, M, NBITS)
    return index


def create_or_load_index(dimension: int):
    """Create new IVFPQ index or load existing safely."""
    if FAISS_INDEX_PATH.exists():
        idx = faiss.read_index(str(FAISS_INDEX_PATH))
        if idx.d != dimension:
            print(f"[WARN] Existing FAISS index dim={idx.d} ≠ {dimension}. Rebuilding.")
            idx = _make_index(dimension)
        else:
            print(f"[INFO] Loaded FAISS index from {FAISS_INDEX_PATH} (ntotal={idx.ntotal})")
        return idx
    else:
        idx = _make_index(dimension)
        print(f"[INFO] Created new FAISS IVFPQ index (dim={dimension})")
        return idx


def save_index(index, metadata: list):
    """Persist FAISS index and metadata."""
    faiss.write_index(index, str(FAISS_INDEX_PATH))
    with open(VECTOR_META_PATH, "w", encoding="utf8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[INFO] Saved FAISS index ({index.ntotal} vectors) + metadata ({len(metadata)})")


def load_metadata():
    if VECTOR_META_PATH.exists():
        return json.load(open(VECTOR_META_PATH, "r", encoding="utf8"))
    return []


# ------------------ Add / Search ------------------ #
def add_vectors(index, embeddings: np.ndarray, metadata: list):
    """Add new embeddings + metadata to FAISS."""
    embeddings = np.asarray(embeddings, dtype="float32")
    n, d = embeddings.shape

    if not index.is_trained:
        print("[INFO] Training FAISS IVFPQ index...")
        index.train(embeddings)
        print("[INFO] FAISS training complete.")

    index.add(embeddings)

    # Extend metadata
    existing = load_metadata()
    existing.extend(metadata)

    save_index(index, existing)
    np.save(EMB_ARRAY_PATH, embeddings)
    print(f"[INFO] Added {n} vectors to FAISS (dim={d})")


def search(index, query_vector, k=5):
    """Return distances and indices for top-k matches."""
    q = np.array(query_vector, dtype="float32").reshape(1, -1)
    distances, indices = index.search(q, k)
    return distances[0].tolist(), indices[0].tolist()


# ------------------ IO Utilities ------------------ #
def save_model(model, path):
    joblib.dump(model, path)


def load_model(path):
    return joblib.load(path)


def save_json(data, path):
    with open(path, "w", encoding="utf8") as f:
        json.dump(data, f, indent=2)


# ------------------ Load FAISS Data ------------------ #
def load_data_from_faiss():
    """
    Load all embeddings and associated metadata from FAISS.
    Falls back to .npy if direct reconstruction fails.
    """
    meta = load_metadata()
    if not meta or not FAISS_INDEX_PATH.exists():
        print("[WARN] No FAISS data found.")
        return None, None, None

    idx = faiss.read_index(str(FAISS_INDEX_PATH))
    n, d = idx.ntotal, idx.d

    # Try reconstruct vectors from FAISS (requires direct_map)
    try:
        if getattr(idx, "direct_map", None) is None:
            idx.make_direct_map()
    except Exception:
        pass

    X = np.zeros((n, d), dtype="float32")
    try:
        for i in range(n):
            X[i] = idx.reconstruct(i)
    except RuntimeError as e:
        print(f"[WARN] Could not reconstruct from FAISS index: {e}")
        if EMB_ARRAY_PATH.exists():
            print(f"[INFO] Loading embeddings from {EMB_ARRAY_PATH}")
            X = np.load(EMB_ARRAY_PATH)
        else:
            raise RuntimeError("No embeddings found in FAISS or disk backup.") from e

    # --- Robust label + path loading --- #
    def _label(m):
        return m.get("label") or m.get("animal") or m.get("class") or "unknown"

    def _path(m):
        return m.get("crop_path") or m.get("path") or m.get("output_path") or ""

    y = np.array([_label(m) for m in meta])
    paths = [_path(m) for m in meta]
    return X, y, paths

# ------------------ NumPy IO Utilities ------------------ #
def save_numpy(array, path):
    """Save a numpy array to disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, array)
    print(f"[INFO] Saved numpy array to {path}")

def load_numpy(path):
    """Load a numpy array from disk."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Numpy file not found: {path}")
    return np.load(path)
