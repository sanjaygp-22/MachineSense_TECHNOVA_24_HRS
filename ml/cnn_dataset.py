import torch
import numpy as np
import librosa
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from torch.utils.data import Dataset
from typing import Tuple
from ml.preprocessing import load_and_preprocess_audio
from ml.config import TARGET_SR


def _process_single_audio(row_tuple) -> Tuple[torch.Tensor, torch.Tensor, str, str]:
    """Processes a single audio file and converts to standardized 2D Log-Mel Spectrogram tensor."""
    _, row = row_tuple
    file_path = str(row["file_path"])
    label = int(row["label"])
    machine_id = str(row["machine_id"])

    y_norm, sr = load_and_preprocess_audio(file_path, target_sr=TARGET_SR)

    S = librosa.feature.melspectrogram(
        y=y_norm,
        sr=sr,
        n_mels=128,
        n_fft=1024,
        hop_length=512,
        fmax=sr // 2
    )

    S_db = librosa.power_to_db(S, ref=np.max)
    mean_val = np.mean(S_db)
    std_val = np.std(S_db) + 1e-6
    S_std = (S_db - mean_val) / std_val

    tensor_x = torch.tensor(S_std, dtype=torch.float32).unsqueeze(0)
    tensor_y = torch.tensor(label, dtype=torch.float32)

    return tensor_x, tensor_y, file_path, machine_id


class CachedMelSpectrogramDataset(Dataset):
    """
    Fast, memory-efficient PyTorch Dataset for MIMII pump acoustic recordings.
    Uses multi-threaded ThreadPoolExecutor to pre-compute and cache 128 Mel bands
    standardized Log-dB Spectrograms in shared memory without process overhead.
    """
    def __init__(self, df: pd.DataFrame, max_workers: int = 8, desc: str = "Caching Spectrograms"):
        self.df = df.reset_index(drop=True)

        rows = list(self.df.iterrows())
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(_process_single_audio, rows))

        self.tensors_x = [r[0] for r in results]
        self.tensors_y = [r[1] for r in results]
        self.file_paths = [r[2] for r in results]
        self.machine_ids = [r[3] for r in results]

    def __len__(self) -> int:
        return len(self.tensors_x)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, str, str]:
        return self.tensors_x[idx], self.tensors_y[idx], self.file_paths[idx], self.machine_ids[idx]
