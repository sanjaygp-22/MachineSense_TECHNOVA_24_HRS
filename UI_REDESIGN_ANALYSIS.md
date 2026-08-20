# MachineSense Application UI Redesign & Architecture Analysis Report

**File:** `UI_REDESIGN_ANALYSIS.md`  
**Workspace:** `d:\projects\MachineSense2`  
**Date:** August 20, 2026  

---

## 1. Executive Summary

This report provides a detailed inspection of the **MachineSense** codebase. MachineSense is an acoustic signal processing and machine-invariant anomaly detection platform built with a React frontend, a Python FastAPI backend, custom Librosa audio processing, a machine-invariant Random Forest ML inference engine, and a persistent SQLite database.

---

## 2. FRONTEND ARCHITECTURE

### 2.1 Framework & Build Tools
* **Core Framework:** React 18.3.1 (using JSX)
* **Build System & Dev Server:** Vite 5.4.1 (ES Modules mode)
* **Icons:** `lucide-react` (v0.427.0) and Google Material Symbols Outlined font
* **Entry HTML:** `frontend/index.html` (mounts React root into `<div id="root"></div>`)
* **Entry JavaScript:** `frontend/src/main.jsx` (renders `<App />` inside `React.StrictMode`)

### 2.2 Frontend Folder Structure
```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── .env
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── config.js
    ├── index.css
    ├── components/
    │   ├── audio/
    │   │   ├── AudioFileCard.jsx
    │   │   └── AudioUploader.jsx
    │   ├── cards/
    │   │   └── MachineCard.jsx
    │   ├── charts/
    │   │   ├── TrendChart.jsx
    │   │   └── WaveformVisualizer.jsx
    │   └── layout/
    │       ├── AmbientShader.jsx
    │       ├── BottomNavigation.jsx
    │       └── TopNavigation.jsx
    ├── pages/
    │   ├── Analyze.jsx
    │   ├── Dashboard.jsx
    │   ├── FrequencyAnalysis.jsx
    │   ├── History.jsx
    │   ├── MachineHealth.jsx
    │   ├── Machines.jsx
    │   ├── Processing.jsx
    │   ├── Results.jsx
    │   └── Settings.jsx
    ├── data/
    │   └── mockData.js
    └── utils/
        └── audioStore.js
```

### 2.3 Pages & Components Overview

#### Pages (9 Total)
1. **`Dashboard.jsx`**: Main overview dashboard featuring the overall fleet health score ring, active machine status cards, 7-day health trend chart, and instant action trigger for analysis.
2. **`Machines.jsx`**: Machine fleet asset directory displaying individual machine status cards and filter options.
3. **`MachineHealth.jsx`**: Individual machine asset telemetry and deep health inspection page.
4. **`Analyze.jsx`**: Machine selector and acoustic capture page. Includes live microphone trigger and drag-and-drop audio file uploader.
5. **`Processing.jsx`**: Real-time progress checklist view while analyzing audio. Calls backend API `POST /api/analyze` using `FormData`.
6. **`Results.jsx`**: Analysis results view. Displays model prediction (`NORMAL`/`ABNORMAL`), confidence percentages, acoustic feature metrics, recommendations, and Mel Spectrogram modal.
7. **`FrequencyAnalysis.jsx`**: FFT spectrum view detailing dominant frequency, top 5 spectral peak frequencies, and spectrum magnitude graph.
8. **`History.jsx`**: Persistent SQLite analysis history log table with machine filter chips (`All`, `id_00`, `id_02`, `id_04`, `id_06`) and aggregate statistics.
9. **`Settings.jsx`**: System configuration, threshold adjustments, and API endpoint settings.

#### Components (8 Total)
1. **`AudioUploader.jsx`**: Drag-and-drop & browse file component. Supports WAV, MP3, FLAC, M4A up to 50MB. Extracts duration via HTML5 `Audio`.
2. **`AudioFileCard.jsx`**: Audio file preview component with play/pause controls, file metadata display, and removal action.
3. **`MachineCard.jsx`**: Status card for displaying individual machine asset health, location, and key statistics.
4. **`TrendChart.jsx`**: Custom Canvas/SVG 7-day health trend line chart.
5. **`WaveformVisualizer.jsx`**: Animated audio waveform bars.
6. **`AmbientShader.jsx`**: WebGL Canvas component rendering an animated GLSL shader background.
7. **`TopNavigation.jsx`**: Desktop & mobile top navigation bar with brand logo and status indicator.
8. **`BottomNavigation.jsx`**: Mobile bottom navigation tab bar with route highlighting.

