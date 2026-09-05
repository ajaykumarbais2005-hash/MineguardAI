import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
import app.models
from app.database import get_db
from app.main import app as fastapi_app
from app.services.seed import seed_demo_data


@pytest.fixture
def database_session() -> Session:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    with session_factory() as session:
        yield session
    engine.dispose()


@pytest.fixture
def auth_client(database_session: Session):
    seed_demo_data(database_session)
    fastapi_app.dependency_overrides[get_db] = lambda: database_session
    with TestClient(fastapi_app) as client:
        yield client
    fastapi_app.dependency_overrides.clear()
