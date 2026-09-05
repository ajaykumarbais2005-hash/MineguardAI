from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.report import ReportFilters, ReportResponse
from app.services.reports import build_report, render_csv

router = APIRouter(prefix="/reports", tags=["reports"])


def _filters(mine_id: Optional[int], date_from: Optional[date], date_to: Optional[date], severity: Optional[str], status: Optional[str], category: Optional[str]) -> ReportFilters:
    return ReportFilters(mine_id=mine_id, date_from=date_from, date_to=date_to, severity=severity, status=status, category=category)


@router.get("/{report_type}", response_model=ReportResponse)
def read_report(report_type: str, mine_id: Optional[int] = Query(default=None, ge=1), date_from: Optional[date] = None, date_to: Optional[date] = None, severity: Optional[str] = None, status: Optional[str] = None, category: Optional[str] = None, database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ReportResponse:
    return build_report(database, report_type, _filters(mine_id, date_from, date_to, severity, status, category))


@router.get("/{report_type}/csv")
def download_report(report_type: str, mine_id: Optional[int] = Query(default=None, ge=1), date_from: Optional[date] = None, date_to: Optional[date] = None, severity: Optional[str] = None, status: Optional[str] = None, category: Optional[str] = None, database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> StreamingResponse:
    report = build_report(database, report_type, _filters(mine_id, date_from, date_to, severity, status, category))
    return StreamingResponse(iter([render_csv(report)]), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=mineguard-{report_type}-report.csv"})
