import os
import numpy as np
import soundfile as sf
import librosa
from pathlib import Path

def measure_file(path_str):
    try:
        y, sr = sf.read(path_str, dtype='float32')
        if y.ndim > 1:
            y = np.mean(y, axis=1)
        raw_peak = float(np.max(np.abs(y)))
        raw_rms = float(np.sqrt(np.mean(y ** 2)))
        duration = float(len(y) / sr)
        return raw_peak, raw_rms, duration
    except Exception as e:
        return 0.0, 0.0, 0.0

def run_validation():
    test_dir = Path("test_audio_samples")
    test_dir.mkdir(exist_ok=True)

    # 1. Create Digital Silence
    silence_path = test_dir / "digital_silence.wav"
    sr = 16000
    sf.write(str(silence_path), np.zeros(sr * 3, dtype=np.float32), sr)

    # 2. Create Quiet Room Noise (simulated mic AGC room noise RMS ~0.025)
    quiet_room_path = test_dir / "quiet_room_sim.wav"
    noise = np.random.normal(0, 0.025, sr * 3).astype(np.float32)
    sf.write(str(quiet_room_path), noise, sr)

    # Gather genuine machine recordings from workspace
    machine_files = []
    for root, dirs, files in os.walk(".."):
        if ".venv" in root or "node_modules" in root or ".git" in root:
            continue
        for f in files:
            if f.endswith(".wav"):
                full_p = Path(root) / f
                machine_files.append(full_p)

    all_tests = [
        ("Digital Silence", silence_path, "No"),
        ("Quiet Room Noise (Measured Mic Log)", Path("id_00_recording.wav_log"), "No"),
        ("Quiet Room Noise (Simulated AGC)", quiet_room_path, "No")
    ]

    for p in machine_files[:15]:
        all_tests.append((f"Machine Asset ({p.name})", p, "Yes"))

    print("\n" + "=" * 90)
    print(f"{'CATEGORY / FILENAME':<40} | {'RAW RMS':<8} | {'RAW PEAK':<8} | {'DUR':<5} | {'CURRENT':<8} | {'PROPOSED':<8} | {'SHOULD REACH RF'}")
    print("=" * 90)

    for cat, p, should_rf in all_tests:
        if not p.exists() and not str(p).endswith("_log"):
            continue
        if str(p).endswith("_log"):
            # Known measured values from system log for id_00_recording.wav
            raw_peak, raw_rms, duration = 1.000000, 0.028298, 6.06
        else:
            raw_peak, raw_rms, duration = measure_file(str(p))

        current_gate = "PASS" if (raw_rms >= 0.002 and raw_peak >= 0.008 and duration >= 0.5) else "REJECT"
        proposed_gate = "PASS" if (raw_rms >= 0.035 and raw_peak >= 0.015 and duration >= 0.5) else "REJECT"

        print(f"{cat[:38]:<40} | {raw_rms:<8.6f} | {raw_peak:<8.6f} | {duration:<5.1f} | {current_gate:<8} | {proposed_gate:<8} | {should_rf}")

    # Clean up temporary test files
    silence_path.unlink()
    quiet_room_path.unlink()
    test_dir.rmdir()

if __name__ == "__main__":
    run_validation()
