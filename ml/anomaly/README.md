# MachineSense - Normal-Only Mel-Spectrogram Autoencoder Anomaly Detection

Phase 5 of the MachineSense ML pipeline evaluates an unsupervised Normal-Only Convolutional Autoencoder (`MelSpectrogramAutoencoder`) on Log-Mel Spectrograms trained strictly on normal operational recordings (`label == 0`) under 4-fold Leave-One-Machine-Out (LOMO) cross-validation on the `NVIDIA GeForce RTX 4050 Laptop GPU`.

---

## 1. Directory Structure

```
ml/anomaly/
├── models/
│   ├── autoencoder_best.pth
│   ├── autoencoder_id_00.pth
│   ├── autoencoder_id_02.pth
│   ├── autoencoder_id_04.pth
│   └── autoencoder_id_06.pth
├── evaluation/
│   ├── results.csv
│   ├── reconstruction_errors.csv
│   └── summary_report.txt
├── plots/
│   ├── confusion_matrices.png
│   ├── roc_curves.png
│   └── error_distributions.png
└── README.md
```

---

## 2. Unsupervised Anomaly Detection Architecture

- **Training Protocol**: Trained **ONLY** on normal acoustic recordings (`label == 0`) from 3 training machines per fold.
- **Strict Unseen Validation Threshold**: Anomaly threshold selected at the **95th percentile** of normal validation reconstruction errors from training machines. Zero held-out test data leakage.
- **Inference Anomaly Score**: MSE(X_mel, X_recon).
- **Total Model Parameters**: 185,857
- **Training Time**: 929.78s

---

## 3. LOMO Cross-Validation Performance

| Held-Out Machine | 95% Val Threshold | Accuracy | Precision | Abnormal Recall | F1-Score | ROC-AUC | Normal MSE (Mean/Med) | Abnormal MSE (Mean/Med) |
|---|---|---|---|---|---|---|---|---|
| **`id_00`** | 0.175691 | 0.8407 | 0.0833 | 0.0280 | 0.0419 | 0.2925 | 0.1355 / 0.1313 | 0.1144 / 0.1126 |
| **`id_02`** | 0.175495 | 0.9158 | 0.7931 | 0.2072 | 0.3286 | 0.4799 | 0.1174 / 0.1147 | 0.1307 / 0.1104 |
| **`id_04`** | 0.152743 | 0.1297 | 0.1013 | 0.7600 | 0.1788 | 0.2885 | 0.2013 / 0.1990 | 0.1790 / 0.1740 |
| **`id_06`** | 0.172737 | 0.9095 | 0.0000 | 0.0000 | 0.0000 | 0.5989 | 0.0608 / 0.0586 | 0.0703 / 0.0618 |
| **OVERALL AGGREGATED** | - | **0.7436** | **0.1244** | **0.2259** | **0.1604** | **0.4939** | **0.1223 / 0.1170** | **0.1227 / 0.1121** |

---

## 4. Benchmark Comparison Across ML Approaches (LOMO CV)

| Model Architecture | Training Strategy | Overall Accuracy | Precision | Abnormal Recall | F1-Score | ROC-AUC |
|---|---|---|---|---|---|---|
| **Random Forest Baseline** | Supervised (33 Handcrafted Feats) | **0.7253** | **0.1899** | 0.4693 | **0.2704** | **0.6443** |
| **Supervised 2D CNN** | Supervised (Mel Spectrograms) | 0.3282 | 0.1334 | **0.9452** | 0.2338 | 0.5445 |
| **Normal-Only Autoencoder** | Unsupervised Reconstruction (Mel-Spectrograms) | **0.7436** | **0.1244** | **0.2259** | **0.1604** | **0.4939** |