from datetime import UTC, datetime, time
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models import AuditLog
from app.schemas.audit import AuditResponse, AuditSummary


def record_security_event(
    database: Session,
    action: str,
    description: str,
    actor_id: Optional[int] = None,
    ip_address: Optional[str] = None,
) -> None:
    database.add(
        AuditLog(
            user_id=actor_id,
            action=action,
            entity="Authentication",
            entity_id=str(actor_id) if actor_id is not None else None,
            description=description,
            ip_address=ip_address,
        )
    )
    database.commit()


def list_logs(database: Session, action: Optional[str], entity: Optional[str], search: Optional[str]) -> list[AuditResponse]:
    query = database.query(AuditLog).options(joinedload(AuditLog.user))
    if action:
        query = query.filter(AuditLog.action == action.upper())
    if entity:
        query = query.filter(AuditLog.entity == entity)
    if search:
        query = query.filter(AuditLog.description.ilike(f"%{search.strip()}%"))
    return [_to_response(item) for item in query.order_by(AuditLog.created_at.desc()).all()]


def summarize(database: Session) -> AuditSummary:
    items = database.query(AuditLog).all()
    today = datetime.now(UTC).date()
    return AuditSummary(total=len(items), today=sum(item.created_at.date() == today for item in items), creates=sum(item.action == "CREATE" for item in items), updates=sum(item.action == "UPDATE" for item in items), deletes=sum(item.action == "DELETE" for item in items))


def _to_response(item: AuditLog) -> AuditResponse:
    return AuditResponse.model_validate(item).model_copy(update={"user_name": item.user.full_name if item.user else None, "user_email": item.user.email if item.user else None})
