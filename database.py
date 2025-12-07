from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./swiftride.db"  # For demo; switch to Postgres/MySQL in prod

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    from fastapi import Depends

    def _get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return Depends(_get_db)
