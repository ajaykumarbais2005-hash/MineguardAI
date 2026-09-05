from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.risk import RiskCalculateRequest, RiskEventResponse
from app.services.risk import calculate_and_store, list_risk_events

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("", response_model=list[RiskEventResponse])
def read_risk_events(mine_id: Optional[int] = Query(default=None, ge=1), level: Optional[str] = Query(default=None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$"), database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[RiskEventResponse]:
    return list_risk_events(database, mine_id, level)


@router.post("/calculate", response_model=RiskEventResponse, status_code=status.HTTP_201_CREATED)
def calculate_risk_event(payload: RiskCalculateRequest, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "INSPECTOR"))) -> RiskEventResponse:
    return calculate_and_store(database, payload, actor)
