def test_gis_map_returns_required_layers(auth_client):
    login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = auth_client.get("/gis/map", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    kinds = {point["kind"] for point in payload["points"]}
    assert {"MINE", "ZONE", "CAMERA", "SENSOR", "RISK", "VIOLATION", "ALERT"} <= kinds
    assert payload["mode"] == "DEMO_DATA"
    assert any(point["demo_position"] for point in payload["points"])


def test_gis_map_requires_authentication(auth_client):
    response = auth_client.get("/gis/map")
    assert response.status_code == 401
