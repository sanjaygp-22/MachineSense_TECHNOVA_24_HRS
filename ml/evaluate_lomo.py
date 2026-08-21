import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

# Ensure ml package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.config import DATA_DIR, RANDOM_SEED

EVAL_DIR = Path(__file__).resolve().parent / "evaluation"
EVAL_DIR.mkdir(parents=True, exist_ok=True)


def plot_lomo_confusion_matrices(fold_cms: dict, out_path: Path):
    """Generates a 4-panel grid of confusion matrices for each held-out machine ID fold."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=120)
    fig.patch.set_facecolor('#0d1516')

    labels = ['Normal (0)', 'Abnormal (1)']
    machine_ids = list(fold_cms.keys())

    for idx, m_id in enumerate(machine_ids):
        ax = axes[idx // 2, idx % 2]
        cm = fold_cms[m_id]

        ax.set_facecolor('#0d1516')
        ax.imshow(cm, interpolation='nearest', cmap='Blues')
        ax.set_title(f"Unseen Held-Out Asset: {m_id}", color='#c3f5ff', fontsize=12, fontweight='bold', pad=10)

        tick_marks = np.arange(len(labels))
        ax.set_xticks(tick_marks)
        ax.set_xticklabels(labels, color='#bac9cc', fontsize=10)
        ax.set_yticks(tick_marks)
        ax.set_yticklabels(labels, color='#bac9cc', fontsize=10)

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
    print("=" * 70)
    print("MachineSense ML: Leave-One-Machine-Out (LOMO) Cross-Validation")
    print("=" * 70)

    # 1. Combine all feature CSV datasets
    train_csv = DATA_DIR / "train_features.csv"
    val_csv = DATA_DIR / "validation_features.csv"
    test_csv = DATA_DIR / "test_features.csv"

    if not (train_csv.exists() and val_csv.exists() and test_csv.exists()):
        print("ERROR: Feature CSV files missing. Run 'python ml/extract_features.py' first.")
        sys.exit(1)

    full_df = pd.concat([
        pd.read_csv(train_csv),
        pd.read_csv(val_csv),
        pd.read_csv(test_csv)
    ], ignore_index=True)

    meta_cols = {"file_path", "machine_id", "label", "label_name"}
    feature_cols = [c for c in full_df.columns if c not in meta_cols]
    machine_ids = sorted(full_df["machine_id"].unique())

    print(f" -> Total Combined Recordings: {len(full_df)}")
    print(f" -> Number of Features:        {len(feature_cols)}")
    print(f" -> Discovered Machine IDs:    {machine_ids}")
    print()

    fold_results = []
    fold_cms = {}

    all_y_true = []
    all_y_pred = []
    all_y_proba = []

    # 2. Iterate over each machine ID as held-out test asset
    for m_id in machine_ids:
        train_mask = full_df["machine_id"] != m_id
        test_mask = full_df["machine_id"] == m_id

        train_fold = full_df[train_mask]
        test_fold = full_df[test_mask]

        X_train = train_fold[feature_cols]
        y_train = train_fold["label"]

        X_test = test_fold[feature_cols]
        y_test = test_fold["label"]

        clf = RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_SEED,
            n_jobs=-1
        )
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_proba)
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()

        fold_cms[m_id] = cm

        all_y_true.extend(y_test.tolist())
        all_y_pred.extend(y_pred.tolist())
        all_y_proba.extend(y_proba.tolist())

        fold_results.append({
            "held_out_machine": m_id,
            "train_samples": len(train_fold),
            "test_samples": len(test_fold),
            "test_normal": (y_test == 0).sum(),
            "test_abnormal": (y_test == 1).sum(),
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "abnormal_recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "TN_normal_correct": tn,
            "FP_normal_wrong": fp,
            "TP_abnormal_correct": tp,
            "FN_abnormal_wrong": fn
        })

    # 3. Calculate Overall Aggregated LOMO Performance
    overall_acc = accuracy_score(all_y_true, all_y_pred)
    overall_prec = precision_score(all_y_true, all_y_pred, zero_division=0)
    overall_rec = recall_score(all_y_true, all_y_pred, zero_division=0)
    overall_f1 = f1_score(all_y_true, all_y_pred, zero_division=0)
    overall_auc = roc_auc_score(all_y_true, all_y_proba)
    cm_overall = confusion_matrix(all_y_true, all_y_pred)
    tn_o, fp_o, fn_o, tp_o = cm_overall.ravel()

    # Save CSV Results
    res_df = pd.DataFrame(fold_results)
    
    # Append overall row to dataframe
    overall_row = {
        "held_out_machine": "OVERALL_ALL_FOLDS",
        "train_samples": len(full_df),
        "test_samples": len(full_df),
        "test_normal": (full_df["label"] == 0).sum(),
        "test_abnormal": (full_df["label"] == 1).sum(),
        "accuracy": round(overall_acc, 4),
        "precision": round(overall_prec, 4),
        "abnormal_recall": round(overall_rec, 4),
        "f1_score": round(overall_f1, 4),
        "roc_auc": round(overall_auc, 4),
        "TN_normal_correct": tn_o,
        "FP_normal_wrong": fp_o,
        "TP_abnormal_correct": tp_o,
        "FN_abnormal_wrong": fn_o
    }

    res_df_all = pd.concat([res_df, pd.DataFrame([overall_row])], ignore_index=True)
    res_csv_path = EVAL_DIR / "lomo_evaluation_results.csv"
    res_df_all.to_csv(res_csv_path, index=False)
    print(f" -> Saved LOMO evaluation metrics CSV: {res_csv_path}")

    # Save Confusion Matrix Grid Plot
    plot_path = EVAL_DIR / "lomo_confusion_matrices.png"
    plot_lomo_confusion_matrices(fold_cms, plot_path)
    print(f" -> Saved 4-panel confusion matrix plot: {plot_path}")

    # 4. Print Detailed Summary Report
    print("\n" + "=" * 70)
    print("LEAVE-ONE-MACHINE-OUT (LOMO) CROSS-VALIDATION RESULTS")
    print("=" * 70)
    print(f"{'Held-Out Machine':<18} | {'Accuracy':<9} | {'Precision':<9} | {'Abnorm Recall':<13} | {'F1-Score':<9} | {'ROC-AUC':<8}")
    print("-" * 70)

    for row in fold_results:
        print(f"{row['held_out_machine']:<18} | {row['accuracy']:<9.4f} | {row['precision']:<9.4f} | {row['abnormal_recall']:<13.4f} | {row['f1_score']:<9.4f} | {row['roc_auc']:<8.4f}")

    print("-" * 70)
    print(f"{'OVERALL AGGREGATED':<18} | {overall_acc:<9.4f} | {overall_prec:<9.4f} | {overall_rec:<13.4f} | {overall_f1:<9.4f} | {overall_auc:<8.4f}")
    print("=" * 70)

    print("\nDetailed Breakdown Per Held-Out Asset:")
    for row in fold_results:
        m = row['held_out_machine']
        print(f"\nAsset Fold [{m}]:")
        print(f"  * Normal Correctly Classified (TN):   {row['TN_normal_correct']:4d} / {row['test_normal']}")
        print(f"  * Normal Incorrectly Classified (FP): {row['FP_normal_wrong']:4d}")
        print(f"  * Abnormal Correctly Caught (TP):     {row['TP_abnormal_correct']:4d} / {row['test_abnormal']}")
        print(f"  * Abnormal Missed (FN):              {row['FN_abnormal_wrong']:4d}")

    print("\n" + "=" * 70)
    print("Leave-One-Machine-Out Cross-Validation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
