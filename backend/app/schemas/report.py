from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field


REPORT_TYPES = ("compliance", "inspection", "violation", "capa", "contractor", "risk", "ai", "iot")


class ReportFilters(BaseModel):
    mine_id: Optional[int] = Field(default=None, ge=1)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None


class ReportResponse(BaseModel):
    report_type: str
    mode: str = "LIVE_API"
    generated_at: str
    rows: list[dict[str, Any]]
