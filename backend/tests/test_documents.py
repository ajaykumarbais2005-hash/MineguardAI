from io import BytesIO

from sqlalchemy import select
from starlette.datastructures import UploadFile

from app.models import AuditLog, Document, OCRResult
from app.schemas.document import DocumentVerification
from app.services.documents import upload_document, verify_document


def test_document_upload_runs_demo_ocr_and_persists_metadata(database_session):
    from app.models import User
    from app.services.seed import seed_demo_data

    seed_demo_data(database_session)
    actor = database_session.scalar(select(User).where(User.email == "safety@mineguard.ai"))
    file = UploadFile(filename="certificate.txt", file=BytesIO(b"Certificate No: CERT-18; Expiry: 2026-12-31"))

    result = upload_document(database_session, file, "Safety Certificate", 1, None, actor)

    assert result.status == "OCR_PROCESSED"
    assert result.ocr_result is not None
    assert result.ocr_result.confidence == 0.96
    assert "certificate_number" in result.ocr_result.detected_fields
    assert database_session.get(Document, result.id) is not None
    assert database_session.scalar(select(OCRResult).where(OCRResult.document_id == result.id)) is not None


def test_document_verification_updates_document_and_ocr(database_session):
    from app.models import User
    from app.services.seed import seed_demo_data

    seed_demo_data(database_session)
    actor = database_session.scalar(select(User).where(User.email == "safety@mineguard.ai"))
    file = UploadFile(filename="evidence.txt", file=BytesIO(b"Evidence record"))
    created = upload_document(database_session, file, "Evidence", 1, None, actor)

    verified = verify_document(database_session, created.id, DocumentVerification(status="VERIFIED"), actor)

    assert verified.status == "VERIFIED"
    assert verified.ocr_result.verification_status == "VERIFIED"
    audit = database_session.scalar(select(AuditLog).where(AuditLog.entity == "Document", AuditLog.entity_id == str(created.id)).order_by(AuditLog.id.desc()))
    assert audit is not None
    assert audit.action == "UPDATE"


def test_document_api_requires_authorized_role_and_rejects_extension(auth_client):
    login = auth_client.post("/auth/login", data={"username": "contractor@mineguard.ai", "password": "contractor123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    invalid = auth_client.post("/documents", files={"file": ("unsafe.exe", b"bad")}, data={"document_type": "Evidence"}, headers=headers)
    assert invalid.status_code == 422

    auditor_login = auth_client.post("/auth/login", data={"username": "auditor@mineguard.ai", "password": "auditor123"})
    auditor_headers = {"Authorization": f"Bearer {auditor_login.json()['access_token']}"}
    denied_upload = auth_client.post("/documents", files={"file": ("evidence.txt", b"text")}, data={"document_type": "Evidence"}, headers=auditor_headers)
    assert denied_upload.status_code == 403
