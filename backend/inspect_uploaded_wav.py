import numpy as np
import soundfile as sf
from pathlib import Path

def inspect_wav(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return

    y, sr = sf.read(str(path), dtype='float32')

    num_channels = 1 if y.ndim == 1 else y.shape[1]
    num_samples = len(y)
    duration = num_samples / sr
    min_val = float(np.min(y))
    max_val = float(np.max(y))
    peak_val = float(np.max(np.abs(y)))
    rms_val = float(np.sqrt(np.mean(y ** 2)))

    near_zero_count = int(np.sum(np.abs(y) < 0.001))
    near_zero_pct = (near_zero_count / num_samples) * 100.0

    print("=" * 70)
    print(f"DIAGNOSTIC METRICS FOR: {path.name}")
    print("=" * 70)
    print(f"Sample Rate:               {sr} Hz")
    print(f"Channels:                  {num_channels}")
    print(f"Number of Samples:         {num_samples}")
    print(f"Duration:                  {duration:.2f} s")
    print(f"Minimum Sample Value:      {min_val:.6f}")
    print(f"Maximum Sample Value:      {max_val:.6f}")
    print(f"Peak Amplitude (abs max):  {peak_val:.6f}")
    print(f"RMS Energy:                {rms_val:.6f}")
    print(f"Samples Near Zero (<0.001): {near_zero_count} / {num_samples} ({near_zero_pct:.2f}%)")
    print("=" * 70)

if __name__ == "__main__":
    inspect_wav("uploads/id_00_recording.wav")
