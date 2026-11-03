from io import BytesIO
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
import pytest
from pydantic import ValidationError
from sqlalchemy import select
from starlette.datastructures import UploadFile

from app.auth.security import create_access_token
from app.config import Settings, get_settings
from app.models import AuditLog, User
from app.services.seed import seed_demo_data


def _login(client, email="admin@mineguard.ai", password="admin123"):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_login_and_profile_never_expose_password_hash(auth_client):
    response = _login(auth_client)

    assert response.status_code == 200
    token = response.json()["access_token"]
    profile = auth_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert "hashed_password" not in profile.json()
    assert "password" not in response.json()


def test_inactive_account_login_uses_generic_authentication_error(auth_client, database_session):
    user = database_session.scalar(select(User).where(User.email == "admin@mineguard.ai"))
    user.is_active = False
    database_session.commit()

    response = _login(auth_client)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.parametrize(
    "token",
    [
        "not-a-valid-jwt",
        jwt.encode(
            {
                "sub": "1",
                "iat": datetime.now(UTC) - timedelta(hours=2),
                "exp": datetime.now(UTC) - timedelta(hours=1),
            },
            get_settings().jwt_secret.get_secret_value(),
            algorithm=get_settings().jwt_algorithm,
        ),
    ],
)
def test_invalid_and_expired_tokens_are_rejected(auth_client, token):
    response = auth_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_inactive_user_cannot_use_an_existing_token(auth_client, database_session):
    user = database_session.scalar(select(User).where(User.email == "admin@mineguard.ai"))
    token = create_access_token(str(user.id), user.role.name)
    user.is_active = False
    database_session.commit()

    response = auth_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


@pytest.mark.parametrize(
    ("email", "password", "allowed"),
    [
        ("admin@mineguard.ai", "admin123", True),
        ("manager@mineguard.ai", "manager123", False),
        ("safety@mineguard.ai", "safety123", False),
        ("inspector@mineguard.ai", "inspector123", False),
        ("contractor@mineguard.ai", "contractor123", False),
        ("auditor@mineguard.ai", "auditor123", False),
    ],
)
def test_admin_endpoint_enforces_all_defined_roles(auth_client, email, password, allowed):
    login = _login(auth_client, email, password)
    response = auth_client.get(
        "/auth/admin-check",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert response.status_code == (200 if allowed else 403)


def test_contractor_cannot_mutate_alert_status(auth_client):
    login = _login(auth_client, "contractor@mineguard.ai", "contractor123")
    response = auth_client.patch(
        "/alerts/1?status=ACKNOWLEDGED",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert response.status_code == 403


def test_invalid_api_input_is_rejected(auth_client):
    login = _login(auth_client)
    response = auth_client.post(
        "/mines",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
        json={
            "mine_name": "Invalid mine",
            "mine_code": "INVALID-001",
            "location": "Test",
            "state": "Test",
            "district": "Test",
            "mine_type": "OPEN_CAST",
            "operator": "Test",
            "latitude": 91,
            "longitude": 0,
        },
    )

    assert response.status_code == 422


def test_non_positive_resource_id_is_rejected(auth_client):
    login = _login(auth_client)
    response = auth_client.get(
        "/mines/0",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert response.status_code == 404


def test_cors_is_configured_for_explicit_origins(auth_client):
    origin = get_settings().cors_origin_list[0]
    response = auth_client.options(
        "/auth/me",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "*" not in get_settings().cors_origin_list


def test_security_headers_are_present_without_disabling_openapi(auth_client):
    response = auth_client.get("/health")
    docs = auth_client.get("/docs")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert "content-security-policy" not in docs.headers
    assert docs.status_code == 200


def test_authentication_events_are_audited_without_credentials(auth_client, database_session):
    _login(auth_client)
    _login(auth_client, password="wrong-password")
    auth_client.get("/auth/me")
    token = _login(auth_client).json()["access_token"]
    auth_client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})

    events = database_session.scalars(
        select(AuditLog).where(AuditLog.entity == "Authentication")
    ).all()
    actions = [event.action for event in events]

    assert actions.count("LOGIN_SUCCESS") == 2
    assert "LOGIN_FAILURE" in actions
    assert "AUTH_FAILURE" in actions
    assert "LOGOUT" in actions
    assert all("password" not in event.description.lower() for event in events)


def test_production_settings_reject_development_secret_and_http_origins():
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            jwt_secret="development-only-secret-change-me-32-bytes",
            cors_origins="https://frontend.example",
            _env_file=None,
        )
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            jwt_secret="replace-with-a-long-random-secret-at-least-32-characters",
            cors_origins="https://frontend.example",
            _env_file=None,
        )
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            jwt_secret="a-unique-production-secret-value-over-32-bytes",
            cors_origins="http://frontend.example",
            _env_file=None,
        )

    settings = Settings(
        environment="production",
        jwt_secret="a-unique-production-secret-value-over-32-bytes",
        cors_origins="https://frontend.example",
        _env_file=None,
    )
    assert settings.cors_origin_list == ["https://frontend.example"]


def test_upload_rejects_mime_mismatch_and_size_limit(auth_client, monkeypatch, tmp_path):
    import app.services.documents as document_service

    monkeypatch.setattr(
        document_service,
        "get_settings",
        lambda: type("TestSettings", (), {"upload_directory": str(tmp_path)})(),
    )
    login = _login(auth_client)
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    wrong_mime = auth_client.post(
        "/documents",
        files={"file": ("certificate.txt", b"plain text", "image/png")},
        data={"document_type": "Evidence"},
        headers=headers,
    )
    oversized = auth_client.post(
        "/documents",
        files={"file": ("large.txt", b"a" * (10 * 1024 * 1024 + 1), "text/plain")},
        data={"document_type": "Evidence"},
        headers=headers,
    )

    assert wrong_mime.status_code == 422
    assert oversized.status_code == 413
    assert list(tmp_path.iterdir()) == []


def test_upload_path_traversal_is_safely_rewritten(database_session, monkeypatch, tmp_path):
    import app.services.documents as document_service

    monkeypatch.setattr(
        document_service,
        "get_settings",
        lambda: type("TestSettings", (), {"upload_directory": str(tmp_path)})(),
    )
    seed_demo_data(database_session)
    actor = database_session.scalar(select(User).where(User.email == "safety@mineguard.ai"))
    file = UploadFile(filename="../../outside.txt", file=BytesIO(b"valid text"))

    result = document_service.upload_document(database_session, file, "Evidence", None, None, actor)

    assert result.file_name == "outside.txt"
    assert Path(result.file_path).name == result.file_path
    assert len(list(tmp_path.iterdir())) == 1
