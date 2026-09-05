from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IoTReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sensor_id: int
    value: float
    recorded_at: datetime
    is_anomaly: bool


class IoTSensorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sensor_code: str
    mine_id: int
    zone_id: Optional[int]
    sensor_type: str
    unit: str
    threshold: float
    status: str
    last_reading: Optional[float]
    last_reading_at: Optional[datetime]
    mine_name: str = ""
    zone_name: Optional[str] = None
    readings: list[IoTReadingResponse] = []


class IoTThresholdUpdate(BaseModel):
    threshold: float = Field(gt=0)


class IoTSimulationResponse(BaseModel):
    sensors: list[IoTSensorResponse]
    alerts_created: int
    mode: str = "SIMULATED_SENSOR_DATA"
