# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================
# Render PostgreSQL Connection URL (Hardcoded)
# ============================================
DATABASE_URL = (
    "postgresql://sharmo_db_user:"
    "f3XpOXxe6SMj8z34fIvp6sf7oUfqt02a"
    "@dpg-d4s0cifpm1nc73aggen0-a/sharmo_db"
)

# Create the database engine for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Session maker for DB sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


# Dependency for DB sessions (FastAPI standard)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
