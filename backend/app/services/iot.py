from datetime import UTC, datetime
from random import Random
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models import Alert, AuditLog, IoTReading, IoTSensor, MineZone, User
from app.schemas.iot import IoTSensorResponse, IoTSimulationResponse, IoTThresholdUpdate


def list_sensors(database: Session) -> list[IoTSensorResponse]:
    sensors = database.query(IoTSensor).options(joinedload(IoTSensor.mine), joinedload(IoTSensor.zone), joinedload(IoTSensor.readings)).order_by(IoTSensor.sensor_code.asc()).all()
    return [_to_response(sensor) for sensor in sensors]


def list_readings(database: Session, sensor_id: int) -> list[IoTReading]:
    sensor = database.query(IoTSensor).filter(IoTSensor.id == sensor_id).first()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return database.query(IoTReading).filter(IoTReading.sensor_id == sensor_id).order_by(IoTReading.recorded_at.desc()).limit(50).all()


def update_threshold(database: Session, sensor_id: int, payload: IoTThresholdUpdate, actor: User) -> IoTSensorResponse:
    sensor = database.query(IoTSensor).options(joinedload(IoTSensor.mine), joinedload(IoTSensor.zone), joinedload(IoTSensor.readings)).filter(IoTSensor.id == sensor_id).first()
    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")
    sensor.threshold = payload.threshold
    database.add(AuditLog(user_id=actor.id, action="UPDATE", entity="IoTSensor", entity_id=str(sensor.id), description=f"Updated threshold for {sensor.sensor_code}"))
    database.commit()
    return _to_response(sensor)


def simulate_readings(database: Session, actor: User, sensor_id: Optional[int] = None) -> IoTSimulationResponse:
    query = database.query(IoTSensor).options(joinedload(IoTSensor.mine), joinedload(IoTSensor.zone), joinedload(IoTSensor.readings))
    if sensor_id is not None:
        query = query.filter(IoTSensor.id == sensor_id)
    sensors = query.all()
    if sensor_id is not None and not sensors:
        raise HTTPException(status_code=404, detail="Sensor not found")
    now = datetime.now(UTC)
    alerts_created = 0
    for sensor in sensors:
        random = Random(f"{sensor.sensor_code}-{now.strftime('%Y%m%d%H%M')}")
        breach = sensor.id % 3 == 0
        value = round(sensor.threshold * (1.15 + random.random() * 0.35) if breach else sensor.threshold * (0.55 + random.random() * 0.25), 2)
        is_anomaly = value > sensor.threshold
        sensor.last_reading = value
        sensor.last_reading_at = now
        sensor.status = "ALERT" if is_anomaly else "ONLINE"
        reading = IoTReading(sensor_id=sensor.id, value=value, recorded_at=now, is_anomaly=is_anomaly)
        database.add(reading)
        if is_anomaly:
            alert = Alert(alert_type=f"HIGH_{sensor.sensor_type.upper()}".replace(" ", "_"), severity="CRITICAL" if value >= sensor.threshold * 1.4 else "HIGH", message=f"{sensor.sensor_type} threshold exceeded on {sensor.sensor_code}: {value} {sensor.unit}.", mine_id=sensor.mine_id, zone_id=sensor.zone_id, status="UNREAD", created_at=now)
            database.add(alert)
            database.flush()
            database.add(AuditLog(user_id=actor.id, action="CREATE", entity="Alert", entity_id=str(alert.id), description=f"Created simulated sensor alert for {sensor.sensor_code}"))
            alerts_created += 1
    database.commit()
    refreshed = database.query(IoTSensor).options(joinedload(IoTSensor.mine), joinedload(IoTSensor.zone), joinedload(IoTSensor.readings)).filter(IoTSensor.id.in_([sensor.id for sensor in sensors])).all() if sensors else []
    return IoTSimulationResponse(sensors=[_to_response(sensor) for sensor in refreshed], alerts_created=alerts_created)


def _to_response(sensor: IoTSensor) -> IoTSensorResponse:
    readings = sorted(sensor.readings, key=lambda item: item.recorded_at, reverse=True)[:24]
    return IoTSensorResponse.model_validate(sensor).model_copy(update={"mine_name": sensor.mine.mine_name, "zone_name": sensor.zone.name if sensor.zone else None, "readings": readings})
