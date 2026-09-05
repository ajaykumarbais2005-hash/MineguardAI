from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CAPACreate(BaseModel):
    action_code: str = Field(min_length=2, max_length=40)
    violation_id: int = Field(ge=1)
    description: str = Field(min_length=2)
    responsible_person_id: int = Field(ge=1)
    contractor_id: Optional[int] = Field(default=None, ge=1)
    priority: str = "MEDIUM"
    deadline: datetime
    evidence_path: Optional[str] = None


class CAPAUpdate(BaseModel):
    description: Optional[str] = None
    responsible_person_id: Optional[int] = None
    contractor_id: Optional[int] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    evidence_path: Optional[str] = None
    verification: Optional[str] = None


class CAPAResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action_code: str
    violation_id: int
    description: str
    responsible_person_id: int
    contractor_id: Optional[int]
    priority: str
    deadline: datetime
    status: str
    evidence_path: Optional[str]
    verification: Optional[str]
    closure_date: Optional[datetime]
    violation_code: Optional[str] = None
    contractor_name: Optional[str] = None
    responsible_person_name: Optional[str] = None


class CAPASummary(BaseModel):
    open: int
    in_progress: int
    submitted: int
    verification_pending: int
    verified: int
    rejected: int
    closed: int
    total: int
