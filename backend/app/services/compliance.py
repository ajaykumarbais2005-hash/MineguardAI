from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AuditLog, ComplianceRequirement, User
from app.schemas.compliance import ComplianceCreate, ComplianceResponse, ComplianceSummary, ComplianceUpdate


def list_requirements(database: Session, search: Optional[str], status_filter: Optional[str], category: Optional[str]) -> list[ComplianceResponse]:
    query = database.query(ComplianceRequirement)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((ComplianceRequirement.title.ilike(term)) | (ComplianceRequirement.requirement_code.ilike(term)) | (ComplianceRequirement.description.ilike(term)))
    if status_filter:
        query = query.filter(ComplianceRequirement.status == status_filter.upper())
    if category:
        query = query.filter(ComplianceRequirement.category == category)
    return [ComplianceResponse.model_validate(item) for item in query.order_by(ComplianceRequirement.next_due_date.asc()).all()]


def summary(database: Session) -> ComplianceSummary:
    values = [item.status.upper() for item in database.query(ComplianceRequirement).all()]
    return ComplianceSummary(compliant=values.count("COMPLIANT"), partially_compliant=values.count("PARTIALLY_COMPLIANT"), non_compliant=values.count("NON_COMPLIANT"), overdue=values.count("OVERDUE"), critical=values.count("CRITICAL"), total=len(values))


def create_requirement(database: Session, payload: ComplianceCreate, actor: User) -> ComplianceResponse:
    item = ComplianceRequirement(**payload.model_dump())
    database.add(item)
    try:
        database.flush()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Requirement code already exists") from error
    database.add(AuditLog(user_id=actor.id, action="CREATE", entity="ComplianceRequirement", entity_id=str(item.id), description=f"Created requirement {item.requirement_code}"))
    database.commit()
    return ComplianceResponse.model_validate(item)


def update_requirement(database: Session, requirement_id: int, payload: ComplianceUpdate, actor: User) -> ComplianceResponse:
    item = database.query(ComplianceRequirement).filter(ComplianceRequirement.id == requirement_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Compliance requirement not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    database.add(AuditLog(user_id=actor.id, action="UPDATE", entity="ComplianceRequirement", entity_id=str(item.id), description=f"Updated requirement {item.requirement_code}"))
    database.commit()
    return ComplianceResponse.model_validate(item)
