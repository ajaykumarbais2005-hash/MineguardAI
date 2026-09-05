from datetime import UTC, datetime

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "database": "configured",
        "ai_mode": settings.ai_mode,
        "ocr_mode": settings.ocr_mode,
        "timestamp": datetime.now(UTC).isoformat(),
    }
