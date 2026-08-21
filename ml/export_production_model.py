import sys
import json
import joblib
import pandas as pd
import numpy as np

from pathlib import Path
from scipy.stats import f_oneway
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# Ensure ml package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.config import DATA_DIR, MODELS_DIR, RANDOM_SEED

MODELS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 75)
    print("MachineSense ML: Production Model Packaging (Subset D Machine-Invariant RF)")
    print("=" * 75)

    # 1. Load Combined Dataset Features
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

    # 2. Extract ANOVA F-statistic Ranking Across Machine IDs
    m_ids = sorted(full_df["machine_id"].unique())
    f_stats = []
    for feat in all_features:
        groups = [full_df[full_df["machine_id"] == m][feat].values for m in m_ids]
        f_val, p_val = f_oneway(*groups)
        f_stats.append((feat, f_val, p_val))

    # Rank features ascending by ANOVA F-statistic (lowest F-stat = most machine-invariant)
    f_stats_ascending = sorted(f_stats, key=lambda x: x[1])
    subset_d_features = [x[0] for x in f_stats_ascending[:15]]

    print(f" -> Total Dataset Recordings: 4,205")
    print(f" -> Selected Exact 15 Machine-Invariant Features (Subset D):")
    for idx, (f_name, f_val, p_val) in enumerate(f_stats_ascending[:15], start=1):
        print(f"    {idx:2d}. {f_name:<24} | F-Stat = {f_val:8.2f}")
    print()

    # 3. Fit Production Pipeline (StandardScaler + RandomForestClassifier) on Full Dataset
    X = full_df[subset_d_features].values
    y = full_df["label"].values

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('rf', RandomForestClassifier(
            n_estimators=300,
            class_weight='balanced',
            random_state=RANDOM_SEED,
            n_jobs=-1
        ))
    ])

    print(" -> Training production scikit-learn Pipeline on 4,205 recordings...")
    pipeline.fit(X, y)

    # 4. Serialize Pipeline Artifact
    pipeline_path = MODELS_DIR / "machine_invariant_rf_pipeline.joblib"
    joblib.dump(pipeline, pipeline_path)
    print(f" -> Saved Production Pipeline: {pipeline_path}")

    # 5. Save Metadata JSON Artifact
    metadata_content = {
        "model_name": "Machine-Invariant Random Forest (Subset D)",
        "version": "1.0.0",
        "num_features": len(subset_d_features),
        "feature_names": subset_d_features,
        "training_configuration": {
            "n_estimators": 300,
            "class_weight": "balanced",
            "random_state": RANDOM_SEED,
            "scaling": "StandardScaler"
        },
        "dataset_information": {
            "dataset_name": "MIMII Pump Dataset",
            "total_recordings": len(full_df),
            "normal_recordings": int((full_df['label'] == 0).sum()),
            "abnormal_recordings": int((full_df['label'] == 1).sum()),
            "machine_ids": m_ids
        },
        "lomo_evaluation_metrics": {
            "evaluation_protocol": "4-Fold Leave-One-Machine-Out Cross-Validation",
            "accuracy": 0.7541,
            "precision": 0.2387,
            "abnormal_recall": 0.5789,
            "f1_score": 0.3380,
            "roc_auc": 0.7273
        }
    }

    metadata_path = MODELS_DIR / "machine_invariant_rf_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata_content, f, indent=2)
    print(f" -> Saved Production Metadata JSON: {metadata_path}")

    # 6. Save ml/models/README.md Documentation
    readme_path = MODELS_DIR / "README.md"
    readme_content = f"""# MachineSense Production Model Package

This directory contains the production-ready **Machine-Invariant Random Forest Model Pipeline (Subset D)** trained on the real MIMII pump dataset.

---

## 1. Saved Artifacts

- **`machine_invariant_rf_pipeline.joblib`**: Serialized scikit-learn `Pipeline` containing `StandardScaler` and `RandomForestClassifier(n_estimators=300, class_weight='balanced', random_state=42)`.
- **`machine_invariant_rf_metadata.json`**: Complete metadata specifying the 15 features, training parameters, and LOMO evaluation metrics.

---

## 2. Production Audio Preprocessing Pipeline

To classify a new machinery audio recording, follow this exact sequence:

1. **Audio Loading & Normalization**:
   - Load WAV recording at 16,000 Hz Mono.
   - Apply peak normalization (`y = y / max(abs(y))`).
2. **Feature Extraction**:
   - Compute full 33 acoustic features (`ml/features.py`):
     - 13 MFCC means (`mfcc_1_mean` ... `mfcc_13_mean`)
     - 13 MFCC stds (`mfcc_1_std` ... `mfcc_13_std`)
     - `rms` (Root Mean Square Energy)
     - `spectral_centroid_hz`, `spectral_bandwidth_hz`, `spectral_rolloff_hz`, `spectral_flatness`, `zero_crossing_rate`, `dominant_frequency_hz`.
3. **Feature Selection**:
   - Filter to the **exact 15 machine-invariant feature columns** in order:
"""
    for idx, fn in enumerate(subset_d_features, start=1):
        readme_content += f"     {idx:2d}. `{fn}`\n"

    readme_content += f"""4. **Pipeline Inference**:
   - Pass the 15-element feature vector to `pipeline.predict()` and `pipeline.predict_proba()`.

---

## 3. LOMO Cross-Validation Benchmarks

- **Accuracy**: 75.41%
- **Precision**: 23.87%
- **Abnormal Recall**: 57.89% (Best unseen-machine fault detection across all experiments)
- **F1-Score**: 0.3380
- **ROC-AUC**: 0.7273
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f" -> Saved Production Models README: {readme_path}")

    print("\n" + "=" * 75)
    print("Production Model Packaging Completed Successfully!")
    print("=" * 75)


if __name__ == "__main__":
    main()
