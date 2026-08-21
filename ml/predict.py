import sys
import json
import joblib
import pandas as pd
import numpy as np

from pathlib import Path
from typing import Dict, Any

# Ensure ml package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.preprocessing import load_and_preprocess_audio
from ml.features import extract_acoustic_features
from ml.config import TARGET_SR, MODELS_DIR


def predict_audio(audio_path: str) -> Dict[str, Any]:
    """
    Loads production pipeline, preprocesses WAV audio, extracts 15 machine-invariant features,
    and returns model prediction & probability score.
    """
    wav_path = Path(audio_path).resolve()
    if not wav_path.exists():
        raise FileNotFoundError(f"Audio file not found: {wav_path}")

    # 1. Load Production Artifacts
    pipeline_file = MODELS_DIR / "machine_invariant_rf_pipeline.joblib"
    metadata_file = MODELS_DIR / "machine_invariant_rf_metadata.json"

    if not (pipeline_file.exists() and metadata_file.exists()):
        raise FileNotFoundError("Production model pipeline or metadata missing! Run 'python ml/export_production_model.py' first.")

    pipeline = joblib.load(pipeline_file)
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    target_features = metadata["feature_names"]

    # 2. Extract machine_id from path if available (e.g. D:\pump\id_00\normal\00000000.wav)
    machine_id = "unknown"
    for part in wav_path.parts:
        if part.startswith("id_"):
            machine_id = part
            break

    # 3. Audio Preprocessing (16kHz mono, peak normalized)
    y_norm, sr = load_and_preprocess_audio(str(wav_path), target_sr=TARGET_SR)

    # 4. Feature Extraction (Full 33 Features)
    raw_feats = extract_acoustic_features(y_norm, sr)

    # 5. Filter to exact 15 production features in order
    selected_feats_dict = {f_name: raw_feats[f_name] for f_name in target_features}
    feature_vector = np.array([[raw_feats[f_name] for f_name in target_features]])

    # 6. Model Inference
    pred_class_idx = int(pipeline.predict(feature_vector)[0])
    probabilities = pipeline.predict_proba(feature_vector)[0]

    label_names = {0: "normal", 1: "abnormal"}
    prediction_label = label_names.get(pred_class_idx, "unknown")

    return {
        "file_name": wav_path.name,
        "file_path": str(wav_path),
        "machine_id": machine_id,
        "prediction": prediction_label,
        "predicted_label": pred_class_idx,
        "anomaly_probability": round(float(probabilities[1]), 4),
        "normal_probability": round(float(probabilities[0]), 4),
        "selected_features": {k: round(float(v), 6) for k, v in selected_feats_dict.items()}
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python ml/predict.py <path_to_wav_file>")
        print("Example: python ml/predict.py D:\\pump\\id_00\\normal\\00000000.wav")
        sys.exit(1)

    wav_input = sys.argv[1]
    print("=" * 75)
    print("MachineSense ML: Production Inference Predictor")
    print("=" * 75)

    try:
        result = predict_audio(wav_input)
        print(f" -> File Name:           {result['file_name']}")
        print(f" -> Machine ID:          {result['machine_id']}")
        print(f" -> Prediction:          {result['prediction'].upper()} (Label: {result['predicted_label']})")
        print(f" -> Anomaly Probability: {result['anomaly_probability'] * 100:.2f}%")
        print(f" -> Normal Probability:  {result['normal_probability'] * 100:.2f}%")
        print()
        print(" -> Selected 15 Machine-Invariant Feature Values:")
        for fn, fv in result["selected_features"].items():
            print(f"    * {fn:<24} = {fv}")
        print("=" * 75)
    except Exception as e:
        print(f"ERROR during prediction: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
