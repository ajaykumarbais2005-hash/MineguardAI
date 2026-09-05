from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.mine import MineCreate, MineDetailResponse, MineResponse, MineUpdate
from app.services.mines import create_mine, delete_mine, get_mine_detail, list_mines, update_mine

router = APIRouter(prefix="/mines", tags=["mines"])


@router.get("", response_model=list[MineResponse])
def read_mines(
    search: Optional[str] = Query(default=None, max_length=100),
    status_filter: Optional[str] = Query(default=None, alias="status", max_length=30),
    risk_level: Optional[str] = Query(default=None, max_length=30),
    sort_by: str = Query(default="mine_name", pattern="^(mine_name|mine_code|status|risk_level|created_at)$"),
    descending: bool = False,
    database: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[MineResponse]:
    return list_mines(database, search, status_filter, risk_level, sort_by, descending)


@router.post("", response_model=MineResponse, status_code=status.HTTP_201_CREATED)
def add_mine(payload: MineCreate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER"))) -> MineResponse:
    return create_mine(database, payload, actor)


@router.get("/{mine_id}", response_model=MineDetailResponse)
def read_mine(mine_id: int, database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> MineDetailResponse:
    return get_mine_detail(database, mine_id)


@router.patch("/{mine_id}", response_model=MineResponse)
def edit_mine(mine_id: int, payload: MineUpdate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER"))) -> MineResponse:
    return update_mine(database, mine_id, payload, actor)


@router.delete("/{mine_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_mine(mine_id: int, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER"))) -> Response:
    delete_mine(database, mine_id, actor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
