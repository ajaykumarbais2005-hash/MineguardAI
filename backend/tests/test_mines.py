from sqlalchemy import select

from app.models import AuditLog, Mine


def test_mine_list_search_and_detail(auth_client):
    login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = auth_client.get("/mines?search=Kusmunda&sort_by=mine_name", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    mine = auth_client.get("/mines/1", headers=headers)
    assert mine.status_code == 200
    assert mine.json()["statistics"] == {
        "zone_count": 2,
        "inspection_count": 1,
        "open_violation_count": 1,
        "active_sensor_count": 2,
        "alert_count": 1,
    }
    assert len(mine.json()["zones"]) == 2


def test_manager_can_create_update_and_delete_empty_mine(auth_client, database_session):
    login = auth_client.post("/auth/login", data={"username": "manager@mineguard.ai", "password": "manager123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    payload = {
        "mine_name": "Test Expansion",
        "mine_code": "MG-TEST-999",
        "location": "Korba, Chhattisgarh",
        "state": "Chhattisgarh",
        "district": "Korba",
        "mine_type": "OPEN_CAST",
        "operator": "MineGuard Demo",
        "status": "ACTIVE",
        "risk_level": "LOW",
    }

    created = auth_client.post("/mines", json=payload, headers=headers)
    assert created.status_code == 201
    mine_id = created.json()["id"]
    updated = auth_client.patch(f"/mines/{mine_id}", json={"risk_level": "HIGH"}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["risk_level"] == "HIGH"
    deleted = auth_client.delete(f"/mines/{mine_id}", headers=headers)
    assert deleted.status_code == 204
    assert database_session.scalar(select(Mine).where(Mine.id == mine_id)) is None
    assert database_session.query(AuditLog).filter(AuditLog.entity == "Mine").count() >= 3


def test_inspector_cannot_create_mine(auth_client):
    login = auth_client.post("/auth/login", data={"username": "inspector@mineguard.ai", "password": "inspector123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/mines", json={"mine_name": "Denied", "mine_code": "DENIED", "location": "Test", "state": "Test", "district": "Test", "mine_type": "OPEN_CAST", "operator": "Test"}, headers=headers)

    assert response.status_code == 403


def test_related_mine_cannot_be_deleted(auth_client):
    login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = auth_client.delete("/mines/1", headers=headers)

    assert response.status_code == 409
