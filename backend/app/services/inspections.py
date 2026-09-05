from datetime import UTC, datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import AuditLog, Inspection, InspectionChecklist, Mine, MineZone, User
from app.schemas.inspection import InspectionCreate, InspectionResponse, InspectionUpdate


def list_inspections(database: Session, status_filter: Optional[str]) -> list[InspectionResponse]:
    query = database.query(Inspection).options(joinedload(Inspection.mine), joinedload(Inspection.zone), joinedload(Inspection.checklist_items))
    if status_filter:
        query = query.filter(Inspection.status == status_filter.upper())
    return [_to_response(item) for item in query.order_by(Inspection.started_at.desc()).all()]


def get_inspection(database: Session, inspection_id: int) -> Inspection:
    item = database.query(Inspection).options(joinedload(Inspection.mine), joinedload(Inspection.zone), joinedload(Inspection.checklist_items)).filter(Inspection.id == inspection_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return item


def create_inspection(database: Session, payload: InspectionCreate, inspector: User) -> InspectionResponse:
    mine = database.query(Mine).filter(Mine.id == payload.mine_id).first()
    if mine is None:
        raise HTTPException(status_code=422, detail="Mine not found")
    _validate_zone(database, payload.mine_id, payload.zone_id)
    item = Inspection(inspector_id=inspector.id, **payload.model_dump(exclude={"checklist_items"}))
    database.add(item)
    try:
        database.flush()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Inspection code already exists") from error
    _replace_checklist(item, payload.checklist_items)
    _audit(database, inspector, "CREATE", item, f"Created inspection {item.inspection_code}")
    database.commit()
    return _to_response(get_inspection(database, item.id))


def update_inspection(database: Session, inspection_id: int, payload: InspectionUpdate, actor: User) -> InspectionResponse:
    item = get_inspection(database, inspection_id)
    values = payload.model_dump(exclude_unset=True, exclude={"checklist_items"})
    if values.get("status") == "SUBMITTED":
        values["submitted_at"] = datetime.now(UTC)
    for field, value in values.items():
        setattr(item, field, value)
    if payload.checklist_items is not None:
        _replace_checklist(item, payload.checklist_items)
    _audit(database, actor, "UPDATE", item, f"Updated inspection {item.inspection_code} to {item.status}")
    database.commit()
    return _to_response(get_inspection(database, inspection_id))


def _replace_checklist(item: Inspection, checklist_items) -> None:
    item.checklist_items.clear()
    item.checklist_items.extend([InspectionChecklist(item_code=entry.item_code, question=entry.question, response=entry.response, remarks=entry.remarks) for entry in checklist_items])


def _validate_zone(database: Session, mine_id: int, zone_id: Optional[int]) -> None:
    if zone_id is not None and database.query(MineZone).filter(MineZone.id == zone_id, MineZone.mine_id == mine_id).first() is None:
        raise HTTPException(status_code=422, detail="Zone does not belong to the selected mine")


def _to_response(item: Inspection) -> InspectionResponse:
    return InspectionResponse.model_validate(item).model_copy(update={"mine_name": item.mine.mine_name, "zone_name": item.zone.name if item.zone else None})


def _audit(database: Session, actor: User, action: str, item: Inspection, description: str) -> None:
    database.add(AuditLog(user_id=actor.id, action=action, entity="Inspection", entity_id=str(item.id), description=description))
