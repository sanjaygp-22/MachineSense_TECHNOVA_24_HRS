import sqlite3
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.config import DB_PATH

logger = logging.getLogger("app.database.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row factory."""
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the SQLite database and creates the analysis_history table if missing."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    analysis_id TEXT PRIMARY KEY,
                    machine_id TEXT NOT NULL,
                    source TEXT DEFAULT 'uploaded',
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
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_machine_created 
                ON analysis_history(machine_id, timestamp_epoch DESC);
            """)
            # Migration check for existing SQLite databases
            cursor.execute("PRAGMA table_info(analysis_history)")
            cols = [col[1] for col in cursor.fetchall()]
            if "source" not in cols:
                cursor.execute("ALTER TABLE analysis_history ADD COLUMN source TEXT DEFAULT 'uploaded'")
            conn.commit()
            logger.info(f"[SQLite DB] Database initialized successfully at {DB_PATH}")
    except Exception as e:
        logger.error(f"[SQLite DB] ERROR initializing database: {e}")
        raise


def save_analysis_record(data: Dict[str, Any]) -> bool:
    """
    Saves a completed analysis result to SQLite database.
    Expects data returned by POST /api/analyze.
    Returns True if successful, False otherwise.
    """
    try:
        analysis_id = data.get("analysis_id")
        machine_id = data.get("machine_id", "unknown")
        source_val = data.get("source", "uploaded")
        prediction = data.get("prediction", {})
        label = prediction.get("label", "unknown")
        pred_class = int(prediction.get("class", 0))
        abnormal_prob = float(prediction.get("abnormal_probability", 0.0))
        normal_prob = float(prediction.get("normal_probability", 0.0))
        confidence = float(max(abnormal_prob, normal_prob) * 100.0)

        freq_data = data.get("frequency", {})
        dom_freq = float(freq_data.get("dominant_frequency_hz", 0.0))

        sig_data = data.get("signal", {})
        rms_val = float(sig_data.get("rms", 0.0))
        sig_quality = sig_data.get("signal_quality", "moderate")

        spectral_data = data.get("spectral_features", {})
        centroid = float(spectral_data.get("centroid_hz", 0.0))

        audio_data = data.get("audio", {})
        dur = float(audio_data.get("duration", 0.0))
        sr = int(audio_data.get("sample_rate", 16000))

        now_dt = datetime.now(timezone.utc)
        created_at_iso = now_dt.isoformat()
        epoch_ts = now_dt.timestamp()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO analysis_history (
                    analysis_id, machine_id, source, created_at, timestamp_epoch,
                    prediction_label, prediction_class, abnormal_probability,
                    normal_probability, confidence, dominant_frequency_hz,
                    rms, signal_quality, centroid_hz, duration, sample_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id, machine_id, source_val, created_at_iso, epoch_ts,
                label, pred_class, abnormal_prob,
                normal_prob, confidence, dom_freq,
                rms_val, sig_quality, centroid, dur, sr
            ))
            conn.commit()
            logger.info(f"[SQLite DB] Saved analysis '{analysis_id}' for machine '{machine_id}'")
            return True
    except Exception as e:
        logger.error(f"[SQLite DB] Failed to save analysis record: {e}")
        return False


def get_all_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves recent analysis records sorted newest first."""
    records = []
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM analysis_history
                ORDER BY timestamp_epoch DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            for row in rows:
                records.append(dict(row))
    except Exception as e:
        logger.error(f"[SQLite DB] Failed to query all history: {e}")
    return records


def get_machine_history(machine_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Retrieves machine-specific history and summary statistics:
    - total_analyses
    - normal_count
    - abnormal_count
    - latest_status
    - latest_dominant_frequency
    - records list
    """
    summary = {
        "machine_id": machine_id,
        "total_analyses": 0,
        "normal_count": 0,
        "abnormal_count": 0,
        "latest_status": "N/A",
        "latest_dominant_frequency_hz": 0.0,
        "records": []
    }
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Summary query
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN LOWER(prediction_label) = 'normal' THEN 1 ELSE 0 END) as normal_cnt,
                    SUM(CASE WHEN LOWER(prediction_label) = 'abnormal' THEN 1 ELSE 0 END) as abnormal_cnt
                FROM analysis_history
                WHERE machine_id = ?
            """, (machine_id,))
            stat = cursor.fetchone()
            if stat:
                summary["total_analyses"] = stat["total"] or 0
                summary["normal_count"] = stat["normal_cnt"] or 0
                summary["abnormal_count"] = stat["abnormal_cnt"] or 0

            # Latest record query
            cursor.execute("""
                SELECT prediction_label, dominant_frequency_hz
                FROM analysis_history
                WHERE machine_id = ?
                ORDER BY timestamp_epoch DESC
                LIMIT 1
            """, (machine_id,))
            latest = cursor.fetchone()
            if latest:
                summary["latest_status"] = latest["prediction_label"].upper()
                summary["latest_dominant_frequency_hz"] = round(float(latest["dominant_frequency_hz"]), 2)

            # Records list
            cursor.execute("""
                SELECT * FROM analysis_history
                WHERE machine_id = ?
                ORDER BY timestamp_epoch DESC
                LIMIT ?
            """, (machine_id, limit))
            rows = cursor.fetchall()
            summary["records"] = [dict(r) for r in rows]

    except Exception as e:
        logger.error(f"[SQLite DB] Failed to query machine history for '{machine_id}': {e}")
    return summary
