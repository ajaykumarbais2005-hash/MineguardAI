from datetime import UTC, datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import Alert, AuditLog, Mine, MineZone, User
from app.schemas.alert import AlertCreate, AlertResponse, AlertSummary


def list_alerts(database: Session, status_filter: Optional[str], severity: Optional[str]) -> list[AlertResponse]:
    query = database.query(Alert).options(joinedload(Alert.mine), joinedload(Alert.zone))
    if status_filter:
        query = query.filter(Alert.status == status_filter.upper())
    if severity:
        query = query.filter(Alert.severity == severity.upper())
    return [_to_response(item) for item in query.order_by(Alert.created_at.desc()).all()]


def summarize(database: Session) -> AlertSummary:
    items = database.query(Alert).all()
    return AlertSummary(unread=sum(item.status == "UNREAD" for item in items), acknowledged=sum(item.status == "ACKNOWLEDGED" for item in items), resolved=sum(item.status == "RESOLVED" for item in items), critical=sum(item.severity == "CRITICAL" for item in items), total=len(items))


def create_alert(database: Session, payload: AlertCreate, actor: User) -> AlertResponse:
    if database.query(Mine).filter(Mine.id == payload.mine_id).first() is None:
        raise HTTPException(status_code=422, detail="Mine not found")
    if payload.zone_id is not None and database.query(MineZone).filter(MineZone.id == payload.zone_id, MineZone.mine_id == payload.mine_id).first() is None:
        raise HTTPException(status_code=422, detail="Zone does not belong to the selected mine")
    item = Alert(**payload.model_dump(), created_at=datetime.now(UTC))
    database.add(item)
    database.flush()
    database.add(AuditLog(user_id=actor.id, action="CREATE", entity="Alert", entity_id=str(item.id), description=f"Created alert {item.alert_type}"))
    database.commit()
    return _to_response(database.query(Alert).options(joinedload(Alert.mine), joinedload(Alert.zone)).filter(Alert.id == item.id).first())


def update_alert(database: Session, alert_id: int, next_status: str, actor: User) -> AlertResponse:
    item = database.query(Alert).options(joinedload(Alert.mine), joinedload(Alert.zone)).filter(Alert.id == alert_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    if next_status not in {"UNREAD", "ACKNOWLEDGED", "RESOLVED"}:
        raise HTTPException(status_code=422, detail="Invalid alert status")
    item.status = next_status
    item.acknowledged_by = actor.full_name if next_status != "UNREAD" else None
    database.add(AuditLog(user_id=actor.id, action="UPDATE", entity="Alert", entity_id=str(item.id), description=f"Updated alert status to {next_status}"))
    database.commit()
    return _to_response(item)


def _to_response(item: Alert) -> AlertResponse:
    return AlertResponse.model_validate(item).model_copy(update={"mine_name": item.mine.mine_name, "zone_name": item.zone.name if item.zone else None})
