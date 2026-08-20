import requests
from pathlib import Path

def test_operating_machine_wav():
    api_url = "http://127.0.0.1:8000/api/analyze"
    sample_wav = Path("uploads/00000005.wav")

    if not sample_wav.exists():
        # Search for any .wav in zip_extracted
        found = list(Path("../zip_extracted").rglob("*.wav"))
        if found:
            sample_wav = found[0]

    print("\n" + "=" * 70)
    print(f"TESTING OPERATING MACHINE WAV ({sample_wav}) AGAINST POST /api/analyze")
    print("=" * 70)

    with open(sample_wav, "rb") as f:
        files = {"audio": (sample_wav.name, f, "audio/wav")}
        data = {"machine_id": "id_00"}
        resp = requests.post(api_url, files=files, data=data)

    print(f"HTTP Status Code: {resp.status_code}")
    if resp.status_code == 200:
        json_data = resp.json()
        print("\nAPI Response Prediction Object:")
        print(json_data.get("prediction"))
        print(f"\nStatus Field: {json_data.get('prediction', {}).get('status')}")
        print(f"Label Field:  {json_data.get('prediction', {}).get('label')}")
        print(f"Confidence:   {json_data.get('prediction', {}).get('normal_probability')}")
    else:
        print("API Error Output:", resp.text)

if __name__ == "__main__":
    test_operating_machine_wav()
