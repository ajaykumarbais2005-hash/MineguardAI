import app.models

from app.database import Base, SessionLocal, engine
from app.services.seed import seed_demo_data


def initialize_database() -> dict[str, int]:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        return seed_demo_data(session)


if __name__ == "__main__":
    counts = initialize_database()
    for table, count in counts.items():
        print(f"{table}: {count}")
