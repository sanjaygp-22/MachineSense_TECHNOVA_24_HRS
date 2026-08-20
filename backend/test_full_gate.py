import requests
import numpy as np
import soundfile as sf
from pathlib import Path

def run_gate_test():
    api_url = "http://127.0.0.1:8000/api/analyze"
    test_path = Path("digital_silence_test.wav")

    # Generate 3s digital silence WAV
    sr = 16000
    zeros = np.zeros(sr * 3, dtype=np.float32)
    sf.write(str(test_path), zeros, sr)

    print("\n" + "=" * 70)
    print("TESTING DIGITAL SILENCE WAV AGAINST POST /api/analyze")
    print("=" * 70)

    with open(test_path, "rb") as f:
        files = {"audio": ("digital_silence_test.wav", f, "audio/wav")}
        data = {"machine_id": "id_00"}
        resp = requests.post(api_url, files=files, data=data)

    print(f"HTTP Status Code: {resp.status_code}")
    if resp.status_code == 200:
        json_data = resp.json()
        print("\nAPI Response Prediction Object:")
        print(json_data.get("prediction"))
        print(f"\nStatus Field: {json_data.get('prediction', {}).get('status')}")
        print(f"Label Field:  {json_data.get('prediction', {}).get('label')}")
        print(f"Message Field:{json_data.get('prediction', {}).get('message')}")
    else:
        print("API Error Output:", resp.text)

    # Clean up test file
    if test_path.exists():
        test_path.unlink()

if __name__ == "__main__":
    run_gate_test()
