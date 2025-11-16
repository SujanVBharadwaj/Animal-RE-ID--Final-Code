# my_utils/thread_utils.py
import os
import cv2
import torch
import numpy as np

def limit_threads():
    # Environment variables to reduce OpenBLAS/MKL thread contention
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    try:
        cv2.setNumThreads(0)
    except Exception:
        pass
    try:
        torch.set_num_threads(1)
    except Exception:
        pass
    # numpy warns -> silence harmless warnings
    np.seterr(all="ignore")
