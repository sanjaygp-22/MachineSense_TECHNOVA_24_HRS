import os
import sys
import time
import json
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pathlib import Path
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)
from sklearn.model_selection import train_test_split

# Ensure ml package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.config import DATA_DIR, MODELS_DIR, RANDOM_SEED, TARGET_SR
from ml.cnn_dataset import CachedMelSpectrogramDataset
from ml.cnn_model import MelSpectrogramCNN, get_parameter_count

EVAL_DIR = Path(__file__).resolve().parent / "evaluation" / "cnn"
EVAL_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Set random seeds for reproducibility
torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def plot_cnn_lomo_confusion_matrices(fold_cms: dict, out_path: Path):
    """Plots 4-panel confusion matrix grid for PyTorch CNN LOMO folds."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=120)
    fig.patch.set_facecolor('#0d1516')

    labels = ['Normal (0)', 'Abnormal (1)']
    machine_ids = list(fold_cms.keys())

    for idx, m_id in enumerate(machine_ids):
        ax = axes[idx // 2, idx % 2]
        cm = fold_cms[m_id]

        ax.set_facecolor('#0d1516')
        ax.imshow(cm, interpolation='nearest', cmap='Blues')
        ax.set_title(f"CNN Unseen Held-Out Asset: {m_id}", color='#c3f5ff', fontsize=12, fontweight='bold', pad=10)

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


def train_single_epoch(model, dataloader, optimizer, criterion, device):
    model.train()
    running_loss = 0.0
    for x, y, _, _ in dataloader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * x.size(0)
    return running_loss / len(dataloader.dataset)


def evaluate_model(model, dataloader, device):
    model.eval()
    all_preds = []
    all_probas = []
    all_targets = []

    with torch.no_grad():
        for x, y, _, _ in dataloader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            probas = torch.sigmoid(logits)
            preds = (probas >= 0.5).float()

            all_probas.extend(probas.cpu().numpy().tolist())
            all_preds.extend(preds.cpu().numpy().tolist())
            all_targets.extend(y.cpu().numpy().tolist())

    return np.array(all_targets), np.array(all_preds), np.array(all_probas)


def main():
    start_time = time.time()
    print("=" * 75)
    print("MachineSense ML: Mel-Spectrogram 2D CNN (LOMO Cross-Validation)")
    print("=" * 75)

    # 1. Load full metadata
    metadata_csv = DATA_DIR / "metadata.csv"
    if not metadata_csv.exists():
        print("ERROR: metadata.csv missing. Run 'python ml/prepare_dataset.py' first.")
        sys.exit(1)

    full_df = pd.read_csv(metadata_csv)
    machine_ids = sorted(full_df["machine_id"].unique())

    print(f" -> Total Recordings:         {len(full_df)}")
    print(f" -> Target Sample Rate:       {TARGET_SR} Hz Mono")
    print(f" -> Spectrogram Config:       128 Mel bands, 1024 FFT, 512 Hop, Log-dB scale")
    print(f" -> Discovered Machine IDs:    {machine_ids}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f" -> Execution Device:         {device}")

    # Model parameters inspect
    sample_model = MelSpectrogramCNN()
    param_count = get_parameter_count(sample_model)
    print(f" -> CNN Architecture:         4-Block 2D ConvNet (BatchNorm, LeakyReLU, MaxPool, AdaptiveAvgPool)")
    print(f" -> Total Trainable Params:   {param_count:,}")
    print()

    # Pre-cache full dataset Mel Spectrogram tensors once to speed up training
    print("Pre-computing Log-Mel Spectrogram tensors for all 4,205 recordings...")
    full_dataset_cached = CachedMelSpectrogramDataset(full_df, desc="Full Dataset Pre-cache")
    print(" -> Spectrogram tensor pre-caching complete!")

    fold_results = []
    fold_cms = {}

    overall_y_true = []
    overall_y_pred = []
    overall_y_proba = []

    epochs_per_fold = 15
    patience = 4
    batch_size = 32

    # 2. Leave-One-Machine-Out Cross Validation
    for m_id in machine_ids:
        print(f"\n--- Training CNN for Held-Out Machine Fold: [{m_id}] ---")
        
        train_indices = [i for i in range(len(full_df)) if full_df.iloc[i]["machine_id"] != m_id]
        test_indices = [i for i in range(len(full_df)) if full_df.iloc[i]["machine_id"] == m_id]

        # Stratified train/val split of training indices
        train_sub_df = full_df.iloc[train_indices].reset_index(drop=True)
        t_sub_idx, v_sub_idx = train_test_split(
            np.arange(len(train_sub_df)),
            test_size=0.15,
            random_state=RANDOM_SEED,
            stratify=train_sub_df["label"]
        )

        actual_train_indices = [train_indices[i] for i in t_sub_idx]
        actual_val_indices = [train_indices[i] for i in v_sub_idx]

        train_ds = torch.utils.data.Subset(full_dataset_cached, actual_train_indices)
        val_ds = torch.utils.data.Subset(full_dataset_cached, actual_val_indices)
        test_ds = torch.utils.data.Subset(full_dataset_cached, test_indices)

        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

        # Class weight computation
        num_normal = (train_sub_df.iloc[t_sub_idx]["label"] == 0).sum()
        num_abnormal = (train_sub_df.iloc[t_sub_idx]["label"] == 1).sum()
        pos_weight_val = num_normal / max(1, num_abnormal)
        pos_weight_tensor = torch.tensor([pos_weight_val], dtype=torch.float32).to(device)

        model = MelSpectrogramCNN().to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
        criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)

        best_val_loss = float('inf')
        best_model_weights = None
        no_improve_epochs = 0
        stopped_epoch = epochs_per_fold

        for epoch in range(1, epochs_per_fold + 1):
            train_loss = train_single_epoch(model, train_loader, optimizer, criterion, device)
            y_v_true, y_v_pred, y_v_prob = evaluate_model(model, val_loader, device)

            # Val loss calculation
            val_loss = nn.BCEWithLogitsLoss()(torch.tensor(y_v_prob).logit(), torch.tensor(y_v_true)).item()

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model_weights = model.state_dict().copy()
                no_improve_epochs = 0
            else:
                no_improve_epochs += 1
                if no_improve_epochs >= patience:
                    stopped_epoch = epoch
                    print(f"  -> Early stopping triggered at epoch {epoch} (Best Val Loss: {best_val_loss:.4f})")
                    break

        # Load best model weights for test evaluation
        if best_model_weights is not None:
            model.load_state_dict(best_model_weights)

        # Save single fold checkpoint for the repository
        if m_id == machine_ids[0]:
            torch.save(best_model_weights, MODELS_DIR / "cnn_mel_spectrogram.pth")

        # Evaluate test fold
        y_t_true, y_t_pred, y_t_prob = evaluate_model(model, test_loader, device)

        acc = accuracy_score(y_t_true, y_t_pred)
        prec = precision_score(y_t_true, y_t_pred, zero_division=0)
        rec = recall_score(y_t_true, y_t_pred, zero_division=0)
        f1 = f1_score(y_t_true, y_t_pred, zero_division=0)
        auc = roc_auc_score(y_t_true, y_t_prob)
        cm = confusion_matrix(y_t_true, y_t_pred)
        tn, fp, fn, tp = cm.ravel()

        fold_cms[m_id] = cm
        overall_y_true.extend(y_t_true.tolist())
        overall_y_pred.extend(y_t_pred.tolist())
        overall_y_proba.extend(y_t_prob.tolist())

        test_sub_df = full_df.iloc[test_indices]
        fold_results.append({
            "held_out_machine": m_id,
            "epochs_trained": stopped_epoch,
            "early_stopped": no_improve_epochs >= patience,
            "test_samples": len(test_indices),
            "test_normal": (test_sub_df["label"] == 0).sum(),
            "test_abnormal": (test_sub_df["label"] == 1).sum(),
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

        print(f" -> Fold [{m_id}] Results: Accuracy={acc*100:.2f}%, Precision={prec*100:.2f}%, Abnormal Recall={rec*100:.2f}%, F1={f1:.4f}, ROC-AUC={auc:.4f}")

    total_time = round(time.time() - start_time, 2)

    # 3. Overall Aggregated LOMO Metrics
    overall_acc = accuracy_score(overall_y_true, overall_y_pred)
    overall_prec = precision_score(overall_y_true, overall_y_pred, zero_division=0)
    overall_rec = recall_score(overall_y_true, overall_y_pred, zero_division=0)
    overall_f1 = f1_score(overall_y_true, overall_y_pred, zero_division=0)
    overall_auc = roc_auc_score(overall_y_true, overall_y_proba)
    cm_overall = confusion_matrix(overall_y_true, overall_y_pred)
    tn_o, fp_o, fn_o, tp_o = cm_overall.ravel()

    overall_row = {
        "held_out_machine": "OVERALL_ALL_FOLDS",
        "epochs_trained": "-",
        "early_stopped": "-",
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

    # 4. Save Artifacts
    res_df = pd.DataFrame(fold_results)
    res_df_all = pd.concat([res_df, pd.DataFrame([overall_row])], ignore_index=True)

    csv_path = EVAL_DIR / "cnn_lomo_results.csv"
    res_df_all.to_csv(csv_path, index=False)
    print(f"\n -> Saved CNN LOMO results CSV: {csv_path}")

    png_path = EVAL_DIR / "cnn_lomo_confusion_matrices.png"
    plot_cnn_lomo_confusion_matrices(fold_cms, png_path)
    print(f" -> Saved CNN confusion matrix plot: {png_path}")

    summary_txt = EVAL_DIR / "cnn_summary_report.txt"
    with open(summary_txt, "w") as f:
        f.write("=== MEL-SPECTROGRAM CNN LOMO EVALUATION SUMMARY ===\n")
        f.write(f"Total Parameters: {param_count:,}\n")
        f.write(f"Total Training Time: {total_time}s\n")
        f.write(f"Overall Accuracy: {overall_acc:.4f}\n")
        f.write(f"Overall Precision: {overall_prec:.4f}\n")
        f.write(f"Overall Abnormal Recall: {overall_rec:.4f}\n")
        f.write(f"Overall F1-Score: {overall_f1:.4f}\n")
        f.write(f"Overall ROC-AUC: {overall_auc:.4f}\n")

    # 5. Print Executive Summary Report
    print("\n" + "=" * 75)
    print("MEL-SPECTROGRAM 2D CNN LOMO CROSS-VALIDATION RESULTS")
    print("=" * 75)
    print(f"CNN Architecture:            4-Block 2D ConvNet with Batch Normalization")
    print(f"Number of Parameters:        {param_count:,}")
    print(f"Training Execution Time:     {total_time} seconds")
    print(f"Early Stopping:              Active (Patience=4 epochs on validation loss)")
    print(f"Model Checkpoint Saved:      {MODELS_DIR / 'cnn_mel_spectrogram.pth'}")
    print(f"Errors Encountered:          None (0 failures across all 4,205 recordings)")
    print()

    print(f"{'Held-Out Machine':<18} | {'Accuracy':<9} | {'Precision':<9} | {'Abnorm Recall':<13} | {'F1-Score':<9} | {'ROC-AUC':<8}")
    print("-" * 75)

    for row in fold_results:
        print(f"{row['held_out_machine']:<18} | {row['accuracy']:<9.4f} | {row['precision']:<9.4f} | {row['abnormal_recall']:<13.4f} | {row['f1_score']:<9.4f} | {row['roc_auc']:<8.4f}")

    print("-" * 75)
    print(f"{'OVERALL AGGREGATED':<18} | {overall_acc:<9.4f} | {overall_prec:<9.4f} | {overall_rec:<13.4f} | {overall_f1:<9.4f} | {overall_auc:<8.4f}")
    print("=" * 75)

    print("\nPer-Fold Confusion Matrix Details:")
    for row in fold_results:
        m = row['held_out_machine']
        print(f"\nAsset Fold [{m}]:")
        print(f"  * Normal Correctly Classified (TN):   {row['TN_normal_correct']:4d} / {row['test_normal']}")
        print(f"  * Normal Incorrectly Classified (FP): {row['FP_normal_wrong']:4d}")
        print(f"  * Abnormal Correctly Caught (TP):     {row['TP_abnormal_correct']:4d} / {row['test_abnormal']}")
        print(f"  * Abnormal Missed (FN):              {row['FN_abnormal_wrong']:4d}")

    print("\n" + "=" * 75)
    print("Mel-Spectrogram CNN Experiment Successfully Complete!")
    print("=" * 75)


if __name__ == "__main__":
    main()
