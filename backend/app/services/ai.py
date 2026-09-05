from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import AIEvent, Alert, AuditLog, Contractor, CorrectiveAction, Mine, MineZone, RiskEvent, User, Violation
from app.schemas.ai import PPEWorkflow, PPEDetectionRequest, PPEDetectionResponse
from app.services.ai_service_adapter import classify_event, simulate_ppe_detection


def run_ppe_detection(database: Session, payload: PPEDetectionRequest, actor: User) -> PPEDetectionResponse:
    if database.query(Mine).filter(Mine.id == payload.mine_id).first() is None:
        raise HTTPException(status_code=422, detail="Mine not found")
    if payload.zone_id is not None and database.query(MineZone).filter(MineZone.id == payload.zone_id, MineZone.mine_id == payload.mine_id).first() is None:
        raise HTTPException(status_code=422, detail="Zone does not belong to the selected mine")
    detections = simulate_ppe_detection(payload.case)
    event_type, severity = classify_event(detections)
    confidence = round(sum(item.confidence for item in detections if item.present) / max(1, sum(item.present for item in detections)), 2)
    event = AIEvent(mine_id=payload.mine_id, zone_id=payload.zone_id, camera=payload.camera, event_type=event_type, confidence=confidence, severity=severity, media_reference=payload.media_reference or f"demo://ppe/{payload.case}", ai_model="DEMO_SIMULATION", status="NEW")
    database.add(event)
    database.flush()
    database.add(AuditLog(user_id=actor.id, action="AI_EVENT", entity="AIEvent", entity_id=str(event.id), description=f"Ran PPE detection in DEMO_SIMULATION mode: {event_type}"))
    workflow = PPEWorkflow(status="COMPLIANT")
    if event_type == "PPE_NON_COMPLIANCE":
        factor = 5.0 if severity == "CRITICAL" else 4.0
        likelihood = 5.0
        exposure = 5.0 if severity == "CRITICAL" else 4.0
        recurrence = 5.0 if severity == "CRITICAL" else 4.0
        score = round((factor * likelihood * exposure * recurrence / 625) * 100, 2)
        level = "CRITICAL" if score > 75 else "HIGH" if score > 50 else "MEDIUM"
        action = "Stop affected work, escalate, and verify controls before restart." if level == "CRITICAL" else "Assign immediate corrective action and verify controls."
        risk = RiskEvent(mine_id=payload.mine_id, zone_id=payload.zone_id, event_type=event_type, score=score, level=level, severity=factor, likelihood=likelihood, exposure=exposure, recurrence=recurrence, reason=f"PPE detection reported {event_type.lower()} in {payload.camera}.", recommended_action=action)
        database.add(risk)
        database.flush()
        violation = Violation(violation_code=f"VIO-AI-{event.id:06d}", mine_id=payload.mine_id, zone_id=payload.zone_id, category="PPE", description=f"AI demo detected PPE non-compliance on {payload.camera}.", severity=severity, detected_by=actor.id, status="OPEN", due_date=datetime.now(UTC) + timedelta(days=3), evidence_path=event.media_reference, assigned_officer=actor.full_name)
        database.add(violation)
        database.flush()
        contractor = database.query(Contractor).filter(Contractor.status == "ACTIVE").order_by(Contractor.id.asc()).first()
        capa = CorrectiveAction(action_code=f"CAPA-AI-{event.id:06d}", violation_id=violation.id, description="Brief the crew, enforce PPE compliance, and attach verification evidence.", responsible_person_id=actor.id, contractor_id=contractor.id if contractor else None, priority=severity, deadline=datetime.now(UTC) + timedelta(days=3), status="OPEN")
        database.add(capa)
        database.flush()
        alert = Alert(alert_type="PPE_VIOLATION", severity=severity, message=f"PPE non-compliance detected by {payload.camera}.", mine_id=payload.mine_id, zone_id=payload.zone_id, violation_id=violation.id, risk_event_id=risk.id, status="UNREAD")
        database.add(alert)
        database.flush()
        event.status = "LINKED"
        event.linked_risk_event_id = risk.id
        event.linked_violation_id = violation.id
        workflow = PPEWorkflow(risk_event_id=risk.id, violation_id=violation.id, alert_id=alert.id, capa_id=capa.id, contractor_id=contractor.id if contractor else None, status="WORKFLOW_CREATED")
        for entity, entity_id, description in (("RiskEvent", risk.id, "Created risk from AI PPE event"), ("Violation", violation.id, "Created violation from AI PPE event"), ("Alert", alert.id, "Created alert from AI PPE event"), ("CorrectiveAction", capa.id, "Created CAPA from AI PPE event")):
            database.add(AuditLog(user_id=actor.id, action="CREATE", entity=entity, entity_id=str(entity_id), description=description))
    database.commit()
    return PPEDetectionResponse(event_id=event.id, mode="DEMO_SIMULATION", event_type=event_type, severity=severity, detections=[item.__dict__ for item in detections], confidence=confidence, mine_id=payload.mine_id, zone_id=payload.zone_id, camera=payload.camera, created_at=event.created_at, disclaimer="No trained production model was used. Results are simulated for demonstration.", workflow=workflow)
