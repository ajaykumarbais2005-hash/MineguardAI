from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    alert_type: str
    severity: str
    message: str
    mine_id: int
    zone_id: Optional[int]
    violation_id: Optional[int]
    risk_event_id: Optional[int]
    status: str
    acknowledged_by: Optional[str]
    created_at: datetime
    mine_name: str = ""
    zone_name: Optional[str] = None


class AlertCreate(BaseModel):
    alert_type: str = Field(min_length=2, max_length=80)
    severity: str = Field(min_length=2, max_length=30)
    message: str = Field(min_length=2)
    mine_id: int = Field(ge=1)
    zone_id: Optional[int] = Field(default=None, ge=1)


class AlertSummary(BaseModel):
    unread: int
    acknowledged: int
    resolved: int
    critical: int
    total: int
