from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.document import DocumentResponse, DocumentVerification
from app.services.documents import list_documents, upload_document, verify_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
def read_documents(database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[DocumentResponse]:
    return list_documents(database)


@router.post("", response_model=DocumentResponse, status_code=201)
def add_document(file: UploadFile = File(...), document_type: str = Form(...), mine_id: Optional[int] = Form(default=None), contractor_id: Optional[int] = Form(default=None), database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "INSPECTOR", "CONTRACTOR"))) -> DocumentResponse:
    return upload_document(database, file, document_type, mine_id, contractor_id, actor)


@router.patch("/{document_id}/verification", response_model=DocumentResponse)
def update_verification(document_id: int, payload: DocumentVerification, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "AUDITOR"))) -> DocumentResponse:
    return verify_document(database, document_id, payload, actor)
