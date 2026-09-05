from io import BytesIO


def test_authenticated_safety_journey_across_phase_15_to_22(auth_client):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    assert auth_client.get("/health").status_code == 200
    assert auth_client.get("/mines", headers=headers).status_code == 200

    ai = auth_client.post("/ai/ppe/detect", json={"mine_id": 1, "zone_id": 1, "camera": "CAM-INTEGRATION-01", "case": "no_helmet"}, headers=headers)
    assert ai.status_code == 200
    assert ai.json()["workflow"]["status"] == "WORKFLOW_CREATED"

    summary = auth_client.get("/workflow/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["ai_events"] >= 2
    assert summary.json()["risk_events"] >= 2
    assert summary.json()["open_capa"] >= 2

    gis = auth_client.get("/gis/map", headers=headers)
    assert gis.status_code == 200
    assert any(point["kind"] == "RISK" for point in gis.json()["points"])

    iot = auth_client.post("/iot/simulate", headers=headers)
    assert iot.status_code == 200
    assert iot.json()["mode"] == "SIMULATED_SENSOR_DATA"

    report = auth_client.get("/reports/violation?mine_id=1", headers=headers)
    assert report.status_code == 200
    assert report.json()["rows"]

    document = auth_client.post("/documents", files={"file": ("integration.txt", BytesIO(b"Certificate No: INT-23; Expiry: 2026-12-31"), "text/plain")}, data={"document_type": "Evidence", "mine_id": "1"}, headers=headers)
    assert document.status_code == 201
    assert document.json()["ocr_result"]["verification_status"] == "PENDING"

    admin_login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    audit = auth_client.get("/audit?entity=AIEvent", headers=admin_headers)
    assert audit.status_code == 200
    assert any(item["entity"] == "AIEvent" for item in audit.json())
