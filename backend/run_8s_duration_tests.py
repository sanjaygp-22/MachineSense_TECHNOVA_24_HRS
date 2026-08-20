import requests
import numpy as np
import soundfile as sf
from pathlib import Path

API_URL = "http://127.0.0.1:8000/api/analyze"

def run_8s_verification_suite():
    test_dir = Path("test_8s_samples")
    test_dir.mkdir(exist_ok=True)
    sr = 16000

    # 1. 3-second audio
    file_3s = test_dir / "audio_3s.wav"
    sf.write(str(file_3s), np.zeros(int(sr * 3.0), dtype=np.float32), sr)

    # 2. 7.9-second audio
    file_7_9s = test_dir / "audio_7_9s.wav"
    sf.write(str(file_7_9s), np.random.normal(0, 0.028, int(sr * 7.9)).astype(np.float32), sr)

    # 3. Exactly 8.0-second machine audio (truncated MIMII machine file)
    pump_file = Path("D:/pump/abnormal/00000000.wav")
    file_8_0s = test_dir / "machine_8_0s.wav"
    if pump_file.exists():
        y_mach, _ = sf.read(str(pump_file), dtype='float32')
        if y_mach.ndim > 1: y_mach = np.mean(y_mach, axis=1)
        sf.write(str(file_8_0s), y_mach[:int(sr * 8.0)], sr)
    else:
        t = np.linspace(0, 8.0, int(sr * 8.0), endpoint=False)
        m_wave = (0.3 * np.sin(2 * np.pi * 450 * t)).astype(np.float32)
        sf.write(str(file_8_0s), m_wave, sr)

    # 4. 10.0-second genuine machine audio (MIMII file 00000000.wav)

    test_cases = [
        ("VERIFICATION 1 (3.0s Audio)", file_3s, "< 8.0s"),
        ("VERIFICATION 2 (7.9s Audio)", file_7_9s, "< 8.0s"),
        ("VERIFICATION 3 (8.0s Machine Audio)", file_8_0s, ">= 8.0s"),
        ("VERIFICATION 4 (10.0s Genuine Machine)", pump_file, ">= 8.0s"),
    ]

    print("\n" + "=" * 125)
    print(f"{'VERIFICATION TEST':<36} | {'DUR (s)':<8} | {'RMS':<8} | {'VALID SIGNAL':<12} | {'ML CALLED?':<10} | {'PREDICTION MESSAGE / STATUS'}")
    print("=" * 125)

    for test_label, file_p, dur_spec in test_cases:
        if not file_p.exists():
            print(f"{test_label:<36} | File not found: {file_p}")
            continue

        with open(file_p, "rb") as f:
            files = {"audio": (file_p.name, f, "audio/wav")}
            data = {"machine_id": "id_00"}
            resp = requests.post(API_URL, files=files, data=data)

        if resp.status_code != 200:
            print(f"{test_label:<36} | HTTP Error: {resp.status_code}")
            continue

        res = resp.json()
        sig = res.get("signal", {})
        pred = res.get("prediction", {})
        dur = res.get("audio", {}).get("duration", 0.0)
        rms = sig.get("rms", 0.0)
        valid_signal = sig.get("valid_machine_signal", False)
        
        ml_called = "YES" if pred.get("label") in ["normal", "abnormal"] else "NO (SKIPPED)"
        msg_or_status = pred.get("message") if pred.get("message") else pred.get("status")

        print(f"{test_label:<36} | {dur:<8.2f} | {rms:<8.5f} | {str(valid_signal):<12} | {ml_called:<10} | {msg_or_status}")

    print("=" * 125 + "\n")

    # Clean up
    for p in [file_3s, file_7_9s, file_8_0s]:
        if p.exists(): p.unlink()
    if test_dir.exists(): test_dir.rmdir()

if __name__ == "__main__":
    run_8s_verification_suite()
