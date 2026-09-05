def test_compliance_list_filter_and_summary(auth_client):
    login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    compliant = auth_client.get("/compliance?status=COMPLIANT", headers=headers)
    totals = auth_client.get("/compliance/summary", headers=headers)

    assert compliant.status_code == 200
    assert len(compliant.json()) == 2
    assert all(item["status"] == "COMPLIANT" for item in compliant.json())
    assert totals.status_code == 200
    assert totals.json() == {
        "compliant": 2,
        "partially_compliant": 1,
        "non_compliant": 0,
        "overdue": 1,
        "critical": 0,
        "total": 4,
    }


def test_safety_officer_can_update_requirement(auth_client):
    login = auth_client.post("/auth/login", data={"username": "safety@mineguard.ai", "password": "safety123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.patch("/compliance/1", json={"status": "CRITICAL"}, headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "CRITICAL"


def test_inspector_cannot_create_requirement(auth_client):
    login = auth_client.post("/auth/login", data={"username": "inspector@mineguard.ai", "password": "inspector123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/compliance", json={"requirement_code": "NEW-001", "title": "Test", "description": "Test requirement", "category": "Safety", "regulation_reference": "Demo", "frequency": "DAILY"}, headers=headers)

    assert response.status_code == 403
