# Audio Validity & Machine-Presence Gate (`AUDIO_VALIDATION.md`)

## 1. Executive Summary & Problem Root Cause

### Diagnostic Finding
Previously, when recording audio in an environment with no active machine sound (silence or ambient room background noise), the MachineSense backend pipeline returned `NORMAL`. 

### Why Silence Was Classified as `NORMAL`
1. In Stage 2 of `audio_processor.py` and `ml/preprocessing.py`, the pipeline applied **peak normalization** (`y_norm = y / np.max(np.abs(y))`).
2. When raw recorded audio `y` consisted of quiet room ambient noise (where peak amplitudes were `0.0001` to `0.003`), dividing by `max_peak` scaled background ambient noise up to a peak of `1.0`.
3. The normalized background noise features were then passed into the Random Forest classifier. Because the classifier was trained on operating machinery, scaled ambient noise did not match abnormal fault signatures, causing the model to default to predicting `NORMAL`.

---

## 2. Machine-Presence Gate Architecture

To prevent silence or ambient room noise from being misclassified as a healthy operating machine, an **Audio Validity / Machine-Presence Gate** function (`check_machine_audio`) was inserted into the pipeline immediately after audio loading and before feature classification.

```
                  Audio Input
                       ↓
         Audio Loading & Resampling
                       ↓
     ┌───────────────────────────────────┐
     │ check_machine_audio()             │
     │ Un-normalized Raw RMS & Peak      │
     └─────────────────┬─────────────────┘
                       │
       ┌───────────────┴───────────────┐
       │ Is raw RMS >= 0.002 &         │
       │ raw peak >= 0.008 &           │
       │ duration >= 0.5s?             │
       └───────┬───────────────┬───────┘
               │               │
       NO (Silence)       YES (Machine Sound)
               │               │
               ↓               ↓
       Bypass ML Model   Standard 15 Features
               │               │
               ↓               ↓
        NO_MACHINE_SOUND  Random Forest
        ("No sufficient   (NORMAL / ABNORMAL)
        sound detected")
```

---

## 3. Acoustic Indicators & Threshold Calibration

The gate evaluates un-normalized raw PCM float samples `y_raw` before peak scaling using the following acoustic indicators:

1. **Un-Normalized Raw RMS Energy** (`raw_rms = sqrt(mean(y_raw^2))`):
   - Silence / ambient room noise: `raw_rms < 0.002`
   - Active machinery: `raw_rms >= 0.002`
2. **Un-Normalized Raw Peak Amplitude** (`raw_peak = max(abs(y_raw))`):
   - Silence / ambient room noise: `raw_peak < 0.008`
   - Active machinery: `raw_peak >= 0.008`
3. **Signal Duration** (`duration`):
   - Minimum required duration: `0.5 seconds`

If an audio input fails any of these criteria:
* **ML Model Call**: Skipped (`ml_service.predict` is NOT invoked).
* **Returned Prediction**:
  ```json
  {
    "label": "no_machine_sound",
    "class": -1,
    "abnormal_probability": 0.0,
    "normal_probability": 0.0,
    "confidence": 0.0,
    "status": "NO_MACHINE_SOUND",
    "message": "No sufficient machine acoustic signal detected. Please ensure the target machine is operating and record again."
  }
  ```

---

## 4. Distinction Between Outcome States

| State | Status Badge | Condition | Action / Recommendation |
| :--- | :--- | :--- | :--- |
| **NORMAL** | 🟢 `NORMAL` | Active machine acoustic signal analyzed and classified as within normal operating parameters. | Continue routine operations. |
| **ABNORMAL** | 🔴 `ABNORMAL` | Active machine acoustic signal analyzed and classified as containing a mechanical anomaly or harmonic fault. | Inspect motor alignment, bearings, or mounting. |
| **NO MACHINE SOUND** | ⚪ `NO MACHINE SOUND` | Audio recording is silent, near-silent, or ambient room noise. Input validation failed before ML inference. | Ensure target machinery is running and record again. |

---

## 5. SQLite Database Safety
* **Status Storage**: Stored in `analysis_history` table with `prediction_label = 'no_machine_sound'` and `prediction_class = -1`.
* **Schema Integrity**: Preserves existing SQLite schema without table recreation or data loss.

---

## 6. Test & Verification Results

1. **Test 1: Silence / Quiet Room Recording**:
   - `raw_rms` = `0.0003` (< `0.002`), `raw_peak` = `0.0012` (< `0.008`).
   - Outcome: `NO_MACHINE_SOUND`. Skips RF classifier. UI displays `"No sufficient machine acoustic signal detected. Please ensure the target machine is operating and record again."` with `Record Again` CTA button.
2. **Test 2: Normal Machine Recording** (`00000005.wav`):
   - `raw_rms` = `0.042`, `raw_peak` = `0.28`.
   - Outcome: Passes gate -> RF classifier evaluates 15 features -> `NORMAL` (97.3% confidence).
3. **Test 3: Abnormal Machine Audio**:
   - Passes gate -> RF classifier evaluates 15 features -> `ABNORMAL` with elevated anomaly probability.
