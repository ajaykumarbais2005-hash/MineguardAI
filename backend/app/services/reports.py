import csv
import io
from datetime import UTC, date, datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import AIEvent, ComplianceRequirement, Contractor, CorrectiveAction, Inspection, IoTReading, RiskEvent, Violation
from app.schemas.report import REPORT_TYPES, ReportFilters, ReportResponse


def build_report(database: Session, report_type: str, filters: ReportFilters) -> ReportResponse:
    if report_type not in REPORT_TYPES:
        raise HTTPException(status_code=404, detail="Unknown report type")
    rows = _rows(database, report_type, filters)
    return ReportResponse(report_type=report_type, generated_at=datetime.now(UTC).isoformat(), rows=rows)


def render_csv(report: ReportResponse) -> str:
    output = io.StringIO()
    fields = sorted({key for row in report.rows for key in row})
    writer = csv.DictWriter(output, fieldnames=fields or ["message"])
    writer.writeheader()
    if report.rows:
        writer.writerows(report.rows)
    else:
        writer.writerow({"message": "No records matched the selected filters."} if not fields else {field: "" for field in fields})
    return output.getvalue()


def _rows(database: Session, report_type: str, filters: ReportFilters) -> list[dict[str, Any]]:
    if report_type == "compliance":
        items = database.query(ComplianceRequirement).all()
        return [{"id": item.id, "code": item.requirement_code, "title": item.title, "category": item.category, "status": item.status, "mandatory": item.mandatory, "next_due_date": _date(item.next_due_date)} for item in items if _matches_text(item.status, filters.status) and _matches_text(item.category, filters.category)]
    if report_type == "contractor":
        items = database.query(Contractor).all()
        return [{"id": item.id, "code": item.contractor_code, "company": item.company_name, "status": item.status, "compliance_score": item.compliance_score, "risk_score": item.risk_score, "workers": item.workers_count} for item in items if _matches_text(item.status, filters.status)]

    model_map = {"inspection": Inspection, "violation": Violation, "capa": CorrectiveAction, "risk": RiskEvent, "ai": AIEvent, "iot": IoTReading}
    model = model_map[report_type]
    query = database.query(model)
    if report_type in {"inspection", "violation", "capa", "risk", "ai"}:
        query = query.options(joinedload(getattr(model, "mine", None))) if hasattr(model, "mine") else query
    items = query.all()
    rows = []
    for item in items:
        row = _row_for(report_type, item)
        if filters.mine_id is not None and row.get("mine_id") != filters.mine_id:
            continue
        if not _matches_date(row.get("date"), filters.date_from, filters.date_to):
            continue
        if not _matches_text(row.get("severity") or row.get("level"), filters.severity):
            continue
        if not _matches_text(row.get("status"), filters.status):
            continue
        if not _matches_text(row.get("category") or row.get("event_type") or row.get("sensor_type"), filters.category):
            continue
        rows.append(row)
    return rows


def _row_for(report_type: str, item: Any) -> dict[str, Any]:
    if report_type == "inspection":
        return {"id": item.id, "code": item.inspection_code, "mine_id": item.mine_id, "mine": item.mine.mine_name, "status": item.status, "category": item.checklist_name, "date": _date(item.started_at)}
    if report_type == "violation":
        return {"id": item.id, "code": item.violation_code, "mine_id": item.mine_id, "mine": item.mine.mine_name, "category": item.category, "severity": item.severity, "status": item.status, "date": _date(item.detected_at)}
    if report_type == "capa":
        return {"id": item.id, "code": item.action_code, "violation_id": item.violation_id, "status": item.status, "category": item.priority, "date": _date(item.deadline)}
    if report_type == "risk":
        return {"id": item.id, "mine_id": item.mine_id, "mine": item.mine.mine_name, "event_type": item.event_type, "level": item.level, "score": item.score, "date": _date(item.created_at)}
    if report_type == "ai":
        return {"id": item.id, "mine_id": item.mine_id, "mine": item.mine.mine_name, "event_type": item.event_type, "severity": item.severity, "confidence": item.confidence, "status": item.status, "date": _date(item.created_at)}
    return {"id": item.id, "sensor_id": item.sensor_id, "value": item.value, "status": "ANOMALY" if item.is_anomaly else "NORMAL", "category": "IoT Reading", "date": _date(item.recorded_at)}


def _matches_text(value: Any, expected: str | None) -> bool:
    return expected is None or str(value or "").upper() == expected.upper() or expected.upper() in str(value or "").upper()


def _matches_date(value: Any, date_from: date | None, date_to: date | None) -> bool:
    if value is None:
        return date_from is None and date_to is None
    current = date.fromisoformat(str(value)[:10])
    return (date_from is None or current >= date_from) and (date_to is None or current <= date_to)


def _date(value: Any) -> str | None:
    return value.isoformat() if value else None
