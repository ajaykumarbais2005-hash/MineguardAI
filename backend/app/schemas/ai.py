from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PPEDetection(BaseModel):
    label: str
    confidence: float
    present: bool


class PPEDetectionRequest(BaseModel):
    mine_id: int = Field(ge=1)
    zone_id: Optional[int] = Field(default=None, ge=1)
    camera: str = Field(default="CAM-DEMO-01", min_length=2, max_length=100)
    case: str = Field(default="no_helmet", pattern="^(compliant|no_helmet|no_helmet_no_vest)$")
    media_reference: Optional[str] = None


class PPEDetectionResponse(BaseModel):
    event_id: int
    mode: str
    event_type: str
    severity: str
    detections: list[PPEDetection]
    confidence: float
    mine_id: int
    zone_id: Optional[int]
    camera: str
    created_at: datetime
    disclaimer: str
