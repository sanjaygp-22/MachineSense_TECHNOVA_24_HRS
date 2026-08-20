import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from app.database.db import get_all_history, get_machine_history

router = APIRouter()
logger = logging.getLogger("app.routes.history")


@router.get("/history")
def read_all_history(
    limit: int = Query(50, ge=1, le=500, description="Maximum records to return"),
    machine_id: Optional[str] = Query(None, description="Optional machine ID filter")
):
    """
    Retrieves analysis history records sorted by newest first.
    Optionally filters by machine_id query parameter.
    """
    try:
        if machine_id:
            return get_machine_history(machine_id, limit=limit)
        else:
            records = get_all_history(limit=limit)
            return {
                "total_records": len(records),
                "records": records
            }
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to retrieve analysis history: {str(e)}"
        )


@router.get("/history/{machine_id}")
def read_machine_history(
    machine_id: str,
    limit: int = Query(50, ge=1, le=500, description="Maximum records to return")
):
    """
    Retrieves persistent analysis records and summary statistics for a target machine.
    """
    try:
        return get_machine_history(machine_id, limit=limit)
    except Exception as e:
        logger.error(f"Error fetching machine history for '{machine_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to retrieve history for machine '{machine_id}': {str(e)}"
        )
