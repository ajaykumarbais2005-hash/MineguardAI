from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import AuditLog, Contractor, ContractorWorker, User
from app.schemas.contractor import ContractorCreate, ContractorResponse, ContractorSummary, ContractorUpdate, WorkerCreate, WorkerResponse


def list_contractors(database: Session, search: Optional[str], status_filter: Optional[str]) -> list[ContractorResponse]:
    query = database.query(Contractor).options(joinedload(Contractor.workers))
    if search:
        query = query.filter((Contractor.company_name.ilike(f"%{search.strip()}%")) | (Contractor.contractor_code.ilike(f"%{search.strip()}%")))
    if status_filter:
        query = query.filter(Contractor.status == status_filter.upper())
    return [ContractorResponse.model_validate(item) for item in query.order_by(Contractor.company_name.asc()).all()]


def summarize(database: Session) -> ContractorSummary:
    items = database.query(Contractor).all()
    return ContractorSummary(total=len(items), active=sum(item.status == "ACTIVE" for item in items), average_compliance_score=round(sum(item.compliance_score for item in items) / len(items), 1) if items else 0, workers=sum(item.workers_count for item in items), high_risk=sum(item.risk_score >= 50 for item in items))


def create_contractor(database: Session, payload: ContractorCreate, actor: User) -> ContractorResponse:
    item = Contractor(**payload.model_dump())
    database.add(item)
    try:
        database.flush()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contractor code or license already exists") from error
    database.add(AuditLog(user_id=actor.id, action="CREATE", entity="Contractor", entity_id=str(item.id), description=f"Created contractor {item.contractor_code}"))
    database.commit()
    return ContractorResponse.model_validate(database.query(Contractor).options(joinedload(Contractor.workers)).filter(Contractor.id == item.id).first())


def update_contractor(database: Session, contractor_id: int, payload: ContractorUpdate, actor: User) -> ContractorResponse:
    item = database.query(Contractor).options(joinedload(Contractor.workers)).filter(Contractor.id == contractor_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Contractor not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    database.add(AuditLog(user_id=actor.id, action="UPDATE", entity="Contractor", entity_id=str(item.id), description=f"Updated contractor {item.contractor_code}"))
    database.commit()
    return ContractorResponse.model_validate(item)


def add_worker(database: Session, contractor_id: int, payload: WorkerCreate, actor: User) -> WorkerResponse:
    contractor = database.query(Contractor).filter(Contractor.id == contractor_id).first()
    if contractor is None:
        raise HTTPException(status_code=404, detail="Contractor not found")
    worker = ContractorWorker(contractor_id=contractor_id, **payload.model_dump())
    database.add(worker)
    contractor.workers_count = contractor.workers_count + 1
    try:
        database.flush()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=409, detail="Worker code already exists") from error
    database.add(AuditLog(user_id=actor.id, action="CREATE", entity="ContractorWorker", entity_id=str(worker.id), description=f"Added worker to {contractor.contractor_code}"))
    database.commit()
    return WorkerResponse.model_validate(worker)
