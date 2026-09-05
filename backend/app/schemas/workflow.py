from pydantic import BaseModel


class WorkflowSummary(BaseModel):
    ai_events: int
    risk_events: int
    open_violations: int
    unread_alerts: int
    open_capa: int
