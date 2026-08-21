import os
import wave
import contextlib
import soundfile as sf
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple
from ml.config import DATASET_DIR, LABEL_MAP


def inspect_audio_file(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """
    Inspects a single WAV file to extract audio properties and detect corruption.
    Returns (metadata_dict, status_string).
    """
    if not file_path.exists():
        return {}, "file_not_found"

    if file_path.stat().st_size == 0:
        return {}, "empty_file"

    if file_path.suffix.lower() != ".wav":
        return {}, "unsupported_format"

    try:
        info = sf.info(str(file_path))
        duration = info.duration
        sample_rate = info.samplerate
        number_of_samples = info.frames
        channels = info.channels

        if duration <= 0 or number_of_samples <= 0:
            return {}, "zero_duration"

        meta = {
            "file_path": str(file_path),
            "duration": round(duration, 4),
            "sample_rate": sample_rate,
            "number_of_samples": number_of_samples,
            "channels": channels
        }
        return meta, "ok"

    except Exception:
        # Fallback to standard library wave module if soundfile encounters header issue
        try:
            with contextlib.closing(wave.open(str(file_path), 'rb')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                channels = f.getnchannels()
                duration = frames / float(rate)
                meta = {
                    "file_path": str(file_path),
                    "duration": round(duration, 4),
                    "sample_rate": rate,
                    "number_of_samples": frames,
                    "channels": channels
                }
                return meta, "ok"
        except Exception as e:
            return {}, f"corrupted: {str(e)}"


def discover_mimii_dataset(dataset_dir: Path = DATASET_DIR) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Recursively scans dataset_dir for all machine IDs and WAV files.
    Extracts metadata and tracks any corrupted or problematic files.
    """
    if not dataset_dir.exists():
        raise FileNotFoundError(f"MIMII dataset directory does not exist at '{dataset_dir}'.")

    records: List[Dict[str, Any]] = []
    seen_paths = set()

    problematic_files = {
        "corrupted": [],
        "empty": [],
        "unsupported": [],
        "duplicates": []
    }

    # Automatically discover all directories inside dataset_dir
    machine_dirs = [d for d in dataset_dir.iterdir() if d.is_dir()]

    for m_dir in sorted(machine_dirs):
        machine_id = m_dir.name  # e.g., id_00, id_02, etc.

        for label_name in ["normal", "abnormal"]:
            label_dir = m_dir / label_name
            if not label_dir.exists():
                continue

            label_code = LABEL_MAP[label_name]

            for file_path in label_dir.glob("*.wav"):
                str_path = str(file_path.resolve())

                if str_path in seen_paths:
                    problematic_files["duplicates"].append(str_path)
                    continue

                seen_paths.add(str_path)

                meta, status = inspect_audio_file(file_path)

                if status == "ok":
                    meta["machine_id"] = machine_id
                    meta["label"] = label_code
                    meta["label_name"] = label_name
                    records.append(meta)
                elif status == "empty_file":
                    problematic_files["empty"].append(str_path)
                elif status == "unsupported_format":
                    problematic_files["unsupported"].append(str_path)
                else:
                    problematic_files["corrupted"].append({"path": str_path, "reason": status})

    # Summary Statistics
    total_files = len(records)
    if total_files == 0:
        stats = {"total_files": 0, "machines": {}}
        return records, stats

    df = pd.DataFrame(records)

    normal_count = int((df["label"] == 0).sum())
    abnormal_count = int((df["label"] == 1).sum())

    durations = df["duration"]
    duration_stats = {
        "min": float(durations.min()),
        "max": float(durations.max()),
        "avg": float(round(durations.mean(), 4))
    }

    sample_rates = df["sample_rate"].value_counts().to_dict()

    machine_stats = {}
    for m_id, group in df.groupby("machine_id"):
        n_cnt = int((group["label"] == 0).sum())
        a_cnt = int((group["label"] == 1).sum())
        machine_stats[m_id] = {
            "total": len(group),
            "normal": n_cnt,
            "abnormal": a_cnt
        }

    stats = {
        "total_files": total_files,
        "normal_count": normal_count,
        "abnormal_count": abnormal_count,
        "machine_stats": machine_stats,
        "duration_stats": duration_stats,
        "sample_rates": sample_rates,
        "problematic_files": problematic_files
    }

    return records, stats
