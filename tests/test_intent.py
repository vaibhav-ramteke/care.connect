"""Unit tests for keyword-based intent detection (the deterministic fallback)."""

from __future__ import annotations

import pytest

from app.agents.intent import INTENTS, IntentDetector
from app.llm import LLMClient
from app.config import Settings

pytestmark = pytest.mark.unit


@pytest.fixture
def detector():
    # A client with no API key -> classify() returns None -> keyword fallback.
    llm = LLMClient(Settings(anthropic_api_key=None))
    assert llm.enabled is False
    return IntentDetector(llm)


@pytest.mark.parametrize(
    "message, expected",
    [
        ("Please cancel my appointment", "appointment_cancellation"),
        ("I want to reschedule my appointment", "appointment_reschedule"),
        ("Is my insurance claim approved?", "insurance_claim_query"),
        ("Can I see my bill?", "billing_query"),
        ("When should I take this tablet?", "prescription_help"),
        ("I was discharged after surgery", "discharge_help"),
        ("Is my blood test report ready?", "lab_report"),
        ("I need a refill of my prescription", "prescription_help"),
        ("Please remind me at 8pm", "medication_reminder"),
        ("What documents should I carry?", "previsit_checklist"),
        ("Where is the radiology counter?", "hospital_navigation"),
        ("Which doctor should I consult for knee pain?", "doctor_search"),
        ("I want to book an appointment", "appointment_booking"),
        ("I have a fever and cough", "symptom_guidance"),
        ("I want to talk to a person", "human_handoff"),
        ("Tell me about the weather", "general"),
    ],
)
def test_keyword_detection(detector, message, expected):
    assert detector.detect(message) == expected


def test_cancellation_beats_appointment_booking(detector):
    # "cancel" is listed before generic "appointment" cues, so it wins.
    assert detector.detect("cancel my appointment booking") == "appointment_cancellation"


def test_prescription_cue_beats_reminder_cue(detector):
    # Documents the keyword precedence: "medicine"/"tablet" are prescription_help
    # cues checked *before* medication_reminder, so "medicine reminder" routes to
    # prescription_help. Use a non-prescription phrase to reach medication_reminder.
    assert detector.detect("I need a medicine reminder") == "prescription_help"
    assert detector.detect("send me a refill reminder") == "medication_reminder"


def test_detect_returns_a_known_intent(detector):
    # Whatever the input, the result must be one of the supported intents.
    for message in ["???", "hello", "I have chest discomfort", "fee details"]:
        assert detector.detect(message) in INTENTS


def test_empty_message_falls_back_to_general(detector):
    assert detector.detect("") == "general"
