# MachineSense Production Model Package

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
      1. `dominant_frequency_hz`
      2. `mfcc_12_mean`
      3. `mfcc_8_mean`
      4. `mfcc_4_mean`
      5. `mfcc_1_std`
      6. `mfcc_5_mean`
      7. `mfcc_9_mean`
      8. `mfcc_3_mean`
      9. `mfcc_2_std`
     10. `mfcc_10_mean`
     11. `mfcc_12_std`
     12. `mfcc_11_std`
     13. `mfcc_13_mean`
     14. `mfcc_13_std`
     15. `mfcc_3_std`
4. **Pipeline Inference**:
   - Pass the 15-element feature vector to `pipeline.predict()` and `pipeline.predict_proba()`.

---

## 3. LOMO Cross-Validation Benchmarks

- **Accuracy**: 75.41%
- **Precision**: 23.87%
- **Abnormal Recall**: 57.89% (Best unseen-machine fault detection across all experiments)
- **F1-Score**: 0.3380
- **ROC-AUC**: 0.7273
