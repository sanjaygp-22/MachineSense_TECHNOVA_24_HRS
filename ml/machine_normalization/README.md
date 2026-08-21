# MachineSense - Machine Normalization & Domain Invariance Experiment

Phase 6 of the MachineSense ML pipeline evaluates whether domain-invariant feature selection and training-set-only feature standardization improve Leave-One-Machine-Out (LOMO) cross-validation generalization on the real MIMII pump audio dataset (`D:\pump`).

---

## 1. Experimental Methodology

- **Classifier**: `RandomForestClassifier(n_estimators=300, class_weight='balanced', random_state=42)` (identical to baseline).
- **Standardization Protocol**: `StandardScaler()` fitted **strictly on training machines** per fold. Zero held-out test data leakage.
- **Feature Subsets Evaluated**:
  - **Subset A (All 33 Features)**: Complete numerical feature space.
  - **Subset B (Remove Top 5 Machine-Dep)**: Removes `zero_crossing_rate`, `spectral_centroid_hz`, `mfcc_2_mean`, `spectral_rolloff_hz`, `mfcc_11_mean`.
  - **Subset C (Remove Top 10 Machine-Dep)**: Removes top 10 ANOVA F-stat machine-dependent features.
  - **Subset D (Relatively Machine-Invariant)**: 15 features with lowest ANOVA F-statistic between physical assets.

---

## 2. Comparative Performance Matrix (LOMO CV)

| Approach / Feature Subset | Accuracy | Precision | Abnormal Recall | F1-Score | ROC-AUC |
|---|---|---|---|---|---|
| **Random Forest Baseline (Unscaled All Feats)** | 0.7253 | 0.1899 | 0.4693 | 0.2704 | 0.6443 |
| **Supervised 2D CNN (Mel Spectrograms)** | 0.3282 | 0.1334 | 0.9452 | 0.2338 | 0.5445 |
| **Normal-Only Autoencoder (Mel Spectrograms)** | 0.7436 | 0.1244 | 0.2259 | 0.1604 | 0.4939 |
| **Domain-Norm RF: Subset A: All Features** | 0.6635 | 0.1435 | 0.4232 | 0.2143 | 0.5770 |
| **Domain-Norm RF: Subset B: Remove Top 5 Machine-Dep** | 0.7253 | 0.1831 | 0.4430 | 0.2591 | 0.6237 |
| **Domain-Norm RF: Subset C: Remove Top 10 Machine-Dep** | 0.7586 | 0.2180 | 0.4737 | 0.2985 | 0.6763 |
| **Domain-Norm RF: Subset D: Relatively Machine-Invariant** | 0.7541 | 0.2387 | 0.5789 | 0.3380 | 0.7273 |