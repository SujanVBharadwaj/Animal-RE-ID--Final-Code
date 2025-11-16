# 🐅 Animal Re-Identification System (Tiger & Deer)

This repository implements a complete **Animal Re-Identification (ReID)** system for **Tiger** and **Deer**, integrating:

- **YOLOv11** (Ultralytics) — Fast object detection  
- **MegaDetector v5a.0.0** — Wildlife-focused detection  
- **Deep CNN feature extraction (ResNet)**  
- **Pattern feature extraction (LBP + Color Histogram)**  
- **Combined feature embedding**  
- **FAISS similarity search**  
- **SVM classifier for ReID**  
- **Incremental learning (auto-add new animals)**  
- **Top-1 best match retrieval with visualization**

The system automatically detects animals, extracts deep + pattern features, stores them in a FAISS index, and retrieves the best match in real-time.

---

# 📌 **Why Two Detectors? (YOLOv11 + MegaDetector)**

This project supports **dual detector mode**:

### 🧠 **1. MegaDetector v5a.0.0 (Microsoft AI4Earth)**
- Specialized for wildlife detection  
- More robust in forest/camera-trap environments  
- Detects broad categories: `"animal"`, `"human"`, `"vehicle"`

### ⚡ **2. YOLOv11 (Ultralytics)**
- Very fast  
- Detects more specific species (tiger/deer) from training data  
- Used when MegaDetector is unavailable or disabled  

The pipeline attempts:

1. **Load MegaDetector → use if available**  
2. **Else fallback to YOLOv11**  

Both models are fully integrated into the detection process.

---

# 🚀 **System Pipeline**

<img width="1144" height="495" alt="image" src="https://github.com/user-attachments/assets/2bbf71a0-2898-43f8-bc5d-8789f944d0f2" />

