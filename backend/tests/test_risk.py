import pytest
from sqlalchemy import select

from app.models import AuditLog, RiskEvent
from app.services.risk import calculate_risk


def test_risk_calculator_covers_levels_and_boundaries():
    cases = [
        ((1, 1, 1, 1), 0.16, "LOW"),
        ((3, 3, 3, 3), 12.96, "LOW"),
        ((4, 4, 4, 4), 40.96, "MEDIUM"),
        ((5, 4, 4, 4), 51.2, "HIGH"),
        ((5, 5, 5, 5), 100.0, "CRITICAL"),
    ]

    for factors, expected_score, expected_level in cases:
        score, level, reason, recommended_action = calculate_risk(*factors)
        assert score == expected_score
        assert level == expected_level
        assert reason
        assert recommended_action


def test_risk_calculator_rejects_invalid_factor():
    with pytest.raises(ValueError, match="between 1 and 5"):
        calculate_risk(0, 3, 3, 3)


def test_risk_api_persists_event_and_audit_log(auth_client, database_session):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/risk/calculate", json={"mine_id": 1, "zone_id": 1, "event_type": "PPE_NON_COMPLIANCE", "severity": 5, "likelihood": 5, "exposure": 5, "recurrence": 5}, headers=headers)

    assert response.status_code == 201
    payload = response.json()
    assert payload["score"] == 100
    assert payload["level"] == "CRITICAL"
    assert payload["recommended_action"]
    event = database_session.get(RiskEvent, payload["id"])
    assert event is not None
    audit = database_session.scalar(select(AuditLog).where(AuditLog.entity == "RiskEvent", AuditLog.entity_id == str(event.id)))
    assert audit is not None
    assert audit.action == "CREATE"


def test_risk_api_rejects_invalid_zone_and_unauthorized_role(auth_client):
    safety_login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    safety_headers = {"Authorization": f"Bearer {safety_login.json()['access_token']}"}
    invalid_zone = auth_client.post("/risk/calculate", json={"mine_id": 2, "zone_id": 1, "event_type": "GENERAL_SAFETY", "severity": 3, "likelihood": 3, "exposure": 3, "recurrence": 3}, headers=safety_headers)
    assert invalid_zone.status_code == 422

    contractor_login = auth_client.post("/auth/login", data={"username": "contractor@mineguard.ai", "password": "contractor123"})
    contractor_headers = {"Authorization": f"Bearer {contractor_login.json()['access_token']}"}
    denied = auth_client.post("/risk/calculate", json={"mine_id": 1, "event_type": "GENERAL_SAFETY", "severity": 3, "likelihood": 3, "exposure": 3, "recurrence": 3}, headers=contractor_headers)
    assert denied.status_code == 403


def test_risk_history_can_filter_by_mine_and_level(auth_client):
    login = auth_client.post("/auth/login", data={"username": "inspector@mineguard.ai", "password": "inspector123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = auth_client.post("/risk/calculate", json={"mine_id": 1, "event_type": "GROUND_CONTROL", "severity": 4, "likelihood": 4, "exposure": 4, "recurrence": 4}, headers=headers)
    filtered = auth_client.get("/risk?mine_id=1&level=MEDIUM", headers=headers)

    assert created.status_code == 201
    assert filtered.status_code == 200
    assert any(item["id"] == created.json()["id"] for item in filtered.json())
