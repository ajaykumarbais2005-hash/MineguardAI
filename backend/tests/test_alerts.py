def test_alert_list_summary_and_acknowledgement(auth_client):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    listed = auth_client.get("/alerts?status=UNREAD", headers=headers)
    summary = auth_client.get("/alerts/summary", headers=headers)
    updated = auth_client.patch("/alerts/1?status=ACKNOWLEDGED", headers=headers)

    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert summary.status_code == 200
    assert summary.json()["unread"] == 1
    assert updated.status_code == 200
    assert updated.json()["status"] == "ACKNOWLEDGED"
    assert updated.json()["acknowledged_by"] == "Safety"


def test_alert_rejects_invalid_status(auth_client):
    login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.patch("/alerts/1?status=INVALID", headers=headers)

    assert response.status_code == 422
