import os
import requests
import numpy as np
import soundfile as sf
from pathlib import Path

API_URL = "http://127.0.0.1:8000/api/analyze"

def run_test_suite():
    test_dir = Path("test_audio_samples")
    test_dir.mkdir(exist_ok=True)
    sr = 16000

    # 1. Digital silence
    silence_path = test_dir / "digital_silence.wav"
    sf.write(str(silence_path), np.zeros(sr * 3, dtype=np.float32), sr)

    # 2. Quiet room AGC enabled simulation
    quiet_agc_path = test_dir / "quiet_room_agc.wav"
    sf.write(str(quiet_agc_path), np.random.normal(0, 0.028, sr * 5).astype(np.float32), sr)

    # 3. Quiet room AGC disabled simulation
    quiet_no_agc_path = test_dir / "quiet_room_no_agc.wav"
    sf.write(str(quiet_no_agc_path), np.random.normal(0, 0.011, sr * 5).astype(np.float32), sr)

    # MIMII Pump Dataset files
    pump_dir = Path("D:/pump")
    dataset_map = {
        "TEST 4 (00000000.wav)": pump_dir / "abnormal" / "00000000.wav",
        "TEST 5 (00000005.wav)": pump_dir / "abnormal" / "00000005.wav",
        "TEST 6 (00000011.wav)": pump_dir / "abnormal" / "00000011.wav",
        "TEST 7 (00000028.wav)": pump_dir / "abnormal" / "00000028.wav",
        "TEST 8 (00000029.wav)": pump_dir / "abnormal" / "00000029.wav",
    }

    test_cases = [
        ("TEST 1 (Digital Silence)", silence_path, False),
        ("TEST 2 (Quiet Room AGC Enabled)", quiet_agc_path, False),
        ("TEST 3 (Quiet Room AGC Disabled)", quiet_no_agc_path, False),
    ]

    for label, path_obj in dataset_map.items():
        if path_obj.exists():
            test_cases.append((label, path_obj, True))
        else:
            # Fallback search
            found = list(pump_dir.rglob(path_obj.name)) if pump_dir.exists() else []
            if found:
                test_cases.append((label, found[0], True))

    print("\n" + "=" * 115)
    print(f"{'TEST CASE':<32} | {'RAW RMS':<8} | {'RAW PEAK':<8} | {'FLATNESS':<8} | {'VALID SIGNAL':<12} | {'ML CALLED?':<10} | {'PREDICTION / STATUS'}")
    print("=" * 115)

    for test_label, file_p, expected_ml in test_cases:
        if not file_p.exists():
            print(f"{test_label:<32} | File not found: {file_p}")
            continue

        with open(file_p, "rb") as f:
            files = {"audio": (file_p.name, f, "audio/wav")}
            data = {"machine_id": "id_00"}
            resp = requests.post(API_URL, files=files, data=data)

        if resp.status_code != 200:
            print(f"{test_label:<32} | HTTP Error: {resp.status_code}")
            continue

        res = resp.json()
        sig = res.get("signal", {})
        pred = res.get("prediction", {})

        raw_rms = sig.get("rms", 0.0)
        raw_peak = sig.get("peak_amplitude", 0.0)
        flatness = sig.get("spectral_flatness", sig.get("flatness", 0.0))
        valid_signal = sig.get("valid_machine_signal", False)
        
        ml_called = "YES" if pred.get("label") in ["normal", "abnormal"] else "NO (SKIPPED)"
        status_or_label = pred.get("status") if pred.get("status") else pred.get("label")

        print(f"{test_label:<32} | {raw_rms:<8.5f} | {raw_peak:<8.4f} | {flatness:<8.5f} | {str(valid_signal):<12} | {ml_called:<10} | {status_or_label}")

    print("=" * 115 + "\n")

    # Clean up test dir
    if silence_path.exists(): silence_path.unlink()
    if quiet_agc_path.exists(): quiet_agc_path.unlink()
    if quiet_no_agc_path.exists(): quiet_no_agc_path.unlink()
    if test_dir.exists(): test_dir.rmdir()

if __name__ == "__main__":
    run_test_suite()
