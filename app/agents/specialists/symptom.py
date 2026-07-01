"""Symptom guidance agent (safe, non-diagnostic)."""

from __future__ import annotations

from ...data import mock_data as md
from ...db import repository as repo
from ...safety import guardrails as g
from ..base import AgentContext, AgentResult, BaseAgent


class SymptomGuidanceAgent(BaseAgent):
    name = "symptom_guidance_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        dept = md.match_department(ctx.message)
        if dept:
            facts = (
                f"- We cannot diagnose, only suggest the next step.\n"
                f"- Based on the described symptoms, the relevant department is "
                f"usually {dept}.\n"
                f"- The patient can book a routine appointment, or choose "
                f"teleconsultation if available.\n"
                f"- If symptoms become severe or sudden, emergency care is advised."
            )
            fallback = (
                f"I can't diagnose the cause, but symptoms like these are usually "
                f"handled by the {dept} department. You can book an appointment, "
                f"or seek emergency care if things suddenly get worse."
            )
            data = {"recommended_department": dept, "doctors": repo.doctors_in(dept)}
            actions = ["Find a doctor", "Book appointment", "Talk to a nurse"]
        else:
            facts = (
                "- We could not confidently map the symptom to a department.\n"
                "- Suggest General Medicine as a safe first step, or talking to "
                "a nurse.\n"
                "- We cannot diagnose."
            )
            fallback = (
                "I can't diagnose this, but a General Medicine consultation is a "
                "safe first step. Would you like me to find a doctor or connect "
                "you to a nurse?"
            )
            data = {"recommended_department": "General Medicine",
                    "doctors": repo.doctors_in("General Medicine")}
            actions = ["Find a doctor", "Book appointment", "Talk to a nurse"]

        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(
            reply=reply,
            agent=self.name,
            data=data,
            quick_actions=actions,
            disclaimer=g.MEDICAL_DISCLAIMER,
            llm_used=used,
        )
