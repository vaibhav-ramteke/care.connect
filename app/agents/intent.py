"""Intent detection (LLM classification with keyword fallback)."""

from __future__ import annotations

from ..llm import LLMClient

# Supported intents (requirements 11.2).
INTENTS: list[str] = [
    "emergency_help",
    "symptom_guidance",
    "doctor_search",
    "department_search",
    "appointment_booking",
    "appointment_reschedule",
    "appointment_cancellation",
    "previsit_checklist",
    "hospital_navigation",
    "lab_report",
    "prescription_help",
    "discharge_help",
    "billing_query",
    "insurance_claim_query",
    "recovery_monitoring",
    "followup_booking",
    "medication_reminder",
    "caregiver_access",
    "human_handoff",
    "general",
]

# Keyword cues for the deterministic fallback. Order matters — earlier intents
# win ties, so the more specific ones are listed first.
_KEYWORDS: list[tuple[str, list[str]]] = [
    ("appointment_cancellation", ["cancel"]),
    ("appointment_reschedule", ["reschedule", "change my appointment", "postpone", "prepone"]),
    ("insurance_claim_query", ["insurance", "claim", "cashless", "policy", "reimburs", "tpa"]),
    ("billing_query", ["bill", "payment", "invoice", "charges", "cost", "pay", "estimate"]),
    ("prescription_help", ["prescription", "medicine", "tablet", "dose", "dosage", "after food", "before food"]),
    ("discharge_help", ["discharge", "discharged", "after surgery", "home care", "wound"]),
    ("lab_report", ["lab test", "lab report", "test result", "blood test", "cbc", "lipid profile", "x-ray", "report ready", "download my report"]),
    ("recovery_monitoring", ["recovery", "check-in", "pain score", "feeling weak", "since discharge"]),
    ("followup_booking", ["follow up", "follow-up", "followup", "review appointment"]),
    ("medication_reminder", ["remind", "reminder", "missed dose", "refill"]),
    ("previsit_checklist", ["what to bring", "documents", "carry", "fasting", "before my visit", "parking"]),
    ("hospital_navigation", ["where is", "which counter", "room number", "lost", "check in", "token", "wheelchair", "reached the hospital"]),
    ("caregiver_access", ["caregiver", "my father", "my mother", "my son", "my daughter", "family member", "add member"]),
    ("doctor_search", ["which doctor", "find a doctor", "doctor for", "best doctor", "available doctor", "should i consult", "should i see"]),
    ("department_search", ["which department", "department for", "specialist"]),
    ("appointment_booking", ["book", "appointment", "slot", "schedule a", "earliest available"]),
    ("symptom_guidance", ["i have", "i feel", "symptom", "pain", "fever", "cough", "headache", "should i", "is it serious"]),
    ("human_handoff", ["speak to a human", "talk to a person", "agent", "representative", "talk to someone"]),
]


class IntentDetector:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def detect(self, message: str) -> str:
        label = self.llm.classify(message, INTENTS)
        if label:
            return label
        return self._keyword_detect(message)

    @staticmethod
    def _keyword_detect(message: str) -> str:
        low = message.lower()
        for intent, cues in _KEYWORDS:
            if any(cue in low for cue in cues):
                return intent
        return "general"
