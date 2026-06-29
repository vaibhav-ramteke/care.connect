"""Database initialisation and seeding.

``init_and_seed()`` is called once on application startup. It:

1. creates all tables,
2. seeds **reference data** (departments, doctors, checklists, demo clinical
   records) from the constants in :mod:`app.data.mock_data` — idempotent, so it
   only inserts what is missing, and
3. seeds a little **realistic operational data** (a couple of past
   conversations, an appointment, and a handoff ticket) the first time the DB is
   empty, so the admin dashboard and history endpoints have something to show.

All the actual INSERTs live here, so the project carries its own seed queries.
"""

from __future__ import annotations

import logging

from ..data import mock_data as md
from . import models as m
from .database import SessionLocal, create_all

logger = logging.getLogger("carepath.db.seed")


# --------------------------------------------------------------------------- #
# Reference data (idempotent)
# --------------------------------------------------------------------------- #
def seed_reference(db) -> None:
    if db.query(m.Department).count() == 0:
        db.add_all(
            m.Department(name=d["name"], description=d["description"])
            for d in md.DEPARTMENTS
        )

    if db.query(m.Doctor).count() == 0:
        db.add_all(
            m.Doctor(
                id=d["id"],
                name=d["name"],
                department=d["department"],
                gender=d["gender"],
                fee=d["fee"],
                teleconsult=d["teleconsult"],
                languages=d["languages"],
                slots=d["slots"],
            )
            for d in md.DOCTORS
        )

    if db.query(m.PrevisitChecklist).count() == 0:
        db.add_all(
            m.PrevisitChecklist(department=dept, items=items)
            for dept, items in md.PREVISIT_CHECKLISTS.items()
        )

    if db.query(m.Prescription).count() == 0:
        rx = md.SAMPLE_PRESCRIPTION
        db.add(m.Prescription(patient=rx["patient"], medicines=rx["medicines"]))

    if db.query(m.DischargeSummary).count() == 0:
        ds = md.SAMPLE_DISCHARGE_SUMMARY
        db.add(
            m.DischargeSummary(
                patient=ds["patient"],
                reason=ds["reason"],
                condition=ds["condition"],
                medicines_days=ds["medicines_days"],
                wound_care=ds["wound_care"],
                activity=ds["activity"],
                follow_up=ds["follow_up"],
                warning_signs=ds["warning_signs"],
            )
        )

    if db.query(m.Bill).count() == 0:
        b = md.SAMPLE_BILL
        db.add(
            m.Bill(
                appointment_id=b["appointment_id"],
                items=b["items"],
                total=b["total"],
                insurance_approved=b["insurance_approved"],
                patient_payable=b["patient_payable"],
            )
        )

    if db.query(m.InsuranceClaim).count() == 0:
        ins = md.SAMPLE_INSURANCE
        db.add(
            m.InsuranceClaim(
                policy=ins["policy"],
                claim_id=ins["claim_id"],
                status=ins["status"],
                approved_amount=ins["approved_amount"],
                pending_documents=ins["pending_documents"],
                uncovered_note=ins["uncovered_note"],
            )
        )


