# MachineSense Industrial Acoustic Intelligence Station — Frontend Redesign Plan

**File:** `FRONTEND_REDESIGN_PLAN.md`  
**Workspace:** `d:\projects\MachineSense2`  
**Target:** Industrial Acoustic Intelligence Station UI Integration  
**Date:** August 20, 2026  

---

## 1. Executive Strategy & Goal

The goal of this project is to integrate the high-contrast, laboratory-grade visual design from `stitch_machinesense_acoustic_intelligence_station.zip` into the existing MachineSense2 React frontend while preserving 100% of the working backend, ML model, audio processing, SQLite database, and API contracts.

### Core Equation
$$\text{NEW INDUSTRIAL UI DESIGN} + \text{EXISTING WORKING FUNCTIONALITY} = \text{MACHINESENSE FINAL FRONTEND}$$

---

## 2. Codebase & ZIP Inspection

### 2.1 Existing Frontend Structure
```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── config.js (`API_URL`)
    ├── index.css
    ├── components/
    │   ├── audio/ (AudioUploader.jsx, AudioFileCard.jsx)
    │   ├── cards/ (MachineCard.jsx)
    │   ├── charts/ (TrendChart.jsx, WaveformVisualizer.jsx)
    │   └── layout/ (TopNavigation.jsx, BottomNavigation.jsx, AmbientShader.jsx)
    ├── pages/
    │   ├── Dashboard.jsx
    │   ├── Machines.jsx
    │   ├── MachineHealth.jsx
    │   ├── Analyze.jsx
    │   ├── Processing.jsx
    │   ├── Results.jsx
    │   ├── FrequencyAnalysis.jsx
    │   ├── History.jsx
    │   └── Settings.jsx
    ├── data/ (mockData.js)
    └── utils/ (audioStore.js)
```

### 2.2 ZIP Reference Structure (`stitch_machinesense_acoustic_intelligence_station.zip`)
```
zip_extracted/stitch_machinesense_acoustic_intelligence_station/
├── machinesense_industrial/
│   └── DESIGN.md (Design System Tokens & Guidelines)
├── machinesense_dashboard_high_contrast/ (Dashboard screen HTML reference)
├── machine_inventory_high_contrast/ (Machine Inventory screen HTML reference)
├── acoustic_analysis_high_contrast/ (Analyze Machine screen HTML reference)
├── analysis_results_high_contrast/ (Results / Diagnostic screen HTML reference)
├── analysis_history_high_contrast/ (History screen HTML reference)
├── asset_health_professional_view/ (Machine Health detail screen HTML reference)
├── research_insights_high_contrast/ (Research / AI Insights screen HTML reference)
├── settings_high_contrast/ (Settings screen HTML reference)
└── shader/ (Shader GLSL visual reference)
```

---

## 3. ZIP Design System Specifications

### 3.1 Color Palette & Theme Tokens
* **Base Surface:** Dark Charcoal (`#111316` / `#121417`)
* **Elevated Panels:** `#1a1c1f` (`surface-container-low`), `#1e2023` (`surface-container`), `#282a2d` (`surface-container-high`), `#333538` (`surface-container-highest`)
* **Primary Accent (Cyan/Electric Blue):** `#00e5ff` (`primary-container`), `#00daf3` (`primary-fixed-dim`), `#c3f5ff` (`primary`), with `0 0 12px rgba(0, 229, 255, 0.4)` illuminated hardware glow.
* **Status Semantic Accents:**
  * **Normal / Optimal:** Emerald Green `#4edea3` / `#00a572` / `#02c953` (`secondary`)
  * **Degrading / Warning:** Amber `#ffc681` / `#ffb95f` (`tertiary-container`)
  * **Critical / Anomaly:** Industrial Red `#ffb4ab` / `#93000a` / `#ba1a1a` (`error`)
* **Technical Outlines & Borders:** `1px solid #3b494c` / `#2D3139` (`outline-variant`) for a blueprint instrument aesthetic.

### 3.2 Typography & Data Hierarchy
* **UI Labels & Headers:** `Inter` (`font-sans`, `font-headline-lg`, `font-label-caps`)
* **Machine Data & Telemetry:** `JetBrains Mono` (`font-mono`, `font-data-lg`, `font-data-sm`) for machine IDs, frequencies (Hz), amplitudes (dB), RMS, timestamps, and model prediction percentages.

### 3.3 Geometry & Shapes
* **Buttons & Inputs:** `4px` (0.25rem) radius (`rounded-DEFAULT` / `rounded-sm`).
* **Panels & Cards:** `8px` - `12px` radius (`rounded-lg` / `rounded-xl`) with technical 1px borders.
* **Status Indicators:** Circular `50%` radius pulsing status dots.

---

## 4. API-Connected Components & Protection Rules

### 4.1 Connected Components & Endpoint Contracts
1. **`Processing.jsx`**:
   * Connected to `POST /api/analyze`.
   * Passes `FormData` containing `audio` (File Blob), `machine_id` (string), `request_id` (string).
   * **Rule:** Must NOT change request field names or content type.
