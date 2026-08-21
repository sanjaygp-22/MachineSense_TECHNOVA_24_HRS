import io
import wave
import struct
import math
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def generate_synthetic_wav(frequency_hz: float = 1000.0, duration_sec: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generates a synthetic 16-bit mono WAV file in memory."""
    buf = io.BytesIO()
    num_samples = int(sample_rate * duration_sec)

    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = float(i) / sample_rate
            sample = int(32767.0 * 0.5 * math.sin(2.0 * math.pi * frequency_hz * t))
            wav_file.writeframes(struct.pack('<h', sample))

    return buf.getvalue()


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "MachineSense" in data["service"]


def test_analyze_valid_audio():
    wav_bytes = generate_synthetic_wav(frequency_hz=1000.0, duration_sec=1.0, sample_rate=16000)

    files = {
        "audio": ("test_motor.wav", wav_bytes, "audio/wav")
    }
    data = {
        "machine_id": "PUMP-ID-00"
    }

    response = client.post("/api/analyze", files=files, data=data)
    assert response.status_code == 200

    res = response.json()
    assert "analysis_id" in res
    assert res["machine_id"] == "PUMP-ID-00"

    # Audio info
    assert res["audio"]["sample_rate"] == 16000
    assert res["audio"]["duration"] >= 0.9

    # Waveform downsampled data
    assert "waveform" in res
    assert res["waveform"]["sample_rate"] == 16000
    assert len(res["waveform"]["samples"]) > 0
    assert len(res["waveform"]["samples"]) <= 500

    # Frequency checks & downsampled spectrum array
    assert "dominant_frequency_hz" in res["frequency"]
    assert abs(res["frequency"]["dominant_frequency_hz"] - 1000.0) < 50.0

    assert "spectrum" in res["frequency"]
    assert "frequencies_hz" in res["frequency"]["spectrum"]
    assert "magnitudes" in res["frequency"]["spectrum"]
    assert len(res["frequency"]["spectrum"]["frequencies_hz"]) > 0
    assert len(res["frequency"]["spectrum"]["frequencies_hz"]) <= 450

    # Spectrogram metadata & URL
    assert "spectrogram" in res
    assert res["spectrogram"]["format"] == "image/png"
    assert res["spectrogram"]["url"].startswith("/api/analysis/")

    # Spectral features & MFCC
    assert "centroid_hz" in res["spectral_features"]
    assert res["mel_spectrogram"]["n_mels"] == 128
    assert res["mfcc"]["n_mfcc"] == 13
    assert len(res["mfcc"]["mean"]) == 13
    assert res["ml"]["status"] == "not_available"

    # Test Spectrogram PNG endpoint using the analysis_id
    analysis_id = res["analysis_id"]
    png_res = client.get(f"/api/analysis/{analysis_id}/spectrogram")
    assert png_res.status_code == 200
    assert png_res.headers["content-type"] == "image/png"
    assert len(png_res.content) > 1000


def test_spectrogram_invalid_id():
    response = client.get("/api/analysis/invalid_id_12345/spectrogram")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_analyze_unsupported_format():
    files = {
        "audio": ("test_file.txt", b"Hello World", "text/plain")
    }
    response = client.post("/api/analyze", files=files, data={"machine_id": "PMP-002"})
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()


def test_analyze_empty_file():
    files = {
        "audio": ("empty.wav", b"", "audio/wav")
    }
    response = client.post("/api/analyze", files=files, data={"machine_id": "PMP-002"})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()
