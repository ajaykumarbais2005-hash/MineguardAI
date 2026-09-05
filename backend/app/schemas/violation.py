from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ViolationCreate(BaseModel):
    violation_code: str = Field(min_length=2, max_length=40)
    mine_id: int = Field(ge=1)
    zone_id: Optional[int] = Field(default=None, ge=1)
    inspection_id: Optional[int] = Field(default=None, ge=1)
    category: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=2)
    severity: str = Field(min_length=2, max_length=30)
    due_date: Optional[datetime] = None
    evidence_path: Optional[str] = Field(default=None, max_length=500)
    assigned_officer: Optional[str] = Field(default=None, max_length=150)


class ViolationUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    evidence_path: Optional[str] = None
    assigned_officer: Optional[str] = None


class ViolationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    violation_code: str
    mine_id: int
    zone_id: Optional[int]
    inspection_id: Optional[int]
    category: str
    description: str
    severity: str
    detected_at: datetime
    detected_by: int
    status: str
    due_date: Optional[datetime]
    evidence_path: Optional[str]
    assigned_officer: Optional[str]
    mine_name: Optional[str] = None
    zone_name: Optional[str] = None


class ViolationSummary(BaseModel):
    open: int
    assigned: int
    in_progress: int
    resolved: int
    verified: int
    closed: int
    critical: int
    total: int
