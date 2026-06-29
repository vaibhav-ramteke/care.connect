"""Tests for reference/demo and session endpoints."""

from __future__ import annotations

import pytest

from tests.conftest import chat

pytestmark = pytest.mark.integration


# --------------------------------------------------------------------------- #
# Health
# --------------------------------------------------------------------------- #
def test_health_reports_rule_based_mode(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["app"] == "CarePath AI"
    assert body["mode"] == "rule-based"
    assert body["model"] is None


def test_root_redirects_to_docs(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/docs"


# --------------------------------------------------------------------------- #
# Doctors & departments
# --------------------------------------------------------------------------- #
def test_list_all_doctors(client):
    body = client.get("/api/doctors").json()
    assert body["count"] == len(body["doctors"]) >= 5


def test_list_doctors_filtered_by_department(client):
    body = client.get("/api/doctors", params={"department": "Cardiology"}).json()
    assert body["count"] >= 1
    assert all(d["department"] == "Cardiology" for d in body["doctors"])


def test_list_doctors_unknown_department_empty(client):
    body = client.get("/api/doctors", params={"department": "Neurology"}).json()
    assert body["count"] == 0


def test_list_departments(client):
    body = client.get("/api/departments").json()
    names = {d["name"] for d in body["departments"]}
    assert {"Cardiology", "Orthopedics", "General Medicine"} <= names


# --------------------------------------------------------------------------- #
# Sessions
# --------------------------------------------------------------------------- #
def test_get_session_returns_history_and_next_action(client):
    created = chat(client, "Which doctor should I consult for knee pain?")
    session_id = created["session_id"]

    body = client.get(f"/api/sessions/{session_id}").json()
    assert body["id"] == session_id
    assert body["journey_stage"] == "doctor_discovery"
    assert body["next_best_action"] == "Pick a doctor and book a slot"
    # history has the user message and the assistant reply.
    assert len(body["history"]) >= 2


def test_get_unknown_session_returns_404(client):
    response = client.get("/api/sessions/does-not-exist")
    assert response.status_code == 404
