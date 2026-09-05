from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChecklistItemInput(BaseModel):
    item_code: str = Field(min_length=1, max_length=40)
    question: str = Field(min_length=2)
    response: Optional[str] = None
    remarks: Optional[str] = None


class ChecklistItemResponse(ChecklistItemInput):
    model_config = ConfigDict(from_attributes=True)

    id: int


class InspectionCreate(BaseModel):
    inspection_code: str = Field(min_length=2, max_length=40)
    mine_id: int = Field(ge=1)
    zone_id: Optional[int] = Field(default=None, ge=1)
    checklist_name: str = Field(min_length=2, max_length=150)
    findings: Optional[str] = None
    remarks: Optional[str] = None
    evidence_path: Optional[str] = Field(default=None, max_length=500)
    checklist_items: list[ChecklistItemInput] = Field(default_factory=list)


class InspectionUpdate(BaseModel):
    status: Optional[str] = None
    findings: Optional[str] = None
    remarks: Optional[str] = None
    evidence_path: Optional[str] = Field(default=None, max_length=500)
    checklist_items: Optional[list[ChecklistItemInput]] = None


class InspectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inspection_code: str
    mine_id: int
    zone_id: Optional[int]
    inspector_id: int
    checklist_name: str
    status: str
    findings: Optional[str]
    remarks: Optional[str]
    evidence_path: Optional[str]
    started_at: datetime
    submitted_at: Optional[datetime]
    mine_name: Optional[str] = None
    zone_name: Optional[str] = None
    checklist_items: list[ChecklistItemResponse] = []
