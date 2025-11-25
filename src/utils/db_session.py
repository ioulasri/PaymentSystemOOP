# SQLAlchemy engine and session setup
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .db_config import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
