"""Unit tests for symptom matching (pure logic), DB-backed reference lookups,
and seed-data integrity."""

from __future__ import annotations

import pytest

from app.data import mock_data as md
from app.db import repository as repo

pytestmark = pytest.mark.unit


# --------------------------------------------------------------------------- #
# Department matching
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "text, expected",
    [
        ("I have knee pain", "Orthopedics"),
        ("my heart is racing", "Cardiology"),
        ("I have a skin rash", "Dermatology"),
        ("I have fever and cough", "General Medicine"),
        ("pregnancy related question", "Gynecology"),
    ],
)
def test_match_department_by_symptom(text, expected):
    assert md.match_department(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("I need a cardiologist", "Cardiology"),
        ("orthopaedic surgeon", "Orthopedics"),
        ("skin specialist", "Dermatology"),
    ],
)
def test_match_department_by_specialty(text, expected):
    assert md.match_department(text) == expected


def test_match_department_specialty_takes_priority():
    # Specialty keywords are checked before symptom keywords.
    assert md.match_department("I want a heart specialist") == "Cardiology"


def test_match_department_no_match_returns_none():
    assert md.match_department("hello there") is None


# --------------------------------------------------------------------------- #
# Doctor lookups
# --------------------------------------------------------------------------- #
def test_doctors_in_filters_by_department():
    ortho = repo.doctors_in("Orthopedics")
    assert ortho and all(d["department"] == "Orthopedics" for d in ortho)


def test_doctors_in_unknown_department_empty():
    assert repo.doctors_in("Neurology") == []


@pytest.mark.parametrize(
    "text, expected_name",
    [
        ("book dr mehta please", "Dr. Mehta"),
        ("I'd like to see Kulkarni", "Dr. Kulkarni"),
        ("appointment with dr. shah", "Dr. Shah"),
    ],
)
def test_find_doctor_by_name(text, expected_name):
    doctor = repo.find_doctor_by_name(text)
    assert doctor is not None and doctor["name"] == expected_name


def test_find_doctor_by_name_no_match():
    assert repo.find_doctor_by_name("book dr nobody") is None


# --------------------------------------------------------------------------- #
# Pre-visit checklist (DB-backed)
# --------------------------------------------------------------------------- #
def test_previsit_checklist_department_specific():
    assert repo.previsit_checklist("Cardiology") == md.PREVISIT_CHECKLISTS["Cardiology"]


def test_previsit_checklist_falls_back_to_default():
    assert repo.previsit_checklist(None) == md.PREVISIT_CHECKLISTS["_default"]
    assert repo.previsit_checklist("Dermatology") == md.PREVISIT_CHECKLISTS["_default"]


# --------------------------------------------------------------------------- #
# Data integrity
# --------------------------------------------------------------------------- #
def test_every_doctor_has_required_fields_and_slots():
    for d in md.DOCTORS:
        for field in ("id", "name", "department", "fee", "languages", "slots"):
            assert field in d, f"{d.get('name')} missing {field}"
        assert len(d["slots"]) >= 3, f"{d['name']} should have >= 3 slots"


def test_every_doctor_department_exists():
    dept_names = {dept["name"] for dept in md.DEPARTMENTS}
    for d in md.DOCTORS:
        assert d["department"] in dept_names


def test_sample_bill_totals_are_consistent():
    bill = md.SAMPLE_BILL
    assert sum(i["amount"] for i in bill["items"]) == bill["total"]
    assert bill["insurance_approved"] + bill["patient_payable"] == bill["total"]
