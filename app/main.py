"""FastAPI application — CarePath AI backend.

Run with:  uvicorn app.main:app --reload
Interactive docs at /docs
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .agents.journey import JourneyAgent
from .agents.orchestrator import Orchestrator
from .config import settings
from .db import repository as repo
from .db.seed import init_and_seed
from .llm import LLMClient
from .schemas import ChatRequest, ChatResponse
from .store import Store

# Create tables and seed reference (+ demo) data before building singletons.
init_and_seed()

app = FastAPI(
    title=f"{settings.app_name} API",
    description=(
        f"{settings.app_tagline}. An Orchestrator AI Agent routes patient "
        "queries to specialized agents (symptom guidance, doctor finder, "
        "appointment, pre-visit, prescription, discharge, billing/insurance, "
        "human handoff) with safety guardrails. Hybrid: uses Claude when an "
        "API key is configured, otherwise deterministic rule-based logic."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared singletons.
_llm = LLMClient(settings)
_store = Store()
_orchestrator = Orchestrator(_llm, _store)
_journey = JourneyAgent()


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "mode": "llm" if _llm.enabled else "rule-based",
        "model": settings.anthropic_model if _llm.enabled else None,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Main entry point — send a patient message, get an orchestrated reply."""
    return _orchestrator.process(request)


# --------------------------------------------------------------------------- #
# Reference / demo data endpoints
# --------------------------------------------------------------------------- #
@app.get("/api/doctors")
def list_doctors(department: str | None = None) -> dict:
    doctors = repo.doctors_in(department) if department else repo.all_doctors()
    return {"count": len(doctors), "doctors": doctors}


@app.get("/api/departments")
def list_departments() -> dict:
    return {"departments": repo.list_departments()}


# --------------------------------------------------------------------------- #
# Session / journey
# --------------------------------------------------------------------------- #
@app.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    session = _store.sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        **session,
        "next_best_action": _journey.next_best_action(session["journey_stage"]),
    }


# --------------------------------------------------------------------------- #
# Admin / staff endpoints
# --------------------------------------------------------------------------- #
@app.get("/api/admin/handoffs")
def list_handoffs() -> dict:
    """Escalation queue for hospital staff."""
    return {"count": len(_store.handoffs), "handoffs": _store.handoffs}


@app.get("/api/admin/audit")
def list_audit(limit: int = 100) -> dict:
    """Conversation audit log (most recent first)."""
    entries = list(reversed(_store.audit))[:limit]
    return {"count": len(entries), "audit": entries}


@app.get("/api/admin/stats")
def stats() -> dict:
    """Lightweight analytics for an admin dashboard."""
    intents: dict[str, int] = {}
    emergencies = 0
    llm_calls = 0
    for entry in _store.audit:
        intents[entry["intent"]] = intents.get(entry["intent"], 0) + 1
        emergencies += 1 if entry.get("emergency") else 0
        llm_calls += 1 if entry.get("llm_used") else 0
    return {
        "total_conversations": len(_store.sessions),
        "total_messages": len(_store.audit),
        "emergency_escalations": emergencies,
        "open_handoffs": len([h for h in _store.handoffs if h["status"] == "open"]),
        "llm_assisted_responses": llm_calls,
        "intent_breakdown": intents,
    }
