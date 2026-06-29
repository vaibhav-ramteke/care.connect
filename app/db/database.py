"""SQLAlchemy engine and session factory.

A single SQLite file backs the whole app by default (zero-config, easy to
handle). Because only the ``DATABASE_URL`` is referenced here, switching to
Postgres/MySQL later is a one-line change — no other module imports a driver.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..config import settings


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model."""


def _make_engine(url: str):
    # check_same_thread=False is required for SQLite under FastAPI's threadpool.
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


engine = _make_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_all() -> None:
    """Create every table. Safe to call repeatedly (idempotent)."""
    # Import models for their side effect of registering with Base.metadata.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def drop_all() -> None:
    """Drop every table — used by the test harness to get a clean schema."""
    from . import models  # noqa: F401

    Base.metadata.drop_all(bind=engine)
