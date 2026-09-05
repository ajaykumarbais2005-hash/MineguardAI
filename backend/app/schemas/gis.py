from typing import Optional

from pydantic import BaseModel


class GISPoint(BaseModel):
    id: str
    kind: str
    label: str
    latitude: float
    longitude: float
    mine_id: int
    zone_id: Optional[int] = None
    status: Optional[str] = None
    risk_level: Optional[str] = None
    severity: Optional[str] = None
    demo_position: bool = False


class GISMapResponse(BaseModel):
    points: list[GISPoint]
    mode: str = "DEMO_DATA"
