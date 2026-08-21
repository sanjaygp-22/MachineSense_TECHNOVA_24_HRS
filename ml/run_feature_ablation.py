import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pathlib import Path
from typing import Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

# Ensure ml package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.config import DATA_DIR, RANDOM_SEED

OUT_DIR = Path(__file__).resolve().parent / "evaluation" / "feature_ablation"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_ablation_comparison(comparison_df: pd.DataFrame, out_path: Path):
    """Plots comparative bar chart of Accuracy, Precision, Abnormal Recall, F1, and ROC-AUC across Sets A, B, C."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
    fig.patch.set_facecolor('#0d1516')
    ax.set_facecolor('#0d1516')

    sets = comparison_df["feature_set"].tolist()
    metrics = ["accuracy", "precision", "abnormal_recall", "f1_score", "roc_auc"]
    metric_labels = ["Accuracy", "Precision", "Abnorm Recall", "F1-Score", "ROC-AUC"]

    x = np.arange(len(metrics))
    width = 0.25

    colors = ['#ffb4ab', '#00e5ff', '#36f1cd']

    for idx, s_name in enumerate(sets):
        row = comparison_df[comparison_df["feature_set"] == s_name].iloc[0]
        vals = [row[m] for m in metrics]
        rects = ax.bar(x + idx * width, vals, width, label=s_name, color=colors[idx], alpha=0.85, edgecolor='#c3f5ff')

        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', color='#ffffff', fontsize=8, fontweight='bold')

    ax.set_title("Overall LOMO Cross-Validation Performance by Feature Set", color='#c3f5ff', fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(x + width)
    ax.set_xticklabels(metric_labels, color='#bac9cc', fontsize=10, fontweight='bold')
    ax.set_ylim(0, 1.15)
    ax.tick_params(colors='#849396')
    ax.legend(facecolor='#151d1e', edgecolor='#3b494c', labelcolor='#c3f5ff')
    for spine in ax.spines.values():
        spine.set_color('#3b494c')

    plt.tight_layout()
    plt.savefig(out_path, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)


def run_lomo_for_feature_set(full_df: pd.DataFrame, feature_set_name: str, feature_cols: list) -> Tuple[list, dict]:
    """Runs 4-fold Leave-One-Machine-Out CV for a specific list of features."""
    machine_ids = sorted(full_df["machine_id"].unique())
    fold_results = []

    all_y_true = []
    all_y_pred = []
    all_y_proba = []

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

        all_y_true.extend(y_test.tolist())
        all_y_pred.extend(y_pred.tolist())
        all_y_proba.extend(y_proba.tolist())

        fold_results.append({
            "feature_set": feature_set_name,
            "held_out_machine": m_id,
            "num_features": len(feature_cols),
            "test_samples": len(test_fold),
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

    # Aggregated metrics across all folds
    overall_acc = accuracy_score(all_y_true, all_y_pred)
    overall_prec = precision_score(all_y_true, all_y_pred, zero_division=0)
    overall_rec = recall_score(all_y_true, all_y_pred, zero_division=0)
    overall_f1 = f1_score(all_y_true, all_y_pred, zero_division=0)
    overall_auc = roc_auc_score(all_y_true, all_y_proba)
    cm_overall = confusion_matrix(all_y_true, all_y_pred)
    tn_o, fp_o, fn_o, tp_o = cm_overall.ravel()

    overall_dict = {
        "feature_set": feature_set_name,
        "held_out_machine": "OVERALL_ALL_FOLDS",
        "num_features": len(feature_cols),
        "test_samples": len(full_df),
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

    return fold_results, overall_dict


def main():
    print("=" * 75)
    print("MachineSense ML: Feature Ablation Experiment (LOMO Cross-Validation)")
    print("=" * 75)

    # 1. Load Combined Data
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
    all_features = [c for c in full_df.columns if c not in meta_cols]

    # 2. Define Feature Sets A, B, and C
    removed_spectral = {
        "zero_crossing_rate",
        "spectral_centroid_hz",
        "spectral_rolloff_hz",
        "spectral_bandwidth_hz",
        "spectral_flatness"
    }

    # Set A: All 33 Features
    set_a_features = list(all_features)

    # Set B: Reduced Spectral Features (Remove 5 top machine-varying spectral features)
    set_b_features = [f for f in all_features if f not in removed_spectral]

    # Set C: Compact Features (13 MFCC means, 13 MFCC stds, RMS, dominant_frequency_hz)
    compact_allowed = {f"mfcc_{i}_mean" for i in range(1, 14)} | \
                      {f"mfcc_{i}_std" for i in range(1, 14)} | \
                      {"rms", "dominant_frequency_hz"}
    set_c_features = [f for f in all_features if f in compact_allowed]

    feature_sets = {
        "Set A: ALL FEATURES": set_a_features,
        "Set B: REDUCED SPECTRAL": set_b_features,
        "Set C: COMPACT FEATURES": set_c_features
    }

    print(f" -> Total Recordings: {len(full_df)}")
    print(f" -> Set A (All Features):            {len(set_a_features)} features")
    print(f" -> Set B (Reduced Spectral):        {len(set_b_features)} features (removed 5 spectral features)")
    print(f" -> Set C (Compact Features):        {len(set_c_features)} features (26 MFCCs + RMS + Dominant Freq)")
    print()

    all_fold_rows = []
    overall_comparison_rows = []

    # 3. Execute LOMO for each feature set
    for s_name, f_cols in feature_sets.items():
        print(f"Evaluating LOMO CV for '{s_name}' ({len(f_cols)} features)...")
        folds, overall = run_lomo_for_feature_set(full_df, s_name, f_cols)
        all_fold_rows.extend(folds)
        all_fold_rows.append(overall)
        overall_comparison_rows.append(overall)

    # 4. Save CSV Output
    results_df = pd.DataFrame(all_fold_rows)
    results_csv_path = OUT_DIR / "results.csv"
    results_df.to_csv(results_csv_path, index=False)
    print(f"\n -> Saved feature ablation results CSV: {results_csv_path}")

    # 5. Generate Comparison Plot
    comp_df = pd.DataFrame(overall_comparison_rows)
    plot_path = OUT_DIR / "ablation_comparison_plot.png"
    plot_ablation_comparison(comp_df, plot_path)
    print(f" -> Saved comparison bar chart plot:  {plot_path}")

    # 6. Save Comparison Text Report
    txt_path = OUT_DIR / "comparison.txt"
    with open(txt_path, "w") as f:
        f.write("=== FEATURE ABLATION EXPERIMENT COMPARISON SUMMARY ===\n\n")
        f.write(f"{'Feature Set':<25} | {'Feats':<5} | {'Accuracy':<9} | {'Precision':<9} | {'Abnorm Recall':<13} | {'F1-Score':<9} | {'ROC-AUC':<8}\n")
        f.write("-" * 90 + "\n")
        for r in overall_comparison_rows:
            f.write(f"{r['feature_set']:<25} | {r['num_features']:<5d} | {r['accuracy']:<9.4f} | {r['precision']:<9.4f} | {r['abnormal_recall']:<13.4f} | {r['f1_score']:<9.4f} | {r['roc_auc']:<8.4f}\n")

    # 7. Print Executive Summary Report
    print("\n" + "=" * 75)
    print("FEATURE ABLATION EXPERIMENT SUMMARY RESULTS")
    print("=" * 75)
    print(f"{'Feature Set':<25} | {'Feats':<5} | {'Accuracy':<9} | {'Precision':<9} | {'Abnorm Recall':<13} | {'F1-Score':<9} | {'ROC-AUC':<8}")
    print("-" * 75)

    for r in overall_comparison_rows:
        print(f"{r['feature_set']:<25} | {r['num_features']:<5d} | {r['accuracy']:<9.4f} | {r['precision']:<9.4f} | {r['abnormal_recall']:<13.4f} | {r['f1_score']:<9.4f} | {r['roc_auc']:<8.4f}")

    print("=" * 75)

    # Identify best feature set for Abnormal Recall & F1
    best_recall_set = max(overall_comparison_rows, key=lambda x: x["abnormal_recall"])
    best_f1_set = max(overall_comparison_rows, key=lambda x: x["f1_score"])

    print("\nCONCLUSION:")
    print(f" -> Best Feature Set for Unseen-Machine Abnormal Recall: '{best_recall_set['feature_set']}' ({best_recall_set['abnormal_recall']*100:.2f}% Recall)")
    print(f" -> Best Feature Set for Unseen-Machine F1-Score:        '{best_f1_set['feature_set']}' ({best_f1_set['f1_score']:.4f} F1)")
    print()
    set_a_rec = comp_df[comp_df['feature_set'] == 'Set A: ALL FEATURES'].iloc[0]['abnormal_recall']
    if best_recall_set['abnormal_recall'] > set_a_rec:
        diff = (best_recall_set['abnormal_recall'] - set_a_rec) * 100
        print(f" -> Removing machine-dependent spectral features IMPROVED unseen-machine abnormal recall by +{diff:.2f}%!")
    else:
        print(" -> Feature ablation results evaluated.")

    print("=" * 75)


if __name__ == "__main__":
    main()
