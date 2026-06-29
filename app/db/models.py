"""SQLAlchemy ORM models — the database schema for CarePath AI.

Two groups of tables:

* **Reference / master data** (seeded, read-mostly): departments, doctors,
  pre-visit checklists, and the demo clinical/billing records.
* **Operational state** (written at runtime): conversation sessions, messages,
  appointments, the audit log, and the human-handoff queue.

List/dict-shaped fields (a doctor's languages, a bill's line items, etc.) are
stored in ``JSON`` columns so the records round-trip back to exactly the dict
shapes the agents already expect.
"""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# --------------------------------------------------------------------------- #
# Reference / master data
# --------------------------------------------------------------------------- #
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255))


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), index=True)
    department: Mapped[str] = mapped_column(String(80), index=True)
    gender: Mapped[str] = mapped_column(String(1))
    fee: Mapped[int] = mapped_column(Integer)
    teleconsult: Mapped[bool] = mapped_column(Boolean, default=False)
    languages: Mapped[list] = mapped_column(JSON, default=list)
    slots: Mapped[list] = mapped_column(JSON, default=list)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "languages": list(self.languages),
            "gender": self.gender,
            "fee": self.fee,
            "teleconsult": self.teleconsult,
            "slots": list(self.slots),
        }


class PrevisitChecklist(Base):
    __tablename__ = "previsit_checklists"

    department: Mapped[str] = mapped_column(String(80), primary_key=True)
    items: Mapped[list] = mapped_column(JSON, default=list)


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient: Mapped[str] = mapped_column(String(120))
    medicines: Mapped[list] = mapped_column(JSON, default=list)

    def as_dict(self) -> dict:
        return {"patient": self.patient, "medicines": list(self.medicines)}


class DischargeSummary(Base):
    __tablename__ = "discharge_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient: Mapped[str] = mapped_column(String(120))
    reason: Mapped[str] = mapped_column(String(255))
    condition: Mapped[str] = mapped_column(String(255))
    medicines_days: Mapped[int] = mapped_column(Integer)
    wound_care: Mapped[str] = mapped_column(String(255))
    activity: Mapped[str] = mapped_column(String(255))
    follow_up: Mapped[str] = mapped_column(String(255))
    warning_signs: Mapped[list] = mapped_column(JSON, default=list)

    def as_dict(self) -> dict:
        return {
            "patient": self.patient,
            "reason": self.reason,
            "condition": self.condition,
            "medicines_days": self.medicines_days,
            "wound_care": self.wound_care,
            "activity": self.activity,
            "follow_up": self.follow_up,
            "warning_signs": list(self.warning_signs),
        }


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appointment_id: Mapped[str] = mapped_column(String(40))
    items: Mapped[list] = mapped_column(JSON, default=list)
    total: Mapped[int] = mapped_column(Integer)
    insurance_approved: Mapped[int] = mapped_column(Integer)
    patient_payable: Mapped[int] = mapped_column(Integer)

    def as_dict(self) -> dict:
        return {
            "appointment_id": self.appointment_id,
            "items": [dict(i) for i in self.items],
            "total": self.total,
            "insurance_approved": self.insurance_approved,
            "patient_payable": self.patient_payable,
        }


class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy: Mapped[str] = mapped_column(String(120))
    claim_id: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(60))
    approved_amount: Mapped[int] = mapped_column(Integer)
    pending_documents: Mapped[list] = mapped_column(JSON, default=list)
    uncovered_note: Mapped[str] = mapped_column(String(255))

    def as_dict(self) -> dict:
        return {
            "policy": self.policy,
            "claim_id": self.claim_id,
            "status": self.status,
            "approved_amount": self.approved_amount,
            "pending_documents": list(self.pending_documents),
            "uncovered_note": self.uncovered_note,
        }


# --------------------------------------------------------------------------- #
# Operational state
# --------------------------------------------------------------------------- #
class SessionRow(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    patient_id: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40))
    journey_stage: Mapped[str] = mapped_column(String(60), default="symptom_discovery")

    messages: Mapped[list["Message"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.id",
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Appointment.id",
    )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "created_at": self.created_at,
            "journey_stage": self.journey_stage,
            "history": [m.as_dict() for m in self.messages],
            "appointments": [a.as_dict() for a in self.appointments],
        }


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    text: Mapped[str] = mapped_column(Text)
    at: Mapped[str] = mapped_column(String(40))

    session: Mapped["SessionRow"] = relationship(back_populates="messages")

    def as_dict(self) -> dict:
        return {"role": self.role, "text": self.text, "at": self.at}


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appointment_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"), index=True)
    doctor: Mapped[str] = mapped_column(String(80))
    department: Mapped[str] = mapped_column(String(80))
    time: Mapped[str] = mapped_column(String(60))
    fee: Mapped[int] = mapped_column(Integer)
    location: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30), default="Confirmed")

    session: Mapped["SessionRow"] = relationship(back_populates="appointments")

    def as_dict(self) -> dict:
        return {
            "appointment_id": self.appointment_id,
            "doctor": self.doctor,
            "department": self.department,
            "time": self.time,
            "fee": self.fee,
            "location": self.location,
            "status": self.status,
        }


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    at: Mapped[str] = mapped_column(String(40), index=True)
    session_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    query: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String(60), index=True)
    journey_stage: Mapped[str] = mapped_column(String(60))
    agent: Mapped[str] = mapped_column(String(60))
    emergency: Mapped[bool] = mapped_column(Boolean, default=False)
    red_flag: Mapped[str | None] = mapped_column(String(120), nullable=True)
    handoff_team: Mapped[str | None] = mapped_column(String(60), nullable=True)
    handoff_ticket: Mapped[str | None] = mapped_column(String(40), nullable=True)
    disclaimer_shown: Mapped[bool] = mapped_column(Boolean, default=False)
    llm_used: Mapped[bool] = mapped_column(Boolean, default=False)

    # Fields a caller may include in the audit dict, mapped to columns above.
    _FIELDS = (
        "session_id", "query", "intent", "journey_stage", "agent", "emergency",
        "red_flag", "handoff_team", "handoff_ticket", "disclaimer_shown", "llm_used",
    )

    def as_dict(self) -> dict:
        return {
            "at": self.at,
            "session_id": self.session_id,
            "query": self.query,
            "intent": self.intent,
            "journey_stage": self.journey_stage,
            "agent": self.agent,
            "emergency": self.emergency,
            "red_flag": self.red_flag,
            "handoff_team": self.handoff_team,
            "handoff_ticket": self.handoff_ticket,
            "disclaimer_shown": self.disclaimer_shown,
            "llm_used": self.llm_used,
        }


class HandoffRow(Base):
    __tablename__ = "handoffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(40), index=True)
    patient_masked: Mapped[str] = mapped_column(String(40))
    team: Mapped[str] = mapped_column(String(60), index=True)
    priority: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str] = mapped_column(String(255))
    query: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[str] = mapped_column(String(40))

    def as_dict(self) -> dict:
        return {
            "ticket_id": self.ticket_id,
            "session_id": self.session_id,
            "patient_masked": self.patient_masked,
            "team": self.team,
            "priority": self.priority,
            "reason": self.reason,
            "query": self.query,
            "status": self.status,
            "created_at": self.created_at,
        }
