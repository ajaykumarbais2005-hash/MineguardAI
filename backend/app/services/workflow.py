from sqlalchemy.orm import Session

from app.models import AIEvent, Alert, CorrectiveAction, RiskEvent, Violation
from app.schemas.workflow import WorkflowSummary


def summarize_workflow(database: Session) -> WorkflowSummary:
    return WorkflowSummary(ai_events=database.query(AIEvent).count(), risk_events=database.query(RiskEvent).count(), open_violations=database.query(Violation).filter(Violation.status.notin_(["CLOSED", "VERIFIED"])).count(), unread_alerts=database.query(Alert).filter(Alert.status == "UNREAD").count(), open_capa=database.query(CorrectiveAction).filter(CorrectiveAction.status.notin_(["CLOSED", "VERIFIED"])).count())
