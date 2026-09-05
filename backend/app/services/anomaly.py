from datetime import UTC, datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import AuditLog, Mine, MineZone, RiskEvent, User
from app.schemas.anomaly import AnomalyDetectRequest, AnomalyDetectResponse
from app.services.risk import calculate_risk

_METRIC_RULES = {
    "gas_level": (25.0, "above"),
    "temperature": (42.0, "above"),
    "dust": (4.0, "above"),
    "vehicle_speed": (40.0, "above"),
    "production": (20.0, "below"),
    "inspection_frequency": (1.0, "below"),
    "violation_frequency": (5.0, "above"),
    "contractor_performance": (75.0, "below"),
}


def detect_and_store(database: Session, payload: AnomalyDetectRequest, actor: User) -> AnomalyDetectResponse:
    mine = database.query(Mine).filter(Mine.id == payload.mine_id).first()
    if mine is None:
        raise HTTPException(status_code=422, detail="Mine not found")
    if payload.zone_id is not None and database.query(MineZone).filter(MineZone.id == payload.zone_id, MineZone.mine_id == payload.mine_id).first() is None:
        raise HTTPException(status_code=422, detail="Zone does not belong to the selected mine")

    default_threshold, direction = _METRIC_RULES[payload.metric]
    threshold = default_threshold if payload.threshold is None else payload.threshold
    is_anomaly = payload.value > threshold if direction == "above" else payload.value < threshold
    severity = 4.0 if is_anomaly else 1.0
    likelihood = 4.0 if is_anomaly else 1.0
    exposure = 4.0 if payload.metric in {"gas_level", "temperature", "dust", "vehicle_speed"} else 3.0
    recurrence = 3.0 if is_anomaly else 1.0
    comparison = "above" if direction == "above" else "below"
    reason = f"{payload.metric} reading {payload.value} is {comparison} the demo threshold {threshold}."
    risk_event = None
    risk_score = None
    risk_level = None
    if is_anomaly:
        risk_score, risk_level, _, recommended_action = calculate_risk(severity, likelihood, exposure, recurrence)
        risk_event = RiskEvent(mine_id=payload.mine_id, zone_id=payload.zone_id, event_type=f"ANOMALY_{payload.metric.upper()}", score=risk_score, level=risk_level, severity=severity, likelihood=likelihood, exposure=exposure, recurrence=recurrence, reason=reason, recommended_action=recommended_action, created_at=datetime.now(UTC))
        database.add(risk_event)
        database.flush()
        database.add(AuditLog(user_id=actor.id, action="CREATE", entity="RiskEvent", entity_id=str(risk_event.id), description=f"Detected DEMO anomaly for {payload.metric}"))
    database.commit()
    return AnomalyDetectResponse(id=risk_event.id if risk_event else None, mine_id=payload.mine_id, zone_id=payload.zone_id, metric=payload.metric, value=payload.value, threshold=threshold, is_anomaly=is_anomaly, severity=severity, likelihood=likelihood, exposure=exposure, recurrence=recurrence, reason=reason, risk_event_id=risk_event.id if risk_event else None, risk_score=risk_score, risk_level=risk_level, created_at=risk_event.created_at if risk_event else datetime.now(UTC), mode="DEMO_SIMULATION")
