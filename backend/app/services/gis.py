from sqlalchemy.orm import Session, joinedload

from app.models import Alert, GISAsset, IoTSensor, Mine, RiskEvent, Violation
from app.schemas.gis import GISMapResponse, GISPoint


def get_map_points(database: Session) -> GISMapResponse:
    points: list[GISPoint] = []
    mines = database.query(Mine).options(joinedload(Mine.zones)).all()
    mine_coordinates: dict[int, tuple[float, float]] = {}
    for mine in mines:
        if mine.latitude is None or mine.longitude is None:
            continue
        mine_coordinates[mine.id] = (mine.latitude, mine.longitude)
        points.append(GISPoint(id=f"mine-{mine.id}", kind="MINE", label=mine.mine_name, latitude=mine.latitude, longitude=mine.longitude, mine_id=mine.id, status=mine.status, risk_level=mine.risk_level))
        for index, zone in enumerate(mine.zones):
            points.append(GISPoint(id=f"zone-{zone.id}", kind="ZONE", label=zone.name, latitude=mine.latitude + (index + 1) * 0.003, longitude=mine.longitude + (index + 1) * 0.003, mine_id=mine.id, zone_id=zone.id, status=zone.status, risk_level=mine.risk_level, demo_position=True))

    assets = database.query(GISAsset).all()
    for asset in assets:
        points.append(GISPoint(id=f"asset-{asset.id}", kind=asset.asset_type, label=asset.name, latitude=asset.latitude, longitude=asset.longitude, mine_id=asset.mine_id, status=asset.status))

    for sensor in database.query(IoTSensor).all():
        coordinates = mine_coordinates.get(sensor.mine_id)
        if coordinates is None:
            continue
        points.append(GISPoint(id=f"sensor-{sensor.id}", kind="SENSOR", label=f"{sensor.sensor_type} / {sensor.sensor_code}", latitude=coordinates[0] - sensor.id * 0.001, longitude=coordinates[1] + sensor.id * 0.001, mine_id=sensor.mine_id, zone_id=sensor.zone_id, status=sensor.status, demo_position=True))

    for event in database.query(RiskEvent).all():
        coordinates = mine_coordinates.get(event.mine_id)
        if coordinates:
            points.append(GISPoint(id=f"risk-{event.id}", kind="RISK", label=event.event_type, latitude=coordinates[0] - event.id * 0.0005, longitude=coordinates[1] - event.id * 0.0005, mine_id=event.mine_id, zone_id=event.zone_id, risk_level=event.level, demo_position=True))

    for violation in database.query(Violation).all():
        coordinates = mine_coordinates.get(violation.mine_id)
        if coordinates:
            points.append(GISPoint(id=f"violation-{violation.id}", kind="VIOLATION", label=violation.violation_code, latitude=coordinates[0] + violation.id * 0.0007, longitude=coordinates[1] - violation.id * 0.0007, mine_id=violation.mine_id, zone_id=violation.zone_id, status=violation.status, severity=violation.severity, demo_position=True))

    for alert in database.query(Alert).all():
        coordinates = mine_coordinates.get(alert.mine_id)
        if coordinates:
            points.append(GISPoint(id=f"alert-{alert.id}", kind="ALERT", label=alert.message, latitude=coordinates[0] + alert.id * 0.0009, longitude=coordinates[1] + alert.id * 0.0009, mine_id=alert.mine_id, zone_id=alert.zone_id, status=alert.status, severity=alert.severity, demo_position=True))
    return GISMapResponse(points=points)
