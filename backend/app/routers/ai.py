from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models import User
from app.schemas.ai import PPEDetectionRequest, PPEDetectionResponse
from app.services.ai import run_ppe_detection

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/ppe/detect", response_model=PPEDetectionResponse)
def detect_ppe(payload: PPEDetectionRequest, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "INSPECTOR"))) -> PPEDetectionResponse:
    return run_ppe_detection(database, payload, actor)
