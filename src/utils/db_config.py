# Database configuration for SQLAlchemy/PostgreSQL
import os

DB_USER = os.getenv("PAYMENT_DB_USER", "payment_user")
DB_PASSWORD = os.getenv("PAYMENT_DB_PASSWORD", "payment_pass")
DB_HOST = os.getenv("PAYMENT_DB_HOST", "localhost")
DB_PORT = os.getenv("PAYMENT_DB_PORT", "5432")
DB_NAME = os.getenv("PAYMENT_DB_NAME", "payment_db")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
