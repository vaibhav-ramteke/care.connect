"""End-to-end tests for POST /api/chat — the main orchestration entry point.

These exercise the full flow: safety check -> intent -> journey stage ->
specialized agent -> guardrails -> handoff -> audit, via the FastAPI TestClient.
"""

from __future__ import annotations

import pytest

from tests.conftest import chat

pytestmark = pytest.mark.integration


# --------------------------------------------------------------------------- #
# Request validation
# --------------------------------------------------------------------------- #
def test_empty_message_is_rejected(client):
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422


def test_missing_message_is_rejected(client):
    response = client.post("/api/chat", json={})
    assert response.status_code == 422


# --------------------------------------------------------------------------- #
# Emergency short-circuit (safety first)
# --------------------------------------------------------------------------- #
def test_emergency_short_circuits_routing(client):
    body = chat(client, "My father has chest pain and difficulty breathing")
    assert body["emergency"] is True
    assert body["intent"] == "emergency_help"
    assert body["agent"] == "safety_guardrail_agent"
    assert body["handoff"]["triggered"] is True
    assert body["handoff"]["team"] == "emergency_team"
    assert body["handoff"]["ticket_id"]
    assert "112" in body["reply"]  # emergency number from settings


def test_emergency_opens_critical_handoff_ticket(client):
    chat(client, "I think I'm having a stroke")
    handoffs = client.get("/api/admin/handoffs").json()["handoffs"]
    assert any(h["priority"] == "critical" for h in handoffs)


# --------------------------------------------------------------------------- #
# Symptom / doctor / department flows
# --------------------------------------------------------------------------- #
def test_symptom_guidance_flow(client):
    body = chat(client, "I have a fever and cough")
    assert body["intent"] == "symptom_guidance"
    assert body["journey_stage"] == "symptom_discovery"
    assert body["disclaimer"]  # clinical reply carries a disclaimer
    assert body["emergency"] is False


def test_doctor_search_flow(client):
    body = chat(client, "Which doctor should I consult for knee pain?")
    assert body["intent"] == "doctor_search"
    assert body["journey_stage"] == "doctor_discovery"
    assert body["data"]["department"] == "Orthopedics"
    assert body["agent"] == "doctor_finder_agent"


# --------------------------------------------------------------------------- #
# Appointment booking + session continuity
# --------------------------------------------------------------------------- #
def test_booking_confirms_appointment(client):
    body = chat(client, "Book an appointment with Dr. Kulkarni")
    assert body["intent"] == "appointment_booking"
    appt = body["data"]["appointment"]
    assert appt["doctor"] == "Dr. Kulkarni"
    assert appt["status"] == "Confirmed"


def test_session_state_persists_across_turns(client):
    first = chat(client, "Book an appointment with Dr. Mehta")
    session_id = first["session_id"]

    # Second turn in the same session: cancel should find the booked appointment.
    second = chat(client, "Actually cancel my appointment", session_id=session_id)
    assert second["session_id"] == session_id
    assert second["data"]["appointment"]["status"] == "Cancelled"


def test_new_session_id_is_returned_when_omitted(client):
    body = chat(client, "hello")
    assert body["session_id"].startswith("sess-")


# --------------------------------------------------------------------------- #
# Prescription / discharge / billing / insurance
# --------------------------------------------------------------------------- #
def test_prescription_flow_has_medication_disclaimer(client):
    body = chat(client, "When should I take these medicines?")
    assert body["intent"] == "prescription_help"
    assert body["journey_stage"] == "prescription_support"
    assert "do not change" in body["disclaimer"].lower()


def test_discharge_flow(client):
    body = chat(client, "I was discharged after surgery, what should I do at home?")
    assert body["intent"] == "discharge_help"
    assert body["journey_stage"] == "discharge_planning"
    assert "discharge_summary" in body["data"]


def test_billing_flow(client):
    body = chat(client, "Can you show me my bill?")
    assert body["intent"] == "billing_query"
    assert body["data"]["bill"]["total"] == 21600


def test_insurance_flow(client):
    body = chat(client, "Is my insurance claim approved?")
    assert body["intent"] == "insurance_claim_query"
    assert body["journey_stage"] == "billing_and_insurance"
    assert "insurance" in body["data"]


# --------------------------------------------------------------------------- #
# Distress -> human handoff
# --------------------------------------------------------------------------- #
def test_distress_forces_handoff(client):
    body = chat(client, "This is useless, I am very frustrated with the billing")
    assert body["handoff"]["triggered"] is True
    assert body["handoff"]["ticket_id"]


def test_explicit_human_request_handoff(client):
    body = chat(client, "I want to speak to a human")
    assert body["intent"] == "human_handoff"
    assert body["handoff"]["triggered"] is True


# --------------------------------------------------------------------------- #
# General fallback
# --------------------------------------------------------------------------- #
def test_general_fallback(client):
    body = chat(client, "Tell me a joke about the weather")
    assert body["intent"] == "general"
    assert body["agent"] == "general_agent"
    assert body["emergency"] is False


# --------------------------------------------------------------------------- #
# Rule-based mode marker
# --------------------------------------------------------------------------- #
def test_llm_not_used_in_rule_based_mode(client):
    body = chat(client, "I have knee pain")
    assert body["llm_used"] is False
