def test_report_json_filters_and_csv_export(auth_client):
    login = auth_client.post("/auth/login", data={"username": "admin@mineguard.ai", "password": "admin123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    report = auth_client.get("/reports/violation?severity=HIGH&category=PPE", headers=headers)
    exported = auth_client.get("/reports/violation/csv?severity=HIGH", headers=headers)

    assert report.status_code == 200
    assert report.json()["report_type"] == "violation"
    assert len(report.json()["rows"]) == 1
    assert exported.status_code == 200
    assert "text/csv" in exported.headers["content-type"]
    assert "violation_code" not in exported.text
    assert "VIO-2026-0001" in exported.text


def test_report_supports_all_report_types(auth_client):
    login = auth_client.post("/auth/login", data={"username": "auditor@mineguard.ai", "password": "auditor123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    for report_type in ("compliance", "inspection", "violation", "capa", "contractor", "risk", "ai", "iot"):
        response = auth_client.get(f"/reports/{report_type}", headers=headers)
        assert response.status_code == 200
        assert response.json()["report_type"] == report_type


def test_report_requires_authentication(auth_client):
    assert auth_client.get("/reports/risk").status_code == 401
    assert auth_client.get("/reports/unknown").status_code == 401
