from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MineBase(BaseModel):
    mine_name: str = Field(min_length=2, max_length=150)
    mine_code: str = Field(min_length=2, max_length=30)
    location: str = Field(min_length=2, max_length=200)
    state: str = Field(min_length=2, max_length=100)
    district: str = Field(min_length=2, max_length=100)
    mine_type: str = Field(min_length=2, max_length=50)
    operator: str = Field(min_length=2, max_length=150)
    production_capacity: Optional[float] = Field(default=None, ge=0)
    current_production: Optional[float] = Field(default=None, ge=0)
    status: str = Field(default="ACTIVE", min_length=2, max_length=30)
    risk_level: str = Field(default="MEDIUM", min_length=2, max_length=30)
    manager_id: Optional[int] = Field(default=None, ge=1)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class MineCreate(MineBase):
    pass


class MineUpdate(BaseModel):
    mine_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    mine_code: Optional[str] = Field(default=None, min_length=2, max_length=30)
    location: Optional[str] = Field(default=None, min_length=2, max_length=200)
    state: Optional[str] = Field(default=None, min_length=2, max_length=100)
    district: Optional[str] = Field(default=None, min_length=2, max_length=100)
    mine_type: Optional[str] = Field(default=None, min_length=2, max_length=50)
    operator: Optional[str] = Field(default=None, min_length=2, max_length=150)
    production_capacity: Optional[float] = Field(default=None, ge=0)
    current_production: Optional[float] = Field(default=None, ge=0)
    status: Optional[str] = Field(default=None, min_length=2, max_length=30)
    risk_level: Optional[str] = Field(default=None, min_length=2, max_length=30)
    manager_id: Optional[int] = Field(default=None, ge=1)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class MineZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    zone_type: str
    status: str


class MineStatistics(BaseModel):
    zone_count: int
    inspection_count: int
    open_violation_count: int
    active_sensor_count: int
    alert_count: int


class MineResponse(MineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    manager_name: Optional[str] = None


class MineDetailResponse(MineResponse):
    zones: list[MineZoneResponse]
    statistics: MineStatistics
