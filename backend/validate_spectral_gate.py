import os
import numpy as np
import soundfile as sf
import librosa
from pathlib import Path

def measure_spectral_features(path_or_array, target_sr=16000):
    if isinstance(path_or_array, (str, Path)):
        p = Path(path_or_array)
        if not p.exists():
            return None
        y, orig_sr = sf.read(str(p), dtype='float32')
        if y.ndim > 1:
            y = np.mean(y, axis=1)
        if orig_sr != target_sr:
            y = librosa.resample(y, orig_sr=orig_sr, target_sr=target_sr)
            sr = target_sr
        else:
            sr = orig_sr
    else:
        y, sr = path_or_array

    raw_peak = float(np.max(np.abs(y)))
    raw_rms = float(np.sqrt(np.mean(y ** 2)))
    duration = float(len(y) / sr)

    # Peak normalization for STFT spectral calculation (same as audio_processor.py)
    if raw_peak > 0:
        y_norm = (y / raw_peak).astype(np.float32)
    else:
        y_norm = y.astype(np.float32)

    n_fft = 2048
    hop_length = 512
    S_stft = np.abs(librosa.stft(y_norm, n_fft=n_fft, hop_length=hop_length))

    spec_centroid = float(np.mean(librosa.feature.spectral_centroid(S=S_stft, sr=sr)))
    spec_bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(S=S_stft, sr=sr)))
    spec_flatness = float(np.mean(librosa.feature.spectral_flatness(S=S_stft)))

    # Dominant Frequency
    fft_vals = np.abs(np.fft.rfft(y_norm))
    fft_freqs = np.fft.rfftfreq(len(y_norm), 1.0 / sr)
    if len(fft_vals) > 1:
        max_idx = np.argmax(fft_vals[1:]) + 1
        dom_freq = float(fft_freqs[max_idx])
    else:
        dom_freq = 0.0

    return {
        "raw_rms": raw_rms,
        "raw_peak": raw_peak,
        "duration": duration,
        "flatness": spec_flatness,
        "centroid": spec_centroid,
        "bandwidth": spec_bandwidth,
        "dom_freq": dom_freq
    }

def run_spectral_validation():
    pump_dir = Path("D:/pump")
    test_files = []

    # 1. Digital Silence
    sr = 16000
    test_files.append(("Digital Silence", (np.zeros(sr * 3, dtype=np.float32), sr)))

    # 2. Quiet Room Mic Log (Simulated AGC room noise RMS 0.028)
    noise_agc = np.random.normal(0, 0.028, sr * 5).astype(np.float32)
    test_files.append(("Quiet Room (Simulated AGC)", (noise_agc, sr)))

    # 3. Quiet Room Mic Log (Simulated AGC Disabled room noise RMS 0.011)
    noise_no_agc = np.random.normal(0, 0.011, sr * 5).astype(np.float32)
    test_files.append(("Quiet Room (Simulated No-AGC)", (noise_no_agc, sr)))

    # 4. Genuine MIMII Pump files (Normal & Abnormal)
    if pump_dir.exists():
        wav_files = list(pump_dir.rglob("*.wav"))
        for p in wav_files[:30]:
            cat = "Machine (Abnormal)" if "abnormal" in str(p).lower() else "Machine (Normal)"
            test_files.append((f"{cat} {p.name}", p))

    print("\n" + "=" * 115)
    print(f"{'CATEGORY / FILENAME':<38} | {'RAW RMS':<8} | {'RAW PEAK':<8} | {'FLATNESS':<8} | {'CENTROID':<8} | {'BANDWIDTH':<9} | {'DOM FREQ'}")
    print("=" * 115)

    flatness_machine = []
    flatness_quiet = []

    for name, item in test_files:
        res = measure_spectral_features(item)
        if not res:
            continue

        is_machine = "Machine" in name
        if is_machine:
            flatness_machine.append(res["flatness"])
        elif "Quiet" in name:
            flatness_quiet.append(res["flatness"])

        print(f"{name[:36]:<38} | {res['raw_rms']:<8.5f} | {res['raw_peak']:<8.4f} | {res['flatness']:<8.5f} | {res['centroid']:<8.1f} | {res['bandwidth']:<9.1f} | {res['dom_freq']:<7.1f} Hz")

    print("=" * 115)
    print("\n[SPECTRAL FLATNESS DISTRIBUTION STATS]")
    if flatness_machine:
        print(f"  Machine Recordings Flatness Range: {min(flatness_machine):.5f} to {max(flatness_machine):.5f} (Avg: {sum(flatness_machine)/len(flatness_machine):.5f})")
    if flatness_quiet:
        print(f"  Quiet Room Recordings Flatness Range: {min(flatness_quiet):.5f} to {max(flatness_quiet):.5f} (Avg: {sum(flatness_quiet)/len(flatness_quiet):.5f})")

if __name__ == "__main__":
    run_spectral_validation()
