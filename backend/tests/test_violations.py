def test_safety_officer_can_create_and_update_violation(auth_client):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    payload = {"violation_code": "VIO-TEST-01", "mine_id": 1, "zone_id": 1, "category": "PPE", "description": "Missing helmet", "severity": "HIGH"}

    created = auth_client.post("/violations", json=payload, headers=headers)
    assert created.status_code == 201
    violation_id = created.json()["id"]
    updated = auth_client.patch(f"/violations/{violation_id}", json={"status": "ASSIGNED"}, headers=headers)

    assert updated.status_code == 200
    assert updated.json()["status"] == "ASSIGNED"


def test_violation_summary_and_filters(auth_client):
    login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    critical = auth_client.get("/violations?severity=CRITICAL", headers=headers)
    summary = auth_client.get("/violations/summary", headers=headers)

    assert critical.status_code == 200
    assert critical.json() == []
    assert summary.status_code == 200
    assert summary.json()["total"] == 1
    assert summary.json()["critical"] == 0


def test_violation_rejects_zone_from_another_mine(auth_client):
    login = auth_client.post("/auth/login", data={"username": "inspector@mineguard.ai", "password": "inspector123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/violations", json={"violation_code": "VIO-BAD-ZONE", "mine_id": 2, "zone_id": 1, "category": "PPE", "description": "Invalid zone", "severity": "LOW"}, headers=headers)

    assert response.status_code == 422
