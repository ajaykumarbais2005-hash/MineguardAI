from sqlalchemy import select

from app.models import Alert, IoTReading, User
from app.schemas.iot import IoTThresholdUpdate
from app.services.iot import simulate_readings, update_threshold
from app.services.seed import seed_demo_data


def test_iot_simulation_persists_readings_and_creates_alert(auth_client, database_session):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/iot/simulate", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "SIMULATED_SENSOR_DATA"
    assert len(payload["sensors"]) == 3
    assert database_session.query(IoTReading).count() >= 9
    assert payload["alerts_created"] >= 1
    assert database_session.query(Alert).filter(Alert.alert_type.like("HIGH_%")).count() >= 1


def test_iot_threshold_update_and_history(auth_client):
    login = auth_client.post("/auth/login", data={"username": "manager@mineguard.ai", "password": "manager123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    updated = auth_client.patch("/iot/1/threshold", json={"threshold": 22}, headers=headers)
    history = auth_client.get("/iot/1/readings", headers=headers)

    assert updated.status_code == 200
    assert updated.json()["threshold"] == 22
    assert history.status_code == 200
    assert len(history.json()) >= 2


def test_iot_requires_authentication_and_valid_sensor(auth_client):
    assert auth_client.get("/iot").status_code == 401
    login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert auth_client.post("/iot/simulate?sensor_id=999", headers=headers).status_code == 404
