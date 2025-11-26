"""
Script to initialize the database and create all tables.
Ensures all SQLAlchemy models are imported for metadata.
"""
import src.models.sqlalchemy_models  # noqa: F401
from src.utils.db_session import Base, engine


def init_db() -> None:
    """Create all tables in the database using SQLAlchemy metadata."""
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully.")


if __name__ == "__main__":
    init_db()
