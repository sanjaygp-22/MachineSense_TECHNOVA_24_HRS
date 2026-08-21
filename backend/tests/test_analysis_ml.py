import pytest
import io
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.services.ml_service import get_ml_service

client = TestClient(app)

REAL_NORMAL_WAV = Path("D:/pump/id_00/normal/00000000.wav")
REAL_ABNORMAL_WAV = Path("D:/pump/id_00/abnormal/00000000.wav")


def test_health_check_includes_ml_model():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["ml_model"] == "loaded"


def test_analyze_normal_wav():
    assert REAL_NORMAL_WAV.exists(), "Real test WAV missing"
    with open(REAL_NORMAL_WAV, "rb") as f:
        response = client.post(
            "/api/analyze",
            files={"audio": ("00000000.wav", f, "audio/wav")},
            data={"machine_id": "id_00"}
        )

    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    pred = data["prediction"]
    assert pred["label"] == "normal"
    assert pred["class"] == 0
    assert 0.0 <= pred["abnormal_probability"] <= 1.0
    assert 0.0 <= pred["normal_probability"] <= 1.0
    assert pred["normal_probability"] > pred["abnormal_probability"]

    assert data["machine_id"] == "id_00"
    assert "audio" in data
    assert "signal" in data
    assert "frequency" in data
    assert "spectral_features" in data


def test_analyze_abnormal_wav():
    assert REAL_ABNORMAL_WAV.exists(), "Real test WAV missing"
    with open(REAL_ABNORMAL_WAV, "rb") as f:
        response = client.post(
            "/api/analyze",
            files={"audio": ("00000000.wav", f, "audio/wav")},
            data={"machine_id": "id_00"}
        )

    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    pred = data["prediction"]
    assert pred["label"] == "abnormal"
    assert pred["class"] == 1
    assert 0.0 <= pred["abnormal_probability"] <= 1.0
    assert 0.0 <= pred["normal_probability"] <= 1.0
    assert pred["abnormal_probability"] > pred["normal_probability"]


def test_analyze_invalid_file_format():
    fake_txt = io.BytesIO(b"This is not a WAV audio file")
    response = client.post(
        "/api/analyze",
        files={"audio": ("test.txt", fake_txt, "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_analyze_model_unavailable(monkeypatch):
    ml_service = get_ml_service()
    monkeypatch.setattr(ml_service, "is_model_loaded", False)
    monkeypatch.setattr(ml_service, "load_error", "Simulated ML Model Failure")

    with open(REAL_NORMAL_WAV, "rb") as f:
        response = client.post(
            "/api/analyze",
            files={"audio": ("00000000.wav", f, "audio/wav")}
        )

    assert response.status_code == 500
    assert "ML Model is unavailable" in response.json()["detail"]
