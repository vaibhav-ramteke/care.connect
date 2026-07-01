# CarePath AI — Agentic Patient Journey Companion

Hackathon project for CitiusTech (Hackcelerate). A journey-aware, safety-first
**Patient Engagement & Communication Platform** built around an **Orchestrator
AI Agent** that routes patient queries to specialized agents — from symptom
discovery through appointment booking, prescriptions, discharge, billing, and
recovery — with healthcare safety guardrails and human escalation.

This repository contains the **working backend** (FastAPI) with a **SQLite
database** (via SQLAlchemy). Reference data (departments, doctors, demo clinical
records) and operational state (conversations, appointments, audit log, handoff
queue) are all persisted — state survives a restart.

---

## Highlights

- **Orchestrator agent** implementing the requirements flow: safety check →
  intent detection → journey-stage detection → route to a specialized agent →
  apply guardrails → human handoff → audit log.
- **Specialized agents:** Symptom Guidance, Doctor/Department Finder,
  Appointment (book/reschedule/cancel), Pre-Visit, Prescription, Discharge,
  Billing & Insurance, Human Handoff — plus Intent, Journey, and Safety agents.
- **Hybrid intelligence:** agents compute verified facts from mock data, then
  optionally ask **Claude (`claude-opus-4-8`)** to phrase a warm, simple reply.
  With **no API key the backend runs fully on deterministic rule-based logic** —
  it simply "gets smarter" when a key is added. The LLM is never trusted with
  facts (doctors, prices, diagnoses) or safety decisions.
- **Safety guardrails:** deterministic emergency red-flag detection (runs before
  any routing/LLM), mandatory medical disclaimers on clinical replies,
  medication-safety notes, distress detection, no diagnosis.
- **Operations:** persisted conversation store, audit log, escalation/handoff
  queue, and a lightweight analytics endpoint for an admin dashboard.
- **Persistence:** SQLite via SQLAlchemy ORM. A single `carepath.db` file is
  created and seeded automatically on first run — zero setup. Move to
  Postgres/MySQL later by changing only the `DATABASE_URL`.

---

## Requirements

- Python **3.14.6**
- Dependencies in [`requirements.txt`](requirements.txt)

---

## Setup

```bash
# from the repo root
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### Optional: enable the LLM path

```bash
cp .env.example .env            # then edit .env
# set ANTHROPIC_API_KEY=sk-ant-...
```

Without a key the server starts in `rule-based` mode (see `/api/health`).

### Database

No setup needed. On startup the app creates a local SQLite file
(`carepath.db`) and seeds it with reference data (departments, doctors, demo
clinical/billing records) plus a few realistic sample conversations. Delete the
file to start fresh — it is rebuilt on the next run. To point at another
database, set `DATABASE_URL` (e.g. `DATABASE_URL=postgresql+psycopg://…`).

---

## Run

```bash
uvicorn app.main:app --reload
```

- Interactive API docs (Swagger): http://127.0.0.1:8000/docs
- Health / mode check: http://127.0.0.1:8000/api/health

---

## API

| Method | Path                       | Purpose                                            |
| ------ | -------------------------- | -------------------------------------------------- |
| POST   | `/api/chat`                | Main entry point — send a patient message          |
| GET    | `/api/health`             | Status + whether LLM or rule-based mode is active  |
| GET    | `/api/doctors`            | Doctor directory (optional `?department=`)         |
| GET    | `/api/departments`        | Department list                                    |
| GET    | `/api/sessions/{id}`      | Conversation history + journey stage               |
| GET    | `/api/admin/handoffs`     | Escalation queue (staff)                           |
| GET    | `/api/admin/audit`        | Conversation audit log                             |
| GET    | `/api/admin/stats`        | Analytics for an admin dashboard                   |

### Example

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have knee pain. Which doctor should I consult?"}'
```

Response (abridged):

```json
{
  "session_id": "sess-abc123",
  "reply": "Knee pain is usually handled by Orthopedics. Dr. Kulkarni ...",
  "agent": "doctor_finder_agent",
  "intent": "doctor_search",
  "journey_stage": "doctor_discovery",
  "emergency": false,
  "disclaimer": null,
  "handoff": {"triggered": false},
  "quick_actions": ["Book earliest slot", "Pre-visit checklist"],
  "data": {"department": "Orthopedics", "doctors": [ ... ]},
  "llm_used": false
}
```

Pass the returned `session_id` back on the next call to keep conversation state
(journey stage, booked appointments).

### Demo scenarios that work today

- *"My father has chest pain and breathing difficulty."* → emergency detected,
  normal flow halted, emergency guidance + critical handoff ticket.
- *"I have knee pain. Which doctor should I consult?"* → Orthopedics + doctors.
- *"Book an appointment with Dr. Kulkarni."* → confirmed appointment + checklist.
- *"When should I take these medicines?"* → schedule from the sample prescription
  with a medication-safety disclaimer.
- *"I was discharged after surgery. What should I do at home?"* → discharge plan,
  warning signs, follow-up offer.
- *"Is my insurance approval done?"* → claim status + pending documents.

---

## Project structure

```
app/
  main.py               FastAPI app + routes (creates/seeds the DB on startup)
  config.py             Settings (env / .env), incl. DATABASE_URL
  schemas.py            Request/response models
  llm.py                Fault-tolerant Anthropic Claude wrapper (hybrid core)
  store.py              DB-backed sessions, appointments, audit log, handoff queue
  db/
    database.py         SQLAlchemy engine + session factory
    models.py           ORM models (the database schema)
    seed.py             Table creation + reference/demo data INSERTs
    repository.py       Read-only reference-data queries
  data/
    mock_data.py        Seed data (doctors, depts, Rx, bill…) + symptom matching
  safety/
    guardrails.py       Emergency detection, disclaimers, distress
  agents/
    base.py             Agent contracts + LLM "phrase verified facts" helper
    orchestrator.py     Central Orchestrator AI Agent
    intent.py           Intent detection (LLM classify + keyword fallback)
    journey.py          Journey-stage detection
    handoff.py          Human Handoff Agent
    specialists/        One module per specialized agent
      symptom.py          Symptom guidance (non-diagnostic)
      doctor_finder.py    Doctor & department finder
      appointment.py      Book / reschedule / cancel
      previsit.py         Pre-visit checklist
      prescription.py     Prescription explanation
      discharge.py        Discharge / home-care
      billing.py          Billing & insurance
      general.py          General fallback
requirements.txt
.env.example
```

---

## Safety notes

- The assistant **never diagnoses** and never changes/stops medication.
- **Emergency detection is deterministic** and runs before any model call.
- Clinical responses always carry a medical disclaimer.
- Sensitive records (prescription, bill, insurance) use **sample/demo data**;
  production would gate these behind authentication.
- Every turn is written to the audit log (query, intent, stage, agent, safety
  flags, handoff, whether the LLM was used).

---

## Out of scope (for this MVP)

Real EHR/billing/insurance integration, payments, authentication, persistence,
multilingual generation beyond best-effort LLM rephrasing, and the patient/admin
UI. These are the next steps.
