# MachineSense Python FastAPI Backend

The MachineSense backend is an acoustic signal processing service built with Python 3.11, FastAPI, Librosa, SciPy, NumPy, and Matplotlib. It analyzes uploaded heavy machinery audio recordings, extracts FFT frequency spectrums, calculates acoustic spectral features, and generates Mel Spectrogram PNG images & 13 MFCC coefficient representations.

---

## 1. Setup & Environment

### Prerequisites
- Python 3.11 or higher
- `pip`

### Virtual Environment Setup

**Windows (PowerShell / Command Prompt):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 2. Running the Server

Start the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The interactive API documentation will be available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 3. API Endpoints

### 1. Health Check
- **Endpoint**: `GET /api/health`
- **Response**:
```json
{
  "status": "ok",
  "service": "MachineSense Backend"
}
```

### 2. Audio Analysis
- **Endpoint**: `POST /api/analyze`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `audio`: File (`.wav`, `.mp3`, `.flac`, `.m4a`, max 50 MB)
  - `machine_id`: String (e.g., `"PUMP-ID-00"`)

- **Response Format**:
```json
{
  "analysis_id": "a9c78d1f2b...",
  "machine_id": "PUMP-ID-00",
  "spectrogram": {
    "url": "/api/analysis/a9c78d1f2b.../spectrogram",
    "format": "image/png"
  },
  "audio": {
    "duration": 10.24,
    "sample_rate": 16000,
    "channels": 1,
    "number_of_samples": 163840
  },
  "signal": {
    "rms": 0.1824,
    "peak_amplitude": 0.9201,
    "crest_factor": 5.04,
    "signal_quality": "good"
  },
  "waveform": {
    "sample_rate": 16000,
    "samples": [0.012, 0.452, -0.218, "... (500 downsampled points)"]
  },
  "frequency": {
    "dominant_frequency_hz": 1620.4,
    "top_peaks": [
      { "frequency_hz": 1620.4, "magnitude": 1.0 },
      { "frequency_hz": 810.2, "magnitude": 0.64 }
    ],
    "spectrum": {
      "frequencies_hz": [0.0, 20.0, 40.0, "... (400 downsampled points)"],
      "magnitudes": [0.01, 0.05, 0.12, "... (400 normalized magnitude points)"]
    }
  },
  "spectral_features": {
    "centroid_hz": 1840.2,
    "bandwidth_hz": 920.4,
    "rolloff_hz": 3200.1,
    "flatness": 0.02,
    "zero_crossing_rate": 0.08
  },
  "mel_spectrogram": {
    "n_mels": 128,
    "frames": 320
  },
  "mfcc": {
    "n_mfcc": 13,
    "frames": 320,
    "mean": [...],
    "std": [...]
  },
  "ml": {
    "status": "not_available",
    "message": "Machine-learning model will be added after dataset preparation and training."
  }
}
```

### 3. Spectrogram Image Retrieval
- **Endpoint**: `GET /api/analysis/{analysis_id}/spectrogram`
- **Response**: PNG Image (`image/png`)

---

## 4. Running Tests

Execute tests with Pytest:

```bash
pytest tests/
```
