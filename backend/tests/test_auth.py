def test_demo_admin_can_login_and_read_profile(auth_client):
    client = auth_client

    response = client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] > 0

    profile = client.get("/auth/me", headers={"Authorization": f"Bearer {payload['access_token']}"})
    assert profile.status_code == 200
    assert profile.json()["role"] == "ADMIN"


def test_invalid_login_is_rejected(auth_client):
    client = auth_client

    response = client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_missing_token_is_rejected(auth_client):
    client = auth_client

    response = client.get("/auth/me")

    assert response.status_code == 401


def test_role_guard_denies_manager_admin_endpoint(auth_client):
    client = auth_client
    login = client.post("/auth/login", data={"username": "manager@mineguard.ai", "password": "manager123"})
    token = login.json()["access_token"]

    response = client.get("/auth/admin-check", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_role_guard_allows_admin(auth_client):
    client = auth_client
    login = client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    token = login.json()["access_token"]

    response = client.get("/auth/admin-check", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "admin@mineguard.ai"
