import pytest
from sqlalchemy import select

from app.models import AuditLog, RiskEvent
from app.schemas.anomaly import ANOMALY_METRICS


def test_anomaly_api_supports_all_phase_17_metrics(auth_client):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    values = {
        "gas_level": 40,
        "temperature": 50,
        "dust": 8,
        "vehicle_speed": 60,
        "production": 10,
        "inspection_frequency": 0,
        "violation_frequency": 10,
        "contractor_performance": 60,
    }

    for metric in ANOMALY_METRICS:
        response = auth_client.post("/anomaly/detect", json={"mine_id": 1, "zone_id": 1, "metric": metric, "value": values[metric]}, headers=headers)
        assert response.status_code == 201
        assert response.json()["is_anomaly"] is True
        assert response.json()["risk_event_id"] is not None


def test_anomaly_api_normal_reading_does_not_create_risk(auth_client):
    login = auth_client.post("/auth/login", data={"username": "inspector@mineguard.ai", "password": "inspector123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/anomaly/detect", json={"mine_id": 1, "zone_id": 1, "metric": "gas_level", "value": 20}, headers=headers)

    assert response.status_code == 201
    assert response.json()["is_anomaly"] is False
    assert response.json()["risk_event_id"] is None
    assert response.json()["mode"] == "DEMO_SIMULATION"


def test_anomaly_api_persists_risk_and_audit(auth_client, database_session):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/anomaly/detect", json={"mine_id": 1, "zone_id": 1, "metric": "temperature", "value": 50}, headers=headers)
    risk_id = response.json()["risk_event_id"]

    assert database_session.get(RiskEvent, risk_id) is not None
    audit = database_session.scalar(select(AuditLog).where(AuditLog.entity == "RiskEvent", AuditLog.entity_id == str(risk_id)))
    assert audit is not None
    assert audit.action == "CREATE"


def test_anomaly_api_rejects_invalid_metric_and_role(auth_client):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    invalid = auth_client.post("/anomaly/detect", json={"mine_id": 1, "metric": "humidity", "value": 90}, headers=headers)
    assert invalid.status_code == 422

    contractor_login = auth_client.post("/auth/login", data={"username": "contractor@mineguard.ai", "password": "contractor123"})
    contractor_headers = {"Authorization": f"Bearer {contractor_login.json()['access_token']}"}
    denied = auth_client.post("/anomaly/detect", json={"mine_id": 1, "metric": "gas_level", "value": 40}, headers=contractor_headers)
    assert denied.status_code == 403
