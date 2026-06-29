"""Read-only reference-data access (departments, doctors, demo records).

Agents and reference endpoints call these helpers instead of touching the ORM
directly. Each opens a short-lived session and returns plain dicts/lists, so the
callers keep working with the same data shapes they always have.
"""

from __future__ import annotations

from . import models as m
from .database import SessionLocal


# --------------------------------------------------------------------------- #
# Departments & doctors
# --------------------------------------------------------------------------- #
def list_departments() -> list[dict]:
    with SessionLocal() as db:
        rows = db.query(m.Department).order_by(m.Department.id).all()
        return [{"name": r.name, "description": r.description} for r in rows]


def all_doctors() -> list[dict]:
    with SessionLocal() as db:
        rows = db.query(m.Doctor).order_by(m.Doctor.id).all()
        return [r.as_dict() for r in rows]


def doctors_in(department: str) -> list[dict]:
    with SessionLocal() as db:
        rows = (
            db.query(m.Doctor)
            .filter(m.Doctor.department == department)
            .order_by(m.Doctor.id)
            .all()
        )
        return [r.as_dict() for r in rows]


def find_doctor_by_name(text: str) -> dict | None:
    """Match a doctor by surname appearing in free text, e.g. 'book dr mehta'."""
    low = text.lower()
    with SessionLocal() as db:
        for r in db.query(m.Doctor).order_by(m.Doctor.id).all():
            surname = r.name.split()[-1].lower()
            if surname in low:
                return r.as_dict()
    return None


def previsit_checklist(department: str | None) -> list[str]:
    with SessionLocal() as db:
        if department:
            row = db.get(m.PrevisitChecklist, department)
            if row:
                return list(row.items)
        default = db.get(m.PrevisitChecklist, "_default")
        return list(default.items) if default else []


# --------------------------------------------------------------------------- #
# Demo clinical / billing records
# --------------------------------------------------------------------------- #
def get_prescription() -> dict:
    with SessionLocal() as db:
        row = db.query(m.Prescription).order_by(m.Prescription.id).first()
        return row.as_dict()


def get_discharge_summary() -> dict:
    with SessionLocal() as db:
        row = db.query(m.DischargeSummary).order_by(m.DischargeSummary.id).first()
        return row.as_dict()


def get_bill() -> dict:
    with SessionLocal() as db:
        row = db.query(m.Bill).order_by(m.Bill.id).first()
        return row.as_dict()


def get_insurance() -> dict:
    with SessionLocal() as db:
        row = db.query(m.InsuranceClaim).order_by(m.InsuranceClaim.id).first()
        return row.as_dict()
