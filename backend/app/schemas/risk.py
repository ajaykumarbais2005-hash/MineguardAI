from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RiskCalculateRequest(BaseModel):
    mine_id: int = Field(ge=1)
    zone_id: Optional[int] = Field(default=None, ge=1)
    event_type: str = Field(min_length=2, max_length=80)
    severity: float = Field(ge=1, le=5)
    likelihood: float = Field(ge=1, le=5)
    exposure: float = Field(ge=1, le=5)
    recurrence: float = Field(ge=1, le=5)


class RiskEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mine_id: int
    zone_id: Optional[int]
    event_type: str
    score: float
    level: str
    severity: float
    likelihood: float
    exposure: float
    recurrence: float
    reason: str
    recommended_action: str
    created_at: datetime
    mine_name: str = ""
    zone_name: Optional[str] = None
