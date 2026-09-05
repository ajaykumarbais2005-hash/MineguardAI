from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.contractor import ContractorCreate, ContractorResponse, ContractorSummary, ContractorUpdate, WorkerCreate, WorkerResponse
from app.services.contractors import add_worker, create_contractor, list_contractors, summarize, update_contractor

router = APIRouter(prefix="/contractors", tags=["contractors"])


@router.get("", response_model=list[ContractorResponse])
def read_contractors(search: Optional[str] = Query(default=None), status_filter: Optional[str] = Query(default=None, alias="status"), database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[ContractorResponse]:
    return list_contractors(database, search, status_filter)


@router.get("/summary", response_model=ContractorSummary)
def read_summary(database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ContractorSummary:
    return summarize(database)


@router.post("", response_model=ContractorResponse, status_code=status.HTTP_201_CREATED)
def add_contractor(payload: ContractorCreate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER"))) -> ContractorResponse:
    return create_contractor(database, payload, actor)


@router.patch("/{contractor_id}", response_model=ContractorResponse)
def edit_contractor(contractor_id: int, payload: ContractorUpdate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER"))) -> ContractorResponse:
    return update_contractor(database, contractor_id, payload, actor)


@router.post("/{contractor_id}/workers", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
def add_contractor_worker(contractor_id: int, payload: WorkerCreate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER"))) -> WorkerResponse:
    return add_worker(database, contractor_id, payload, actor)
