"""Shared pytest fixtures for the CarePath AI test suite.

Three things every test relies on:

1. **A clean, isolated database.** Before importing the app we point
   ``DATABASE_URL`` at a throwaway SQLite file and delete any stale copy, so the
   suite never touches the developer's real ``carepath.db``. The app seeds
   reference data (departments, doctors, demo records) on import.

2. **Deterministic (rule-based) mode.** The app is a hybrid: it uses Claude when
   an API key is configured, otherwise deterministic logic. Tests assert on the
   deterministic fallback, so ``force_rule_based`` disables the LLM everywhere.

3. **Isolated operational state.** ``reset_state`` wipes sessions / messages /
   appointments / audit / handoffs (but not reference data) before each test so
   they don't leak between tests.
"""

from __future__ import annotations

import os

# Must be set BEFORE any app module (and therefore the DB engine) is imported.
_TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "carepath_test.db")
if os.path.exists(_TEST_DB_PATH):
    os.remove(_TEST_DB_PATH)
os.environ["DATABASE_URL"] = "sqlite:///" + _TEST_DB_PATH.replace("\\", "/")
os.environ.pop("ANTHROPIC_API_KEY", None)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.main as main_module  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def force_rule_based():
    """Guarantee deterministic, offline behaviour for every test."""
    previous = main_module._llm.enabled
    main_module._llm.enabled = False
    try:
        yield
    finally:
        main_module._llm.enabled = previous


@pytest.fixture(autouse=True)
def reset_state():
    """Wipe operational DB state so tests don't interfere with one another."""
    main_module._store.reset()
    yield


@pytest.fixture
def store():
    """The app's shared (DB-backed) store, with operational state reset."""
    return main_module._store


@pytest.fixture
def client():
    """A FastAPI TestClient bound to the application."""
    with TestClient(app) as test_client:
        yield test_client


def chat(client, message, *, session_id=None, patient_id=None, language="en"):
    """Helper: POST /api/chat and return the parsed JSON body."""
    payload = {"message": message, "language": language}
    if session_id is not None:
        payload["session_id"] = session_id
    if patient_id is not None:
        payload["patient_id"] = patient_id
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200, response.text
    return response.json()
