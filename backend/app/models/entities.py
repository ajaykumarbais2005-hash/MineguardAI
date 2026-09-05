from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    role: Mapped["Role"] = relationship(back_populates="users")
    managed_mines: Mapped[list["Mine"]] = relationship(back_populates="manager")
    inspections: Mapped[list["Inspection"]] = relationship(back_populates="inspector")
    detected_violations: Mapped[list["Violation"]] = relationship(back_populates="detected_by_user")
    corrective_actions: Mapped[list["CorrectiveAction"]] = relationship(back_populates="responsible_person")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


class Mine(Base):
    __tablename__ = "mines"

    id: Mapped[int] = mapped_column(primary_key=True)
    mine_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    mine_name: Mapped[str] = mapped_column(String(150), index=True)
    location: Mapped[str] = mapped_column(String(200))
    state: Mapped[str] = mapped_column(String(100))
    district: Mapped[str] = mapped_column(String(100))
    mine_type: Mapped[str] = mapped_column(String(50))
    operator: Mapped[str] = mapped_column(String(150))
    production_capacity: Mapped[Optional[float]] = mapped_column(Float)
    current_production: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    risk_level: Mapped[str] = mapped_column(String(30), default="MEDIUM")
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    manager: Mapped[Optional["User"]] = relationship(back_populates="managed_mines")
    zones: Mapped[list["MineZone"]] = relationship(back_populates="mine", cascade="all, delete-orphan")
    inspections: Mapped[list["Inspection"]] = relationship(back_populates="mine")
    violations: Mapped[list["Violation"]] = relationship(back_populates="mine")
    ai_events: Mapped[list["AIEvent"]] = relationship(back_populates="mine")
    risk_events: Mapped[list["RiskEvent"]] = relationship(back_populates="mine")
    sensors: Mapped[list["IoTSensor"]] = relationship(back_populates="mine")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="mine")
    documents: Mapped[list["Document"]] = relationship(back_populates="mine")
    gis_assets: Mapped[list["GISAsset"]] = relationship(back_populates="mine")


class MineZone(Base):
    __tablename__ = "mine_zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    mine_id: Mapped[int] = mapped_column(ForeignKey("mines.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    zone_type: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    mine: Mapped["Mine"] = relationship(back_populates="zones")
    inspections: Mapped[list["Inspection"]] = relationship(back_populates="zone")
    violations: Mapped[list["Violation"]] = relationship(back_populates="zone")
    ai_events: Mapped[list["AIEvent"]] = relationship(back_populates="zone")
    risk_events: Mapped[list["RiskEvent"]] = relationship(back_populates="zone")
    sensors: Mapped[list["IoTSensor"]] = relationship(back_populates="zone")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="zone")


class ComplianceRequirement(Base):
    __tablename__ = "compliance_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    requirement_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80))
    regulation_reference: Mapped[str] = mapped_column(String(200))
    mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    applicable_mine_type: Mapped[str] = mapped_column(String(80), default="ALL")
    frequency: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(40), default="PENDING")
    last_verification: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    next_due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(primary_key=True)
    inspection_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    mine_id: Mapped[int] = mapped_column(ForeignKey("mines.id"), index=True)
    zone_id: Mapped[Optional[int]] = mapped_column(ForeignKey("mine_zones.id"))
    inspector_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    checklist_name: Mapped[str] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    findings: Mapped[Optional[str]] = mapped_column(Text)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    evidence_path: Mapped[Optional[str]] = mapped_column(String(500))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    mine: Mapped["Mine"] = relationship(back_populates="inspections")
    zone: Mapped[Optional["MineZone"]] = relationship(back_populates="inspections")
    inspector: Mapped["User"] = relationship(back_populates="inspections")
    checklist_items: Mapped[list["InspectionChecklist"]] = relationship(back_populates="inspection", cascade="all, delete-orphan")
    violations: Mapped[list["Violation"]] = relationship(back_populates="inspection")


