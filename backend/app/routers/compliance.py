from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.compliance import ComplianceCreate, ComplianceResponse, ComplianceSummary, ComplianceUpdate
from app.services.compliance import create_requirement, list_requirements, summary, update_requirement

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get("", response_model=list[ComplianceResponse])
def read_requirements(search: Optional[str] = Query(default=None, max_length=100), status_filter: Optional[str] = Query(default=None, alias="status", max_length=40), category: Optional[str] = Query(default=None, max_length=80), database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[ComplianceResponse]:
    return list_requirements(database, search, status_filter, category)


@router.get("/summary", response_model=ComplianceSummary)
def read_summary(database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ComplianceSummary:
    return summary(database)


@router.post("", response_model=ComplianceResponse, status_code=status.HTTP_201_CREATED)
def add_requirement(payload: ComplianceCreate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "SAFETY_OFFICER"))) -> ComplianceResponse:
    return create_requirement(database, payload, actor)


@router.patch("/{requirement_id}", response_model=ComplianceResponse)
def edit_requirement(requirement_id: int, payload: ComplianceUpdate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "SAFETY_OFFICER"))) -> ComplianceResponse:
    return update_requirement(database, requirement_id, payload, actor)
