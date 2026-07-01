"""Specialized agents the orchestrator routes to.

Each agent lives in its own module and computes verified facts from the
database, builds a deterministic fallback reply, then optionally lets the LLM
rephrase those facts (hybrid). They are re-exported here so callers can keep
importing ``from app.agents.specialists import SymptomGuidanceAgent`` etc.
"""

from __future__ import annotations

from .appointment import AppointmentAgent
from .billing import BillingInsuranceAgent
from .discharge import DischargeAgent
from .doctor_finder import DoctorFinderAgent
from .general import GeneralAgent
from .previsit import PreVisitAgent
from .prescription import PrescriptionAgent
from .symptom import SymptomGuidanceAgent

__all__ = [
    "SymptomGuidanceAgent",
    "DoctorFinderAgent",
    "AppointmentAgent",
    "PreVisitAgent",
    "PrescriptionAgent",
    "DischargeAgent",
    "BillingInsuranceAgent",
    "GeneralAgent",
]