class InspectionChecklist(Base):
    __tablename__ = "inspection_checklists"

    id: Mapped[int] = mapped_column(primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"), index=True)
    item_code: Mapped[str] = mapped_column(String(40))
    question: Mapped[str] = mapped_column(Text)
    response: Mapped[Optional[str]] = mapped_column(String(50))
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    inspection: Mapped["Inspection"] = relationship(back_populates="checklist_items")


class Contractor(Base):
    __tablename__ = "contractors"

    id: Mapped[int] = mapped_column(primary_key=True)
    contractor_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(180), index=True)
    license_number: Mapped[str] = mapped_column(String(100), unique=True)
    contact_person: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(255))
    work_type: Mapped[str] = mapped_column(String(120))
    workers_count: Mapped[int] = mapped_column(Integer, default=0)
    compliance_score: Mapped[float] = mapped_column(Float, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    workers: Mapped[list["ContractorWorker"]] = relationship(back_populates="contractor", cascade="all, delete-orphan")
    corrective_actions: Mapped[list["CorrectiveAction"]] = relationship(back_populates="contractor")
    documents: Mapped[list["Document"]] = relationship(back_populates="contractor")


class ContractorWorker(Base):
    __tablename__ = "contractor_workers"

    id: Mapped[int] = mapped_column(primary_key=True)
    worker_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    contractor_id: Mapped[int] = mapped_column(ForeignKey("contractors.id"), index=True)
    name: Mapped[str] = mapped_column(String(150))
    role: Mapped[str] = mapped_column(String(100))
    training_status: Mapped[str] = mapped_column(String(40))
    ppe_status: Mapped[str] = mapped_column(String(40))
    medical_valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    training_valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    site_assignment: Mapped[Optional[str]] = mapped_column(String(150))
    contractor: Mapped["Contractor"] = relationship(back_populates="workers")


class Violation(Base):
    __tablename__ = "violations"

    id: Mapped[int] = mapped_column(primary_key=True)
    violation_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    mine_id: Mapped[int] = mapped_column(ForeignKey("mines.id"), index=True)
    zone_id: Mapped[Optional[int]] = mapped_column(ForeignKey("mine_zones.id"))
    inspection_id: Mapped[Optional[int]] = mapped_column(ForeignKey("inspections.id"))
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(30), index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    detected_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(40), default="OPEN", index=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    evidence_path: Mapped[Optional[str]] = mapped_column(String(500))
    assigned_officer: Mapped[Optional[str]] = mapped_column(String(150))
    mine: Mapped["Mine"] = relationship(back_populates="violations")
    zone: Mapped[Optional["MineZone"]] = relationship(back_populates="violations")
    inspection: Mapped[Optional["Inspection"]] = relationship(back_populates="violations")
    detected_by_user: Mapped["User"] = relationship(back_populates="detected_violations")
    corrective_actions: Mapped[list["CorrectiveAction"]] = relationship(back_populates="violation", cascade="all, delete-orphan")
    ai_events: Mapped[list["AIEvent"]] = relationship(back_populates="linked_violation")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="violation")


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    action_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    violation_id: Mapped[int] = mapped_column(ForeignKey("violations.id"), index=True)
    description: Mapped[str] = mapped_column(Text)
    responsible_person_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    contractor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contractors.id"))
    priority: Mapped[str] = mapped_column(String(30), default="MEDIUM")
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), default="OPEN", index=True)
    evidence_path: Mapped[Optional[str]] = mapped_column(String(500))
    verification: Mapped[Optional[str]] = mapped_column(Text)
    closure_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    violation: Mapped["Violation"] = relationship(back_populates="corrective_actions")
    responsible_person: Mapped["User"] = relationship(back_populates="corrective_actions")
    contractor: Mapped[Optional["Contractor"]] = relationship(back_populates="corrective_actions")


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    mine_id: Mapped[int] = mapped_column(ForeignKey("mines.id"), index=True)
    zone_id: Mapped[Optional[int]] = mapped_column(ForeignKey("mine_zones.id"))
    event_type: Mapped[str] = mapped_column(String(80))
    score: Mapped[float] = mapped_column(Float)
    level: Mapped[str] = mapped_column(String(30), index=True)
    severity: Mapped[float] = mapped_column(Float)
    likelihood: Mapped[float] = mapped_column(Float)
    exposure: Mapped[float] = mapped_column(Float)
    recurrence: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text)
    recommended_action: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    mine: Mapped["Mine"] = relationship(back_populates="risk_events")
    zone: Mapped[Optional["MineZone"]] = relationship(back_populates="risk_events")
    ai_events: Mapped[list["AIEvent"]] = relationship(back_populates="linked_risk_event")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="risk_event")


