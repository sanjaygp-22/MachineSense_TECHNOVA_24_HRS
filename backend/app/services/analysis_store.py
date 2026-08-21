import time
from typing import Dict, Any, Optional

_STORE: Dict[str, Dict[str, Any]] = {}
EXPIRATION_SECONDS = 3600  # 1 hour TTL


def _cleanup_expired():
    now = time.time()
    expired_keys = [
        k for k, v in _STORE.items() if now - v.get("timestamp", 0) > EXPIRATION_SECONDS
    ]
    for k in expired_keys:
        _STORE.pop(k, None)


def store_analysis(analysis_id: str, data: Dict[str, Any], spectrogram_png: bytes):
    _cleanup_expired()
    _STORE[analysis_id] = {
        "data": data,
        "spectrogram_png": spectrogram_png,
        "timestamp": time.time()
    }


def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    _cleanup_expired()
    record = _STORE.get(analysis_id)
    return record["data"] if record else None


def get_spectrogram_png(analysis_id: str) -> Optional[bytes]:
    _cleanup_expired()
    record = _STORE.get(analysis_id)
    return record["spectrogram_png"] if record else None
