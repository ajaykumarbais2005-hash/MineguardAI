from datetime import UTC, datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import AuditLog, Inspection, Mine, MineZone, User, Violation
from app.schemas.violation import ViolationCreate, ViolationResponse, ViolationSummary, ViolationUpdate


def list_violations(database: Session, status_filter: Optional[str], severity: Optional[str]) -> list[ViolationResponse]:
    query = database.query(Violation).options(joinedload(Violation.mine), joinedload(Violation.zone))
    if status_filter:
        query = query.filter(Violation.status == status_filter.upper())
    if severity:
        query = query.filter(Violation.severity == severity.upper())
    return [_to_response(item) for item in query.order_by(Violation.detected_at.desc()).all()]


def get_violation(database: Session, violation_id: int) -> Violation:
    item = database.query(Violation).options(joinedload(Violation.mine), joinedload(Violation.zone)).filter(Violation.id == violation_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Violation not found")
    return item


def summarize(database: Session) -> ViolationSummary:
    values = [item.status.upper() for item in database.query(Violation).all()]
    severities = [item.severity.upper() for item in database.query(Violation).all()]
    return ViolationSummary(open=values.count("OPEN"), assigned=values.count("ASSIGNED"), in_progress=values.count("IN_PROGRESS"), resolved=values.count("RESOLVED"), verified=values.count("VERIFIED"), closed=values.count("CLOSED"), critical=severities.count("CRITICAL"), total=len(values))


def create_violation(database: Session, payload: ViolationCreate, actor: User) -> ViolationResponse:
    mine = database.query(Mine).filter(Mine.id == payload.mine_id).first()
    if mine is None:
        raise HTTPException(status_code=422, detail="Mine not found")
    _validate_references(database, payload.mine_id, payload.zone_id, payload.inspection_id)
    item = Violation(detected_by=actor.id, detected_at=datetime.now(UTC), **payload.model_dump())
    database.add(item)
    try:
        database.flush()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Violation code already exists") from error
    database.add(AuditLog(user_id=actor.id, action="CREATE", entity="Violation", entity_id=str(item.id), description=f"Created violation {item.violation_code}"))
    database.commit()
    return _to_response(get_violation(database, item.id))


def update_violation(database: Session, violation_id: int, payload: ViolationUpdate, actor: User) -> ViolationResponse:
    item = get_violation(database, violation_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    database.add(AuditLog(user_id=actor.id, action="UPDATE", entity="Violation", entity_id=str(item.id), description=f"Updated violation {item.violation_code} to {item.status}"))
    database.commit()
    return _to_response(get_violation(database, violation_id))


def _validate_references(database: Session, mine_id: int, zone_id: Optional[int], inspection_id: Optional[int]) -> None:
    if zone_id is not None and database.query(MineZone).filter(MineZone.id == zone_id, MineZone.mine_id == mine_id).first() is None:
        raise HTTPException(status_code=422, detail="Zone does not belong to the selected mine")
    if inspection_id is not None and database.query(Inspection).filter(Inspection.id == inspection_id, Inspection.mine_id == mine_id).first() is None:
        raise HTTPException(status_code=422, detail="Inspection does not belong to the selected mine")


def _to_response(item: Violation) -> ViolationResponse:
    return ViolationResponse.model_validate(item).model_copy(update={"mine_name": item.mine.mine_name, "zone_name": item.zone.name if item.zone else None})
