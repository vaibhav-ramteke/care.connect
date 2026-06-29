"""Shared pytest fixtures for the CarePath AI test suite.

Two things every test relies on:

1. **Deterministic (rule-based) mode.** The app is a hybrid: it uses Claude when
   an API key is configured, otherwise deterministic logic. Tests assert on the
   deterministic fallback text/behaviour, so the ``force_rule_based`` autouse
   fixture disables the LLM for every test — results stay stable whether or not
   the developer running the suite happens to have ``ANTHROPIC_API_KEY`` set.

2. **Isolated in-memory state.** ``app.main`` builds singletons (store,
   orchestrator) at import time. The ``reset_state`` autouse fixture clears the
   shared store before each test so sessions / audit / handoffs don't leak
   between tests.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app


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
    """Wipe shared in-memory state so tests don't interfere with one another."""
    store = main_module._store
    store.sessions.clear()
    store.audit.clear()
    store.handoffs.clear()
    store._apt_counter = 10245
    yield


@pytest.fixture
def store():
    """The app's shared in-memory store (already reset by ``reset_state``)."""
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
