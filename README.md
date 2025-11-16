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

# 🚀 **Output Screenshots**

<img width="1318" height="242" alt="Screenshot 2025-11-16 120642" src="https://github.com/user-attachments/assets/a295d6f1-f6ee-41d1-a76f-49aa1ca0c129" />

<img width="1213" height="343" alt="Screenshot 2025-11-16 120651" src="https://github.com/user-attachments/assets/75546de1-928d-47f3-8fa0-633ca875c407" />

<img width="1022" height="721" alt="Screenshot 2025-11-16 124205" src="https://github.com/user-attachments/assets/ccd64c45-bba6-4d6b-bae7-c150d2b91a2a" />

<img width="1032" height="428" alt="Screenshot 2025-11-16 124214" src="https://github.com/user-attachments/assets/e869e3e6-a720-4134-ba3a-c815155e4e46" />



