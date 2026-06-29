"""Operational state — sessions, messages, appointments, audit log, handoffs.

Backed by the database (SQLAlchemy). This module owns every operational
INSERT/UPDATE in the project. The rest of the app keeps working with plain
``dict`` session objects: methods here persist changes to the DB *and* mutate
the in-flight dict so the current response reflects them. State survives a
restart because it lives in the database, not in process memory.

Swapping the datastore only touches this module and :mod:`app.db`.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, func, select

from .db import models as m
from .db.database import SessionLocal

_APT_BASE = 10245  # appointment ids start after the sample bill's APT-10245
_APT_RE = re.compile(r"APT-(\d+)")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self) -> None:
        self._apt_counter = self._highest_appointment_number()

    # ------------------------------------------------------------------
    # Counters
    # ------------------------------------------------------------------
    def _highest_appointment_number(self) -> int:
        with SessionLocal() as db:
            highest = _APT_BASE
            for (apt_id,) in db.execute(select(m.Appointment.appointment_id)):
                match = _APT_RE.fullmatch(apt_id or "")
                if match:
                    highest = max(highest, int(match.group(1)))
            return highest

    def next_appointment_id(self) -> str:
        self._apt_counter += 1
        return f"APT-{self._apt_counter}"

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------
    def get_or_create_session(
        self, session_id: str | None, patient_id: str | None = None
    ) -> dict:
        with SessionLocal() as db:
            if session_id:
                row = db.get(m.SessionRow, session_id)
                if row:
                    return row.as_dict()

            sid = session_id or f"sess-{uuid.uuid4().hex[:10]}"
            row = m.SessionRow(
                id=sid,
                patient_id=patient_id,
                created_at=_now(),
                journey_stage="symptom_discovery",
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return row.as_dict()

    def get_session_view(self, session_id: str) -> dict | None:
        with SessionLocal() as db:
            row = db.get(m.SessionRow, session_id)
            return row.as_dict() if row else None

    def set_journey_stage(self, session: dict, stage: str) -> None:
        with SessionLocal() as db:
            row = db.get(m.SessionRow, session["id"])
            if row:
                row.journey_stage = stage
                db.commit()
        session["journey_stage"] = stage

    def add_message(self, session: dict, role: str, text: str) -> None:
        at = _now()
        with SessionLocal() as db:
            db.add(m.Message(session_id=session["id"], role=role, text=text, at=at))
            db.commit()
        session.setdefault("history", []).append({"role": role, "text": text, "at": at})

    # ------------------------------------------------------------------
    # Appointments
    # ------------------------------------------------------------------
    def add_appointment(self, session: dict, appointment: dict) -> None:
        with SessionLocal() as db:
            db.add(
                m.Appointment(
                    appointment_id=appointment["appointment_id"],
                    session_id=session["id"],
                    doctor=appointment["doctor"],
                    department=appointment["department"],
                    time=appointment["time"],
                    fee=appointment["fee"],
                    location=appointment["location"],
                    status=appointment["status"],
                )
            )
            db.commit()
        session.setdefault("appointments", []).append(appointment)

    def update_appointment_status(self, appointment_id: str, status: str) -> None:
        with SessionLocal() as db:
            row = (
                db.query(m.Appointment)
                .filter(m.Appointment.appointment_id == appointment_id)
                .one_or_none()
            )
            if row:
                row.status = status
                db.commit()

    # ------------------------------------------------------------------
    # Audit log
    # ------------------------------------------------------------------
    def log_audit(self, entry: dict) -> None:
        with SessionLocal() as db:
            db.add(
                m.AuditLog(
                    at=_now(),
                    session_id=entry.get("session_id"),
                    query=entry.get("query", ""),
                    intent=entry.get("intent", ""),
                    journey_stage=entry.get("journey_stage", ""),
                    agent=entry.get("agent", ""),
                    emergency=bool(entry.get("emergency", False)),
                    red_flag=entry.get("red_flag"),
                    handoff_team=entry.get("handoff_team"),
                    handoff_ticket=entry.get("handoff_ticket"),
                    disclaimer_shown=bool(entry.get("disclaimer_shown", False)),
                    llm_used=bool(entry.get("llm_used", False)),
                )
            )
            db.commit()

    # ------------------------------------------------------------------
    # Escalation queue
    # ------------------------------------------------------------------
    def create_handoff(
        self,
        *,
        session_id: str,
        team: str,
        reason: str,
        query: str,
        priority: str = "normal",
        patient_id: str | None = None,
    ) -> dict:
        ticket = {
            "ticket_id": f"TKT-{uuid.uuid4().hex[:8].upper()}",
            "session_id": session_id,
            "patient_masked": (patient_id[:2] + "***") if patient_id else "anonymous",
            "team": team,
            "priority": priority,
            "reason": reason,
            "query": query,
            "status": "open",
            "created_at": _now(),
        }
        with SessionLocal() as db:
            db.add(m.HandoffRow(**ticket))
            db.commit()
        return ticket

    # ------------------------------------------------------------------
    # Read views (rebuilt from the DB on access)
    # ------------------------------------------------------------------
    @property
    def sessions(self) -> dict[str, dict]:
        with SessionLocal() as db:
            rows = db.query(m.SessionRow).all()
            return {r.id: r.as_dict() for r in rows}

    @property
    def audit(self) -> list[dict]:
        """All audit entries, oldest first (so ``[-1]`` is the most recent)."""
        with SessionLocal() as db:
            rows = db.query(m.AuditLog).order_by(m.AuditLog.id).all()
            return [r.as_dict() for r in rows]

    @property
    def handoffs(self) -> list[dict]:
        with SessionLocal() as db:
            rows = db.query(m.HandoffRow).order_by(m.HandoffRow.id).all()
            return [r.as_dict() for r in rows]

    def count_sessions(self) -> int:
        with SessionLocal() as db:
            return db.scalar(select(func.count()).select_from(m.SessionRow)) or 0

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------
    def reset(self) -> None:
        """Clear all operational state (used by tests). Reference data stays."""
        with SessionLocal() as db:
            for model in (m.Message, m.Appointment, m.AuditLog, m.HandoffRow, m.SessionRow):
                db.execute(delete(model))
            db.commit()
        self._apt_counter = _APT_BASE
