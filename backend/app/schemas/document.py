from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


DOCUMENT_TYPES = ("Inspection Report", "Compliance Certificate", "Safety Certificate", "Training Certificate", "License", "Evidence", "Other")


class OCRResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    extracted_text: str
    confidence: float
    detected_fields: Optional[str]
    verification_status: str
    processed_at: datetime


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    document_type: str
    file_path: str
    mine_id: Optional[int]
    contractor_id: Optional[int]
    uploaded_by: int
    uploaded_at: datetime
    status: str
    mine_name: Optional[str] = None
    contractor_name: Optional[str] = None
    ocr_result: Optional[OCRResultResponse] = None


class DocumentVerification(BaseModel):
    status: str = Field(pattern="^(PENDING|VERIFIED|REJECTED)$")
