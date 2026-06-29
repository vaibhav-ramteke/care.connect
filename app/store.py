"""In-memory state: sessions, audit log, escalation queue.

No database — everything lives in process memory for the hackathon MVP.
Swapping this for a real datastore later only touches this module.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self) -> None:
        self.sessions: dict[str, dict] = {}
        self.audit: list[dict] = []
        self.handoffs: list[dict] = []
        self._apt_counter = 10245  # next appointment id starts after the sample

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------
    def get_or_create_session(
        self, session_id: str | None, patient_id: str | None = None
    ) -> dict:
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]

        sid = session_id or f"sess-{uuid.uuid4().hex[:10]}"
        session = {
            "id": sid,
            "patient_id": patient_id,
            "created_at": _now(),
            "journey_stage": "symptom_discovery",
            "history": [],
            "appointments": [],
        }
        self.sessions[sid] = session
        return session

    def add_message(self, session: dict, role: str, text: str) -> None:
        session["history"].append({"role": role, "text": text, "at": _now()})

    # ------------------------------------------------------------------
    # Appointments
    # ------------------------------------------------------------------
    def next_appointment_id(self) -> str:
        self._apt_counter += 1
        return f"APT-{self._apt_counter}"

    # ------------------------------------------------------------------
    # Audit log
    # ------------------------------------------------------------------
    def log_audit(self, entry: dict) -> None:
        entry = {"at": _now(), **entry}
        self.audit.append(entry)

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
        self.handoffs.append(ticket)
        return ticket
