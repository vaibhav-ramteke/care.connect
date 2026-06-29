"""Patient Journey Agent — identifies the current journey stage.

Derives the stage primarily from the detected intent, with light keyword
hints, and keeps the stage sticky within a conversation.
"""

from __future__ import annotations

# Journey stages (requirements 10.1).
JOURNEY_STAGES = [
    "symptom_discovery",
    "doctor_discovery",
    "appointment_booking",
    "pre_visit_preparation",
    "hospital_arrival",
    "consultation",
    "diagnostics",
    "prescription_support",
    "surgery",
    "inpatient_admission",
    "discharge_planning",
    "billing_and_insurance",
    "post_discharge_care",
    "follow_up",
    "medication_reminders",
    "recovery_monitoring",
    "preventive_care",
]

_INTENT_STAGE = {
    "emergency_help": "symptom_discovery",
    "symptom_guidance": "symptom_discovery",
    "doctor_search": "doctor_discovery",
    "department_search": "doctor_discovery",
    "appointment_booking": "appointment_booking",
    "appointment_reschedule": "appointment_booking",
    "appointment_cancellation": "appointment_booking",
    "previsit_checklist": "pre_visit_preparation",
    "hospital_navigation": "hospital_arrival",
    "lab_report": "diagnostics",
    "prescription_help": "prescription_support",
    "discharge_help": "discharge_planning",
    "billing_query": "billing_and_insurance",
    "insurance_claim_query": "billing_and_insurance",
    "recovery_monitoring": "recovery_monitoring",
    "followup_booking": "follow_up",
    "medication_reminder": "medication_reminders",
    "caregiver_access": "post_discharge_care",
}

NEXT_BEST_ACTION = {
    "symptom_discovery": "Understand urgency and find the right department",
    "doctor_discovery": "Pick a doctor and book a slot",
    "appointment_booking": "Confirm the appointment and prepare for the visit",
    "pre_visit_preparation": "Carry the checklist items to your visit",
    "hospital_arrival": "Complete check-in and reach the correct counter",
    "diagnostics": "Complete tests and track report status",
    "prescription_support": "Follow the medicine schedule correctly",
    "discharge_planning": "Follow home-care steps and book follow-up",
    "billing_and_insurance": "Review charges and insurance status",
    "post_discharge_care": "Watch for warning signs and stay on schedule",
    "recovery_monitoring": "Log daily recovery and escalate red flags",
    "follow_up": "Attend the follow-up consultation",
    "medication_reminders": "Take medicines on time and refill in advance",
}


class JourneyAgent:
    def detect(self, intent: str, current_stage: str) -> str:
        return _INTENT_STAGE.get(intent, current_stage)

    def next_best_action(self, stage: str) -> str:
        return NEXT_BEST_ACTION.get(stage, "Continue your care journey")
