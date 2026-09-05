import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.models import AuditLog, Contractor, Document, Mine, OCRResult, User
from app.schemas.document import DocumentResponse, DocumentVerification

_ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}
_MAX_BYTES = 10 * 1024 * 1024


def list_documents(database: Session) -> list[DocumentResponse]:
    query = database.query(Document).options(joinedload(Document.mine), joinedload(Document.contractor), joinedload(Document.ocr_result))
    return [_to_response(item) for item in query.order_by(Document.uploaded_at.desc()).all()]


def upload_document(database: Session, file: UploadFile, document_type: str, mine_id: Optional[int], contractor_id: Optional[int], actor: User) -> DocumentResponse:
    if not file.filename:
        raise HTTPException(status_code=422, detail="A file is required")
    extension = Path(file.filename).suffix.lower()
    if extension not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail="Unsupported document type")
    if document_type not in {"Inspection Report", "Compliance Certificate", "Safety Certificate", "Training Certificate", "License", "Evidence", "Other"}:
        raise HTTPException(status_code=422, detail="Unsupported document category")
    if mine_id is not None and database.query(Mine).filter(Mine.id == mine_id).first() is None:
        raise HTTPException(status_code=422, detail="Mine not found")
    if contractor_id is not None and database.query(Contractor).filter(Contractor.id == contractor_id).first() is None:
        raise HTTPException(status_code=422, detail="Contractor not found")

    content = file.file.read(_MAX_BYTES + 1)
    if len(content) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB limit")
    upload_directory = Path(get_settings().upload_directory)
    upload_directory.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{extension}"
    stored_path = upload_directory / stored_name
    stored_path.write_bytes(content)

    document = Document(file_name=file.filename, document_type=document_type, file_path=str(stored_path), mine_id=mine_id, contractor_id=contractor_id, uploaded_by=actor.id, uploaded_at=datetime.now(UTC), status="OCR_PROCESSED")
    database.add(document)
    database.flush()
    extracted_text, detected_fields, confidence = _demo_ocr(file.filename, content)
    database.add(OCRResult(document_id=document.id, extracted_text=extracted_text, confidence=confidence, detected_fields=json.dumps(detected_fields), verification_status="PENDING", processed_at=datetime.now(UTC)))
    database.add(AuditLog(user_id=actor.id, action="CREATE", entity="Document", entity_id=str(document.id), description=f"Uploaded document {file.filename} with DEMO OCR processing"))
    database.commit()
    return _to_response(database.query(Document).options(joinedload(Document.mine), joinedload(Document.contractor), joinedload(Document.ocr_result)).filter(Document.id == document.id).first())


def verify_document(database: Session, document_id: int, payload: DocumentVerification, actor: User) -> DocumentResponse:
    document = database.query(Document).options(joinedload(Document.mine), joinedload(Document.contractor), joinedload(Document.ocr_result)).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    document.status = payload.status
    if document.ocr_result:
        document.ocr_result.verification_status = payload.status
    database.add(AuditLog(user_id=actor.id, action="UPDATE", entity="Document", entity_id=str(document.id), description=f"Updated document verification to {payload.status}"))
    database.commit()
    return _to_response(document)


def _demo_ocr(file_name: str, content: bytes) -> tuple[str, dict[str, str], float]:
    text = content.decode("utf-8", errors="ignore")[:5000]
    if not text.strip():
        text = f"DEMO OCR extract for {file_name}. Certificate No: DEMO-{uuid4().hex[:8].upper()}; Expiry: 2026-12-31."
    fields = {}
    certificate = re.search(r"(?:certificate|license)\s*(?:no|number)?\s*[:#-]\s*([A-Z0-9-]+)", text, re.IGNORECASE)
    expiry = re.search(r"expiry\s*[:#-]\s*([0-9-]+)", text, re.IGNORECASE)
    if certificate:
        fields["certificate_number"] = certificate.group(1)
    if expiry:
        fields["expiry_date"] = expiry.group(1)
    fields["document_type"] = "DEMO_OCR"
    return text, fields, 0.96 if fields.get("certificate_number") else 0.82


def _to_response(item: Document) -> DocumentResponse:
    return DocumentResponse.model_validate(item).model_copy(update={"mine_name": item.mine.mine_name if item.mine else None, "contractor_name": item.contractor.company_name if item.contractor else None})
