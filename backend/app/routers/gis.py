from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.gis import GISMapResponse
from app.services.gis import get_map_points

router = APIRouter(prefix="/gis", tags=["gis"])


@router.get("/map", response_model=GISMapResponse)
def read_map(database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> GISMapResponse:
    return get_map_points(database)
