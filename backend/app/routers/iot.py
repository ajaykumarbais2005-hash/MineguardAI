from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models import User
from app.schemas.iot import IoTReadingResponse, IoTSensorResponse, IoTSimulationResponse, IoTThresholdUpdate
from app.services.iot import list_readings, list_sensors, simulate_readings, update_threshold

router = APIRouter(prefix="/iot", tags=["iot"])


@router.get("", response_model=list[IoTSensorResponse])
def read_sensors(database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[IoTSensorResponse]:
    return list_sensors(database)


@router.get("/{sensor_id}/readings", response_model=list[IoTReadingResponse])
def read_sensor_history(sensor_id: int, database: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[IoTReadingResponse]:
    return list_readings(database, sensor_id)


@router.patch("/{sensor_id}/threshold", response_model=IoTSensorResponse)
def edit_threshold(sensor_id: int, payload: IoTThresholdUpdate, database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER"))) -> IoTSensorResponse:
    return update_threshold(database, sensor_id, payload, actor)


@router.post("/simulate", response_model=IoTSimulationResponse)
def simulate(sensor_id: Optional[int] = Query(default=None, ge=1), database: Session = Depends(get_db), actor: User = Depends(require_roles("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "INSPECTOR"))) -> IoTSimulationResponse:
    return simulate_readings(database, actor, sensor_id)
