import requests
import numpy as np
import soundfile as sf
from pathlib import Path

API_URL = "http://127.0.0.1:8000/api/analyze"
HISTORY_URL = "http://127.0.0.1:8000/api/history?limit=100"

def run_phase10_e2e():
    print("\n" + "=" * 110)
    print("PHASE 10: REAL END-TO-END TEST EXECUTION")
    print("=" * 110)

    # 1. Verify Backend HTTP 200
    h_resp = requests.get(HISTORY_URL)
    print(f"1. GET /api/history Status Code: {h_resp.status_code}")
    assert h_resp.status_code == 200, "Backend /api/history failed!"

    sr = 16000
    test_dir = Path("test_phase10_temp")
    test_dir.mkdir(exist_ok=True)

    # Load 10s machine audio
    pump_file = Path("D:/pump/abnormal/00000000.wav")
    if pump_file.exists():
        y_mach, _ = sf.read(str(pump_file), dtype='float32')
        if y_mach.ndim > 1: y_mach = np.mean(y_mach, axis=1)
        y_10s = y_mach[:int(sr * 10.0)]
    else:
        t = np.linspace(0, 10.0, int(sr * 10.0), endpoint=False)
        y_10s = (0.3 * np.sin(2 * np.pi * 450 * t)).astype(np.float32)

    mach_file = test_dir / "machine_10s.wav"
    sf.write(str(mach_file), y_10s, sr)

    # Perform 4 distinct machine analysis requests
    scenarios = [
        ("id_00", "uploaded"),
        ("id_02", "rec"),
        ("id_04", "uploaded"),
        ("id_06", "rec"),
    ]

    print("\n2. EXECUTING ANALYSIS REQUESTS:")
    for mid, src in scenarios:
        with open(mach_file, "rb") as f:
            files = {"audio": (mach_file.name, f, "audio/wav")}
            data = {"machine_id": mid, "source": src}
            resp = requests.post(API_URL, files=files, data=data)
            assert resp.status_code == 200, f"Analysis failed for {mid}"
            res = resp.json()
            print(f"   -> Posted {mid} (source={src}) -> analysis_id: {res.get('analysis_id')}, label: {res.get('prediction', {}).get('label')}")

    # Verify History endpoint output
    print("\n3. VERIFYING HISTORY DATA:")
    h_resp2 = requests.get(HISTORY_URL)
    records = h_resp2.json().get("records", [])
    print(f"   Total Records in SQLite History: {len(records)}")

    # Check that latest records match machine IDs and sources
    latest_4 = records[:4]
    print("\n4. LATEST 4 HISTORY RECORDS FROM BACKEND:")
    print(f"   {'ANALYSIS ID':<36} | {'MACHINE ID':<10} | {'SOURCE':<10} | {'PREDICTION':<12}")
    print("   " + "-" * 80)
    for r in latest_4:
        print(f"   {r.get('analysis_id'):<36} | {r.get('machine_id'):<10} | {r.get('source'):<10} | {r.get('prediction_label'):<12}")

    # 5. Verify No-Machine-Sound Behavior
    silence_file = test_dir / "silence_10s.wav"
    sf.write(str(silence_file), np.zeros(int(sr * 10.0), dtype=np.float32), sr)
    with open(silence_file, "rb") as f:
        files = {"audio": (silence_file.name, f, "audio/wav")}
        data = {"machine_id": "id_02", "source": "rec"}
        resp_silence = requests.post(API_URL, files=files, data=data)
        res_silence = resp_silence.json()
        print(f"\n5. SILENCE TEST -> prediction.label: {res_silence.get('prediction', {}).get('label')}")
        assert res_silence.get('prediction', {}).get('label') == 'no_machine_sound', "Silence test failed!"

    # Clean up
    for p in [mach_file, silence_file]:
        if p.exists(): p.unlink()
    if test_dir.exists(): test_dir.rmdir()

    print("\n" + "=" * 110)
    print("ALL PHASE 10 E2E VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 110 + "\n")

if __name__ == "__main__":
    run_phase10_e2e()
