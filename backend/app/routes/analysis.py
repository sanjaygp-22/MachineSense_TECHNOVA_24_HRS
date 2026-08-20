import os
import time
import uuid
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response, status
from app.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES, UPLOAD_DIR
from app.services.audio_processor import process_audio_signal
from app.services.analysis_store import store_analysis, get_spectrogram_png
from app.services.ml_service import get_ml_service
from app.database.db import save_analysis_record
from ml.preprocessing import load_and_preprocess_audio

router = APIRouter()
logger = logging.getLogger("app.routes.analysis")


@router.post("/analyze")
async def analyze_audio(
    audio: UploadFile = File(...),
    machine_id: str = Form("id_00"),
    source: str = Form("uploaded"),
    request_id: Optional[str] = Form(None)
):
    t_start_total = time.perf_counter()

    if not audio or not audio.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio file uploaded."
        )

    # Extension check
    file_ext = Path(audio.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Stage 1: Audio Upload & Save to Disk
    t_upload_start = time.perf_counter()
    unique_filename = f"{uuid.uuid4().hex}_{Path(audio.filename).name}"
    temp_file_path = UPLOAD_DIR / unique_filename

    try:
        file_bytes = await audio.read()
        if len(file_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
            size_mb = len(file_bytes) / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({size_mb:.1f} MB) exceeds maximum upload limit of 50 MB."
            )

        with open(temp_file_path, "wb") as f:
            f.write(file_bytes)

        t_upload_end = time.perf_counter()
        upload_disk_save_ms = (t_upload_end - t_upload_start) * 1000

        # Stage 2-5: Audio Loading, Machine-Presence Gate, Preprocessing & Feature Extraction
        t_load_start = time.perf_counter()
        analysis_result, spectrogram_png, timings = process_audio_signal(str(temp_file_path))
        t_load_end = time.perf_counter()
        audio_loading_ms = timings.get("audio_loading_ms", (t_load_end - t_load_start) * 1000)

        sig_info = analysis_result.get("signal", {})
        is_valid_signal = sig_info.get("valid_machine_signal", True)

        # Print explicit Audio Validation Gating Logs
        print("\n" + "=" * 75)
        print(f"[AUDIO VALIDATION GATING LOG] (File: {audio.filename})")
        print("=" * 75)
        print(f"  Raw Peak Amplitude:   {sig_info.get('peak_amplitude', 0.0):.6f}")
        print(f"  Raw RMS Energy:       {sig_info.get('rms', 0.0):.6f}")
        print(f"  Duration:             {analysis_result.get('audio', {}).get('duration', 0.0)} s")
        print(f"  Machine Signal Valid: {is_valid_signal}")
        print(f"  Reason:               {sig_info.get('machine_presence_reason', '')}")
        print("=" * 75)

        if not is_valid_signal:
            print("[AUDIO VALIDATION] INVALID SIGNAL -> ML MODEL INFERENCE SKIPPED\n")
            logger.info(f"Audio validation gate: NO_MACHINE_SOUND for {audio.filename}")
            ml_result = {
                "machine_id": machine_id,
                "prediction": {
                    "label": "no_machine_sound",
                    "class": -1,
                    "abnormal_probability": 0.0,
                    "normal_probability": 0.0,
                    "confidence": 0.0,
                    "status": "NO_MACHINE_SOUND",
                    "message": sig_info.get(
                        "machine_presence_reason",
                        "No sufficient machine acoustic signal detected. Please ensure the target machine is operating and record again."
                    )
                }
            }
            ml_inference_ms = 0.0
        else:
            print("[AUDIO VALIDATION] VALID SIGNAL -> PROCEEDING TO RANDOM FOREST ML INFERENCE\n")
            # Load peak-normalized signal specifically for Random Forest feature prediction
            y_norm, sr = load_and_preprocess_audio(str(temp_file_path))
            ml_service = get_ml_service()
            if not ml_service.is_loaded():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"ML Model is unavailable: {ml_service.load_error or 'Model pipeline failed to load'}"
                )

            # Stage 6: ML Model Inference
            t_ml_start = time.perf_counter()
            ml_result = ml_service.predict(y_norm, sr, filename_or_path=audio.filename)
            t_ml_end = time.perf_counter()
            ml_inference_ms = (t_ml_end - t_ml_start) * 1000

        # Stage 7: Response Generation & Caching
        t_resp_start = time.perf_counter()
        analysis_id = request_id.strip() if request_id and request_id.strip() else uuid.uuid4().hex
        
        # Prioritize selected machine_id from HTTP Form data over filename parsing
        clean_machine_id = machine_id.strip() if machine_id and machine_id.strip() not in ["", "unknown"] else "id_00"

        spectrogram_info = {
            "url": f"/api/analysis/{analysis_id}/spectrogram",
            "format": "image/png"
        }

        full_response = {
            "analysis_id": analysis_id,
            "machine_id": clean_machine_id,
            "source": source,
            "prediction": ml_result["prediction"],
            "spectrogram": spectrogram_info,
            **analysis_result
        }

        # Cache in-memory for fast spectrogram image retrieval
        store_analysis(analysis_id, full_response, spectrogram_png)

        # Persist to SQLite Database (idempotent primary key save)
        try:
            save_analysis_record(full_response)
        except Exception as db_err:
            logger.error(f"[SQLite DB] Non-fatal error auto-saving analysis to DB: {db_err}")

        t_resp_end = time.perf_counter()
        response_generation_ms = (t_resp_end - t_resp_start) * 1000

        t_total_end = time.perf_counter()
        total_preview_time_ms = (t_total_end - t_start_total) * 1000

        # Print Timing Log Report
        print("\n" + "=" * 75)
        print(f"PREVIEW PIPELINE STAGE TIMING LOGS (File: {audio.filename})")
        print("=" * 75)
        print(f"  1. Audio Upload & Disk Save:      {upload_disk_save_ms:.2f} ms")
        print(f"  2. Audio Loading:                  {audio_loading_ms:.2f} ms")
        print(f"  3. Noise Filtering & Normalization: {timings.get('noise_filtering_and_norm_ms', 0):.2f} ms")
        print(f"  4. Resampling:                     {timings.get('resampling_ms', 0):.2f} ms")
        print(f"  5. Feature Extraction:             {timings.get('feature_extraction_ms', 0):.2f} ms")
        print(f"  6. ML Model Inference:             {ml_inference_ms:.2f} ms")
        print(f"  7. Response Generation & DB Save:  {response_generation_ms:.2f} ms")
        print("-" * 75)
        print(f"TOTAL PREVIEW PIPELINE EXECUTION TIME: {total_preview_time_ms:.2f} ms ({total_preview_time_ms/1000:.3f} s)")
        print("=" * 75 + "\n")

        return full_response

    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Audio processing error: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred while processing audio: {str(e)}"
        )
    finally:
        if temp_file_path.exists():
            try:
                os.remove(temp_file_path)
            except Exception:
                pass


@router.get("/analysis/{analysis_id}/spectrogram")
def get_spectrogram_image(analysis_id: str):
    png_bytes = get_spectrogram_png(analysis_id)
    if not png_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spectrogram image for analysis_id '{analysis_id}' was not found or has expired."
        )

    return Response(content=png_bytes, media_type="image/png")
