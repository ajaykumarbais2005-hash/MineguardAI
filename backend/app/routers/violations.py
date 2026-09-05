from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.violation import ViolationCreate, ViolationResponse, ViolationSummary, ViolationUpdate
from app.services.violations import create_violation, get_violation, list_violations, summarize, update_violation, _to_response

router = APIRouter(prefix="/violations", tags=["violations"])


@router.get("", response_model=list[ViolationResponse])
def read_violations(status_filter: Optional[str] = Query(default=None, alias="status"), severity: Optional[str] = None, database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[ViolationResponse]:
    return list_violations(database, status_filter, severity)


@router.get("/summary", response_model=ViolationSummary)
def read_summary(database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ViolationSummary:
    return summarize(database)


@router.get("/{violation_id}", response_model=ViolationResponse)
def read_violation(violation_id: int, database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ViolationResponse:
    return _to_response(get_violation(database, violation_id))


@router.post("", response_model=ViolationResponse, status_code=status.HTTP_201_CREATED)
def add_violation(payload: ViolationCreate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "INSPECTOR"))) -> ViolationResponse:
    return create_violation(database, payload, actor)


@router.patch("/{violation_id}", response_model=ViolationResponse)
def edit_violation(violation_id: int, payload: ViolationUpdate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "INSPECTOR"))) -> ViolationResponse:
    return update_violation(database, violation_id, payload, actor)
