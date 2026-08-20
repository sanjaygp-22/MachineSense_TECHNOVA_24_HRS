# MachineSense ZIP Visual Reference Audit (`UI_ZIP_REFERENCE.md`)

This document is the authoritative visual and component audit of `stitch_machinesense_acoustic_intelligence_station.zip`.

---

## 1. Executive Summary & ZIP Inspection

* **ZIP File**: `stitch_machinesense_acoustic_intelligence_station.zip` (Extracted to `zip_extracted/stitch_machinesense_acoustic_intelligence_station/`)
* **Completeness**: Contains **8 full page/screen templates** with standalone HTML reference files and PNG preview renders + **1 WebGL ambient shader** + **DESIGN.md** specifications.
* **UI Architecture**: Tailwind CSS design system with custom HSL/HEX color tokens, Material Symbols Outlined icons, Inter & JetBrains Mono typography, technical 1px borders (`#3b494c` / `#2D3139`), cyan glow accents (`#00e5ff`), and hardware control-room layouts.

---

## 2. Identified Screens in ZIP Reference

| # | ZIP Directory | Screen Name | Key UI Elements & Layout Features |
|---|---|---|---|
| **1** | `machinesense_dashboard_high_contrast` | **Overview / Dashboard** | Desktop top app bar + Mobile navbar, Engineer greeting, Overall Health radial progress ring (`94%`), Monitored machines KPI, Recent alerts badge, Quick Analyze Sound banner with Record/Upload CTAs, Active machine cards (`MOTOR-01`, `PUMP-02`) with sparkline SVGs. |
| **2** | `machine_inventory_high_contrast` | **Machine Inventory** | Desktop top app bar + central tab navigation, Header with machine search input & filter button, 4-column bento card grid (`MOTOR-01`, `PUMP-02`, `COMP-04`, `GEN-12`), status dot indicators (Green Normal, Amber Degrading, Red Abnormal), telemetry signature pairs (`98dB \| 16kHz`), and direct `Analyze` CTAs. |
| **3** | `acoustic_analysis_high_contrast` | **Acoustic Analysis (Analyze)** | Top navigation with active `Analyze` indicator, Target Asset selector dropdown with metadata strip (Type, Last Analysis, Health status), Audio Input panel with Mode Toggle tabs (Record Audio vs Upload Audio), Timer display (`00:00:00`), Glowing mic button, Live Acoustic Stream grid visualizer (`16 kHz \| 16-bit PCM`). |
| **4** | `analysis_results_high_contrast` | **Analysis Results & Diagnosis** | Desktop Navigation Drawer + Mobile top app bar, Status pipeline tracker nodes (`Capture` → `Process` → `Analyze`), Status Hero Banner (`Normal Status`, Anomaly Score `0.12 / 1.0`, Confidence `94.8%`), Time-Domain Waveform SVG panel, 8-bar Frequency Spectrum peak chart, Mel Spectrogram heatmap viewer, Technical Metrics table, and LOMO Research Context panel. |
| **5** | `analysis_history_high_contrast` | **Analysis History** | Desktop Navigation Drawer + Mobile header, Search bar (`Search ID or Machine...`), Filter buttons (`Machine`, `Status`, `EXPORT`), High-contrast analysis log records table with status badges (`NORMAL`, `DEGRADING`, `ABNORMAL`), prediction anomaly scores (`0.94`, `0.12`), peak frequencies (`1450 Hz`), and pagination footer. |
| **6** | `asset_health_professional_view` | **Asset Health Detail** | Desktop sidebar + Header with asset ID badge (`M-01 Centrifugal Pump`), Status indicator (`HEALTHY`), 3 KPI cards (Total Analyses `342`, Anomaly Score `0.12`, Signal Quality `94%`), 30-day Anomaly Score trend bar chart with threshold line (`TH: 0.85`), and Recent Observations feed. |
| **7** | `research_insights_high_contrast` | **Research Insights** | Technical validation metrics bento grid: Machine Dependence accuracy (`99.76%`), Generalization LOMO evaluation badge, Primary Architecture card (`Machine-Invariant RF vs CNN/Autoencoder`). |
| **8** | `settings_high_contrast` | **Settings** | Desktop navigation drawer + Mobile header, Appearance radio selector (Light, System, Dark), Default Target Machine dropdown, Auto-save toggle, Critical Alerts check boxes, About MachineSense version & stack info. |
| **9** | `shader` | **Ambient WebGL Shader** | Three.js / WebGL raymarching fragment shader for ambient acoustic backdrop visualizer (`code.html`). |

---

## 3. Global Reusable Components

1. **Top Navigation App Bar (`TopNavigation.jsx`)**
   - Brand title `MachineSense` (or `Acoustic Intelligence`)
   - Sensor diagnostic icon trigger
   - Desktop tab links: `Overview`, `Machines`, `Analyze`, `History` (with active bottom accent bar `#00e5ff`)
   - Mobile responsive menu toggle button

2. **Mobile Bottom Navigation Bar (`BottomNavigation.jsx`)**
   - Fixed bottom dock (`h-16` / `h-20`, `bg-surface-container`)
   - 4 tab items: `Overview` (`dashboard`), `Machines` (`precision_manufacturing`), `Analyze` (`analytics`), `History` (`history`)
   - Active tab rounded pill container with soft cyan background highlight

3. **Desktop Sidebar Drawer (`SidebarNavigation.jsx`)**
   - Fixed left drawer (`w-80`, `bg-surface-container-low`, `border-r border-outline-variant`)
   - Brand title header `MachineSense System`
   - Vertical link stack with icon + label + active route container

4. **Target Machine Selector Card (`MachineSelector.jsx`)**
   - Dropdown select field with chevron icon
   - Metadata ribbon: `Type`, `Last Analysis`, `Health` (`98% OPTIMAL`)

