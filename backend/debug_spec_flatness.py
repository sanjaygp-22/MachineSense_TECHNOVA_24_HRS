import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
from app.services.audio_processor import check_machine_audio

def debug_wav():
    sr = 16000
    # 1. Digital silence
    silence = np.zeros(sr * 3, dtype=np.float32)

    # 2. Quiet room noise AGC enabled (RMS 0.028)
    noise_agc = np.random.normal(0, 0.028, sr * 5).astype(np.float32)

    # 3. Quiet room noise AGC disabled (RMS 0.011)
    noise_no_agc = np.random.normal(0, 0.011, sr * 5).astype(np.float32)

    samples = [
        ("Digital Silence", silence),
        ("Quiet Room AGC Enabled (RMS 0.028)", noise_agc),
        ("Quiet Room AGC Disabled (RMS 0.011)", noise_no_agc)
    ]

    for name, y in samples:
        raw_peak = float(np.max(np.abs(y)))
        raw_rms = float(np.sqrt(np.mean(y ** 2)))
        duration = float(len(y) / sr)

        if raw_peak > 0:
            y_norm = (y / raw_peak).astype(np.float32)
        else:
            y_norm = y.astype(np.float32)

        n_fft = 2048
        hop_length = 512
        S_stft = np.abs(librosa.stft(y_norm, n_fft=n_fft, hop_length=hop_length))
        spec_flatness = float(np.mean(librosa.feature.spectral_flatness(S=S_stft)))

        gate_result = check_machine_audio(raw_rms, raw_peak, duration, spec_flatness)

        print("\n" + "=" * 75)
        print(f"DEBUG EVALUATION FOR: {name}")
        print("=" * 75)
        print(f"Raw Peak:          {raw_peak:.6f}")
        print(f"Raw RMS:           {raw_rms:.6f}")
        print(f"Duration:          {duration:.2f} s")
        print(f"Spectral Flatness: {spec_flatness:.6f}")
        print(f"Gate Valid:        {gate_result['valid_machine_signal']}")
        print(f"Gate Reason:       {gate_result['reason']}")
        print("=" * 75)

if __name__ == "__main__":
    debug_wav()
