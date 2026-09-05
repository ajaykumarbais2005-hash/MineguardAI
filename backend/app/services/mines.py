from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Alert, AuditLog, IoTSensor, Inspection, Mine, MineZone, User, Violation
from app.schemas.mine import MineCreate, MineDetailResponse, MineResponse, MineStatistics, MineUpdate, MineZoneResponse

SORTABLE_FIELDS = {
    "mine_name": Mine.mine_name,
    "mine_code": Mine.mine_code,
    "status": Mine.status,
    "risk_level": Mine.risk_level,
    "created_at": Mine.created_at,
}


def list_mines(database: Session, search: Optional[str], status_filter: Optional[str], risk_level: Optional[str], sort_by: str, descending: bool) -> list[MineResponse]:
    query = database.query(Mine).options(joinedload(Mine.manager))
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(Mine.mine_name.ilike(term), Mine.mine_code.ilike(term), Mine.location.ilike(term), Mine.operator.ilike(term)))
    if status_filter:
        query = query.filter(Mine.status == status_filter.upper())
    if risk_level:
        query = query.filter(Mine.risk_level == risk_level.upper())
    order_column = SORTABLE_FIELDS.get(sort_by, Mine.mine_name)
    query = query.order_by(order_column.desc() if descending else order_column.asc())
    return [_to_response(mine) for mine in query.all()]


def get_mine(database: Session, mine_id: int) -> Mine:
    mine = database.query(Mine).options(joinedload(Mine.manager)).filter(Mine.id == mine_id).first()
    if mine is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mine not found")
    return mine


def create_mine(database: Session, payload: MineCreate, actor: User) -> MineResponse:
    _validate_manager(database, payload.manager_id)
    mine = Mine(**payload.model_dump())
    database.add(mine)
    try:
        database.flush()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Mine code already exists") from error
    _write_audit(database, actor, "CREATE", "Mine", str(mine.id), f"Created mine {mine.mine_code}")
    database.commit()
    return _to_response(get_mine(database, mine.id))


def update_mine(database: Session, mine_id: int, payload: MineUpdate, actor: User) -> MineResponse:
    mine = get_mine(database, mine_id)
    values = payload.model_dump(exclude_unset=True)
    _validate_manager(database, values.get("manager_id"))
    for field, value in values.items():
        setattr(mine, field, value)
    try:
        database.flush()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Mine code already exists") from error
    _write_audit(database, actor, "UPDATE", "Mine", str(mine.id), f"Updated mine {mine.mine_code}")
    database.commit()
    return _to_response(get_mine(database, mine.id))


def delete_mine(database: Session, mine_id: int, actor: User) -> None:
    mine = get_mine(database, mine_id)
    if any((mine.zones, mine.inspections, mine.violations, mine.ai_events, mine.risk_events, mine.sensors, mine.alerts, mine.documents, mine.gis_assets)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Mine cannot be deleted while related records exist")
    code = mine.mine_code
    database.delete(mine)
    _write_audit(database, actor, "DELETE", "Mine", str(mine_id), f"Deleted mine {code}")
    database.commit()


def get_mine_detail(database: Session, mine_id: int) -> MineDetailResponse:
    mine = get_mine(database, mine_id)
    statistics = MineStatistics(
        zone_count=len(mine.zones),
        inspection_count=database.query(Inspection).filter(Inspection.mine_id == mine_id).count(),
        open_violation_count=database.query(Violation).filter(Violation.mine_id == mine_id, Violation.status.not_in(["CLOSED", "VERIFIED"])).count(),
        active_sensor_count=database.query(IoTSensor).filter(IoTSensor.mine_id == mine_id, IoTSensor.status == "ONLINE").count(),
        alert_count=database.query(Alert).filter(Alert.mine_id == mine_id, Alert.status == "UNREAD").count(),
    )
    response = MineDetailResponse(**_to_response(mine).model_dump(), zones=[MineZoneResponse.model_validate(zone) for zone in mine.zones], statistics=statistics)
    return response


def _to_response(mine: Mine) -> MineResponse:
    return MineResponse.model_validate(mine).model_copy(update={"manager_name": mine.manager.full_name if mine.manager else None})


def _validate_manager(database: Session, manager_id: Optional[int]) -> None:
    if manager_id is not None and database.query(User).filter(User.id == manager_id).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Manager user not found")


def _write_audit(database: Session, actor: User, action: str, entity: str, entity_id: str, description: str) -> None:
    database.add(AuditLog(user_id=actor.id, action=action, entity=entity, entity_id=entity_id, description=description))
