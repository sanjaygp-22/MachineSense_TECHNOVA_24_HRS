"""
MachineSense Production ML Inference Service
Pre-loads and warms up the machine-invariant Random Forest pipeline for fast real-time acoustic classification.
"""
import sys
import json
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

# Root directory of workspace
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from ml.features import extract_acoustic_features


class MLService:
    """
    Singleton service that loads the production Machine-Invariant Random Forest pipeline once
    on startup and performs fast real-time machinery anomaly prediction.
    """
    _instance: Optional['MLService'] = None

    def __init__(self):
        self.pipeline = None
        self.metadata = None
        self.feature_names = []
        self.is_model_loaded = False
        self.load_error = None
        self._load_model()

    @classmethod
    def get_instance(cls) -> 'MLService':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model(self):
        try:
            models_dir = ROOT_DIR / "ml" / "models"
            pipeline_path = models_dir / "machine_invariant_rf_pipeline.joblib"
            metadata_path = models_dir / "machine_invariant_rf_metadata.json"

            if not (pipeline_path.exists() and metadata_path.exists()):
                raise FileNotFoundError(f"Production model artifacts missing at {models_dir}")

            self.pipeline = joblib.load(pipeline_path)
            with open(metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            self.feature_names = self.metadata.get("feature_names", [])
            self.is_model_loaded = True
            self.load_error = None

            # Warmup JIT & Librosa routines during startup
            dummy_y = np.zeros(16000, dtype=np.float32)
            _ = extract_acoustic_features(dummy_y, 16000)

            print(f"[MLService] Production model pipeline successfully loaded & warmed up ({len(self.feature_names)} features).")
        except Exception as e:
            self.is_model_loaded = False
            self.load_error = str(e)
            print(f"[MLService] ERROR loading production ML model: {e}")

    def is_loaded(self) -> bool:
        return self.is_model_loaded

    def predict(self, y: np.ndarray, sr: int, filename_or_path: str = "") -> Dict[str, Any]:
        """
        Runs ML prediction on preprocessed 16kHz mono audio array.
        Extracts 15 machine-invariant features and scores with Random Forest pipeline.
        """
        if not self.is_model_loaded:
            raise RuntimeError(f"ML Model unavailable: {self.load_error or 'Model not loaded'}")

        # Extract full acoustic features
        raw_feats = extract_acoustic_features(y, sr)

        # Filter to exact 15 production features in exact order
        feature_vector = np.array([[raw_feats[f_name] for f_name in self.feature_names]])

        # Model Inference
        pred_class_idx = int(self.pipeline.predict(feature_vector)[0])
        probabilities = self.pipeline.predict_proba(feature_vector)[0]

        label_names = {0: "normal", 1: "abnormal"}
        prediction_label = label_names.get(pred_class_idx, "unknown")

        # Parse machine_id if present in path/filename
        machine_id = "unknown"
        path_str = str(filename_or_path)
        for part in Path(path_str).parts:
            if part.startswith("id_"):
                machine_id = part
                break

        return {
            "machine_id": machine_id,
            "prediction": {
                "label": prediction_label,
                "class": pred_class_idx,
                "abnormal_probability": round(float(probabilities[1]), 4),
                "normal_probability": round(float(probabilities[0]), 4)
            }
        }


# Global instance helper
def get_ml_service() -> MLService:
    return MLService.get_instance()
