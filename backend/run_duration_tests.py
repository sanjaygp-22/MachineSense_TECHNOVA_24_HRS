import requests
import numpy as np
import soundfile as sf
import librosa
from pathlib import Path

API_URL = "http://127.0.0.1:8000/api/analyze"

def run_duration_test_suite():
    test_dir = Path("test_duration_samples")
    test_dir.mkdir(exist_ok=True)
    sr = 16000

    # 1. 3-second digital silence
    silence_3s = test_dir / "silence_3s.wav"
    sf.write(str(silence_3s), np.zeros(int(sr * 3.0), dtype=np.float32), sr)

    # 2. 5-second quiet room
    quiet_5s = test_dir / "quiet_5s.wav"
    sf.write(str(quiet_5s), np.random.normal(0, 0.028, int(sr * 5.0)).astype(np.float32), sr)

    # 3. 6.99-second machine recording (truncated MIMII machine file)
    pump_file = Path("D:/pump/abnormal/00000000.wav")
    machine_6_99s = test_dir / "machine_6_99s.wav"
    if pump_file.exists():
        y_mach, _ = sf.read(str(pump_file), dtype='float32')
        if y_mach.ndim > 1: y_mach = np.mean(y_mach, axis=1)
        sf.write(str(machine_6_99s), y_mach[:int(sr * 6.99)], sr)
    else:
        # Synthetic machine wave for 6.99s
        t = np.linspace(0, 6.99, int(sr * 6.99), endpoint=False)
        m_wave = (0.3 * np.sin(2 * np.pi * 450 * t)).astype(np.float32)
        sf.write(str(machine_6_99s), m_wave, sr)

    # 4. 7.00s+ genuine machine recording (10s MIMII file 00000000.wav)
    # pump_file used directly

    # 5. 8.0-second quiet room recording
    quiet_8s = test_dir / "quiet_8s.wav"
    sf.write(str(quiet_8s), np.random.normal(0, 0.028, int(sr * 8.0)).astype(np.float32), sr)

    test_cases = [
        ("TEST 1 (3.0s Digital Silence)", silence_3s, "< 7.0s"),
        ("TEST 2 (5.0s Quiet Room Noise)", quiet_5s, "< 7.0s"),
        ("TEST 3 (6.99s Machine Recording)", machine_6_99s, "< 7.0s"),
        ("TEST 4 (10.0s Genuine Machine)", pump_file, ">= 7.0s"),
        ("TEST 5 (8.0s Quiet Room Noise)", quiet_8s, ">= 7.0s"),
    ]

    print("\n" + "=" * 125)
    print(f"{'TEST CASE':<35} | {'DUR (s)':<8} | {'RMS':<8} | {'VALID SIGNAL':<12} | {'ML CALLED?':<10} | {'PREDICTION MESSAGE / STATUS'}")
    print("=" * 125)

    for test_label, file_p, dur_spec in test_cases:
        if not file_p.exists():
            print(f"{test_label:<35} | File not found: {file_p}")
            continue

        with open(file_p, "rb") as f:
            files = {"audio": (file_p.name, f, "audio/wav")}
            data = {"machine_id": "id_00"}
            resp = requests.post(API_URL, files=files, data=data)

        if resp.status_code != 200:
            print(f"{test_label:<35} | HTTP Error: {resp.status_code}")
            continue

        res = resp.json()
        sig = res.get("signal", {})
        pred = res.get("prediction", {})
        dur = res.get("audio", {}).get("duration", 0.0)
        rms = sig.get("rms", 0.0)
        valid_signal = sig.get("valid_machine_signal", False)
        
        ml_called = "YES" if pred.get("label") in ["normal", "abnormal"] else "NO (SKIPPED)"
        msg_or_status = pred.get("message") if pred.get("message") else pred.get("status")

        print(f"{test_label:<35} | {dur:<8.2f} | {rms:<8.5f} | {str(valid_signal):<12} | {ml_called:<10} | {msg_or_status}")

    print("=" * 125 + "\n")

    # Clean up
    for p in [silence_3s, quiet_5s, machine_6_99s, quiet_8s]:
        if p.exists(): p.unlink()
    if test_dir.exists(): test_dir.rmdir()

if __name__ == "__main__":
    run_duration_test_suite()
