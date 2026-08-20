# 🎙️ MachineSense — Acoustic Intelligence Station

MachineSense is an advanced AI-powered predictive maintenance system that analyzes machine acoustics to detect abnormal mechanical conditions in real-time. Built for industrial machinery diagnostics (such as centrifugal pumps and motors), MachineSense uses audio signal processing, machine-invariant acoustic feature extraction, noise-resilient gating, and Random Forest classification trained on the MIMII dataset.

---

## 🌟 Key System Capabilities

- **Real-Time Audio Analysis**: Analyzes 16 kHz PCM acoustic recordings from microphone input or uploaded WAV files.
- **Machine-Invariant Feature Extraction**: Extracts 15 core acoustic features (MFCCs, spectral centroid, spectral bandwidth, spectral rolloff, spectral flatness, RMS, crest factor) that decouple machine-specific acoustic signatures from physical anomaly indicators.
- **Acoustic Presence & Noise Gating**:
  - **Duration Gate**: Enforces valid recording lengths (9.0s – 12.0s).
  - **Silence Gate**: Detects digital silence (RMS < 0.002, Peak < 0.008).
  - **Spectral Flatness Gate**: Filters out uninformative background room noise and mic static (Flatness $\ge 0.25$).
- **Multi-Asset Telemetry**: Supports independent monitoring across multiple machine assets (`id_00`, `id_02`, `id_04`, `id_06`).
- **Interactive Visualizations**:
  - **Time-Domain Waveform**: 500-point vector SVG curve displaying real acoustic amplitude oscillations.
  - **Log-Mel Spectrogram**: Dynamic dB power spectrum image generated via `librosa` and `matplotlib`.
  - **FFT Spectrum Decomposition**: Real-time spectral breakdown with dominant frequency peak tracking.
- **Persistent Analytics & Fleet Trends**:
  - SQLite database history storage with source tagging (`REC` vs `UPLOADED`).
  - Active fleet condition aggregation and 7-day health trend tracking.

---

## 🏗️ Architecture & Technology Stack

```
MachineSense/
├── backend/                  # FastAPI REST Service & ML Pipeline
│   ├── app/
│   │   ├── main.py           # FastAPI Application Entry & Static Serving
│   │   ├── config.py         # App Configuration & Storage Paths
│   │   ├── database/db.py    # SQLite Database Persistence Layer
│   │   ├── routes/           # API Endpoints (/api/analyze, /api/history, etc.)
│   │   └── services/         # Audio Processor & ML Service Singletons
│   ├── machinesense.db       # SQLite Database
│   └── uploads/              # Saved Spectrograms & Temp Files
├── frontend/                 # React 18 + Vite Web Interface
│   ├── src/
│   │   ├── components/       # Waveform, TrendChart, Top & Sidebar Nav
│   │   ├── pages/            # Analyze, Results, History, Dashboard, Frequency
│   │   └── data/             # Asset Telemetry Configuration
│   ├── index.html            # Main HTML Entry
│   └── vite.config.js        # Vite Build & Dev Server Config
└── ml/                       # Machine Learning Model & Training Modules
    ├── features.py           # Machine-Invariant Acoustic Feature Extractor
    └── models/               # Trained Random Forest Model & Pipeline Metadata
```

---

## 🛠️ Quickstart & Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Activate environment:
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The application will be accessible at:
- **Frontend Dashboard**: `http://localhost:3000`
- **FastAPI OpenAPI Documentation**: `http://127.0.0.1:8000/docs`

---

## 📄 License
Designed for industrial predictive maintenance and acoustic diagnostics.
