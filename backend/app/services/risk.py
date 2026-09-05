from datetime import UTC, datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import AuditLog, Mine, MineZone, RiskEvent, User
from app.schemas.risk import RiskCalculateRequest, RiskEventResponse

_ACTIONS = {
    "LOW": "Continue routine controls and scheduled monitoring.",
    "MEDIUM": "Review controls and increase monitoring frequency.",
    "HIGH": "Assign immediate corrective action and verify controls.",
    "CRITICAL": "Stop affected work, escalate, and verify controls before restart.",
}


def calculate_risk(severity: float, likelihood: float, exposure: float, recurrence: float) -> tuple[float, str, str, str]:
    factors = (severity, likelihood, exposure, recurrence)
    if any(factor < 1 or factor > 5 for factor in factors):
        raise ValueError("Risk factors must be between 1 and 5")
    score = round((severity * likelihood * exposure * recurrence / 625) * 100, 2)
    level = "LOW" if score <= 25 else "MEDIUM" if score <= 50 else "HIGH" if score <= 75 else "CRITICAL"
    reason = f"Score reflects severity {severity}, likelihood {likelihood}, exposure {exposure}, and recurrence {recurrence}."
    return score, level, reason, _ACTIONS[level]


def calculate_and_store(database: Session, payload: RiskCalculateRequest, actor: User) -> RiskEventResponse:
    mine = database.query(Mine).filter(Mine.id == payload.mine_id).first()
    if mine is None:
        raise HTTPException(status_code=422, detail="Mine not found")
    zone = None
    if payload.zone_id is not None:
        zone = database.query(MineZone).filter(MineZone.id == payload.zone_id, MineZone.mine_id == payload.mine_id).first()
        if zone is None:
            raise HTTPException(status_code=422, detail="Zone does not belong to the selected mine")

    score, level, reason, recommended_action = calculate_risk(payload.severity, payload.likelihood, payload.exposure, payload.recurrence)
    event = RiskEvent(
        mine_id=payload.mine_id,
        zone_id=payload.zone_id,
        event_type=payload.event_type,
        score=score,
        level=level,
        severity=payload.severity,
        likelihood=payload.likelihood,
        exposure=payload.exposure,
        recurrence=payload.recurrence,
        reason=reason,
        recommended_action=recommended_action,
        created_at=datetime.now(UTC),
    )
    database.add(event)
    database.flush()
    database.add(AuditLog(user_id=actor.id, action="CREATE", entity="RiskEvent", entity_id=str(event.id), description=f"Calculated {level} risk for {payload.event_type}"))
    database.commit()
    return _to_response(database.query(RiskEvent).options(joinedload(RiskEvent.mine), joinedload(RiskEvent.zone)).filter(RiskEvent.id == event.id).first())


def list_risk_events(database: Session, mine_id: Optional[int], level: Optional[str]) -> list[RiskEventResponse]:
    query = database.query(RiskEvent).options(joinedload(RiskEvent.mine), joinedload(RiskEvent.zone))
    if mine_id is not None:
        query = query.filter(RiskEvent.mine_id == mine_id)
    if level:
        query = query.filter(RiskEvent.level == level.upper())
    return [_to_response(item) for item in query.order_by(RiskEvent.created_at.desc()).all()]


def _to_response(item: RiskEvent) -> RiskEventResponse:
    return RiskEventResponse.model_validate(item).model_copy(update={"mine_name": item.mine.mine_name, "zone_name": item.zone.name if item.zone else None})
