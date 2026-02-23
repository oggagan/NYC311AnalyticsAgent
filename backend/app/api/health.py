from fastapi import APIRouter
from app.db.database import db_manager
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok" if db_manager.is_loaded else "degraded",
        db_connected=db_manager.is_loaded,
        rows_loaded=db_manager.row_count,
    )
