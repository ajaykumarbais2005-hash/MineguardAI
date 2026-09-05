from datetime import UTC, datetime, timedelta


def test_safety_officer_can_create_and_close_capa(auth_client):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    payload = {"action_code": "CAPA-TEST-01", "violation_id": 1, "description": "Run toolbox talk", "responsible_person_id": 3, "contractor_id": 1, "priority": "HIGH", "deadline": (datetime.now(UTC) + timedelta(days=2)).isoformat()}

    created = auth_client.post("/corrective-actions", json=payload, headers=headers)
    assert created.status_code == 201
    action_id = created.json()["id"]
    closed = auth_client.patch(f"/corrective-actions/{action_id}", json={"status": "CLOSED", "verification": "Verified"}, headers=headers)

    assert closed.status_code == 200
    assert closed.json()["closure_date"] is not None


def test_capa_summary_and_status_filter(auth_client):
    login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    actions = auth_client.get("/corrective-actions?status=IN_PROGRESS", headers=headers)
    summary = auth_client.get("/corrective-actions/summary", headers=headers)

    assert actions.status_code == 200
    assert len(actions.json()) == 1
    assert summary.status_code == 200
    assert summary.json()["total"] == 1
