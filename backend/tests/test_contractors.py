def test_contractor_list_and_summary(auth_client):
    login = auth_client.post("/auth/login", data={"username": "manager@mineguard.ai", "password": "manager123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    listed = auth_client.get("/contractors?search=Bharat", headers=headers)
    summary = auth_client.get("/contractors/summary", headers=headers)

    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert summary.status_code == 200
    assert summary.json()["total"] == 2
    assert summary.json()["workers"] == 40


def test_manager_can_add_contractor_worker(auth_client):
    login = auth_client.post("/auth/login", data={"username": "manager@mineguard.ai", "password": "manager123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/contractors/1/workers", json={"worker_code": "WRK-TEST-01", "name": "Test Worker", "role": "Operator"}, headers=headers)

    assert response.status_code == 201
    assert response.json()["name"] == "Test Worker"


def test_inspector_cannot_create_contractor(auth_client):
    login = auth_client.post("/auth/login", data={"username": "inspector@mineguard.ai", "password": "inspector123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/contractors", json={"contractor_code": "DENIED", "company_name": "Denied", "license_number": "DENIED-LIC", "contact_person": "Test", "phone": "12345", "email": "test@example.com", "work_type": "Test"}, headers=headers)

    assert response.status_code == 403
