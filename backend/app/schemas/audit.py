from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: Optional[int]
    action: str
    entity: str
    entity_id: Optional[str]
    description: str
    ip_address: Optional[str]
    created_at: datetime
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class AuditSummary(BaseModel):
    total: int
    today: int
    creates: int
    updates: int
    deletes: int
