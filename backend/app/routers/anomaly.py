from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models import User
from app.schemas.anomaly import AnomalyDetectRequest, AnomalyDetectResponse
from app.services.anomaly import detect_and_store

router = APIRouter(prefix="/anomaly", tags=["anomaly"])


@router.post("/detect", response_model=AnomalyDetectResponse, status_code=status.HTTP_201_CREATED)
def detect_anomaly(payload: AnomalyDetectRequest, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "INSPECTOR"))) -> AnomalyDetectResponse:
    return detect_and_store(database, payload, actor)