class AIEvent(Base):
    __tablename__ = "ai_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    mine_id: Mapped[int] = mapped_column(ForeignKey("mines.id"), index=True)
    zone_id: Mapped[Optional[int]] = mapped_column(ForeignKey("mine_zones.id"))
    camera: Mapped[Optional[str]] = mapped_column(String(100))
    event_type: Mapped[str] = mapped_column(String(80))
    confidence: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(30))
    media_reference: Mapped[Optional[str]] = mapped_column(String(500))
    ai_model: Mapped[str] = mapped_column(String(100), default="DEMO_SIMULATION")
    status: Mapped[str] = mapped_column(String(40), default="NEW")
    linked_violation_id: Mapped[Optional[int]] = mapped_column(ForeignKey("violations.id"))
    linked_risk_event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("risk_events.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    mine: Mapped["Mine"] = relationship(back_populates="ai_events")
    zone: Mapped[Optional["MineZone"]] = relationship(back_populates="ai_events")
    linked_violation: Mapped[Optional["Violation"]] = relationship(back_populates="ai_events")
    linked_risk_event: Mapped[Optional["RiskEvent"]] = relationship(back_populates="ai_events")


class IoTSensor(Base):
    __tablename__ = "iot_sensors"

    id: Mapped[int] = mapped_column(primary_key=True)
    sensor_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    mine_id: Mapped[int] = mapped_column(ForeignKey("mines.id"), index=True)
    zone_id: Mapped[Optional[int]] = mapped_column(ForeignKey("mine_zones.id"))
    sensor_type: Mapped[str] = mapped_column(String(60))
    unit: Mapped[str] = mapped_column(String(20))
    threshold: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="ONLINE")
    last_reading: Mapped[Optional[float]] = mapped_column(Float)
    last_reading_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    mine: Mapped["Mine"] = relationship(back_populates="sensors")
    zone: Mapped[Optional["MineZone"]] = relationship(back_populates="sensors")
    readings: Mapped[list["IoTReading"]] = relationship(back_populates="sensor", cascade="all, delete-orphan")


class IoTReading(Base):
    __tablename__ = "iot_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("iot_sensors.id"), index=True)
    value: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    sensor: Mapped["IoTSensor"] = relationship(back_populates="readings")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_type: Mapped[str] = mapped_column(String(80))
    severity: Mapped[str] = mapped_column(String(30), index=True)
    message: Mapped[str] = mapped_column(Text)
    mine_id: Mapped[int] = mapped_column(ForeignKey("mines.id"), index=True)
    zone_id: Mapped[Optional[int]] = mapped_column(ForeignKey("mine_zones.id"))
    violation_id: Mapped[Optional[int]] = mapped_column(ForeignKey("violations.id"))
    risk_event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("risk_events.id"))
    status: Mapped[str] = mapped_column(String(30), default="UNREAD", index=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    mine: Mapped["Mine"] = relationship(back_populates="alerts")
    zone: Mapped[Optional["MineZone"]] = relationship(back_populates="alerts")
    violation: Mapped[Optional["Violation"]] = relationship(back_populates="alerts")
    risk_event: Mapped[Optional["RiskEvent"]] = relationship(back_populates="alerts")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255))
    document_type: Mapped[str] = mapped_column(String(80))
    file_path: Mapped[str] = mapped_column(String(500))
    mine_id: Mapped[Optional[int]] = mapped_column(ForeignKey("mines.id"))
    contractor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contractors.id"))
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    status: Mapped[str] = mapped_column(String(30), default="UPLOADED")
    mine: Mapped[Optional["Mine"]] = relationship(back_populates="documents")
    contractor: Mapped[Optional["Contractor"]] = relationship(back_populates="documents")
    ocr_result: Mapped[Optional["OCRResult"]] = relationship(back_populates="document", uselist=False, cascade="all, delete-orphan")


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), unique=True)
    extracted_text: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    detected_fields: Mapped[Optional[str]] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(30), default="PENDING")
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    document: Mapped["Document"] = relationship(back_populates="ocr_result")


class GISAsset(Base):
    __tablename__ = "gis_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    mine_id: Mapped[int] = mapped_column(ForeignKey("mines.id"), index=True)
    asset_type: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(150))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    mine: Mapped["Mine"] = relationship(back_populates="gis_assets")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(80))
    entity: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[Optional[str]] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")
