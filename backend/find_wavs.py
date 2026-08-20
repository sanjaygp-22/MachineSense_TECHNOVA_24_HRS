import os
from pathlib import Path
import soundfile as sf
import numpy as np

def scan_wavs():
    root_dir = Path("..").resolve()
    print("Searching from:", root_dir)
    wavs = list(root_dir.rglob("*.wav"))
    print(f"Total WAV files found: {len(wavs)}")
    
    for w in wavs:
        if ".venv" in str(w) or "node_modules" in str(w):
            continue
        try:
            y, sr = sf.read(str(w), dtype='float32')
            if y.ndim > 1:
                y = np.mean(y, axis=1)
            raw_peak = float(np.max(np.abs(y)))
            raw_rms = float(np.sqrt(np.mean(y ** 2)))
            duration = float(len(y) / sr)
            print(f"{w.name:<25} | RMS: {raw_rms:.6f} | Peak: {raw_peak:.6f} | Dur: {duration:.2f}s | Path: {w}")
        except Exception as e:
            print(f"Error reading {w.name}: {e}")

if __name__ == "__main__":
    scan_wavs()
