def test_ppe_demo_mode_generates_missing_helmet_event(auth_client):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/ai/ppe/detect", json={"mine_id": 1, "zone_id": 1, "camera": "CAM-DEMO-01", "case": "no_helmet"}, headers=headers)

    assert response.status_code == 200
    assert response.json()["mode"] == "DEMO_SIMULATION"
    assert response.json()["event_type"] == "PPE_NON_COMPLIANCE"
    assert response.json()["severity"] == "HIGH"
    assert any(item["label"] == "no_helmet" and item["present"] for item in response.json()["detections"])


def test_ppe_demo_mode_reports_compliant_case(auth_client):
    login = auth_client.post("/auth/login", data={"username": "inspector@mineguard.ai", "password": "inspector123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/ai/ppe/detect", json={"mine_id": 1, "case": "compliant"}, headers=headers)

    assert response.status_code == 200
    assert response.json()["event_type"] == "PPE_COMPLIANT"
    assert response.json()["severity"] == "LOW"
