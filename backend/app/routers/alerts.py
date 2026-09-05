from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.alert import AlertCreate, AlertResponse, AlertSummary
from app.services.alerts import create_alert, list_alerts, summarize, update_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
def read_alerts(status_filter: Optional[str] = Query(default=None, alias="status"), severity: Optional[str] = None, database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[AlertResponse]:
    return list_alerts(database, status_filter, severity)


@router.get("/summary", response_model=AlertSummary)
def read_summary(database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> AlertSummary:
    return summarize(database)


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def add_alert(payload: AlertCreate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER"))) -> AlertResponse:
    return create_alert(database, payload, actor)


@router.patch("/{alert_id}", response_model=AlertResponse)
def edit_alert(alert_id: int, next_status: str = Query(..., alias="status"), database: Session = Depends(get_db), actor: User = Depends(get_current_user)) -> AlertResponse:
    return update_alert(database, alert_id, next_status, actor)
