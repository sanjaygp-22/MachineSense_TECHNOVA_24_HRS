import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Tuple
from ml.config import TARGET_SR, MONO


def load_and_preprocess_audio(
    file_path: str,
    target_sr: int = TARGET_SR,
    mono: bool = MONO
) -> Tuple[np.ndarray, int]:
    """
    Loads an audio file from disk, converts to mono, resamples to target_sr (default 16,000 Hz),
    normalizes amplitude to [-1.0, 1.0], and validates signal sanity.
    Uses fast direct C-library soundfile loading when available.
    Does NOT modify the original file on disk.
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    try:
        # Fast path using PySoundFile C library (100x-1000x faster than audioread)
        y, orig_sr = sf.read(str(path_obj), dtype='float32')

        # Convert stereo to mono if required
        if y.ndim > 1:
            if mono:
                y = np.mean(y, axis=1)
            else:
                y = y[:, 0]

        # Resample if sample rate differs from target_sr
        if orig_sr != target_sr:
            y = librosa.resample(y, orig_sr=orig_sr, target_sr=target_sr)
            sr = target_sr
        else:
            sr = orig_sr
    except Exception:
        # Fallback to librosa.load if soundfile fails
        try:
            y, sr = librosa.load(str(path_obj), sr=target_sr, mono=mono)
        except Exception as e:
            raise ValueError(f"Failed to load or decode audio file '{file_path}': {str(e)}")

    if len(y) == 0:
        raise ValueError(f"Loaded audio signal from '{file_path}' is empty.")

    # Amplitude Normalization / Noise Filtering Peak Scaling
    max_peak = np.max(np.abs(y))
    if max_peak > 0:
        y_norm = y / max_peak
    else:
        y_norm = y

    return y_norm.astype(np.float32), sr
