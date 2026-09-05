from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import AIEvent, AuditLog, Mine, MineZone, User
from app.schemas.ai import PPEDetectionRequest, PPEDetectionResponse
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
    database.commit()
    return PPEDetectionResponse(event_id=event.id, mode="DEMO_SIMULATION", event_type=event_type, severity=severity, detections=[item.__dict__ for item in detections], confidence=confidence, mine_id=payload.mine_id, zone_id=payload.zone_id, camera=payload.camera, created_at=event.created_at, disclaimer="No trained production model was used. Results are simulated for demonstration.")
