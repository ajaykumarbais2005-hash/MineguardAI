from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ComplianceBase(BaseModel):
    requirement_code: str = Field(min_length=2, max_length=40)
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=2)
    category: str = Field(min_length=2, max_length=80)
    regulation_reference: str = Field(min_length=2, max_length=200)
    mandatory: bool = True
    applicable_mine_type: str = "ALL"
    frequency: str = Field(min_length=2, max_length=50)
    status: str = Field(default="PENDING", min_length=2, max_length=40)
    last_verification: Optional[datetime] = None
    next_due_date: Optional[datetime] = None


class ComplianceCreate(ComplianceBase):
    pass


class ComplianceUpdate(BaseModel):
    requirement_code: Optional[str] = Field(default=None, min_length=2, max_length=40)
    title: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, min_length=2)
    category: Optional[str] = Field(default=None, min_length=2, max_length=80)
    regulation_reference: Optional[str] = Field(default=None, min_length=2, max_length=200)
    mandatory: Optional[bool] = None
    applicable_mine_type: Optional[str] = None
    frequency: Optional[str] = None
    status: Optional[str] = None
    last_verification: Optional[datetime] = None
    next_due_date: Optional[datetime] = None


class ComplianceResponse(ComplianceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ComplianceSummary(BaseModel):
    compliant: int
    partially_compliant: int
    non_compliant: int
    overdue: int
    critical: int
    total: int