2. **`Results.jsx`**:
   * Receives JSON response payload from `Processing.jsx`.
   * Displays `prediction.label`, `prediction.abnormal_probability`, `frequency.dominant_frequency_hz`, `signal.rms`, `spectral_features.centroid_hz`, and Mel Spectrogram PNG image `spectrogram.url`.
   * **Rule:** Must consume real payload fields without inventing fake backend metrics.
3. **`History.jsx`**:
   * Connected to `GET /api/history` and `GET /api/history/{machine_id}`.
   * Displays SQLite-backed analysis records table and summary statistics.
   * **Rule:** Must continue to query real SQLite data.

### 4.2 Untouched Files (STRICT PROTECTION)
* `backend/**/*` (Python FastAPI backend, `analysis.py`, `audio_processor.py`, `ml_service.py`, `db.py`, `machinesense.db`)
* `ml/**/*` (Random forest model artifacts, `predict.py`, `features.py`, `preprocessing.py`)
* `frontend/src/config.js` (`API_URL`)
* `frontend/src/utils/audioStore.js` (DOM File memory storage bridge)

---

## 5. Components to Reuse & Redesign

### 5.1 Shared Layout & Shell Components
* **`TopNavigation.jsx`**: Redesign into the industrial top app header featuring the MachineSense brand emblem, live status indicator, asset monitoring trigger, and desktop/mobile responsiveness.
* **`BottomNavigation.jsx` / Navigation Drawer**: Redesign mobile bottom navbar and desktop sidebar navigation with active route highlighting.

### 5.2 Page Components to Redesign
1. **`Dashboard.jsx`**: Implement radial progress health score ring, active machine status cards, 7-day trend chart, recent alerts banner, and quick analysis trigger.
2. **`Machines.jsx`**: Redesign machine inventory grid cards with real `machinesData`, status badges (`NORMAL`, `DEGRADING`, `CRITICAL`), signal quality meters, and direct analysis actions.
3. **`MachineHealth.jsx`**: Redesign detailed asset inspection view with frequency sparklines, telemetry breakdown, and diagnostic logs.
4. **`Analyze.jsx`**: Redesign target machine selector, live audio capture button, drag-and-drop WAV/MP3 uploader (`AudioUploader.jsx`), and acoustic proximity notice.
5. **`Processing.jsx`**: Implement the industrial 5-stage progress indicator (`Audio Captured` → `Audio Preprocessing` → `Frequency Analysis` → `Acoustic Feature Extraction` → `AI Anomaly Detection`) with active real-time progress state, WebGL/Canvas shader visualizer, and error fallback with retry.
6. **`Results.jsx`**: Implement high-impact industrial diagnostic result card, normal/abnormal status badges, confidence gauges, time-domain waveform visualizer, frequency spectrum chart, technical metrics table, research context panel, and Mel Spectrogram viewer.
7. **`History.jsx`**: Redesign persistent SQLite records table with machine filter chips (`All`, `id_00`, `id_02`, `id_04`, `id_06`), summary counter cards, status indicators, and detail view navigation.
8. **`FrequencyAnalysis.jsx`**: Redesign spectrum decomposition, FFT peak markers, and frequency response graphs.
9. **`Settings.jsx`**: Redesign system configuration panels, audio sensitivity controls, and backend status monitor.

---

## 6. Phased Implementation Plan

```
PHASE 1: Inspect ZIP + Existing Frontend (COMPLETED)
   ├── Extracted & inspected ZIP reference HTML/CSS screens
   ├── Verified DESIGN.md tokens & color variables
   └── Created FRONTEND_REDESIGN_PLAN.md

PHASE 2: Global Design System & Styling Update
   ├── Update frontend/tailwind.config.js with industrial tokens, font families, and color aliases
   └── Update frontend/src/index.css with technical grid styles, soft cyan glow, radial progress, and instrument border utilities

PHASE 3: Layout & Navigation Redesign
   ├── Update TopNavigation.jsx & Sidebar/Drawer navigation
   └── Update BottomNavigation.jsx for mobile support

PHASE 4: Dashboard Page Redesign
   └── Adapt Dashboard.jsx to ZIP design system connected to real machine fleet data

PHASE 5: Machine Inventory Page Redesign
   └── Adapt Machines.jsx & MachineHealth.jsx to ZIP card/detail layouts

PHASE 6: Analyze Page Redesign
   └── Adapt Analyze.jsx, AudioUploader.jsx & AudioFileCard.jsx preserving audioStore.js integration

PHASE 7: Processing Page Redesign
   └── Adapt Processing.jsx with 5-stage real-time progress, error handling, and fetch execution

PHASE 8: Results Page Redesign
   └── Adapt Results.jsx to ZIP diagnostic screen with real ML predictions & Mel Spectrogram modal

PHASE 9: History Page Redesign
   └── Adapt History.jsx to ZIP history table connected to SQLite API endpoints

PHASE 10: Frequency Analysis & Settings Redesign
   └── Adapt FrequencyAnalysis.jsx & Settings.jsx

PHASE 11: Comprehensive End-to-End System Testing
   └── Verify full flow: Target Machine -> Record/Upload Audio -> POST /api/analyze -> ML Model Inference -> Results UI -> SQLite DB History
```

---
*Plan created. Ready to proceed to Phase 2.*
