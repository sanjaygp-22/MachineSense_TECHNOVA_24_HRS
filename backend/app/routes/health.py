from fastapi import APIRouter
from app.services.ml_service import get_ml_service

router = APIRouter()

@router.get("/health")
def health_check():
    ml_service = get_ml_service()
    ml_status = "loaded" if ml_service.is_loaded() else "unavailable"

    return {
        "status": "ok",
        "service": "MachineSense Backend",
        "ml_model": ml_status
    }
