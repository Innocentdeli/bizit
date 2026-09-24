"""
Points the app at an isolated, throwaway SQLite file for the test session so
tests never touch the real dev database (bizit_pulse.db). Must set the env
var before any app module is imported, since database/database.py reads
DATABASE_URL at import time.
"""
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
TEST_DB_PATH = Path(__file__).resolve().parent / "_test_marketing_os.db"

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
sys.path.insert(0, str(BACKEND_ROOT))

import pytest


@pytest.fixture(scope="session", autouse=True)
def _isolated_test_database():
    # database/models.py (OrganismActivity, Business, etc.) lives on its own
    # Base separate from marketing_os.py's Base — both need creating here since
    # nothing else does it for a bare test run (main.py normally triggers this).
    from database.database import Base, engine
    from database import models  # noqa: F401  (registers models on Base)
    Base.metadata.create_all(bind=engine)
    yield
    # Dispose the connection pool first — on Windows an open sqlite3 handle
    # blocks unlink() with a silently-swallowed PermissionError, leaving stale
    # data for the next run (which is exactly what happened while writing this).
    engine.dispose()
    try:
        TEST_DB_PATH.unlink()
    except FileNotFoundError:
        pass


@pytest.fixture
def db_session():
    from database.database import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
