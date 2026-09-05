from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


ANOMALY_METRICS = (
    "gas_level",
    "temperature",
    "dust",
    "vehicle_speed",
    "production",
    "inspection_frequency",
    "violation_frequency",
    "contractor_performance",
)


class AnomalyDetectRequest(BaseModel):
    mine_id: int = Field(ge=1)
    zone_id: Optional[int] = Field(default=None, ge=1)
    metric: str = Field(pattern="^(gas_level|temperature|dust|vehicle_speed|production|inspection_frequency|violation_frequency|contractor_performance)$")
    value: float
    threshold: Optional[float] = None


class AnomalyDetectResponse(BaseModel):
    id: Optional[int]
    mine_id: int
    zone_id: Optional[int]
    metric: str
    value: float
    threshold: float
    is_anomaly: bool
    severity: float
    likelihood: float
    exposure: float
    recurrence: float
    reason: str
    risk_event_id: Optional[int]
    risk_score: Optional[float]
    risk_level: Optional[str]
    created_at: datetime
    mode: str
