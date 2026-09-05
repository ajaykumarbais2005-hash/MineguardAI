from sqlalchemy import select

from app.models import AIEvent, Alert, AuditLog, CorrectiveAction, RiskEvent, Violation


def test_ppe_detection_creates_complete_safety_workflow(auth_client, database_session):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/ai/ppe/detect", json={"mine_id": 1, "zone_id": 1, "camera": "CAM-WORKFLOW-01", "case": "no_helmet"}, headers=headers)

    assert response.status_code == 200
    workflow = response.json()["workflow"]
    assert workflow["status"] == "WORKFLOW_CREATED"
    assert all(workflow[key] for key in ("risk_event_id", "violation_id", "alert_id", "capa_id", "contractor_id"))
    event = database_session.get(AIEvent, response.json()["event_id"])
    risk = database_session.get(RiskEvent, workflow["risk_event_id"])
    violation = database_session.get(Violation, workflow["violation_id"])
    alert = database_session.get(Alert, workflow["alert_id"])
    capa = database_session.get(CorrectiveAction, workflow["capa_id"])
    assert event.linked_risk_event_id == risk.id
    assert event.linked_violation_id == violation.id
    assert alert.risk_event_id == risk.id and alert.violation_id == violation.id
    assert capa.violation_id == violation.id and capa.contractor_id == workflow["contractor_id"]
    expected_audits = [("RiskEvent", risk.id), ("Violation", violation.id), ("Alert", alert.id), ("CorrectiveAction", capa.id)]
    assert all(database_session.query(AuditLog).filter(AuditLog.entity == entity, AuditLog.entity_id == str(entity_id)).count() == 1 for entity, entity_id in expected_audits)


def test_compliant_ppe_does_not_create_downstream_workflow(auth_client):
    login = auth_client.post("/auth/login", data={"username": "inspector@mineguard.ai", "password": "inspector123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = auth_client.post("/ai/ppe/detect", json={"mine_id": 1, "case": "compliant"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["workflow"]["status"] == "COMPLIANT"
    assert response.json()["workflow"]["risk_event_id"] is None
