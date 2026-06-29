"""Unit tests for the specialized agents (deterministic fallback path).

Each agent is exercised directly through ``handle(ctx)`` with the LLM disabled,
so we assert on the verified facts and the deterministic fallback reply.
"""

from __future__ import annotations

import pytest

from app.agents.base import AgentContext
from app.agents.handoff import HumanHandoffAgent, route_team
from app.agents.specialists import (
    AppointmentAgent,
    BillingInsuranceAgent,
    DischargeAgent,
    DoctorFinderAgent,
    GeneralAgent,
    PreVisitAgent,
    PrescriptionAgent,
    SymptomGuidanceAgent,
)
from app.config import Settings
from app.data import mock_data as md
from app.llm import LLMClient
from app.store import Store

pytestmark = pytest.mark.unit


@pytest.fixture
def llm():
    client = LLMClient(Settings(anthropic_api_key=None))
    assert client.enabled is False
    return client


@pytest.fixture
def store():
    return Store()


def make_ctx(store, message, intent="general", stage="symptom_discovery"):
    session = store.get_or_create_session(None)
    return AgentContext(
        message=message,
        session=session,
        intent=intent,
        journey_stage=stage,
    )


# --------------------------------------------------------------------------- #
# Symptom guidance
# --------------------------------------------------------------------------- #
def test_symptom_agent_maps_department(llm, store):
    ctx = make_ctx(store, "I have knee pain", intent="symptom_guidance")
    result = SymptomGuidanceAgent(llm).handle(ctx)
    assert result.agent == "symptom_guidance_agent"
    assert result.data["recommended_department"] == "Orthopedics"
    assert result.disclaimer  # clinical reply must carry a disclaimer
    assert result.llm_used is False


def test_symptom_agent_defaults_to_general_medicine(llm, store):
    ctx = make_ctx(store, "I feel strange", intent="symptom_guidance")
    result = SymptomGuidanceAgent(llm).handle(ctx)
    assert result.data["recommended_department"] == "General Medicine"


# --------------------------------------------------------------------------- #
# Doctor finder
# --------------------------------------------------------------------------- #
def test_doctor_finder_filters_by_department(llm, store):
    ctx = make_ctx(store, "find a doctor for knee pain", intent="doctor_search")
    result = DoctorFinderAgent(llm).handle(ctx)
    assert result.data["department"] == "Orthopedics"
    assert all(d["department"] == "Orthopedics" for d in result.data["doctors"])


def test_doctor_finder_lists_all_when_no_department(llm, store):
    ctx = make_ctx(store, "show me any doctor", intent="doctor_search")
    result = DoctorFinderAgent(llm).handle(ctx)
    assert len(result.data["doctors"]) == len(md.DOCTORS)


# --------------------------------------------------------------------------- #
# Appointment booking / reschedule / cancel
# --------------------------------------------------------------------------- #
def test_book_named_doctor_confirms_and_persists(llm, store):
    ctx = make_ctx(store, "book dr mehta", intent="appointment_booking")
    result = AppointmentAgent(llm, store).handle(ctx)
    appt = result.data["appointment"]
    assert appt["doctor"] == "Dr. Mehta"
    assert appt["status"] == "Confirmed"
    assert appt["appointment_id"].startswith("APT-")
    # The appointment is stored on the session.
    assert ctx.session["appointments"][-1] == appt


def test_book_without_doctor_asks_for_clarification(llm, store):
    ctx = make_ctx(store, "I want to book", intent="appointment_booking")
    result = AppointmentAgent(llm, store).handle(ctx)
    assert "appointment" not in result.data
    assert "Find a doctor" in result.quick_actions


def test_reschedule_without_existing_appointment(llm, store):
    ctx = make_ctx(store, "reschedule my appointment", intent="appointment_reschedule")
    result = AppointmentAgent(llm, store).handle(ctx)
    assert "couldn't find" in result.reply.lower()


def test_cancel_marks_latest_appointment_cancelled(llm, store):
    book_ctx = make_ctx(store, "book dr mehta", intent="appointment_booking")
    agent = AppointmentAgent(llm, store)
    agent.handle(book_ctx)
    # Reuse the same session to cancel.
    cancel_ctx = AgentContext(
        message="cancel it",
        session=book_ctx.session,
        intent="appointment_cancellation",
    )
    result = agent.handle(cancel_ctx)
    assert result.data["appointment"]["status"] == "Cancelled"


# --------------------------------------------------------------------------- #
# Pre-visit / prescription / discharge
# --------------------------------------------------------------------------- #
def test_previsit_uses_last_appointment_department(llm, store):
    book_ctx = make_ctx(store, "book dr kulkarni", intent="appointment_booking")
    AppointmentAgent(llm, store).handle(book_ctx)
    previsit_ctx = AgentContext(
        message="what should I bring",
        session=book_ctx.session,
        intent="previsit_checklist",
    )
    result = PreVisitAgent(llm).handle(previsit_ctx)
    assert result.data["department"] == "Orthopedics"
    assert result.data["checklist"] == md.PREVISIT_CHECKLISTS["Orthopedics"]


def test_prescription_includes_medication_safety_note(llm, store):
    ctx = make_ctx(store, "explain my medicines", intent="prescription_help")
    result = PrescriptionAgent(llm).handle(ctx)
    assert result.data["prescription"] == md.SAMPLE_PRESCRIPTION
    assert "do not change" in result.disclaimer.lower()


def test_discharge_returns_warning_signs(llm, store):
    ctx = make_ctx(store, "I was discharged", intent="discharge_help")
    result = DischargeAgent(llm).handle(ctx)
    assert result.data["discharge_summary"] == md.SAMPLE_DISCHARGE_SUMMARY
    assert result.disclaimer


# --------------------------------------------------------------------------- #
# Billing / insurance
# --------------------------------------------------------------------------- #
def test_billing_returns_bill(llm, store):
    ctx = make_ctx(store, "show my bill", intent="billing_query")
    result = BillingInsuranceAgent(llm).handle(ctx)
    assert result.data["bill"] == md.SAMPLE_BILL


def test_insurance_returns_claim(llm, store):
    ctx = make_ctx(store, "insurance claim status", intent="insurance_claim_query")
    result = BillingInsuranceAgent(llm).handle(ctx)
    assert result.data["insurance"] == md.SAMPLE_INSURANCE


# --------------------------------------------------------------------------- #
# General fallback
# --------------------------------------------------------------------------- #
def test_general_agent_offers_capabilities(llm, store):
    ctx = make_ctx(store, "hi", intent="general")
    result = GeneralAgent(llm).handle(ctx)
    assert result.agent == "general_agent"
    assert "Talk to a human" in result.quick_actions


# --------------------------------------------------------------------------- #
# Human handoff routing
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "message, expected_team",
    [
        ("question about my bill", "billing_team"),
        ("my insurance claim", "insurance_desk"),
        ("reschedule my slot", "appointment_desk"),
        ("I need a nurse", "nurse"),
        ("talk to the doctor", "doctor_coordinator"),
        ("just connect me to someone", "front_desk"),
    ],
)
def test_route_team(message, expected_team):
    assert route_team(message) == expected_team


def test_handoff_agent_sets_needs_handoff(llm, store):
    ctx = make_ctx(store, "I need a nurse", intent="human_handoff")
    result = HumanHandoffAgent(llm).handle(ctx)
    assert result.needs_handoff is True
    assert result.handoff_team == "nurse"
