from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.workflow import WorkflowSummary
from app.services.workflow import summarize_workflow

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.get("/summary", response_model=WorkflowSummary)
def read_summary(database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> WorkflowSummary:
    return summarize_workflow(database)
