import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive background backend
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

# Ensure ml package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.config import DATA_DIR, MODELS_DIR, RANDOM_SEED

EVAL_DIR = Path(__file__).resolve().parent / "evaluation"
EVAL_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def plot_confusion_matrices(cm_val, cm_test, out_path: Path):
    """Generates and saves a clean side-by-side confusion matrix plot for Val and Test sets."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=120)
    fig.patch.set_facecolor('#0d1516')

    labels = ['Normal (0)', 'Abnormal (1)']

    for ax, cm, title in zip(axes, [cm_val, cm_test], ['Validation Set', 'Test Set']):
        ax.set_facecolor('#0d1516')
        im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
        ax.set_title(f"Confusion Matrix ({title})", color='#c3f5ff', fontsize=12, fontweight='bold', pad=10)

        tick_marks = np.arange(len(labels))
        ax.set_xticks(tick_marks)
        ax.set_xticklabels(labels, color='#bac9cc', fontsize=10)
        ax.set_yticks(tick_marks)
        ax.set_yticklabels(labels, color='#bac9cc', fontsize=10)

        # Annotate text counts
        thresh = cm.max() / 2.0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                val = cm[i, j]
                color = "white" if val > thresh else "black"
                ax.text(j, i, f"{val}", ha="center", va="center", color=color, fontsize=14, fontweight='bold')

        ax.set_xlabel('Predicted Label', color='#bac9cc', fontsize=10)
        ax.set_ylabel('True Label', color='#bac9cc', fontsize=10)
        ax.tick_params(colors='#849396')
        for spine in ax.spines.values():
            spine.set_color('#3b494c')

    plt.tight_layout()
    plt.savefig(out_path, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)


def main():
    print("=" * 65)
    print("MachineSense ML Phase 3: Baseline Model Training (Random Forest)")
    print("=" * 65)

    # 1. Load Data
    train_csv = DATA_DIR / "train_features.csv"
    val_csv = DATA_DIR / "validation_features.csv"
    test_csv = DATA_DIR / "test_features.csv"

    if not (train_csv.exists() and val_csv.exists() and test_csv.exists()):
        print("ERROR: Feature CSV files missing. Run 'python ml/extract_features.py' first.")
        sys.exit(1)

    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)
    test_df = pd.read_csv(test_csv)

    meta_cols = {"file_path", "machine_id", "label", "label_name"}
    feature_cols = [c for c in train_df.columns if c not in meta_cols]

    print(f" -> Training set size:    {len(train_df)} samples")
    print(f" -> Validation set size:  {len(val_df)} samples")
    print(f" -> Test set size:        {len(test_df)} samples")
    print(f" -> Number of features:   {len(feature_cols)}")
    print()

    # Save exact feature column order
    feature_order_path = MODELS_DIR / "feature_columns.json"
    with open(feature_order_path, "w") as f:
        json.dump(feature_cols, f, indent=2)
    print(f" -> Saved feature column order: {feature_order_path}")

    # Prepare X and y
    X_train = train_df[feature_cols]
    y_train = train_df["label"]

    X_val = val_df[feature_cols]
    y_val = val_df["label"]

    X_test = test_df[feature_cols]
    y_test = test_df["label"]

    # 2. Train Random Forest Baseline Classifier
    print("\nTraining RandomForestClassifier(n_estimators=300, class_weight='balanced', random_state=42)...")
    clf = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    # Save model checkpoint
    model_path = MODELS_DIR / "random_forest_baseline.joblib"
    joblib.dump(clf, model_path)
    print(f" -> Saved trained model to: {model_path}")

    # 3. Evaluate on Validation Set
    y_val_pred = clf.predict(X_val)
    y_val_proba = clf.predict_proba(X_val)[:, 1]

    val_acc = accuracy_score(y_val, y_val_pred)
    val_prec = precision_score(y_val, y_val_pred, zero_division=0)
    val_rec = recall_score(y_val, y_val_pred, zero_division=0)
    val_f1 = f1_score(y_val, y_val_pred, zero_division=0)
    val_auc = roc_auc_score(y_val, y_val_proba)
    cm_val = confusion_matrix(y_val, y_val_pred)
    tn_v, fp_v, fn_v, tp_v = cm_val.ravel()

    # 4. Evaluate on Test Set (One Final Pass)
    y_test_pred = clf.predict(X_test)
    y_test_proba = clf.predict_proba(X_test)[:, 1]

    test_acc = accuracy_score(y_test, y_test_pred)
    test_prec = precision_score(y_test, y_test_pred, zero_division=0)
    test_rec = recall_score(y_test, y_test_pred, zero_division=0)
    test_f1 = f1_score(y_test, y_test_pred, zero_division=0)
    test_auc = roc_auc_score(y_test, y_test_proba)
    cm_test = confusion_matrix(y_test, y_test_pred)
    tn_t, fp_t, fn_t, tp_t = cm_test.ravel()

    # 5. Feature Importances
    importances = clf.feature_importances_
    feat_imp_df = pd.DataFrame({
        "feature": feature_cols,
        "importance": importances
    }).sort_values("importance", ascending=False)

    feat_imp_path = EVAL_DIR / "feature_importance.csv"
    feat_imp_df.to_csv(feat_imp_path, index=False)
    print(f" -> Saved feature importances to: {feat_imp_path}")

    # 6. Save Confusion Matrix Plot
    cm_plot_path = EVAL_DIR / "confusion_matrix.png"
    plot_confusion_matrices(cm_val, cm_test, cm_plot_path)
    print(f" -> Saved confusion matrix plot to: {cm_plot_path}")

    # 7. Save Classification Report Text
    txt_report_path = EVAL_DIR / "classification_report.txt"
    with open(txt_report_path, "w") as f:
        f.write("=== VALIDATION SET CLASSIFICATION REPORT ===\n")
        f.write(classification_report(y_val, y_val_pred, target_names=["normal", "abnormal"]))
        f.write("\n=== TEST SET CLASSIFICATION REPORT ===\n")
        f.write(classification_report(y_test, y_test_pred, target_names=["normal", "abnormal"]))
    print(f" -> Saved classification reports text to: {txt_report_path}")

    # 8. Print Final Executive Report
    print("\n" + "=" * 65)
    print("MODEL: Random Forest Baseline")
    print("=" * 65)
    print("\nTRAIN DATASET:")
    print(f"  Total samples:   {len(train_df)}")
    print(f"  Normal (0):      {(y_train == 0).sum()}")
    print(f"  Abnormal (1):    {(y_train == 1).sum()}")

    print("\nVALIDATION RESULTS:")
    print(f"  Accuracy:        {val_acc:.4f}")
    print(f"  Precision:       {val_prec:.4f}")
    print(f"  Recall (Abnorm): {val_rec:.4f}  <-- Critical Metric")
    print(f"  F1-Score:        {val_f1:.4f}")
    print(f"  ROC-AUC:         {val_auc:.4f}")
    print("  Confusion Breakdown:")
    print(f"    - Normal Correctly Classified (TN):   {tn_v}")
    print(f"    - Normal Incorrectly Classified (FP): {fp_v}")
    print(f"    - Abnormal Correctly Classified (TP): {tp_v}")
    print(f"    - Abnormal Incorrectly Classified (FN):{fn_v}")

    print("\nTEST RESULTS (Single Final Pass):")
    print(f"  Accuracy:        {test_acc:.4f}")
    print(f"  Precision:       {test_prec:.4f}")
    print(f"  Recall (Abnorm): {test_rec:.4f}  <-- Critical Metric")
    print(f"  F1-Score:        {test_f1:.4f}")
    print(f"  ROC-AUC:         {test_auc:.4f}")
    print("  Confusion Breakdown:")
    print(f"    - Normal Correctly Classified (TN):   {tn_t}")
    print(f"    - Normal Incorrectly Classified (FP): {fp_t}")
    print(f"    - Abnormal Correctly Classified (TP): {tp_t}")
    print(f"    - Abnormal Incorrectly Classified (FN):{fn_t}")

    print("\nTOP 15 MOST IMPORTANT FEATURES:")
    top_15 = feat_imp_df.head(15)
    for idx, (_, row) in enumerate(top_15.iterrows(), 1):
        print(f"  {idx:2d}. {row['feature']:25s} -> {row['importance']:.4f}")

    print("\n" + "=" * 65)
    print("Baseline Model Training & Evaluation Complete!")
    print("=" * 65)


if __name__ == "__main__":
    main()
