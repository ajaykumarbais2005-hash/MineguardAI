from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database import get_db
from app.models import User
from app.schemas.audit import AuditResponse, AuditSummary
from app.services.audit import list_logs, summarize

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditResponse])
def read_logs(action: Optional[str] = Query(default=None), entity: Optional[str] = Query(default=None), search: Optional[str] = Query(default=None), database: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN", "AUDITOR"))) -> list[AuditResponse]:
    return list_logs(database, action, entity, search)


@router.get("/summary", response_model=AuditSummary)
def read_summary(database: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN", "AUDITOR"))) -> AuditSummary:
    return summarize(database)
