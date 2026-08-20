import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Security & CORS settings
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,*"
).split(",")

# File upload constraints
MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a"}

# Temporary upload folder
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# SQLite Database Location
DB_PATH = BASE_DIR / "machinesense.db"
