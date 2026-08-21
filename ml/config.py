import os
from pathlib import Path

# Paths
DATASET_DIR = Path(os.getenv("MIMII_DATASET_DIR", "D:/pump")).resolve()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ML_DIR = Path(__file__).resolve().parent
DATA_DIR = ML_DIR / "data"
FEATURES_DIR = ML_DIR / "features"
MODELS_DIR = ML_DIR / "models"

# Audio Preprocessing Configuration
TARGET_SR = 16000
MONO = True

# Data Leakage Prevention
RANDOM_SEED = 42
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Label Mapping
LABEL_MAP = {
    "normal": 0,
    "abnormal": 1
}

INV_LABEL_MAP = {
    0: "normal",
    1: "abnormal"
}
