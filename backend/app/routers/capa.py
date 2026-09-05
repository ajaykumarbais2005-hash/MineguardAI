from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.capa import CAPACreate, CAPAResponse, CAPASummary, CAPAUpdate
from app.services.capa import create_action, list_actions, summarize, update_action

router = APIRouter(prefix="/corrective-actions", tags=["corrective-actions"])


@router.get("", response_model=list[CAPAResponse])
def read_actions(status_filter: Optional[str] = Query(default=None, alias="status"), database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[CAPAResponse]:
    return list_actions(database, status_filter)


@router.get("/summary", response_model=CAPASummary)
def read_summary(database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> CAPASummary:
    return summarize(database)


@router.post("", response_model=CAPAResponse, status_code=status.HTTP_201_CREATED)
def add_action(payload: CAPACreate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER"))) -> CAPAResponse:
    return create_action(database, payload, actor)


@router.patch("/{action_id}", response_model=CAPAResponse)
def edit_action(action_id: int, payload: CAPAUpdate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "AUDITOR"))) -> CAPAResponse:
    return update_action(database, action_id, payload, actor)