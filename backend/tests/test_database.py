from sqlalchemy import inspect, select

from app.database import Base
from app.models import Mine, MineZone, Violation
from app.services.seed import seed_demo_data


def test_all_phase_two_tables_are_registered():
    expected_tables = {
        "users", "roles", "mines", "mine_zones", "inspections", "inspection_checklists",
        "compliance_requirements", "violations", "corrective_actions", "contractors",
        "contractor_workers", "ai_events", "risk_events", "iot_sensors", "iot_readings",
        "alerts", "documents", "ocr_results", "gis_assets", "audit_logs",
    }

    assert set(Base.metadata.tables) == expected_tables


def test_schema_contains_foreign_keys(database_session):
    inspector = inspect(database_session.bind)

    foreign_keys = {
        key["constrained_columns"][0]: key["referred_table"]
        for key in inspector.get_foreign_keys("violations")
    }
    assert foreign_keys == {
        "mine_id": "mines",
        "zone_id": "mine_zones",
        "inspection_id": "inspections",
        "detected_by": "users",
    }


def test_demo_seed_populates_relationships_and_is_idempotent(database_session):
    first_counts = seed_demo_data(database_session)
    second_counts = seed_demo_data(database_session)

    assert first_counts == second_counts
    assert first_counts["mines"] == 5
    assert first_counts["users"] == 6
    assert first_counts["mine_zones"] == 10
    assert first_counts["violations"] == 1
    assert first_counts["corrective_actions"] == 1
    assert first_counts["iot_readings"] == 6

    mine = database_session.scalar(select(Mine).where(Mine.mine_code == "MG-JH-001"))
    assert mine is not None
    assert len(mine.zones) == 2
    assert len(mine.violations) == 1
    assert mine.violations[0].corrective_actions[0].status == "IN_PROGRESS"

    violation = database_session.scalar(select(Violation).where(Violation.violation_code == "VIO-2026-0001"))
    assert violation is not None
    assert violation.detected_by_user.email == "safety@mineguard.ai"


def test_zone_relationship_is_scoped_to_its_mine(database_session):
    seed_demo_data(database_session)

    zone = database_session.scalar(select(MineZone).where(MineZone.name == "Main Haul Road"))
    assert zone is not None
    assert zone.mine.mine_code == "MG-JH-001"
