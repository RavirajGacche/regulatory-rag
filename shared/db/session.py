from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from shared.config import settings

engine = create_engine(
    url=settings.postgres_url, pool_pre_ping=True, pool_size=5, echo=False, max_overflow=10
)


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope() -> Generator[Session]:
    """One unit of work: commit on success, roll back on error, always close."""

    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
