from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.inspection import InspectionCreate, InspectionResponse, InspectionUpdate
from app.services.inspections import _to_response, create_inspection, get_inspection, list_inspections, update_inspection

router = APIRouter(prefix="/inspections", tags=["inspections"])


@router.get("", response_model=list[InspectionResponse])
def read_inspections(status_filter: Optional[str] = Query(default=None, alias="status", max_length=30), database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[InspectionResponse]:
    return list_inspections(database, status_filter)


@router.get("/{inspection_id}", response_model=InspectionResponse)
def read_inspection(inspection_id: int, database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> InspectionResponse:
    return _to_response(get_inspection(database, inspection_id))


@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
def add_inspection(payload: InspectionCreate, database: Session = Depends(get_db), inspector: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "INSPECTOR"))) -> InspectionResponse:
    return create_inspection(database, payload, inspector)


@router.patch("/{inspection_id}", response_model=InspectionResponse)
def edit_inspection(inspection_id: int, payload: InspectionUpdate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "INSPECTOR"))) -> InspectionResponse:
    return update_inspection(database, inspection_id, payload, actor)