### 2.4 Routing System
* **Library:** `react-router-dom` (v6.26.1)
* **Configuration:** Defined in `frontend/src/App.jsx` using `<BrowserRouter>`, `<Routes>`, `<Route>`:
  * `/` → Redirects to `/dashboard`
  * `/dashboard` → `Dashboard.jsx`
  * `/machines` → `Machines.jsx`
  * `/health` → `MachineHealth.jsx`
  * `/analyze` → `Analyze.jsx`
  * `/processing` → `Processing.jsx`
  * `/results` → `Results.jsx`
  * `/frequency` → `FrequencyAnalysis.jsx`
  * `/history` → `History.jsx`
  * `/settings` → `Settings.jsx`
  * `*` → Redirects to `/dashboard`

### 2.5 Styling System
* **Tailwind CSS:** Version 3.4.10 with PostCSS and Autoprefixer.
* **Design Tokens:** Configured in `frontend/tailwind.config.js`:
  * Colors: Dark theme (`background`: `#0a0e14`, `primary`: `#00e5ff`, `secondary`: `#02c953`, `error`: `#ffb4ab`).
  * Custom font families (`sans`, `headline`, `mono`, `label`).
  * Custom breakpoints and layout container widths.
* **Custom CSS Utilities:** Defined in `frontend/src/index.css` (glassmorphism `.glass-panel`, `.glow-accent`, `.pulse-ring`, `.scanning-effect`).

### 2.6 API Communication & State Management
* **Endpoint URL:** `frontend/src/config.js` exports `API_URL` (defaults to `http://127.0.0.1:8000`).
* **Temporary Audio In-Memory Store:** `frontend/src/utils/audioStore.js` keeps reference to DOM `File` object during React Router navigation.
* **API Calls:**
  * `POST /api/analyze`: In `Processing.jsx`, sends `FormData` containing `audio` (File Blob), `machine_id` (string), `request_id` (string).
  * `GET /api/history`: In `History.jsx`, fetches recent SQLite records.
  * `GET /api/history/{machine_id}`: In `History.jsx`, fetches machine-filtered history and summary counts.
  * `GET /api/analysis/{analysis_id}/spectrogram`: In `Results.jsx`, loads Mel Spectrogram PNG image inside a modal.

---

## 3. BACKEND ARCHITECTURE

### 3.1 FastAPI Structure
* **Framework:** Python FastAPI web framework served with Uvicorn.
* **Entry Point:** `backend/app/main.py`. Initializes CORS middleware, triggers SQLite DB schema setup (`init_db()`), warms up ML model (`get_ml_service()`), and mounts routes under `/api`.
* **Config:** `backend/app/config.py` (specifies CORS origins, file size limit 50MB, upload directory `backend/uploads/`, DB path `backend/machinesense.db`).

### 3.2 Backend Directory Structure
```
backend/
├── machinesense.db
├── benchmark_pipeline.py
├── requirements.txt
└── app/
    ├── main.py
    ├── config.py
    ├── database/
    │   └── db.py
    ├── routes/
    │   ├── analysis.py
    │   ├── health.py
    │   └── history.py
    └── services/
        ├── analysis_store.py
        ├── audio_processor.py
        └── ml_service.py
```

### 3.3 Endpoints Summary
1. `GET /`
   * Root welcome endpoint with API documentation links.
2. `GET /api/health`
   * Health check returning service status and ML model load state (`"loaded"` or `"unavailable"`).
3. `POST /api/analyze`
   * **Request:** `Multipart/Form-Data`
     * `audio`: File upload (`.wav`, `.mp3`, `.flac`, `.m4a`)
     * `machine_id`: Form string (default `"id_00"`)
     * `request_id`: Form string (optional)
   * **Response:** JSON Object containing:
     * `analysis_id`: Unique request ID
     * `machine_id`: Target machine ID
     * `prediction`: `{ label: "normal" | "abnormal", class: 0 | 1, abnormal_probability: float, normal_probability: float }`
     * `audio`: `{ duration, sample_rate, channels, number_of_samples }`
     * `signal`: `{ rms, peak_amplitude, crest_factor, signal_quality }`
     * `frequency`: `{ dominant_frequency_hz, top_peaks, spectrum: { frequencies_hz, magnitudes } }`
     * `spectral_features`: `{ centroid_hz, bandwidth_hz, rolloff_hz, flatness, zero_crossing_rate }`
     * `mel_spectrogram`: `{ n_mels, frames }`
     * `mfcc`: `{ n_mfcc, frames, mean, std }`
     * `spectrogram`: `{ url: "/api/analysis/{analysis_id}/spectrogram", format: "image/png" }`