5. **Audio Capture Control Box (`AudioInputPanel.jsx`)**
   - Mode switcher tabs (`Record Audio` vs `Upload Audio`)
   - Large circular mic recording button (`w-24 h-24`) with hover ring
   - Live timer readout (`00:00:00`)
   - Drag-and-drop file upload dropzone for `.wav`, `.mp3`, `.flac`

6. **Waveform & Spectral Visualizers (`WaveformVisualizer.jsx`, `SpectrumChart.jsx`)**
   - Technical grid background pattern (`20px 20px` or `40px 40px` grid overlay)
   - SVG time-domain waveform line
   - Peak frequency bar breakdown chart with cyan glow
   - Mel Spectrogram heatmap overlay

7. **Status Prediction Hero Banner (`StatusBanner.jsx`)**
   - Large status icon circle with ring border (`#4edea3` for Normal, `#ffb4ab` for Critical)
   - Anomaly score meter (`0.12 / 1.0`)
   - Confidence percentage badge (`94.8%`)
   - Action buttons (`Save Analysis`, `View History`)

8. **Analysis Pipeline Checklist (`PipelineTracker.jsx`)**
   - Connected horizontal sequence nodes: `Capture` → `Process` → `Analyze`
   - Active glowing cyan state for completed/running steps

9. **Analysis History Table (`HistoryTable.jsx`)**
   - Search input & filter action buttons
   - Grid table rows with status badges (`NORMAL`, `DEGRADING`, `ABNORMAL`)
   - Data columns: Analysis ID, Machine, Date & Time, Prediction, Score, Peak Frequency

---

## 4. Design System Tokens & Utility Classes

### Colors (Extracted from `DESIGN.md`)
- **Surface Background**: `#111316` (Deep Charcoal)
- **Card Containers**: `#1e2023` / `#1a1c1f`
- **Primary Accent**: `#00e5ff` (Electric Cyan)
- **Primary Fixed Dim**: `#00daf3`
- **Secondary (Healthy)**: `#4edea3` / `#00a572` (Emerald Green)
- **Warning Status**: `#ffc681` / `#ffb95f` (Amber)
- **Critical Error**: `#ffb4ab` / `#93000a` (Industrial Red)
- **Borders & Dividers**: `#3b494c` / `#2D3139`

### Typography Tokens
- **`font-headline-lg`**: Inter, 30px / 38px, bold, letter-spacing -0.02em
- **`font-headline-md`**: Inter, 24px / 32px, semi-bold, letter-spacing -0.01em
- **`font-body-md`**: Inter, 16px / 24px, regular
- **`font-body-sm`**: Inter, 14px / 20px, regular
- **`font-data-lg`**: JetBrains Mono, 18px / 24px, semi-bold
- **`font-data-sm`**: JetBrains Mono, 12px / 16px, medium, letter-spacing 0.02em
- **`font-label-caps`**: Inter, 11px / 12px, bold, uppercase, letter-spacing 0.08em

### CSS Utilities (`index.css`)
```css
.technical-grid {
    background-size: 20px 20px;
    background-image: linear-gradient(to right, rgba(191, 200, 202, 0.2) 1px, transparent 1px),
                      linear-gradient(to bottom, rgba(191, 200, 202, 0.2) 1px, transparent 1px);
}

.soft-cyan-glow {
    box-shadow: 0 0 8px rgba(0, 229, 255, 0.3);
}

.tech-border {
    border: 1px solid #3b494c;
}
```

---

## 5. Functionality Mapping Matrix

| ZIP Reference Screen | MachineSense2 Existing Route | Backend / Data Contract |
|---|---|---|
| `machinesense_dashboard_high_contrast` | `/` (`Dashboard.jsx`) | Calculated overall health, active fleet list, quick analyze CTAs |
| `machine_inventory_high_contrast` | `/machines` (`Machines.jsx`) | Monitored assets list, machine filter chips, telemetry stats |
| `asset_health_professional_view` | `/health` (`MachineHealth.jsx`) | Target machine detail, 30-day stability, historical observation feed |
| `acoustic_analysis_high_contrast` | `/analyze` (`Analyze.jsx`) | Selected `machine_id`, live mic recorder, file dropzone (`WAV`/`MP3`/`FLAC`) |
| *[Processing Stage]* | `/processing` (`Processing.jsx`) | Dispatch `POST /api/analyze` with `FormData` (`audio`, `machine_id`, `request_id`) |
| `analysis_results_high_contrast` | `/results` (`Results.jsx`) | Real JSON payload (`prediction`, `frequency`, `signal`, `spectral_features`, `spectrogram.url`) |
| `analysis_history_high_contrast` | `/history` (`History.jsx`) | `GET /api/history` and `GET /api/history/{machine_id}` SQLite database records |
| `research_insights_high_contrast` | `/research` (`ResearchInsights.jsx`) | LOMO cross-validation stats & MIMII dataset metrics |
| `settings_high_contrast` | `/settings` (`Settings.jsx`) | Engineer profile & system preferences |

---

## 6. Implementation Strategy & Fidelity Rules

1. **Exact HTML Structure & CSS Classes**: Replicate the exact Tailwind class combinations from the ZIP's `code.html` files into React JSX components.
2. **Preserve Audio Store & State Flow**: Use `frontend/src/utils/audioStore.js` to transfer transient `File` object between `/analyze` and `/processing`.
3. **Real Backend Responses**: Bind real data from FastAPI `POST /api/analyze` and SQLite `GET /api/history`. For ZIP fields that the backend doesn't output, display `"N/A"`.
4. **No Git & No Backend Modifications**: Keep all changes local and restricted strictly to `frontend/`.
