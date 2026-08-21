import sys
import time
import json
import numpy as np
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from ml.preprocessing import load_and_preprocess_audio
from app.services.audio_processor import process_audio_file
from app.services.ml_service import get_ml_service

TEST_WAV = Path("D:/pump/id_00/normal/00000000.wav")

def main():
    print("=" * 75)
    print("BACKEND PREVIEW PIPELINE PROFILING & BENCHMARK")
    print("=" * 75)
    
    if not TEST_WAV.exists():
        print(f"ERROR: Test WAV file does not exist: {TEST_WAV}")
        sys.exit(1)
        
    t_start = time.perf_counter()
    
    # Stage 1: Audio Loading & Resampling
    t0 = time.perf_counter()
    y_norm, sr = load_and_preprocess_audio(str(TEST_WAV))
    t1 = time.perf_counter()
    load_time_ms = (t1 - t0) * 1000
    print(f"Stage 1 [Audio Load & Preprocess]: {load_time_ms:.2f} ms")
    
    # Stage 2: Signal Analysis & Feature Extraction (process_audio_file)
    t2 = time.perf_counter()
    analysis_dict, spec_bytes = process_audio_file(str(TEST_WAV))
    t3 = time.perf_counter()
    analysis_time_ms = (t3 - t2) * 1000
    print(f"Stage 2 [Process Audio & Spectrogram PNG]: {analysis_time_ms:.2f} ms")
    print(f"   -> Spectrogram PNG size: {len(spec_bytes):,} bytes")
    
    # Stage 3: ML Model Service Inference
    t4 = time.perf_counter()
    ml_service = get_ml_service()
    ml_result = ml_service.predict(y_norm, sr, filename_or_path="00000000.wav")
    t5 = time.perf_counter()
    ml_time_ms = (t5 - t4) * 1000
    print(f"Stage 3 [ML Feature Extraction & Inference]: {ml_time_ms:.2f} ms")
    print(f"   -> ML Prediction: {ml_result['prediction']}")
    
    t_total = (time.perf_counter() - t_start) * 1000
    print("=" * 75)
    print(f"TOTAL PREVIEW ENDPOINT EXECUTION TIME: {t_total:.2f} ms ({t_total/1000:.3f} s)")
    print("=" * 75)

if __name__ == "__main__":
    main()
