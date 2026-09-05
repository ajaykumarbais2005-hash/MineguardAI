from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.models import (
    AIEvent,
    Alert,
    AuditLog,
    ComplianceRequirement,
    Contractor,
    ContractorWorker,
    CorrectiveAction,
    Document,
    GISAsset,
    Inspection,
    InspectionChecklist,
    IoTReading,
    IoTSensor,
    Mine,
    MineZone,
    OCRResult,
    RiskEvent,
    Role,
    User,
    Violation,
)

ROLES = ("ADMIN", "MINE_MANAGER", "SAFETY_OFFICER", "INSPECTOR", "CONTRACTOR", "AUDITOR")


def _demo_password(email: str) -> str:
    return hash_password({
        "admin@mineguard.ai": "admin123",
        "manager@mineguard.ai": "manager123",
        "safety@mineguard.ai": "safety123",
        "inspector@mineguard.ai": "inspector123",
        "contractor@mineguard.ai": "contractor123",
        "auditor@mineguard.ai": "auditor123",
    }[email])


def seed_demo_data(session: Session) -> dict[str, int]:
    if session.scalar(select(Role.id).limit(1)) is not None:
        return {table: session.query(model).count() for table, model in _seed_models().items()}

    now = datetime.now(UTC)
    roles = {name: Role(name=name, description=f"MineGuard {name.replace('_', ' ').title()} role") for name in ROLES}
    session.add_all(roles.values())
    session.flush()

    account_roles = {
        "admin@mineguard.ai": "ADMIN",
        "manager@mineguard.ai": "MINE_MANAGER",
        "safety@mineguard.ai": "SAFETY_OFFICER",
        "inspector@mineguard.ai": "INSPECTOR",
        "contractor@mineguard.ai": "CONTRACTOR",
        "auditor@mineguard.ai": "AUDITOR",
    }
    users = {
        email: User(email=email, full_name=email.split("@")[0].replace(".", " ").title(), hashed_password=_demo_password(email), role=roles[role_name])
        for email, role_name in account_roles.items()
    }
    session.add_all(users.values())
    session.flush()

    mines = [
        Mine(mine_code="MG-JH-001", mine_name="Kusmunda North Extension", location="Korba, Chhattisgarh", state="Chhattisgarh", district="Korba", mine_type="OPEN_CAST", operator="South Eastern Coalfields Limited", production_capacity=52.0, current_production=47.5, status="ACTIVE", risk_level="HIGH", manager=users["manager@mineguard.ai"], latitude=22.353, longitude=82.686),
        Mine(mine_code="MG-JH-002", mine_name="Gevra Central Block", location="Korba, Chhattisgarh", state="Chhattisgarh", district="Korba", mine_type="OPEN_CAST", operator="South Eastern Coalfields Limited", production_capacity=60.0, current_production=55.2, status="ACTIVE", risk_level="MEDIUM", manager=users["manager@mineguard.ai"], latitude=22.384, longitude=82.657),
        Mine(mine_code="MG-OD-003", mine_name="Brajrajnagar Underground", location="Jharsuguda, Odisha", state="Odisha", district="Jharsuguda", mine_type="UNDERGROUND", operator="Mahanadi Coalfields Limited", production_capacity=18.0, current_production=15.8, status="ACTIVE", risk_level="MEDIUM", manager=users["manager@mineguard.ai"], latitude=21.817, longitude=83.864),
        Mine(mine_code="MG-WB-004", mine_name="Raniganj Safety Pilot", location="Asansol, West Bengal", state="West Bengal", district="Paschim Bardhaman", mine_type="UNDERGROUND", operator="Eastern Coalfields Limited", production_capacity=12.0, current_production=10.1, status="MAINTENANCE", risk_level="HIGH", manager=users["manager@mineguard.ai"], latitude=23.687, longitude=87.111),
        Mine(mine_code="MG-MP-005", mine_name="Singrauli East Pit", location="Singrauli, Madhya Pradesh", state="Madhya Pradesh", district="Singrauli", mine_type="OPEN_CAST", operator="Northern Coalfields Limited", production_capacity=40.0, current_production=38.4, status="ACTIVE", risk_level="LOW", manager=users["manager@mineguard.ai"], latitude=24.201, longitude=82.671),
    ]
    session.add_all(mines)
    session.flush()

    zones = []
    for mine in mines:
        zones.extend([MineZone(mine=mine, name="Main Haul Road", zone_type="TRANSPORT", status="ACTIVE"), MineZone(mine=mine, name="Processing Area", zone_type="PLANT", status="ACTIVE")])
    session.add_all(zones)
    session.flush()

    requirements = [
        ComplianceRequirement(requirement_code="DGMS-PPE-001", title="Personal protective equipment", description="Workers must wear approved helmet, high-visibility vest, boots, and respiratory protection where required.", category="Worker Safety", regulation_reference="DGMS Safety Circular", frequency="DAILY", status="COMPLIANT", last_verification=now - timedelta(days=2), next_due_date=now + timedelta(days=1)),
        ComplianceRequirement(requirement_code="DGMS-GAS-002", title="Atmospheric gas monitoring", description="Monitor mine atmosphere and maintain readings within approved operating limits.", category="Environment", regulation_reference="Coal Mines Regulations", frequency="DAILY", status="PARTIALLY_COMPLIANT", last_verification=now - timedelta(days=4), next_due_date=now + timedelta(days=2)),
        ComplianceRequirement(requirement_code="DGMS-INS-003", title="Statutory inspection records", description="Complete and retain scheduled statutory inspection records for active work areas.", category="Inspections", regulation_reference="Mines Act, 1952", frequency="WEEKLY", status="COMPLIANT", last_verification=now - timedelta(days=5), next_due_date=now + timedelta(days=2)),
        ComplianceRequirement(requirement_code="DGMS-VEH-004", title="Heavy vehicle speed control", description="Haul trucks must remain within posted speed limits and have functioning proximity controls.", category="Transport", regulation_reference="DGMS Traffic Management Guidance", frequency="WEEKLY", status="OVERDUE", last_verification=now - timedelta(days=12), next_due_date=now - timedelta(days=2)),
    ]
    session.add_all(requirements)

    contractors = [
        Contractor(contractor_code="CTR-001", company_name="Bharat Mine Services", license_number="LIC-BMS-2026", contact_person="Ravi Sharma", phone="+91-9876501001", email="ops@bharatmine.example", work_type="Haul Road Maintenance", workers_count=24, compliance_score=91.0, risk_score=18.0, status="ACTIVE"),
        Contractor(contractor_code="CTR-002", company_name="Eastern Industrial Support", license_number="LIC-EIS-2026", contact_person="Neha Verma", phone="+91-9876501002", email="safety@eis.example", work_type="Electrical Maintenance", workers_count=16, compliance_score=76.0, risk_score=42.0, status="ACTIVE"),
    ]
    session.add_all(contractors)
    session.flush()
    session.add_all([
        ContractorWorker(worker_code="WRK-001", contractor=contractors[0], name="Arjun Patel", role="Haul Truck Operator", training_status="VALID", ppe_status="COMPLIANT", medical_valid_until=now + timedelta(days=90), training_valid_until=now + timedelta(days=120), site_assignment=mines[0].mine_name),
        ContractorWorker(worker_code="WRK-002", contractor=contractors[1], name="Sanjay Das", role="Electrical Technician", training_status="EXPIRING_SOON", ppe_status="REVIEW_REQUIRED", medical_valid_until=now + timedelta(days=20), training_valid_until=now + timedelta(days=10), site_assignment=mines[1].mine_name),
    ])

    inspection = Inspection(inspection_code="INS-2026-0001", mine=mines[0], zone=zones[0], inspector=users["inspector@mineguard.ai"], checklist_name="Daily Transport Safety", status="SUBMITTED", findings="PPE gap observed near haul road access.", remarks="Supervisor notified for immediate correction.", started_at=now - timedelta(days=1), submitted_at=now - timedelta(hours=20))
    session.add(inspection)
    session.flush()
    session.add_all([
        InspectionChecklist(inspection=inspection, item_code="TR-01", question="Are haul road workers wearing approved helmets?", response="NO", remarks="One worker observed without helmet."),
        InspectionChecklist(inspection=inspection, item_code="TR-02", question="Are vehicle routes clearly segregated?", response="YES", remarks="Segregation visible at inspection time."),
    ])

    violation = Violation(violation_code="VIO-2026-0001", mine=mines[0], zone=zones[0], inspection=inspection, category="PPE", description="Worker detected without a safety helmet at Main Haul Road access.", severity="HIGH", detected_at=now - timedelta(hours=18), detected_by_user=users["safety@mineguard.ai"], status="OPEN", due_date=now + timedelta(days=3), assigned_officer="Safety Control Room")
    session.add(violation)
    session.flush()
    action = CorrectiveAction(action_code="CAPA-2026-0001", violation=violation, description="Conduct toolbox talk and enforce helmet compliance at haul road access.", responsible_person=users["safety@mineguard.ai"], contractor=contractors[0], priority="HIGH", deadline=now + timedelta(days=2), status="IN_PROGRESS")
    session.add(action)

    risk = RiskEvent(mine=mines[0], zone=zones[0], event_type="PPE_NON_COMPLIANCE", score=68.0, level="HIGH", severity=4.0, likelihood=4.0, exposure=4.0, recurrence=2.0, reason="Repeated PPE observation in a high-traffic transport zone.", recommended_action="Pause access, brief the crew, and verify PPE before re-entry.")
    session.add(risk)
    session.flush()
    ai_event = AIEvent(mine=mines[0], zone=zones[0], camera="CAM-HAUL-01", event_type="NO_HELMET", confidence=0.94, severity="HIGH", media_reference="demo://ppe/no-helmet-0001", ai_model="DEMO_SIMULATION", status="LINKED", linked_violation=violation, linked_risk_event=risk)
    session.add(ai_event)

    sensors = [
        IoTSensor(sensor_code="GAS-001", mine=mines[0], zone=zones[0], sensor_type="Gas", unit="ppm", threshold=25.0, status="ONLINE", last_reading=18.4, last_reading_at=now),
        IoTSensor(sensor_code="DUST-001", mine=mines[0], zone=zones[1], sensor_type="Dust", unit="mg/m3", threshold=4.0, status="ONLINE", last_reading=3.2, last_reading_at=now),
        IoTSensor(sensor_code="TEMP-001", mine=mines[1], zone=zones[2], sensor_type="Temperature", unit="C", threshold=42.0, status="ONLINE", last_reading=39.6, last_reading_at=now),
    ]
    session.add_all(sensors)
    session.flush()
    for sensor in sensors:
        session.add_all([IoTReading(sensor=sensor, value=sensor.last_reading - 1.2, recorded_at=now - timedelta(hours=2)), IoTReading(sensor=sensor, value=sensor.last_reading, recorded_at=now)])

    session.add(Alert(alert_type="PPE_VIOLATION", severity="HIGH", message="Worker without helmet detected at Main Haul Road access.", mine=mines[0], zone=zones[0], violation=violation, risk_event=risk, status="UNREAD"))
    document = Document(file_name="haul-road-safety-certificate.pdf", document_type="Safety Certificate", file_path="data/demo/haul-road-safety-certificate.pdf", mine=mines[0], contractor=contractors[0], uploaded_by=users["safety@mineguard.ai"].id, status="OCR_PENDING")
    session.add(document)
    session.flush()
    session.add(OCRResult(document=document, extracted_text="Certificate No: DEMO-2026-001; Expiry: 2026-12-31", confidence=0.96, detected_fields='{"certificate_number":"DEMO-2026-001","expiry_date":"2026-12-31"}', verification_status="PENDING"))
    session.add_all([
        GISAsset(mine=mines[0], asset_type="CAMERA", name="Haul Road Camera 01", latitude=22.354, longitude=82.688, status="ACTIVE"),
        GISAsset(mine=mines[0], asset_type="SENSOR", name="Gas Sensor 001", latitude=22.352, longitude=82.684, status="ACTIVE"),
        AuditLog(user=users["safety@mineguard.ai"], action="SEED", entity="SYSTEM", entity_id="phase-2", description="Created deterministic Phase 2 demo dataset.", ip_address="127.0.0.1"),
    ])
    session.commit()
    return {table: session.query(model).count() for table, model in _seed_models().items()}


def _seed_models() -> dict[str, type]:
    return {
        "roles": Role,
        "users": User,
        "mines": Mine,
        "mine_zones": MineZone,
        "inspections": Inspection,
        "inspection_checklists": InspectionChecklist,
        "compliance_requirements": ComplianceRequirement,
        "violations": Violation,
        "corrective_actions": CorrectiveAction,
        "contractors": Contractor,
        "contractor_workers": ContractorWorker,
        "ai_events": AIEvent,
        "risk_events": RiskEvent,
        "iot_sensors": IoTSensor,
        "iot_readings": IoTReading,
        "alerts": Alert,
        "documents": Document,
        "ocr_results": OCRResult,
        "gis_assets": GISAsset,
        "audit_logs": AuditLog,
    }
