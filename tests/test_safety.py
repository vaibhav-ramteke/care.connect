"""Unit tests for the deterministic safety guardrails.

These rules are the most safety-critical part of the system: emergency
detection must run before any routing or LLM call and must be 100% deterministic.
"""

from __future__ import annotations

import pytest

from app.safety import guardrails as g

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# Emergency detection
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "text, expected_phrase",
    [
        ("I have chest pain since morning", "chest pain"),
        ("My father has difficulty breathing", "difficulty breathing"),
        ("He suddenly can't breathe", "can't breathe"),
        ("She had a seizure", "seizure"),
        ("There is severe bleeding from the wound", "severe bleeding"),
        ("I think I'm having a stroke, my face is drooping", "stroke"),
        ("I want to die", "want to die"),
        ("He took an overdose of pills", "overdose"),
        ("The baby is not breathing", "not breathing"),
    ],
)
def test_detect_emergency_matches_red_flags(text, expected_phrase):
    assert g.detect_emergency(text) == expected_phrase


def test_detect_emergency_is_case_insensitive():
    assert g.detect_emergency("CHEST PAIN and DIFFICULTY BREATHING") == "chest pain"


@pytest.mark.parametrize(
    "text",
    [
        "I have a mild headache",
        "I want to book an appointment",
        "When should I take my medicine?",
        "What documents should I bring?",
        "",
    ],
)
def test_detect_emergency_ignores_non_emergencies(text):
    assert g.detect_emergency(text) is None


def test_detect_emergency_returns_first_phrase_in_list_order():
    # "chest pain" appears earlier in EMERGENCY_PHRASES than "seizure".
    text = "he had a seizure and chest pain"
    assert g.detect_emergency(text) == "chest pain"


# --------------------------------------------------------------------------- #
# Distress detection
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "text",
    [
        "this is useless",
        "worst service ever",
        "I am very angry",
        "I want to speak to a human",
        "Just let me talk to a person",
    ],
)
def test_detect_distress_true(text):
    assert g.detect_distress(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "Thank you, that was helpful",
        "I have knee pain",
        "Book me an appointment please",
    ],
)
def test_detect_distress_false(text):
    assert g.detect_distress(text) is False


# --------------------------------------------------------------------------- #
# Disclaimers / constants
# --------------------------------------------------------------------------- #
def test_clinical_intents_cover_expected_set():
    assert g.CLINICAL_INTENTS == {
        "symptom_guidance",
        "emergency_help",
        "prescription_help",
        "discharge_help",
        "lab_report",
        "recovery_monitoring",
        "medication_reminder",
    }


def test_disclaimers_are_non_empty_strings():
    for text in (g.MEDICAL_DISCLAIMER, g.EMERGENCY_DISCLAIMER, g.MEDICATION_SAFETY_NOTE):
        assert isinstance(text, str) and text.strip()
