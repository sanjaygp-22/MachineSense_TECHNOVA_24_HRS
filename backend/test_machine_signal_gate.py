import requests
import numpy as np
import soundfile as sf
from pathlib import Path

def test_machine_signal():
    api_url = "http://127.0.0.1:8000/api/analyze"
    test_path = Path("operating_machine_signal.wav")

    # Generate 3s operating machine acoustic signal (450 Hz fundamental + harmonics, RMS ~ 0.08)
    sr = 16000
    t = np.linspace(0, 3, sr * 3, endpoint=False)
    machine_wave = (
        0.3 * np.sin(2 * np.pi * 450 * t) +
        0.15 * np.sin(2 * np.pi * 900 * t) +
        0.05 * np.random.normal(0, 1, sr * 3)
    ).astype(np.float32)
    sf.write(str(test_path), machine_wave, sr)

    print("\n" + "=" * 70)
    print("TESTING ACTIVE OPERATING MACHINE SOUND WAV AGAINST POST /api/analyze")
    print("=" * 70)

    with open(test_path, "rb") as f:
        files = {"audio": ("operating_machine_signal.wav", f, "audio/wav")}
        data = {"machine_id": "id_00"}
        resp = requests.post(api_url, files=files, data=data)

    print(f"HTTP Status Code: {resp.status_code}")
    if resp.status_code == 200:
        json_data = resp.json()
        print("\nAPI Response Prediction Object:")
        print(json_data.get("prediction"))
        print(f"\nStatus Field: {json_data.get('prediction', {}).get('status')}")
        print(f"Label Field:  {json_data.get('prediction', {}).get('label')}")
        print(f"Normal Probability:   {json_data.get('prediction', {}).get('normal_probability')}")
        print(f"Abnormal Probability: {json_data.get('prediction', {}).get('abnormal_probability')}")
    else:
        print("API Error Output:", resp.text)

    # Clean up test file
    if test_path.exists():
        test_path.unlink()

if __name__ == "__main__":
    test_machine_signal()