# --------------------------------------------------------------------------- #
# Realistic demo operational data (only when the DB has no sessions yet)
# --------------------------------------------------------------------------- #
def seed_demo_operational(db) -> None:
    if db.query(m.SessionRow).count() > 0:
        return

    # 1) A completed booking conversation (Orthopedics).
    s1 = m.SessionRow(
        id="sess-demo-knee01",
        patient_id="P100231",
        created_at="2026-06-27T09:12:00+00:00",
        journey_stage="appointment_booking",
    )
    s1.messages = [
        m.Message(role="user", text="I have knee pain. Which doctor should I consult?",
                  at="2026-06-27T09:12:00+00:00"),
        m.Message(role="assistant",
                  text="Knee pain is usually handled by Orthopedics. Dr. Kulkarni is available tomorrow at 11:00 AM.",
                  at="2026-06-27T09:12:01+00:00"),
        m.Message(role="user", text="Book an appointment with Dr. Kulkarni",
                  at="2026-06-27T09:13:10+00:00"),
        m.Message(role="assistant",
                  text="Your appointment is confirmed with Dr. Kulkarni (Orthopedics) tomorrow at 11:00 AM.",
                  at="2026-06-27T09:13:11+00:00"),
    ]
    s1.appointments = [
        m.Appointment(
            appointment_id="APT-10246",
            doctor="Dr. Kulkarni",
            department="Orthopedics",
            time="Tomorrow 11:00 AM",
            fee=900,
            location="OPD Block, Room 204",
            status="Confirmed",
        )
    ]
    db.add(s1)

    # 2) A billing question conversation.
    s2 = m.SessionRow(
        id="sess-demo-bill02",
        patient_id="P100994",
        created_at="2026-06-28T15:40:00+00:00",
        journey_stage="billing_and_insurance",
    )
    s2.messages = [
        m.Message(role="user", text="Can you show me my bill?",
                  at="2026-06-28T15:40:00+00:00"),
        m.Message(role="assistant",
                  text="Your total is Rs.21600. Insurance approved Rs.16000, you pay Rs.5600.",
                  at="2026-06-28T15:40:01+00:00"),
    ]
    db.add(s2)

    # 3) An emergency conversation that escalated to a human.
    s3 = m.SessionRow(
        id="sess-demo-emerg03",
        patient_id="P101777",
        created_at="2026-06-29T07:05:00+00:00",
        journey_stage="symptom_discovery",
    )
    s3.messages = [
        m.Message(role="user", text="My father has chest pain and breathing difficulty",
                  at="2026-06-29T07:05:00+00:00"),
        m.Message(role="assistant",
                  text="This may be urgent. Please call 112 now or go to the nearest Emergency Department.",
                  at="2026-06-29T07:05:01+00:00"),
    ]
    db.add(s3)

    # Matching handoff tickets.
    db.add_all([
        m.HandoffRow(
            ticket_id="TKT-DEMO0001",
            session_id="sess-demo-emerg03",
            patient_masked="P1***",
            team="emergency_team",
            priority="critical",
            reason="Emergency red flag detected: chest pain",
            query="My father has chest pain and breathing difficulty",
            status="open",
            created_at="2026-06-29T07:05:01+00:00",
        ),
        m.HandoffRow(
            ticket_id="TKT-DEMO0002",
            session_id="sess-demo-bill02",
            patient_masked="P1***",
            team="billing_team",
            priority="normal",
            reason="Patient requested human assistance",
            query="I want to talk to the billing team",
            status="resolved",
            created_at="2026-06-28T15:42:00+00:00",
        ),
    ])

    # Matching audit entries (one per assistant turn above).
    db.add_all([
        m.AuditLog(at="2026-06-27T09:12:01+00:00", session_id="sess-demo-knee01",
                   query="I have knee pain. Which doctor should I consult?",
                   intent="doctor_search", journey_stage="doctor_discovery",
                   agent="doctor_finder_agent", llm_used=False),
        m.AuditLog(at="2026-06-27T09:13:11+00:00", session_id="sess-demo-knee01",
                   query="Book an appointment with Dr. Kulkarni",
                   intent="appointment_booking", journey_stage="appointment_booking",
                   agent="appointment_agent", llm_used=False),
        m.AuditLog(at="2026-06-28T15:40:01+00:00", session_id="sess-demo-bill02",
                   query="Can you show me my bill?",
                   intent="billing_query", journey_stage="billing_and_insurance",
                   agent="billing_insurance_agent", llm_used=False),
        m.AuditLog(at="2026-06-29T07:05:01+00:00", session_id="sess-demo-emerg03",
                   query="My father has chest pain and breathing difficulty",
                   intent="emergency_help", journey_stage="symptom_discovery",
                   agent="safety_guardrail_agent", emergency=True, red_flag="chest pain",
                   handoff_team="emergency_team", handoff_ticket="TKT-DEMO0001",
                   disclaimer_shown=True, llm_used=False),
    ])


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def init_and_seed(*, with_demo: bool = True) -> None:
    """Create tables and seed reference (+ optionally demo) data."""
    create_all()
    with SessionLocal() as db:
        seed_reference(db)
        if with_demo:
            seed_demo_operational(db)
        db.commit()
    logger.info("Database initialised and seeded (demo=%s).", with_demo)
