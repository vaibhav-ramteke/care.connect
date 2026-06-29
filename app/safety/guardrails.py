"""Safety & privacy guardrails — emergency detection, disclaimers, distress.

These rules are deterministic by design. Patient-safety decisions must never
depend on a best-effort LLM call, so emergency detection runs before any
routing or model invocation.
"""

from __future__ import annotations

MEDICAL_DISCLAIMER = (
    "This is general information and not a substitute for professional medical "
    "advice. Please consult a doctor for diagnosis and treatment."
)

EMERGENCY_DISCLAIMER = (
    "This may be urgent. Please seek emergency medical care immediately or call "
    "local emergency services."
)

MEDICATION_SAFETY_NOTE = (
    "Please do not change the dose, stop, or combine medicines without "
    "confirming with your doctor or pharmacist."
)

# Red-flag phrases drawn from the requirements (sections 11.5 / 16.3).
EMERGENCY_PHRASES: list[str] = [
    "chest pain",
    "chest discomfort",
    "chest tightness",
    "pressure in chest",
    "difficulty breathing",
    "breathing difficulty",
    "trouble breathing",
    "can't breathe",
    "cant breathe",
    "not breathing",
    "shortness of breath",
    "stroke",
    "face drooping",
    "slurred speech",
    "sudden weakness",
    "sudden confusion",
    "loss of consciousness",
    "unconscious",
    "fainted",
    "passing out",
    "severe bleeding",
    "heavy bleeding",
    "seizure",
    "convulsion",
    "fits",
    "severe allergic",
    "anaphyla",
    "blurred vision",
    "suicid",
    "self harm",
    "self-harm",
    "kill myself",
    "want to die",
    "overdose",
    "severe abdominal pain",
    "high fever in infant",
    "baby not breathing",
]

DISTRESS_PHRASES: list[str] = [
    "this is useless",
    "worst service",
    "very angry",
    "frustrated",
    "fed up",
    "terrible experience",
    "speak to a human",
    "talk to a person",
    "talk to someone",
]


def detect_emergency(text: str) -> str | None:
    """Return the matched red-flag phrase, or None."""
    low = text.lower()
    for phrase in EMERGENCY_PHRASES:
        if phrase in low:
            return phrase
    return None


def detect_distress(text: str) -> bool:
    low = text.lower()
    return any(phrase in low for phrase in DISTRESS_PHRASES)


# Intents whose responses are clinical and must carry the medical disclaimer.
CLINICAL_INTENTS = {
    "symptom_guidance",
    "emergency_help",
    "prescription_help",
    "discharge_help",
    "lab_report",
    "recovery_monitoring",
    "medication_reminder",
}
