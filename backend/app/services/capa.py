from datetime import UTC, datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import AuditLog, Contractor, CorrectiveAction, User, Violation
from app.schemas.capa import CAPACreate, CAPAResponse, CAPASummary, CAPAUpdate


def list_actions(database: Session, status_filter: Optional[str]) -> list[CAPAResponse]:
    query = database.query(CorrectiveAction).options(joinedload(CorrectiveAction.violation), joinedload(CorrectiveAction.contractor), joinedload(CorrectiveAction.responsible_person))
    if status_filter:
        query = query.filter(CorrectiveAction.status == status_filter.upper())
    return [_to_response(item) for item in query.order_by(CorrectiveAction.deadline.asc()).all()]


def summarize(database: Session) -> CAPASummary:
    values = [item.status.upper() for item in database.query(CorrectiveAction).all()]
    return CAPASummary(open=values.count("OPEN"), in_progress=values.count("IN_PROGRESS"), submitted=values.count("SUBMITTED"), verification_pending=values.count("VERIFICATION_PENDING"), verified=values.count("VERIFIED"), rejected=values.count("REJECTED"), closed=values.count("CLOSED"), total=len(values))


def create_action(database: Session, payload: CAPACreate, actor: User) -> CAPAResponse:
    violation = database.query(Violation).filter(Violation.id == payload.violation_id).first()
    if violation is None:
        raise HTTPException(status_code=422, detail="Violation not found")
    _validate_people(database, payload.responsible_person_id, payload.contractor_id)
    item = CorrectiveAction(**payload.model_dump())
    database.add(item)
    try:
        database.flush()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Action code already exists") from error
    database.add(AuditLog(user_id=actor.id, action="CREATE", entity="CorrectiveAction", entity_id=str(item.id), description=f"Created CAPA {item.action_code}"))
    database.commit()
    return _to_response(database.query(CorrectiveAction).options(joinedload(CorrectiveAction.violation), joinedload(CorrectiveAction.contractor), joinedload(CorrectiveAction.responsible_person)).filter(CorrectiveAction.id == item.id).first())


def update_action(database: Session, action_id: int, payload: CAPAUpdate, actor: User) -> CAPAResponse:
    item = database.query(CorrectiveAction).filter(CorrectiveAction.id == action_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Corrective action not found")
    values = payload.model_dump(exclude_unset=True)
    _validate_people(database, values.get("responsible_person_id"), values.get("contractor_id"))
    for field, value in values.items():
        setattr(item, field, value)
    if item.status == "CLOSED":
        item.closure_date = datetime.now(UTC)
    database.add(AuditLog(user_id=actor.id, action="UPDATE", entity="CorrectiveAction", entity_id=str(item.id), description=f"Updated CAPA {item.action_code} to {item.status}"))
    database.commit()
    return _to_response(database.query(CorrectiveAction).options(joinedload(CorrectiveAction.violation), joinedload(CorrectiveAction.contractor), joinedload(CorrectiveAction.responsible_person)).filter(CorrectiveAction.id == action_id).first())


def _validate_people(database: Session, responsible_person_id: Optional[int], contractor_id: Optional[int]) -> None:
    if responsible_person_id is not None and database.query(User).filter(User.id == responsible_person_id).first() is None:
        raise HTTPException(status_code=422, detail="Responsible person not found")
    if contractor_id is not None and database.query(Contractor).filter(Contractor.id == contractor_id).first() is None:
        raise HTTPException(status_code=422, detail="Contractor not found")


def _to_response(item: CorrectiveAction) -> CAPAResponse:
    return CAPAResponse.model_validate(item).model_copy(update={"violation_code": item.violation.violation_code, "contractor_name": item.contractor.company_name if item.contractor else None, "responsible_person_name": item.responsible_person.full_name})
