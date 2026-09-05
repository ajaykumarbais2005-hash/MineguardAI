from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkerCreate(BaseModel):
    worker_code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=150)
    role: str = Field(min_length=2, max_length=100)
    training_status: str = "VALID"
    ppe_status: str = "COMPLIANT"
    medical_valid_until: Optional[datetime] = None
    training_valid_until: Optional[datetime] = None
    site_assignment: Optional[str] = None


class WorkerResponse(WorkerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ContractorCreate(BaseModel):
    contractor_code: str = Field(min_length=2, max_length=40)
    company_name: str = Field(min_length=2, max_length=180)
    license_number: str = Field(min_length=2, max_length=100)
    contact_person: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=5, max_length=30)
    email: str = Field(min_length=5, max_length=255)
    work_type: str = Field(min_length=2, max_length=120)
    workers_count: int = Field(default=0, ge=0)
    compliance_score: float = Field(default=0, ge=0, le=100)
    risk_score: float = Field(default=0, ge=0, le=100)
    status: str = "ACTIVE"


class ContractorUpdate(BaseModel):
    compliance_score: Optional[float] = Field(default=None, ge=0, le=100)
    risk_score: Optional[float] = Field(default=None, ge=0, le=100)
    status: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ContractorResponse(ContractorCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    workers: list[WorkerResponse] = []


class ContractorSummary(BaseModel):
    total: int
    active: int
    average_compliance_score: float
    workers: int
    high_risk: int
