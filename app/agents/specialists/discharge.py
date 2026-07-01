"""Discharge / home-care assistant agent."""

from __future__ import annotations

from ...db import repository as repo
from ...safety import guardrails as g
from ..base import AgentContext, AgentResult, BaseAgent


class DischargeAgent(BaseAgent):
    name = "discharge_agent"

    def handle(self, ctx: AgentContext) -> AgentResult:
        ds = repo.get_discharge_summary()
        facts = (
            f"Discharge summary (sample):\n"
            f"- Reason: {ds['reason']}; {ds['condition']}.\n"
            f"- Medicines for {ds['medicines_days']} days.\n"
            f"- Wound care: {ds['wound_care']}.\n"
            f"- Activity: {ds['activity']}.\n"
            f"- {ds['follow_up']}.\n"
            f"- Warning signs to call the hospital: {', '.join(ds['warning_signs'])}."
        )
        fallback = (
            "Here's your home-care plan after discharge:\n"
            f"• Medicines for {ds['medicines_days']} days\n"
            f"• {ds['wound_care']}\n"
            f"• {ds['activity']}\n"
            f"• {ds['follow_up']}\n"
            f"• Call us immediately if you notice: {', '.join(ds['warning_signs'])}.\n\n"
            "Would you like daily recovery check-ins?"
        )
        reply, used = self.phrase(ctx, facts, fallback)
        return AgentResult(reply=reply, agent=self.name,
                           data={"discharge_summary": ds},
                           quick_actions=["Start recovery check-ins", "Book follow-up"],
                           disclaimer=g.MEDICAL_DISCLAIMER, llm_used=used)
