"""Unit tests for the Patient Journey agent (stage detection + next action)."""

from __future__ import annotations

import pytest

from app.agents.journey import JOURNEY_STAGES, JourneyAgent

pytestmark = pytest.mark.unit


@pytest.fixture
def journey():
    return JourneyAgent()


@pytest.mark.parametrize(
    "intent, expected_stage",
    [
        ("emergency_help", "symptom_discovery"),
        ("symptom_guidance", "symptom_discovery"),
        ("doctor_search", "doctor_discovery"),
        ("appointment_booking", "appointment_booking"),
        ("previsit_checklist", "pre_visit_preparation"),
        ("prescription_help", "prescription_support"),
        ("discharge_help", "discharge_planning"),
        ("billing_query", "billing_and_insurance"),
        ("insurance_claim_query", "billing_and_insurance"),
    ],
)
def test_intent_maps_to_stage(journey, intent, expected_stage):
    assert journey.detect(intent, "symptom_discovery") == expected_stage


def test_unknown_intent_keeps_current_stage(journey):
    # An intent with no mapping should be "sticky" — keep the current stage.
    assert journey.detect("general", "appointment_booking") == "appointment_booking"


def test_mapped_stages_are_valid(journey):
    for intent in [
        "doctor_search",
        "prescription_help",
        "discharge_help",
        "followup_booking",
    ]:
        assert journey.detect(intent, "symptom_discovery") in JOURNEY_STAGES


def test_next_best_action_known_stage(journey):
    assert journey.next_best_action("doctor_discovery") == "Pick a doctor and book a slot"


def test_next_best_action_unknown_stage_has_default(journey):
    assert journey.next_best_action("nonexistent_stage") == "Continue your care journey"
