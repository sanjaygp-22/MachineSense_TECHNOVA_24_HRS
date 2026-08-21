# MachineSense - Machine Learning Dataset Pipeline

Phase 6 of the MachineSense ML pipeline evaluates Machine Normalization & Domain-Invariant Feature Selection under Leave-One-Machine-Out (LOMO) cross-validation on the real MIMII pump audio dataset (`D:\pump`).

---

## 1. Directory Architecture

```
ml/
├── config.py                 # Paths, sample rate (16kHz), random seed=42, label maps
├── dataset.py                # Dataset discovery & corruption audit engine
├── preprocessing.py          # Mono loading, 16kHz resampling, peak normalization
├── features.py               # Feature extraction (33 features: 26 MFCCs + 7 acoustic metrics)
├── prepare_dataset.py        # Master dataset discovery & split script
├── extract_features.py       # Master feature table extraction script
├── train_baseline.py         # Master baseline model training & evaluation script
├── evaluate_lomo.py          # Master Leave-One-Machine-Out Cross-Validation script
├── analyze_machine_dependence.py # Master Machine-ID dependence analysis script
├── run_feature_ablation.py    # Master Feature Ablation Experiment script
├── cnn_dataset.py             # Memory-efficient PyTorch Dataset for Log-Mel Spectrograms
├── cnn_model.py               # PyTorch 2D MelSpectrogramCNN architecture definition
├── train_cnn_gpu.py           # Master GPU-accelerated CNN training script
├── autoencoder_model.py       # PyTorch Conv2D Autoencoder architecture
├── train_autoencoder.py       # Master GPU-accelerated Autoencoder training script
├── run_machine_normalization.py # [NEW] Master Machine Normalization script
├── requirements.txt          # Dependencies
├── machine_normalization/     # [NEW] Saved machine normalization outputs
│   ├── results.csv
│   ├── comparison_table.csv
│   ├── summary_report.txt
│   ├── normalization_comparison_plot.png
│   └── README.md
└── anomaly/
```

---

## 2. Running Machine Normalization Experiment

To execute the domain-invariance and scaled LOMO experiment across Subsets A, B, C, and D:

```bash
& "D:\MachineSense\backend\.venv\Scripts\python.exe" "ml/run_machine_normalization.py"
```

---

## 3. Comparative Benchmark Performance (LOMO Cross-Validation)

| Model / Feature Subset | Features | Accuracy | Precision | Abnormal Recall | F1-Score | ROC-AUC |
|---|---|---|---|---|---|---|
| **Random Forest Baseline (Unscaled)** | 33 | 0.7253 | 0.1899 | 0.4693 | 0.2704 | 0.6443 |
| **Supervised 2D CNN** | Image | 0.3282 | 0.1334 | 0.9452 | 0.2338 | 0.5445 |
| **Normal-Only Autoencoder** | Image | 0.7436 | 0.1244 | 0.2259 | 0.1604 | 0.4939 |
| **Domain-Norm RF: Subset A (All Feats)** | 33 | 0.6635 | 0.1435 | 0.4232 | 0.2143 | 0.5770 |
| **Domain-Norm RF: Subset B (No Top 5)** | 28 | 0.7253 | 0.1831 | 0.4430 | 0.2591 | 0.6237 |
| **Domain-Norm RF: Subset C (No Top 10)** | 23 | 0.7586 | 0.2180 | 0.4737 | 0.2985 | 0.6763 |
| **Domain-Norm RF: Subset D (Machine-Invariant)** | **15** | **0.7541** | **0.2387** | **0.5789** | **0.3380** | **0.7273** |