4. `GET /api/analysis/{analysis_id}/spectrogram`
   * Returns in-memory rendered PNG image bytes (`image/png`).
5. `GET /api/history?limit=50`
   * Returns JSON list of recent SQLite analysis records sorted newest first.
6. `GET /api/history/{machine_id}?limit=50`
   * Returns JSON object with target machine summary stats (`total_analyses`, `normal_count`, `abnormal_count`, `latest_status`, `latest_dominant_frequency_hz`) and records list.

---

## 4. MACHINE LEARNING (ML) ARCHITECTURE

### 4.1 Production Model Artifacts
* **Model Pipeline:** `ml/models/machine_invariant_rf_pipeline.joblib` (Scikit-Learn Random Forest Pipeline with scaler).
* **Model Metadata:** `ml/models/machine_invariant_rf_metadata.json` (stores selected 15 machine-invariant feature names and accuracy metrics).

### 4.2 Inference Entry Points
1. **FastAPI Service:** `backend/app/services/ml_service.py` (`MLService` singleton loaded once during server startup).
2. **Standalone Script:** `ml/predict.py` (`predict_audio(audio_path)`).

### 4.3 Input & Feature Extraction Pipeline
* **Input Audio:** 16,000 Hz mono audio array (`y_norm`) normalized to peak amplitude `[-1.0, 1.0]`.
* **Feature Extractor:** `ml/features.py` (`extract_acoustic_features()`).
  * Computes 33 raw acoustic numerical features (13 MFCC means, 13 MFCC stds, RMS energy, spectral centroid, spectral bandwidth, spectral rolloff, spectral flatness, zero crossing rate, dominant frequency).
  * Uses single-pass STFT for high-speed feature computation.
* **Production Feature Selector:** Filters raw 33 features down to 15 machine-invariant production features in exact metadata order.

### 4.4 Model Output Format
```json
{
  "machine_id": "id_00",
  "prediction": {
    "label": "normal",
    "class": 0,
    "abnormal_probability": 0.0267,
    "normal_probability": 0.9733
  }
}
```

---

## 5. DATABASE ARCHITECTURE (SQLite)

### 5.1 Structure & Location
* **Database File:** `backend/machinesense.db`
* **DB Module:** `backend/app/database/db.py`

### 5.2 SQLite Schema (`analysis_history` table)
```sql
CREATE TABLE IF NOT EXISTS analysis_history (
    analysis_id TEXT PRIMARY KEY,
    machine_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    timestamp_epoch REAL NOT NULL,
    prediction_label TEXT NOT NULL,
    prediction_class INTEGER NOT NULL,
    abnormal_probability REAL NOT NULL,
    normal_probability REAL NOT NULL,
    confidence REAL NOT NULL,
    dominant_frequency_hz REAL NOT NULL,
    rms REAL NOT NULL,
    signal_quality TEXT NOT NULL,
    centroid_hz REAL NOT NULL,
    duration REAL NOT NULL,
    sample_rate INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_machine_created 
ON analysis_history(machine_id, timestamp_epoch DESC);
```

### 5.3 History Data Flow
1. Upon completing an analysis request in `POST /api/analyze`, the route invokes `save_analysis_record(full_response)`.
2. The result is inserted into `analysis_history` using `INSERT OR REPLACE INTO`.
3. When the user navigates to the History page in the frontend, `History.jsx` calls `GET /api/history` or `GET /api/history/{machine_id}`.
4. `db.py` queries SQLite with `ORDER BY timestamp_epoch DESC` and returns records & machine summary counters to the frontend table.

---

## 6. END-TO-END SYSTEM INTEGRATION FLOW

The exact step-by-step execution flow of the MachineSense application:

```
[1. User selects/records audio file in UI]
             │
             ▼
[2. Analyze.jsx / AudioUploader.jsx]
   • Saves DOM File object in audioStore.js
   • Navigates to /processing with machine_id
             │
             ▼
[3. Processing.jsx]
   • Prepares FormData (audio Blob, machine_id, request_id)
   • Makes HTTP POST to API_URL/api/analyze
             │
             ▼
[4. FastAPI backend/app/routes/analysis.py]
   • Receives UploadFile & validates size/extension
   • Saves temporary audio file to backend/uploads/
             │
             ▼
[5. Audio Processing (backend/app/services/audio_processor.py & ml/preprocessing.py)]
   • Loads audio with SoundFile / Librosa
   • Converts to 16,000 Hz Mono
   • Peak normalizes waveform [-1.0, 1.0]
   • Computes FFT spectrum, STFT, Mel Spectrogram, MFCCs, Spectral Features
   • Generates Mel Spectrogram PNG image in memory
             │
             ▼
[6. ML Inference Engine (backend/app/services/ml_service.py & ml/features.py)]
   • Extracts 33 acoustic features from normalized signal
   • Subsets vector to 15 machine-invariant production features
   • Scores vector with Random Forest pipeline (.joblib)
   • Obtains prediction label ("normal"/"abnormal") & probability scores
             │
             ▼
[7. SQLite Database Persistence (backend/app/database/db.py)]
   • Auto-saves analysis record into backend/machinesense.db (analysis_history table)
   • Caches result & spectrogram PNG in memory (analysis_store.py)
   • Deletes temporary upload file from disk
             │
             ▼
[8. API Response returned to Frontend]
   • Returns complete JSON response payload to Processing.jsx
             │
             ▼
[9. Frontend Results & History Display]
   • Processing.jsx receives JSON and navigates to Results.jsx
   • Results.jsx displays prediction status, confidence, acoustic metrics & spectrogram
   • History.jsx fetches logged records from GET /api/history
```

---

## 7. UI REDESIGN BOUNDARIES & SAFE FILES

### Files Safe to Redesign (Frontend UI Scope)
The following files control the visual appearance, layout, styling, and user experience, and can be completely redesigned:

* **Page Components:**
  * `frontend/src/pages/Dashboard.jsx`
  * `frontend/src/pages/Machines.jsx`
  * `frontend/src/pages/MachineHealth.jsx`
  * `frontend/src/pages/Analyze.jsx`
  * `frontend/src/pages/Processing.jsx`
  * `frontend/src/pages/Results.jsx`
  * `frontend/src/pages/FrequencyAnalysis.jsx`
  * `frontend/src/pages/History.jsx`
  * `frontend/src/pages/Settings.jsx`
* **UI Components:**
  * `frontend/src/components/audio/AudioUploader.jsx`
  * `frontend/src/components/audio/AudioFileCard.jsx`
  * `frontend/src/components/cards/MachineCard.jsx`
  * `frontend/src/components/charts/TrendChart.jsx`
  * `frontend/src/components/charts/WaveformVisualizer.jsx`
  * `frontend/src/components/layout/TopNavigation.jsx`
  * `frontend/src/components/layout/BottomNavigation.jsx`
  * `frontend/src/components/layout/AmbientShader.jsx`
* **Styles & HTML:**
  * `frontend/src/index.css`
  * `frontend/tailwind.config.js`
  * `frontend/index.html`

### Immutable Interfaces (MUST NOT BE BROKEN)
When redesigning the UI components, the following API contracts and data bridges must remain intact:

1. **`frontend/src/config.js`**: `API_URL` import must be maintained.
2. **`frontend/src/utils/audioStore.js`**: Functions `setActiveAudioFile`, `getActiveAudioFile`, `clearActiveAudioFile` must be used to pass raw DOM `File` objects across routes.
3. **`POST /api/analyze` FormData Contract**: Must continue sending `audio` (file), `machine_id` (string), `request_id` (string).
4. **API Response Structure**: The redesigned UI must consume the exact JSON response keys (`prediction.label`, `prediction.abnormal_probability`, `frequency.dominant_frequency_hz`, `spectrogram.url`, etc.).
5. **Backend, ML, SQLite, and Audio Processing files**: No modifications to `backend/` or `ml/`.

---
*Report compiled successfully. Analysis completed without codebase modifications.*
