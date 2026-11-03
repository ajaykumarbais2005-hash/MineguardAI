def test_admin_can_filter_audit_logs_and_read_summary(auth_client):
    login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    logs = auth_client.get("/audit?entity=SYSTEM", headers=headers)
    summary = auth_client.get("/audit/summary", headers=headers)

    assert logs.status_code == 200
    assert len(logs.json()) == 1
    assert logs.json()[0]["entity"] == "SYSTEM"
    assert summary.status_code == 200
    assert summary.json()["total"] == 2


def test_auditor_can_read_audit_trail(auth_client):
    login = auth_client.post("/auth/login", data={"username": "auditor@mineguard.ai", "password": "auditor123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.get("/audit", headers=headers)

    assert response.status_code == 200


def test_safety_officer_cannot_read_audit_trail(auth_client):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.get("/audit", headers=headers)

    assert response.status_code == 403
