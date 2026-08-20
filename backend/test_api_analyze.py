import requests
import numpy as np
import soundfile as sf
from pathlib import Path

def test_api_endpoint():
    api_url = "http://127.0.0.1:8000/api/analyze"
    test_dir = Path("test_audio_samples")
    test_dir.mkdir(exist_ok=True)

    # 1. Create pure digital silence WAV
    silence_path = test_dir / "digital_silence.wav"
    sr = 16000
    zeros = np.zeros(sr * 3, dtype=np.float32)
    sf.write(str(silence_path), zeros, sr)

    print("\n=======================================================")
    print("SENDING DIGITAL SILENCE WAV TO POST /api/analyze...")
    print("=======================================================")
    with open(silence_path, "rb") as f:
        files = {"audio": ("digital_silence.wav", f, "audio/wav")}
        data = {"machine_id": "id_00"}
        resp = requests.post(api_url, files=files, data=data)

    print(f"HTTP Status Code: {resp.status_code}")
    json_data = resp.json()
    print("Response Content:", json_data)

    if silence_path.exists():
        silence_path.unlink()
    if test_dir.exists():
        test_dir.rmdir()

if __name__ == "__main__":
    test_api_endpoint()
