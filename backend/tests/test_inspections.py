def test_inspector_can_create_and_submit_inspection(auth_client):
    login = auth_client.post("/auth/login", data={"username": "inspector@mineguard.ai", "password": "inspector123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    payload = {
        "inspection_code": "INS-TEST-01",
        "mine_id": 1,
        "zone_id": 1,
        "checklist_name": "PPE Round",
        "findings": "Helmet gap",
        "remarks": "Follow-up required",
        "checklist_items": [{"item_code": "PPE-01", "question": "Helmet present?", "response": "NO", "remarks": "One worker"}],
    }

    created = auth_client.post("/inspections", json=payload, headers=headers)
    assert created.status_code == 201
    assert len(created.json()["checklist_items"]) == 1
    inspection_id = created.json()["id"]

    submitted = auth_client.patch(f"/inspections/{inspection_id}", json={"status": "SUBMITTED"}, headers=headers)
    assert submitted.status_code == 200
    assert submitted.json()["submitted_at"] is not None


def test_inspection_rejects_zone_from_another_mine(auth_client):
    login = auth_client.post("/auth/login", data={"username": "inspector@mineguard.ai", "password": "inspector123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    payload = {"inspection_code": "INS-INVALID-ZONE", "mine_id": 2, "zone_id": 1, "checklist_name": "Safety Round"}

    response = auth_client.post("/inspections", json=payload, headers=headers)

    assert response.status_code == 422
    assert response.json()["detail"] == "Zone does not belong to the selected mine"


def test_contractor_cannot_create_inspection(auth_client):
    login = auth_client.post("/auth/login", data={"username": "contractor@mineguard.ai", "password": "contractor123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.post("/inspections", json={"inspection_code": "INS-DENIED", "mine_id": 1, "checklist_name": "Safety Round"}, headers=headers)

    assert response.status_code == 403
