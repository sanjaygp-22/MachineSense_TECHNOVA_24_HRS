import requests
import numpy as np
import soundfile as sf
from pathlib import Path

API_URL = "http://127.0.0.1:8000/api/analyze"
HISTORY_URL = "http://127.0.0.1:8000/api/history?limit=10"

def run_verification():
    sr = 16000
    test_dir = Path("test_verify_temp")
    test_dir.mkdir(exist_ok=True)

    # Load 10s genuine pump audio
    pump_file = Path("D:/pump/abnormal/00000000.wav")
    if pump_file.exists():
        y_mach, _ = sf.read(str(pump_file), dtype='float32')
        if y_mach.ndim > 1: y_mach = np.mean(y_mach, axis=1)
        y_10s = y_mach[:int(sr * 10.0)]
    else:
        t = np.linspace(0, 10.0, int(sr * 10.0), endpoint=False)
        y_10s = (0.3 * np.sin(2 * np.pi * 450 * t)).astype(np.float32)

    test_wav = test_dir / "sample_10s.wav"
    sf.write(str(test_wav), y_10s, sr)

    print("\n" + "=" * 125)
    print(f"{'VERIFICATION TEST':<36} | {'MACHINE ID':<12} | {'SOURCE':<10} | {'PREDICTION':<16} | {'DB RECORD VALIDATION'}")
    print("=" * 125)

    scenarios = [
        ("TEST 1: Mic Recording on id_02", "id_02", "rec"),
        ("TEST 2: File Upload on id_04", "id_04", "uploaded"),
        ("TEST 3: Mic Recording on id_06", "id_06", "rec"),
        ("TEST 4: File Upload on id_00", "id_00", "uploaded"),
    ]

    for label, target_mid, target_src in scenarios:
        with open(test_wav, "rb") as f:
            files = {"audio": (test_wav.name, f, "audio/wav")}
            data = {"machine_id": target_mid, "source": target_src}
            resp = requests.post(API_URL, files=files, data=data)

        if resp.status_code != 200:
            print(f"{label:<36} | {target_mid:<12} | {target_src:<10} | HTTP {resp.status_code}")
            continue

        res = resp.json()
        analysis_id = res.get("analysis_id")
        rec_mid = res.get("machine_id")
        rec_src = res.get("source")
        pred_label = res.get("prediction", {}).get("label")

        # Verify DB history record
        h_resp = requests.get(HISTORY_URL)
        h_records = h_resp.json().get("records", []) if h_resp.status_code == 200 else []
        db_match = next((r for r in h_records if r.get("analysis_id") == analysis_id), None)

        db_valid = "FAILED"
        if db_match and db_match.get("machine_id") == target_mid and db_match.get("source") == target_src:
            db_valid = f"PASSED (ID={db_match.get('machine_id')}, SRC={db_match.get('source')})"

        print(f"{label:<36} | {rec_mid:<12} | {rec_src:<10} | {pred_label:<16} | {db_valid}")

    print("=" * 125 + "\n")

    # Clean up
    if test_wav.exists(): test_wav.unlink()
    if test_dir.exists(): test_dir.rmdir()

if __name__ == "__main__":
    run_verification()
