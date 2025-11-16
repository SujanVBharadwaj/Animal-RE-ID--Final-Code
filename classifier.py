# classifier.py — Fixed and Robust SVM Integration
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import f1_score, classification_report
from sklearn.utils.class_weight import compute_class_weight
from my_utils.db_utils import save_model
from my_utils.config import CLASSIFIER_PATH, METRICS_DIR
import json
from pathlib import Path

def train_and_select(X, y):
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Compute class weights to balance underrepresented animals
    classes = np.unique(y_train)
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
    class_weight_dict = {cls: w for cls, w in zip(classes, weights)}

    # ----------------------------------------------------
    # Train Random Forest
    # ----------------------------------------------------
    rf = RandomForestClassifier(
        n_estimators=250,
        max_depth=None,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    preds_rf = rf.predict(X_val)
    f1_rf = f1_score(y_val, preds_rf, average="macro", zero_division=1)

    # ----------------------------------------------------
    # Train Balanced SVM with tuned C and gamma
    # ----------------------------------------------------
    svm_params = {
        "C": [0.5, 1, 2],
        "gamma": ["scale", "auto"],
        "kernel": ["rbf"]
    }
    svm = GridSearchCV(
        SVC(probability=True, class_weight=class_weight_dict, random_state=42),
        param_grid=svm_params,
        scoring="f1_macro",
        cv=3,
        n_jobs=-1
    )
    svm.fit(X_train, y_train)
    preds_svm = svm.predict(X_val)
    f1_svm = f1_score(y_val, preds_svm, average="macro", zero_division=1)

    print("\n[INFO] --- Classifier Performance ---")
    print(f"RandomForest f1: {f1_rf:.3f}")
    print(f"SVM f1: {f1_svm:.3f}")
    print(f"SVM Best Params: {svm.best_params_}")
    print(classification_report(y_val, preds_svm))

    # ----------------------------------------------------
    # Choose Best Model
    # ----------------------------------------------------
    if f1_svm >= f1_rf:
        best_model = svm.best_estimator_
        summary = {"chosen": "SVM", "RandomForest_f1": float(f1_rf), "SVM_f1": float(f1_svm)}
    else:
        best_model = rf
        summary = {"chosen": "RandomForest", "RandomForest_f1": float(f1_rf), "SVM_f1": float(f1_svm)}

    save_model(best_model, CLASSIFIER_PATH)

    # Save metrics
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = METRICS_DIR / "classifier_metrics.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[INFO] Best Model: {summary['chosen']} saved → {CLASSIFIER_PATH}")
    return best_model, summary
